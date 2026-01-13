"""Hashdive API Client for fetching PolyMarket trade data"""
import logging
import hashlib
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class HashdiveClient:
    """Client for interacting with the Hashdive (Hashmaps) API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.hashdive.io"):
        """
        Initialize Hashdive client
        
        Args:
            api_key: Optional API key for authentication
            base_url: Base URL for Hashdive API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })
    
    def get_trades(
        self,
        wallet_address: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch trades for a specific wallet address
        
        Args:
            wallet_address: The PolyMarket wallet address to query
            start_time: Optional start time for filtering trades
            end_time: Optional end time for filtering trades
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        try:
            endpoint = f"{self.base_url}/get_trades"
            
            params = {
                "wallet": wallet_address,
                "limit": limit
            }
            
            if start_time:
                params["start_time"] = int(start_time.timestamp())
            if end_time:
                params["end_time"] = int(end_time.timestamp())
            
            logger.debug(f"Fetching trades for wallet {wallet_address}")
            
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            trades = data.get("trades", [])
            
            # Enrich and normalize trades
            normalized_trades = []
            for trade in trades:
                normalized = self.normalize_trade(trade, wallet_address)
                normalized_trades.append(normalized)
            
            logger.info(f"Fetched {len(normalized_trades)} trades for wallet {wallet_address}")
            
            return normalized_trades
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trades from Hashdive: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_trades: {e}")
            return []
    
    def normalize_trade(self, trade: Dict[str, Any], wallet_address: str) -> Dict[str, Any]:
        """
        Normalize and enrich trade data
        
        Args:
            trade: Raw trade data from Hashdive
            wallet_address: Wallet address for this trade
            
        Returns:
            Normalized trade dictionary with trade_uid
        """
        # Generate trade UID (prefer Hashdive ID if available, otherwise hash)
        trade_uid = trade.get("id") or trade.get("trade_id")
        
        if not trade_uid:
            # Generate deterministic hash
            trade_uid = self.generate_trade_uid(trade, wallet_address)
        
        # Extract and normalize fields
        normalized = {
            "trade_uid": trade_uid,
            "wallet_address": wallet_address,
            "asset_id": trade.get("asset_id") or trade.get("token_id"),
            "market_name": trade.get("market") or trade.get("market_name"),
            "side": self.normalize_side(trade.get("side")),
            "price": self.safe_float(trade.get("price")),
            "usd_amount": self.safe_float(trade.get("usd_amount") or trade.get("value_usd")),
            "shares": self.safe_float(trade.get("shares") or trade.get("size") or trade.get("amount")),
            "timestamp": self.normalize_timestamp(trade.get("timestamp")),
            "raw": trade  # Store full raw data
        }
        
        # Calculate USD amount if missing
        if not normalized["usd_amount"] and normalized["price"] and normalized["shares"]:
            normalized["usd_amount"] = normalized["price"] * normalized["shares"]
        
        return normalized
    
    def generate_trade_uid(self, trade: Dict[str, Any], wallet_address: str) -> str:
        """
        Generate deterministic trade UID from trade attributes
        
        Args:
            trade: Trade data
            wallet_address: Wallet address
            
        Returns:
            SHA256 hash as trade UID
        """
        # Combine key fields for unique identification
        uid_data = {
            "wallet": wallet_address,
            "asset": trade.get("asset_id") or trade.get("token_id") or "",
            "timestamp": trade.get("timestamp"),
            "side": trade.get("side"),
            "price": trade.get("price"),
            "amount": trade.get("usd_amount") or trade.get("shares") or trade.get("size"),
        }
        
        # Create deterministic hash
        uid_string = json.dumps(uid_data, sort_keys=True)
        return hashlib.sha256(uid_string.encode()).hexdigest()
    
    @staticmethod
    def normalize_side(side: Optional[str]) -> Optional[str]:
        """Normalize trade side to 'buy' or 'sell'"""
        if not side:
            return None
        side_lower = side.lower()
        if side_lower in ["buy", "long"]:
            return "buy"
        elif side_lower in ["sell", "short"]:
            return "sell"
        return side_lower
    
    @staticmethod
    def normalize_timestamp(timestamp: Any) -> str:
        """Normalize timestamp to ISO format string"""
        if isinstance(timestamp, int):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp).isoformat()
        elif isinstance(timestamp, str):
            # Already string, try to parse and reformat
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.isoformat()
            except:
                return timestamp
        elif isinstance(timestamp, datetime):
            return timestamp.isoformat()
        else:
            return datetime.utcnow().isoformat()
    
    @staticmethod
    def safe_float(value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
