"""Hashdive API Client for fetching PolyMarket trade data"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class HashdiveClient:
    """Client for interacting with the Hashdive (Hashmaps) API"""
    
    BASE_URL = "https://api.hashdive.io"  # Update with actual Hashdive API URL
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hashdive client
        
        Args:
            api_key: Optional API key for authentication
        """
        self.api_key = api_key
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
            endpoint = f"{self.BASE_URL}/get_trades"
            
            params = {
                "wallet": wallet_address,
                "limit": limit
            }
            
            if start_time:
                params["start_time"] = int(start_time.timestamp())
            if end_time:
                params["end_time"] = int(end_time.timestamp())
            
            logger.debug(f"Fetching trades for wallet {wallet_address}")
            
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            trades = data.get("trades", [])
            
            logger.info(f"Fetched {len(trades)} trades for wallet {wallet_address}")
            
            return trades
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trades from Hashdive: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_trades: {e}")
            return []
    
    def get_trade_by_id(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific trade by ID
        
        Args:
            trade_id: The trade ID to fetch
            
        Returns:
            Trade dictionary or None if not found
        """
        try:
            endpoint = f"{self.BASE_URL}/trade/{trade_id}"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching trade {trade_id}: {e}")
            return None
    
    def enrich_trade(self, trade: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich trade data with additional information
        
        Args:
            trade: Raw trade data
            
        Returns:
            Enriched trade data with formatted fields
        """
        enriched = trade.copy()
        
        # Parse timestamp if present
        if "timestamp" in trade:
            try:
                enriched["timestamp_dt"] = datetime.fromtimestamp(trade["timestamp"])
            except (ValueError, TypeError):
                pass
        
        # Calculate USD value if price and size are present
        if "price" in trade and "size" in trade:
            try:
                enriched["value_usd"] = float(trade["price"]) * float(trade["size"])
            except (ValueError, TypeError):
                pass
        
        return enriched
