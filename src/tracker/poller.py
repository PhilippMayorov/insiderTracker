"""Poller - periodically checks for new trades"""
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import yaml

from integrations.hashdive import HashdiveClient
from tracker.state import TradeState
from tracker.alerts import AlertManager
from email.smtp import EmailNotifier

logger = logging.getLogger(__name__)


class TradePoller:
    """Polls for new trades from tracked wallets"""
    
    def __init__(
        self,
        hashdive_client: HashdiveClient,
        trade_state: TradeState,
        alert_manager: AlertManager,
        email_notifier: EmailNotifier,
        config_path: str = "config/wallets.yaml"
    ):
        """
        Initialize trade poller
        
        Args:
            hashdive_client: Client for fetching trade data
            trade_state: State tracker for seen trades
            alert_manager: Alert logic manager
            email_notifier: Email notification sender
            config_path: Path to wallets configuration file
        """
        self.hashdive_client = hashdive_client
        self.trade_state = trade_state
        self.alert_manager = alert_manager
        self.email_notifier = email_notifier
        self.config_path = config_path
        self.config = self._load_config()
        self.running = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {
                "wallets": [],
                "polling": {"interval_seconds": 60},
                "filters": {}
            }
    
    def get_enabled_wallets(self) -> List[Dict[str, Any]]:
        """Get list of enabled wallets from configuration"""
        wallets = self.config.get("wallets", [])
        return [w for w in wallets if w.get("enabled", True)]
    
    def poll_wallet(self, wallet: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Poll a single wallet for new trades
        
        Args:
            wallet: Wallet configuration dictionary
            
        Returns:
            List of new (unseen) trades
        """
        wallet_address = wallet["address"]
        wallet_name = wallet.get("name", wallet_address[:8])
        
        logger.info(f"Polling wallet: {wallet_name}")
        
        # Determine lookback time
        last_timestamp = self.trade_state.get_last_trade_timestamp(wallet_address)
        
        if last_timestamp:
            start_time = datetime.fromtimestamp(last_timestamp)
        else:
            # First run - look back according to config
            lookback_hours = self.config.get("polling", {}).get("initial_lookback_hours", 24)
            start_time = datetime.now() - timedelta(hours=lookback_hours)
        
        # Fetch trades from API
        trades = self.hashdive_client.get_trades(
            wallet_address=wallet_address,
            start_time=start_time,
            limit=100
        )
        
        # Filter for new trades
        new_trades = []
        
        for trade in trades:
            # Enrich trade data
            trade = self.hashdive_client.enrich_trade(trade)
            trade["wallet_address"] = wallet_address
            
            trade_id = trade.get("id") or trade.get("trade_id")
            
            if not trade_id:
                logger.warning("Trade missing ID, skipping")
                continue
            
            # Check if we've seen this trade
            if not self.trade_state.is_trade_seen(trade_id):
                logger.info(f"New trade detected: {trade_id}")
                new_trades.append(trade)
                
                # Mark as seen
                self.trade_state.mark_trade_seen(trade)
                
                # Check if should alert
                if self.alert_manager.should_alert(trade):
                    self.alert_manager.add_pending_alert(
                        wallet_address=wallet_address,
                        wallet_name=wallet_name,
                        trade=trade
                    )
        
        logger.info(f"Found {len(new_trades)} new trades for {wallet_name}")
        
        return new_trades
    
    def poll_all_wallets(self):
        """Poll all enabled wallets"""
        wallets = self.get_enabled_wallets()
        
        if not wallets:
            logger.warning("No enabled wallets to poll")
            return
        
        logger.info(f"Polling {len(wallets)} wallets")
        
        for wallet in wallets:
            try:
                self.poll_wallet(wallet)
            except Exception as e:
                logger.error(f"Error polling wallet {wallet.get('name', 'unknown')}: {e}")
        
        # Check if we should send alerts
        if self.alert_manager.should_flush_batch():
            self.send_pending_alerts()
    
    def send_pending_alerts(self):
        """Send any pending alerts"""
        alerts = self.alert_manager.get_pending_alerts()
        
        if not alerts:
            return
        
        logger.info(f"Sending {len(alerts)} alerts")
        
        if self.alert_manager.batch_alerts and len(alerts) > 1:
            # Send as batch
            grouped = self.alert_manager.group_alerts_by_wallet(alerts)
            self.email_notifier.send_batch_alert(grouped)
        else:
            # Send individual alerts
            for alert in alerts:
                self.email_notifier.send_trade_alert(
                    wallet_address=alert["wallet_address"],
                    wallet_name=alert["wallet_name"],
                    trade=alert["trade"]
                )
    
    def run_once(self):
        """Run a single polling iteration"""
        logger.info("Starting polling iteration")
        self.poll_all_wallets()
        logger.info("Polling iteration complete")
    
    def run_continuous(self):
        """Run continuous polling loop"""
        interval = self.config.get("polling", {}).get("interval_seconds", 60)
        
        logger.info(f"Starting continuous polling (interval: {interval}s)")
        self.running = True
        
        try:
            while self.running:
                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"Error in polling iteration: {e}")
                
                # Sleep until next iteration
                logger.info(f"Sleeping for {interval} seconds")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping poller")
            self.running = False
    
    def stop(self):
        """Stop the continuous polling loop"""
        logger.info("Stopping poller")
        self.running = False
