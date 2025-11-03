"""
Fetch top 10 markets from PolyMarket API
"""
import requests
from typing import List, Dict, Any

from insiderDetection import is_insider_market 


def get_top_markets(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top markets from PolyMarket Gamma API
    
    Args:
        limit: Number of markets to return (default: 10)
        
    Returns:
        List of market dictionaries containing market information
    """
    url = "https://gamma-api.polymarket.com/markets"
    
    try:
        # Add parameters to limit results
        params = {
            "limit": limit,
            "closed": False  # Only get active markets
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        markets = response.json()
        
        # Return top markets (API returns them sorted by volume/popularity)
        if isinstance(markets, list):
            return markets[:limit]
        else:
            # If response is paginated or has a different structure
            return markets.get('data', [])[:limit] if isinstance(markets, dict) else []
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching markets: {e}")
        return []

def is_insider_market(market: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine if a market is an insider trading market based on specific criteria.
    
    Args:
        market: A dictionary containing market information.

    """

    






def print_market_summary(markets: List[Dict[str, Any]]) -> None:
    """
    Print a formatted summary of markets
    
    Args:
        markets: List of market dictionaries
    """
    if not markets:
        print("No markets found")
        return
    
    print(f"\n{'='*80}")
    print(f"TOP {len(markets)} POLYMARKET MARKETS")
    print(f"{'='*80}\n")
    
    for idx, market in enumerate(markets, 1):
        question = market.get('question', 'Unknown Market')
        market_slug = market.get('market_slug', 'N/A')
        volume = market.get('volume', 0)
        liquidity = market.get('liquidity', 0)
        outcome_prices = market.get('outcomePrices', [])
        
        print(f"{idx}. {question}")
        print(f"   Slug: {market_slug}")
        print(f"   Volume: ${float(volume):,.2f}")
        print(f"   Liquidity: ${float(liquidity):,.2f}")
        if outcome_prices:
            print(f"   Outcome Prices: {outcome_prices}")
        print()


if __name__ == "__main__":
    # Fetch top 10 markets
    markets = get_top_markets(limit=10)
    
    # Print summary
    print_market_summary(markets)
    
    # Optionally print full JSON for first market
    if markets:
        print(f"{'='*80}")
        print("SAMPLE MARKET (Full JSON):")
        print(f"{'='*80}")
        import json
        print(json.dumps(markets[0], indent=2))
