"""CRUD operations for database access"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from src.backend.models import TrackedWallet, Trade, AlertLog


# ============================================================================
# Wallet CRUD
# ============================================================================

def get_tracked_wallets(db: Session, skip: int = 0, limit: int = 100) -> List[TrackedWallet]:
    """Get all tracked wallets"""
    return db.query(TrackedWallet).offset(skip).limit(limit).all()


def get_wallet(db: Session, wallet_address: str) -> Optional[TrackedWallet]:
    """Get a specific wallet by address"""
    return db.query(TrackedWallet).filter(TrackedWallet.wallet_address == wallet_address).first()


def get_wallet_by_name(db: Session, custom_name: str) -> Optional[TrackedWallet]:
    """Get a specific wallet by custom name"""
    return db.query(TrackedWallet).filter(TrackedWallet.custom_name == custom_name).first()


def create_wallet(
    db: Session,
    wallet_address: str,
    custom_name: Optional[str] = None,
    main_market: Optional[str] = None,
    alerts_enabled: bool = True
) -> TrackedWallet:
    """Add a new tracked wallet"""
    wallet = TrackedWallet(
        wallet_address=wallet_address,
        custom_name=custom_name,
        main_market=main_market,
        alerts_enabled=1 if alerts_enabled else 0,
        created_at=datetime.utcnow().isoformat()
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def update_wallet(
    db: Session,
    wallet_address: str,
    custom_name: Optional[str] = None,
    main_market: Optional[str] = None,
    alerts_enabled: Optional[bool] = None
) -> Optional[TrackedWallet]:
    """Update wallet details"""
    wallet = get_wallet(db, wallet_address)
    if not wallet:
        return None
    
    if custom_name is not None:
        wallet.custom_name = custom_name
    if main_market is not None:
        wallet.main_market = main_market
    if alerts_enabled is not None:
        wallet.alerts_enabled = 1 if alerts_enabled else 0
    
    db.commit()
    db.refresh(wallet)
    return wallet


def delete_wallet(db: Session, wallet_address: str) -> bool:
    """Delete a tracked wallet"""
    wallet = get_wallet(db, wallet_address)
    if not wallet:
        return False
    
    db.delete(wallet)
    db.commit()
    return True


# ============================================================================
# Trade CRUD
# ============================================================================

def get_trades(
    db: Session,
    wallet_address: Optional[str] = None,
    side: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_usd: Optional[float] = None,
    max_usd: Optional[float] = None,
    market: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    skip: int = 0,
    limit: int = 50
) -> tuple[List[Trade], int]:
    """
    Query trades with filters, sorting, and pagination
    Returns (trades, total_count)
    """
    query = db.query(Trade)
    
    # Apply filters
    if wallet_address:
        # Check if it's a custom name or wallet address
        # First try to find a wallet with this custom name
        tracked_wallet = db.query(TrackedWallet).filter(
            TrackedWallet.custom_name == wallet_address
        ).first()
        
        if tracked_wallet:
            # It's a custom name, use the actual wallet address
            query = query.filter(Trade.wallet_address == tracked_wallet.wallet_address)
        else:
            # It's a wallet address
            query = query.filter(Trade.wallet_address == wallet_address)
    
    if side:
        query = query.filter(Trade.side == side.lower())
    
    if min_price is not None:
        query = query.filter(Trade.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Trade.price <= max_price)
    
    if min_usd is not None:
        query = query.filter(Trade.usd_amount >= min_usd)
    
    if max_usd is not None:
        query = query.filter(Trade.usd_amount <= max_usd)
    
    if market:
        query = query.filter(Trade.market_name.ilike(f"%{market}%"))
    
    # Get total count
    total_count = query.count()
    
    # Apply sorting
    sort_column_map = {
        "timestamp": Trade.timestamp,
        "side": Trade.side,
        "share_type": Trade.share_type,
        "market": Trade.market_name,
        "price": Trade.price,
        "usd_amount": Trade.usd_amount,
        "shares": Trade.shares,
        "wallet": Trade.wallet_address
    }
    
    if sort_by and sort_by in sort_column_map:
        sort_column = sort_column_map[sort_by]
        if sort_order and sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
    else:
        # Default: sort by timestamp descending (most recent first)
        query = query.order_by(Trade.timestamp.desc())
    
    # Apply pagination
    trades = query.offset(skip).limit(limit).all()
    
    return trades, total_count


def get_trade(db: Session, trade_uid: str) -> Optional[Trade]:
    """Get a specific trade by UID"""
    return db.query(Trade).filter(Trade.trade_uid == trade_uid).first()


def create_trade(db: Session, trade_data: Dict[str, Any]) -> Optional[Trade]:
    """
    Create a new trade record
    Returns None if trade already exists (deduplication)
    """
    trade_uid = trade_data.get("trade_uid")
    
    # Check if trade already exists
    existing = get_trade(db, trade_uid)
    if existing:
        return None
    
    trade = Trade(
        trade_uid=trade_uid,
        wallet_address=trade_data.get("wallet_address"),
        asset_id=trade_data.get("asset_id"),
        market_name=trade_data.get("market_name"),
        side=trade_data.get("side"),
        share_type=trade_data.get("share_type"),
        price=trade_data.get("price"),
        usd_amount=trade_data.get("usd_amount"),
        shares=trade_data.get("shares"),
        timestamp=trade_data.get("timestamp"),
        
        # Market info fields
        market_question=trade_data.get("market_question"),
        market_outcome=trade_data.get("market_outcome"),
        market_tags=trade_data.get("market_tags"),
        market_target_price=trade_data.get("market_target_price"),
        market_resolved=trade_data.get("market_resolved"),
        market_is_winner=trade_data.get("market_is_winner"),
        market_resolved_price=trade_data.get("market_resolved_price"),
        
        raw_json=json.dumps(trade_data.get("raw", {})),
        created_at=datetime.utcnow().isoformat()
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def bulk_create_trades(db: Session, trades_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Bulk import trades from a list of trade dictionaries
    Handles deduplication automatically
    
    Args:
        db: Database session
        trades_data: List of normalized trade dictionaries
        
    Returns:
        Dictionary with counts: {"imported": X, "skipped": Y, "total": Z}
    """
    imported = 0
    skipped = 0
    
    for trade_data in trades_data:
        result = create_trade(db, trade_data)
        if result:
            imported += 1
        else:
            skipped += 1
    
    return {
        "imported": imported,
        "skipped": skipped,
        "total": len(trades_data)
    }


def get_distinct_markets(db: Session, wallet_address: Optional[str] = None) -> List[str]:
    """Get distinct market names for filter dropdown"""
    query = db.query(Trade.market_name).distinct()
    
    if wallet_address:
        query = query.filter(Trade.wallet_address == wallet_address)
    
    markets = [m[0] for m in query.all() if m[0]]
    return sorted(markets)


# ============================================================================
# Alert Log CRUD
# ============================================================================

def create_alert_log(
    db: Session,
    trade_uid: str,
    wallet_address: str,
    sent_to: str,
    status: str,
    error_message: Optional[str] = None
) -> AlertLog:
    """Log an email alert attempt"""
    alert = AlertLog(
        trade_uid=trade_uid,
        wallet_address=wallet_address,
        sent_to=sent_to,
        sent_at=datetime.utcnow().isoformat(),
        status=status,
        error_message=error_message
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def was_alert_sent(db: Session, trade_uid: str) -> bool:
    """Check if an alert was already sent for this trade"""
    return db.query(AlertLog).filter(AlertLog.trade_uid == trade_uid).first() is not None
