"""SMTP Email notification system"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
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
        to_email: str,
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
            to_email: Recipient email address
            use_tls: Whether to use TLS encryption
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.to_email = to_email
        self.use_tls = use_tls
    
    def send_trade_alert(
        self,
        wallet_address: str,
        custom_name: str,
        trade: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Send email alert for a new trade
        
        Args:
            wallet_address: Wallet address
            custom_name: Custom name for the wallet
            trade: Trade data dictionary
            
        Returns:
            (success: bool, error_message: str)
        """
        try:
            subject = f"🚨 New Trade Alert: {custom_name or wallet_address[:8]}"
            body = self._format_trade_email(wallet_address, custom_name, trade)
            
            return self._send_email(subject, body)
            
        except Exception as e:
            error_msg = f"Failed to send trade alert: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _format_trade_email(
        self,
        wallet_address: str,
        custom_name: str,
        trade: Dict[str, Any]
    ) -> str:
        """Format trade data into email body"""
        
        # Format timestamp
        timestamp_str = trade.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            timestamp_display = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            timestamp_display = timestamp_str
        
        # Build email body
        body = f"""
New PolyMarket Trade Detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WALLET INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name:           {custom_name or 'Unknown'}
Address:        {wallet_address}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRADE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Market:         {trade.get('market_name', 'Unknown')}
Asset ID:       {trade.get('asset_id', 'N/A')}
Side:           {trade.get('side', 'Unknown').upper()}
Price:          ${trade.get('price', 0):.4f}
Shares:         {trade.get('shares', 0):,.2f}
USD Amount:     ${trade.get('usd_amount', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIMING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Timestamp:      {timestamp_display}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This is an automated alert from your PolyMarket Trade Tracker.
"""
        
        return body
    
    def _send_email(self, subject: str, body: str) -> tuple[bool, str]:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect and send
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {self.to_email}")
            return True, ""
            
        except Exception as e:
            error_msg = f"SMTP error: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def test_connection(self) -> tuple[bool, str]:
        """Test SMTP connection"""
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10)
            
            server.login(self.smtp_user, self.smtp_password)
            server.quit()
            
            logger.info("SMTP connection test successful")
            return True, "Connection successful"
            
        except Exception as e:
            error_msg = f"SMTP connection failed: {e}"
            logger.error(error_msg)
            return False, error_msg
