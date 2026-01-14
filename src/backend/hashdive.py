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
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://hashdive.com"):
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
                "x-api-key": api_key
            })
    
    def get_trades(
        self,
        wallet_address: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch trades for a specific wallet address from Hashdive API
        
        Args:
            wallet_address: The PolyMarket wallet address to query
            start_time: Optional start time for filtering trades (not used in current API)
            end_time: Optional end time for filtering trades (not used in current API)
            limit: Maximum number of trades to return (not strictly enforced by API)
            
        Returns:
            List of trade dictionaries with normalized fields
        """
        try:
            endpoint = f"{self.base_url}/api/get_trades"
            
            params = {
                "user_address": wallet_address,
                "format": "json"
            }
            
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            logger.debug(f"Fetching trades for wallet {wallet_address}")
            
            response = self.session.get(endpoint, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Hashdive returns a list of trade dictionaries directly
            # or may be wrapped in a 'data' field
            if isinstance(data, list):
                trades = data
            elif isinstance(data, dict) and "data" in data:
                trades = data["data"]
            elif isinstance(data, dict) and "trades" in data:
                trades = data["trades"]
            else:
                logger.warning(f"Unexpected response format from Hashdive API: {type(data)}")
                trades = []
            
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
        Normalize and enrich trade data from Hashdive API
        
        Hashdive API returns trades with the following structure:
        - user_address: wallet address
        - asset_id: asset identifier
        - side: 'b' (buy) or 's' (sell)
        - price: price per share
        - shares: number of shares
        - usd_amount: USD value of trade
        - timestamp: trade timestamp (format: 'M/D/YYYY H:MM')
        - market_info.question: market question
        - market_info.outcome: 'Yes' or 'No'
        - market_info.tags: list of tags
        - market_info.target_price: target price
        - market_info.resolved: boolean
        - market_info.is_winner: boolean
        - market_info.resolved_price: resolved price
        
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
        
        # Extract market_info if present
        market_info = trade.get("market_info", {})
        if not isinstance(market_info, dict):
            market_info = {}
        
        # Parse tags (may be a list or string)
        tags = market_info.get("tags", [])
        if isinstance(tags, list):
            tags_json = json.dumps(tags)
        elif isinstance(tags, str):
            tags_json = tags
        else:
            tags_json = "[]"
        
        # Normalize side: 'b' -> 'buy', 's' -> 'sell'
        side_raw = trade.get("side", "")
        if side_raw == "b":
            side = "buy"
        elif side_raw == "s":
            side = "sell"
        else:
            side = self.normalize_side(side_raw)
        
        # Extract and normalize fields
        normalized = {
            "trade_uid": trade_uid,
            "wallet_address": wallet_address,
            "asset_id": str(trade.get("asset_id", "")) if trade.get("asset_id") else None,
            "market_name": market_info.get("question") or trade.get("market") or trade.get("market_name"),
            "side": side,
            "share_type": market_info.get("outcome"),  # 'Yes' or 'No'
            "price": self.safe_float(trade.get("price")),
            "usd_amount": self.safe_float(trade.get("usd_amount") or trade.get("value_usd")),
            "shares": self.safe_float(trade.get("shares") or trade.get("size") or trade.get("amount")),
            "timestamp": self.normalize_timestamp(trade.get("timestamp")),
            
            # Market info fields
            "market_question": market_info.get("question"),
            "market_outcome": market_info.get("outcome"),
            "market_tags": tags_json,
            "market_target_price": self.safe_float(market_info.get("target_price")),
            "market_resolved": 1 if market_info.get("resolved") else 0,
            "market_is_winner": 1 if market_info.get("is_winner") else 0,
            "market_resolved_price": self.safe_float(market_info.get("resolved_price")),
            
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
        """
        Normalize timestamp to ISO format string
        
        Handles multiple formats:
        - Unix timestamp (int)
        - ISO format string
        - Hashdive format: "M/D/YYYY H:MM" or "MM/DD/YYYY HH:MM"
        - datetime object
        """
        if isinstance(timestamp, int):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp).isoformat()
        elif isinstance(timestamp, str):
            # Try to parse Hashdive format: "1/14/2026 17:47"
            # Windows-compatible: parse manually for single-digit dates
            try:
                # Split the timestamp into date and time parts
                parts = timestamp.split(' ')
                if len(parts) == 2:
                    date_part = parts[0]
                    time_part = parts[1]
                    
                    # Parse date: M/D/YYYY or MM/DD/YYYY
                    date_components = date_part.split('/')
                    if len(date_components) == 3:
                        month = int(date_components[0])
                        day = int(date_components[1])
                        year = int(date_components[2])
                        
                        # Parse time: H:MM or HH:MM or H:MM:SS
                        time_components = time_part.split(':')
                        if len(time_components) >= 2:
                            hour = int(time_components[0])
                            minute = int(time_components[1])
                            second = int(time_components[2]) if len(time_components) > 2 else 0
                            
                            dt = datetime(year, month, day, hour, minute, second)
                            return dt.isoformat()
            except (ValueError, IndexError, AttributeError):
                pass
            
            # Try standard formats as fallback
            for fmt in [
                "%m/%d/%Y %H:%M",  # 01/14/2026 17:47
                "%m/%d/%Y %H:%M:%S",  # 01/14/2026 17:47:30
            ]:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.isoformat()
                except (ValueError, AttributeError):
                    continue
            
            # Try ISO format
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.isoformat()
            except:
                pass
            
            # Return as-is if can't parse
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
