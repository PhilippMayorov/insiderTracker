"""Alert logic - determines when to send notifications"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alert logic and batching"""
    
    def __init__(
        self,
        min_trade_size_usd: float = 0,
        batch_alerts: bool = False,
        batch_window_seconds: int = 300
    ):
        """
        Initialize alert manager
        
        Args:
            min_trade_size_usd: Minimum trade size to alert on (USD)
            batch_alerts: Whether to batch multiple alerts together
            batch_window_seconds: Time window for batching alerts
        """
        self.min_trade_size_usd = min_trade_size_usd
        self.batch_alerts = batch_alerts
        self.batch_window_seconds = batch_window_seconds
        self.pending_alerts: List[Dict[str, Any]] = []
        self.last_batch_sent: Optional[datetime] = None
    
    def should_alert(self, trade: Dict[str, Any]) -> bool:
        """
        Determine if a trade should trigger an alert
        
        Args:
            trade: Trade data dictionary
            
        Returns:
            True if alert should be sent, False otherwise
        """
        # Check minimum trade size
        value_usd = trade.get("value_usd", 0)
        
        if value_usd < self.min_trade_size_usd:
            logger.debug(
                f"Trade value ${value_usd:.2f} below threshold "
                f"${self.min_trade_size_usd:.2f}, skipping alert"
            )
            return False
        
        # Add more filtering logic here if needed
        # For example:
        # - Exclude certain markets
        # - Only alert on specific sides (YES/NO)
        # - Time-based filtering
        
        return True
    
    def add_pending_alert(
        self,
        wallet_address: str,
        wallet_name: str,
        trade: Dict[str, Any]
    ):
        """
        Add an alert to the pending queue
        
        Args:
            wallet_address: Wallet address
            wallet_name: Friendly wallet name
            trade: Trade data
        """
        self.pending_alerts.append({
            "wallet_address": wallet_address,
            "wallet_name": wallet_name,
            "trade": trade,
            "added_at": datetime.now()
        })
        
        logger.debug(f"Added alert to pending queue ({len(self.pending_alerts)} total)")
    
    def should_flush_batch(self) -> bool:
        """
        Check if pending alerts should be sent
        
        Returns:
            True if batch should be flushed, False otherwise
        """
        if not self.batch_alerts:
            return len(self.pending_alerts) > 0
        
        if not self.pending_alerts:
            return False
        
        # Check if batch window has elapsed
        if self.last_batch_sent is None:
            return True
        
        elapsed = (datetime.now() - self.last_batch_sent).total_seconds()
        
        return elapsed >= self.batch_window_seconds
    
    def get_pending_alerts(self) -> List[Dict[str, Any]]:
        """
        Get and clear pending alerts
        
        Returns:
            List of pending alert dictionaries
        """
        alerts = self.pending_alerts.copy()
        self.pending_alerts.clear()
        self.last_batch_sent = datetime.now()
        
        return alerts
    
    def group_alerts_by_wallet(
        self,
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group alerts by wallet
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Dictionary mapping wallet names to lists of trades
        """
        grouped = {}
        
        for alert in alerts:
            wallet_name = alert["wallet_name"]
            
            if wallet_name not in grouped:
                grouped[wallet_name] = []
            
            grouped[wallet_name].append(alert["trade"])
        
        return grouped
    
    def format_alert_summary(self, alerts: List[Dict[str, Any]]) -> str:
        """
        Format a summary of pending alerts
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Human-readable summary string
        """
        if not alerts:
            return "No pending alerts"
        
        grouped = self.group_alerts_by_wallet(alerts)
        
        summary_lines = [f"{len(alerts)} pending alerts:"]
        
        for wallet_name, trades in grouped.items():
            total_value = sum(t.get("value_usd", 0) for t in trades)
            summary_lines.append(
                f"  {wallet_name}: {len(trades)} trades (${total_value:.2f})"
            )
        
        return "\n".join(summary_lines)
