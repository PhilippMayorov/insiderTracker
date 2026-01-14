"""FastAPI Backend for PolyMarket Trade Tracker"""
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.backend.db import get_db, init_db
from src.backend.settings import settings
from src.backend.hashdive import HashdiveClient
from src.backend.emailer import EmailNotifier
from src.backend.poller import TradePoller
from src.backend import crud, models

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global poller instance
poller: Optional[TradePoller] = None


# ============================================================================
# Pydantic Models (Request/Response)
# ============================================================================

class WalletCreate(BaseModel):
    wallet_address: str
    custom_name: Optional[str] = None
    main_market: Optional[str] = None
    alerts_enabled: bool = True


class WalletUpdate(BaseModel):
    custom_name: Optional[str] = None
    main_market: Optional[str] = None
    alerts_enabled: Optional[bool] = None


class WalletResponse(BaseModel):
    wallet_address: str
    custom_name: Optional[str]
    main_market: Optional[str]
    alerts_enabled: bool
    created_at: str
    
    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    trade_uid: str
    wallet_address: str
    asset_id: Optional[str]
    market_name: Optional[str]
    side: Optional[str]
    share_type: Optional[str]
    price: Optional[float]
    usd_amount: Optional[float]
    shares: Optional[float]
    timestamp: str
    created_at: str
    
    class Config:
        from_attributes = True


class TradesQueryResponse(BaseModel):
    items: List[TradeResponse]
    total_results: int
    total_pages: int
    current_page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str
    poller_running: bool
    database_connected: bool


# ============================================================================
# FastAPI Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and start poller
    global poller
    
    # Startup
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Starting background poller...")
    hashdive_client = HashdiveClient(
        api_key=settings.hashdive_api_key,
        base_url=settings.hashdive_api_url
    )
    
    email_notifier = EmailNotifier(
        smtp_host=settings.email_host,
        smtp_port=settings.email_port,
        smtp_user=settings.email_username,
        smtp_password=settings.email_password,
        from_email=settings.email_from,
        to_email=settings.email_to,
        use_tls=settings.email_use_tls
    )
    
    poller = TradePoller(
        hashdive_client=hashdive_client,
        email_notifier=email_notifier,
        # poll_interval=settings.poll_interval_seconds
        poll_interval=100000  # For testing purposes
    )
    
    await poller.start()
    logger.info("Backend services started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down background poller...")
    if poller:
        await poller.stop()
    logger.info("Backend services stopped")


# Create FastAPI app
app = FastAPI(
    title="PolyMarket Trade Tracker API",
    description="Backend API for tracking PolyMarket wallet trades",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Wallet Management Endpoints
# ============================================================================

@app.get("/favorites", response_model=List[WalletResponse])
def get_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all tracked wallets (favorites)"""
    wallets = crud.get_tracked_wallets(db, skip=skip, limit=limit)
    return [WalletResponse.from_orm(w) for w in wallets]


@app.post("/favorites", response_model=WalletResponse, status_code=201)
def create_favorite(
    wallet: WalletCreate,
    db: Session = Depends(get_db)
):
    """Add a new tracked wallet"""
    # Check if wallet already exists
    existing = crud.get_wallet(db, wallet.wallet_address)
    if existing:
        raise HTTPException(status_code=400, detail="Wallet already tracked")
    
    # Create wallet
    new_wallet = crud.create_wallet(
        db=db,
        wallet_address=wallet.wallet_address,
        custom_name=wallet.custom_name,
        main_market=wallet.main_market,
        alerts_enabled=wallet.alerts_enabled
    )
    
    logger.info(f"Added new tracked wallet: {wallet.wallet_address}")
    return WalletResponse.from_orm(new_wallet)


@app.patch("/favorites/{wallet_address}", response_model=WalletResponse)
def update_favorite(
    wallet_address: str,
    updates: WalletUpdate,
    db: Session = Depends(get_db)
):
    """Update a tracked wallet"""
    updated_wallet = crud.update_wallet(
        db=db,
        wallet_address=wallet_address,
        custom_name=updates.custom_name,
        main_market=updates.main_market,
        alerts_enabled=updates.alerts_enabled
    )
    
    if not updated_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    logger.info(f"Updated wallet: {wallet_address}")
    return WalletResponse.from_orm(updated_wallet)


@app.delete("/favorites/{wallet_address}", status_code=204)
def delete_favorite(
    wallet_address: str,
    db: Session = Depends(get_db)
):
    """Remove a tracked wallet"""
    success = crud.delete_wallet(db, wallet_address)
    
    if not success:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    logger.info(f"Deleted wallet: {wallet_address}")
    return None


# ============================================================================
# Trades Query Endpoints
# ============================================================================

@app.get("/trades", response_model=TradesQueryResponse)
def get_trades(
    wallet: Optional[str] = Query(None, description="Filter by wallet address"),
    side: Optional[str] = Query(None, description="Filter by side (buy/sell)"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_usd: Optional[float] = Query(None, description="Minimum USD amount"),
    max_usd: Optional[float] = Query(None, description="Maximum USD amount"),
    market: Optional[str] = Query(None, description="Filter by market name (partial match)"),
    sort_by: Optional[str] = Query(None, description="Sort by column: timestamp, side, share_type, market, price, usd_amount, shares, wallet"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Query trades with filters and pagination
    
    Returns paginated trade results with total count
    """
    skip = (page - 1) * page_size
    
    trades, total_count = crud.get_trades(
        db=db,
        wallet_address=wallet,
        side=side,
        min_price=min_price,
        max_price=max_price,
        min_usd=min_usd,
        max_usd=max_usd,
        market=market,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=page_size
    )
    
    total_pages = (total_count + page_size - 1) // page_size
    
    return TradesQueryResponse(
        items=[TradeResponse.from_orm(t) for t in trades],
        total_results=total_count,
        total_pages=total_pages,
        current_page=page,
        page_size=page_size
    )


@app.get("/markets", response_model=List[str])
def get_markets(
    wallet: Optional[str] = Query(None, description="Filter by wallet address or custom name"),
    db: Session = Depends(get_db)
):
    """Get distinct market names (for filter dropdown)"""
    # Convert custom name to wallet address if needed
    wallet_address = wallet
    if wallet:
        tracked_wallet = crud.get_wallet_by_name(db, wallet)
        if tracked_wallet:
            wallet_address = tracked_wallet.wallet_address
    
    markets = crud.get_distinct_markets(db, wallet_address=wallet_address)
    return markets


# ============================================================================
# System Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    global poller
    
    # Test database connection
    db_connected = False
    try:
        db.execute("SELECT 1")
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    return HealthResponse(
        status="ok" if db_connected else "degraded",
        poller_running=poller is not None and poller.running,
        database_connected=db_connected
    )


@app.post("/poller/run-once", status_code=202)
async def trigger_poll():
    """Manually trigger a polling cycle (dev/testing only)"""
    global poller
    
    if not poller:
        raise HTTPException(status_code=503, detail="Poller not initialized")
    
    # Trigger poll in background
    import asyncio
    asyncio.create_task(poller.poll_once())
    
    return {"message": "Polling cycle triggered"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "PolyMarket Trade Tracker API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
