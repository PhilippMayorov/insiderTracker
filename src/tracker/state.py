"""Trade state tracking - keeps track of last seen trades"""
import logging
import sqlite3
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class TradeState:
    """Manages state of seen trades to prevent duplicate alerts"""
    
    def __init__(self, db_path: str = "data/trades.db"):
        """
        Initialize trade state tracker
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist"""
        try:
            # Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seen_trades (
                    trade_id TEXT PRIMARY KEY,
                    wallet_address TEXT NOT NULL,
                    market_name TEXT,
                    side TEXT,
                    price REAL,
                    size REAL,
                    value_usd REAL,
                    timestamp INTEGER,
                    first_seen_at INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_wallet_address 
                ON seen_trades(wallet_address)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON seen_trades(timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise
    
    def is_trade_seen(self, trade_id: str) -> bool:
        """
        Check if a trade has been seen before
        
        Args:
            trade_id: Unique trade identifier
            
        Returns:
            True if trade was seen before, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT COUNT(*) FROM seen_trades WHERE trade_id = ?",
                (trade_id,)
            )
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking trade {trade_id}: {e}")
            return True  # Assume seen to prevent duplicate alerts on error
    
    def mark_trade_seen(self, trade: Dict[str, Any]) -> bool:
        """
        Mark a trade as seen
        
        Args:
            trade: Trade data dictionary
            
        Returns:
            True if successfully marked, False otherwise
        """
        try:
            trade_id = trade.get("id") or trade.get("trade_id")
            
            if not trade_id:
                logger.warning("Trade missing ID, cannot mark as seen")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = int(datetime.now().timestamp())
            
            cursor.execute("""
                INSERT OR REPLACE INTO seen_trades 
                (trade_id, wallet_address, market_name, side, price, size, 
                 value_usd, timestamp, first_seen_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_id,
                trade.get("wallet_address", ""),
                trade.get("market_name", ""),
                trade.get("side", ""),
                trade.get("price"),
                trade.get("size"),
                trade.get("value_usd"),
                trade.get("timestamp"),
                now,
                now
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Marked trade {trade_id} as seen")
            return True
            
        except Exception as e:
            logger.error(f"Error marking trade as seen: {e}")
            return False
    
    def get_last_trade_timestamp(self, wallet_address: str) -> Optional[int]:
        """
        Get the timestamp of the last seen trade for a wallet
        
        Args:
            wallet_address: Wallet address to query
            
        Returns:
            Unix timestamp of last trade, or None if no trades seen
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT MAX(timestamp) 
                FROM seen_trades 
                WHERE wallet_address = ?
            """, (wallet_address,))
            
            result = cursor.fetchone()[0]
            conn.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting last timestamp for {wallet_address}: {e}")
            return None
    
    def get_seen_trade_ids(self, wallet_address: str, limit: int = 1000) -> Set[str]:
        """
        Get a set of seen trade IDs for a wallet
        
        Args:
            wallet_address: Wallet address to query
            limit: Maximum number of IDs to return
            
        Returns:
            Set of trade IDs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT trade_id 
                FROM seen_trades 
                WHERE wallet_address = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (wallet_address, limit))
            
            trade_ids = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            return trade_ids
            
        except Exception as e:
            logger.error(f"Error getting seen trade IDs: {e}")
            return set()
    
    def cleanup_old_trades(self, days: int = 30) -> int:
        """
        Remove trades older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of trades deleted
        """
        try:
            cutoff_timestamp = int((datetime.now().timestamp() - (days * 86400)))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM seen_trades 
                WHERE timestamp < ?
            """, (cutoff_timestamp,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old trades")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up old trades: {e}")
            return 0
