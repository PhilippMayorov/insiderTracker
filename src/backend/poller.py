"""Background polling service for fetching trades"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from src.backend.hashdive import HashdiveClient
from src.backend.emailer import EmailNotifier
from src.backend import crud
from src.backend.db import SessionLocal
from src.backend.settings import settings

logger = logging.getLogger(__name__)


class TradePoller:
    """Background service that polls Hashdive for new trades"""
    
    def __init__(
        self,
        hashdive_client: HashdiveClient,
        email_notifier: EmailNotifier,
        poll_interval: int = 60
    ):
        """
        Initialize the poller
        
        Args:
            hashdive_client: Hashdive API client
            email_notifier: Email notification service
            poll_interval: Seconds between polls
        """
        self.hashdive_client = hashdive_client
        self.email_notifier = email_notifier
        self.poll_interval = poll_interval
        self.running = False
        self.task = None
    
    async def start(self):
        """Start the background polling loop"""
        if self.running:
            logger.warning("Poller already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._poll_loop())
        logger.info("Trade poller started")
    
    async def stop(self):
        """Stop the background polling loop"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Trade poller stopped")
    
    async def _poll_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                await self.poll_once()
            except Exception as e:
                logger.error(f"Error in poll loop: {e}", exc_info=True)
            
            # Wait for next poll interval
            await asyncio.sleep(self.poll_interval)
    
    async def poll_once(self):
        """Execute one polling cycle for all tracked wallets"""
        db = SessionLocal()
        try:
            # Get all tracked wallets
            wallets = crud.get_tracked_wallets(db)
            
            if not wallets:
                logger.debug("No tracked wallets found")
                return
            
            logger.info(f"Polling {len(wallets)} tracked wallets")
            
            # Poll each wallet (with rate limiting)
            for wallet in wallets:
                try:
                    await self.poll_wallet(db, wallet)
                    
                    # Rate limiting: 1 request per second
                    await asyncio.sleep(1.05)
                    
                except Exception as e:
                    logger.error(f"Error polling wallet {wallet.wallet_address}: {e}")
            
            logger.info("Polling cycle complete")
            
        finally:
            db.close()
    
    async def poll_wallet(self, db: Session, wallet):
        """
        Poll a single wallet for new trades
        
        Args:
            db: Database session
            wallet: TrackedWallet model instance
        """
        wallet_address = wallet.wallet_address
        logger.debug(f"Polling wallet: {wallet_address}")
        
        # Calculate lookback time (default: 7 days)
        start_time = datetime.utcnow() - timedelta(days=settings.initial_lookback_days)
        
        # Fetch trades from Hashdive
        trades = self.hashdive_client.get_trades(
            wallet_address=wallet_address,
            start_time=start_time,
            limit=100
        )
        
        if not trades:
            logger.debug(f"No trades found for wallet {wallet_address}")
            return
        
        new_trades_count = 0
        
        # Process each trade
        for trade_data in trades:
            try:
                # Attempt to insert trade (deduplication happens in DB)
                trade = crud.create_trade(db, trade_data)
                
                if trade:
                    # New trade detected
                    new_trades_count += 1
                    logger.info(f"New trade detected: {trade.trade_uid}")
                    
                    # Send alert if enabled and meets threshold
                    if wallet.alerts_enabled and self.should_send_alert(trade):
                        await self.send_alert(db, wallet, trade)
                
            except Exception as e:
                logger.error(f"Error processing trade: {e}")
        
        if new_trades_count > 0:
            logger.info(f"Found {new_trades_count} new trades for wallet {wallet_address}")
    
    def should_send_alert(self, trade) -> bool:
        """Determine if an alert should be sent for this trade"""
        # Check minimum trade size
        if trade.usd_amount and trade.usd_amount < settings.min_trade_size_usd:
            return False
        
        return True
    
    async def send_alert(self, db: Session, wallet, trade):
        """
        Send email alert for a new trade
        
        Args:
            db: Database session
            wallet: TrackedWallet instance
            trade: Trade instance
        """
        # Check if alert was already sent
        if crud.was_alert_sent(db, trade.trade_uid):
            logger.debug(f"Alert already sent for trade {trade.trade_uid}")
            return
        
        # Prepare trade data for email
        trade_data = {
            "trade_uid": trade.trade_uid,
            "market_name": trade.market_name,
            "asset_id": trade.asset_id,
            "side": trade.side,
            "price": trade.price,
            "usd_amount": trade.usd_amount,
            "shares": trade.shares,
            "timestamp": trade.timestamp
        }
        
        # Send email
        success, error_message = self.email_notifier.send_trade_alert(
            wallet_address=wallet.wallet_address,
            custom_name=wallet.custom_name or wallet.wallet_address[:8],
            trade=trade_data
        )
        
        # Log the alert attempt
        crud.create_alert_log(
            db=db,
            trade_uid=trade.trade_uid,
            wallet_address=wallet.wallet_address,
            sent_to=settings.email_to,
            status="success" if success else "failed",
            error_message=error_message if not success else None
        )
        
        if success:
            logger.info(f"Alert sent for trade {trade.trade_uid}")
        else:
            logger.error(f"Alert failed for trade {trade.trade_uid}: {error_message}")
