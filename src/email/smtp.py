"""SMTP Email notification system"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Send email notifications for new trades"""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        to_emails: List[str],
        use_tls: bool = True
    ):
        """
        Initialize email notifier
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Email address to send from
            to_emails: List of recipient email addresses
            use_tls: Whether to use TLS encryption
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.to_emails = to_emails
        self.use_tls = use_tls
    
    def send_trade_alert(
        self,
        wallet_address: str,
        wallet_name: str,
        trade: Dict[str, Any]
    ) -> bool:
        """
        Send an email alert for a new trade
        
        Args:
            wallet_address: The wallet address that made the trade
            wallet_name: Friendly name for the wallet
            trade: Trade data dictionary
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = f"🚨 New Trade Alert: {wallet_name}"
            body = self._format_trade_email(wallet_address, wallet_name, trade)
            
            return self._send_email(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending trade alert: {e}")
            return False
    
    def send_batch_alert(
        self,
        trades_by_wallet: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        """
        Send a batch alert for multiple trades
        
        Args:
            trades_by_wallet: Dictionary mapping wallet names to lists of trades
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            total_trades = sum(len(trades) for trades in trades_by_wallet.values())
            subject = f"🚨 Trade Alert: {total_trades} New Trades"
            body = self._format_batch_email(trades_by_wallet)
            
            return self._send_email(subject, body)
            
        except Exception as e:
            logger.error(f"Error sending batch alert: {e}")
            return False
    
    def _format_trade_email(
        self,
        wallet_address: str,
        wallet_name: str,
        trade: Dict[str, Any]
    ) -> str:
        """Format trade data into email body"""
        market_name = trade.get("market_name", "Unknown Market")
        side = trade.get("side", "UNKNOWN")
        price = trade.get("price", 0)
        size = trade.get("size", 0)
        value_usd = trade.get("value_usd", price * size)
        timestamp = trade.get("timestamp_dt", trade.get("timestamp", "Unknown"))
        
        body = f"""
A new trade has been detected from tracked wallet: {wallet_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRADE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Wallet: {wallet_name}
Address: {wallet_address}

Market: {market_name}
Side: {side}
Price: ${price:.4f}
Size: {size}
Value: ${value_usd:.2f}

Timestamp: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from PolyMarket Trade Tracker.
"""
        return body
    
    def _format_batch_email(
        self,
        trades_by_wallet: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Format multiple trades into email body"""
        total_trades = sum(len(trades) for trades in trades_by_wallet.values())
        
        body = f"""
{total_trades} new trades detected from tracked wallets.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRADE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for wallet_name, trades in trades_by_wallet.items():
            body += f"\n{wallet_name} ({len(trades)} trades):\n"
            
            for trade in trades:
                market = trade.get("market_name", "Unknown")
                side = trade.get("side", "?")
                value = trade.get("value_usd", 0)
                body += f"  • {market} - {side} - ${value:.2f}\n"
        
        body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from PolyMarket Trade Tracker.
"""
        return body
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send an email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            logger.debug(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}")
            
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(self.to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test SMTP connection and credentials"""
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            server.login(self.smtp_user, self.smtp_password)
            server.quit()
            
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
