"""
Fetch top 10 markets from PolyMarket API with top holders data
"""
import requests
from typing import List, Dict, Any, Optional

# Import insider detection function
from .insiderDetection import is_insider_market 


def get_top_markets(limit: int = 10, include_holders: bool = False, holder_limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top markets from PolyMarket Gamma API
    
    Args:
        limit: Number of markets to return (default: 10)
        include_holders: Whether to fetch and include top holders data (default: False)
        holder_limit: Number of top holders to include per market (default: 10)
        
    Returns:
        List of market dictionaries containing market information (and optionally holders)
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
            result_markets = markets[:limit]
        else:
            # If response is paginated or has a different structure
            result_markets = markets.get('data', [])[:limit] if isinstance(markets, dict) else []
        
        # Optionally enrich with holders data
        if include_holders and result_markets:
            print(f"\nEnriching {len(result_markets)} markets with holder data...")
            result_markets = enrich_markets_with_holders(result_markets, holder_limit=holder_limit)
        
        return result_markets
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching markets: {e}")
        return []


def get_market_holders(condition_id: str, limit: int = 10, min_balance: int = 1) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch top holders for a specific market using the PolyMarket Data API.
    
    Args:
        condition_id: The condition ID (token) for the market
        limit: Maximum number of holders to return (default: 10)
        min_balance: Minimum balance threshold (default: 1)
        
    Returns:
        List of holder dictionaries containing holder information, or None if error
    """
    url = "https://data-api.polymarket.com/holders"
    
    try:
        params = {
            "limit": limit,
            "market": condition_id,
            "minBalance": min_balance
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        holders_data = response.json()
        
        # The API returns a list of token objects, each with a 'holders' array
        # Format: [{"token": "...", "holders": [...]}, {"token": "...", "holders": [...]}]
        if isinstance(holders_data, list):
            # Flatten all holders from all tokens into a single list
            all_holders = []
            for token_obj in holders_data:
                if isinstance(token_obj, dict) and 'holders' in token_obj:
                    all_holders.extend(token_obj['holders'])
            
            return all_holders if all_holders else None
        else:
            print(f"Unexpected response format for holders: {type(holders_data)}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching holders for market {condition_id}: {e}")
        return None


def enrich_markets_with_holders(markets: List[Dict[str, Any]], holder_limit: int = 10) -> List[Dict[str, Any]]:
    """
    Enrich market data with top holders information.
    
    Args:
        markets: List of market dictionaries
        holder_limit: Number of top holders to include per market (default: 10)
        
    Returns:
        List of markets enriched with 'top_holders' field
    """
    enriched_markets = []
    
    for market in markets:
        # Create a copy to avoid modifying original
        enriched_market = market.copy()
        
        # Get the condition ID (token) from the market
        condition_id = market.get('conditionId')
        
        if condition_id:
            print(f"Fetching holders for market: {market.get('question', 'Unknown')[:50]}...")
            holders = get_market_holders(condition_id, limit=10, min_balance=1)
            
            if holders:
                # Add top N holders to the market data
                enriched_market['top_holders'] = holders[:holder_limit]
                enriched_market['total_holders_count'] = len(holders)
                print(f"  ✓ Found {len(holders)} holders (showing top {holder_limit})")
            else:
                enriched_market['top_holders'] = []
                enriched_market['total_holders_count'] = 0
                print(f"  ✗ No holders found")
        else:
            print(f"⚠️  No condition ID found for market: {market.get('question', 'Unknown')[:50]}")
            enriched_market['top_holders'] = []
            enriched_market['total_holders_count'] = 0
        
        enriched_markets.append(enriched_market)
    
    return enriched_markets

def get_insider_markets(limit: int = 10, include_holders: bool = False, holder_limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top markets from PolyMarket and filter for those with insider trading potential.
    
    Args:
        limit: Number of markets to fetch (default: 10)
        include_holders: Whether to fetch and include top holders data (default: False)
        holder_limit: Number of top holders to include per market (default: 10)

    Returns:
        List of market dictionaries flagged as having insider trading potential
    """
    # Fetch markets
    markets = get_top_markets(limit=limit, include_holders=include_holders, holder_limit=holder_limit)
    
    if not markets:
        return []
    
    # Filter for insider trading potential
    insider_markets = is_insider_market(markets)
    
    return insider_markets

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
        market_slug = market.get('slug', 'N/A')
        volume = market.get('volume', 0)
        liquidity = market.get('liquidity', 0)
        outcome_prices = market.get('outcomePrices', [])
        
        print(f"{idx}. {question}")
        print(f"   Slug: {market_slug}")
        print(f"   Volume: ${float(volume):,.2f}")
        print(f"   Liquidity: ${float(liquidity):,.2f}")
        if outcome_prices:
            print(f"   Outcome Prices: {outcome_prices}")
        
        # Display holder information if available
        if 'top_holders' in market:
            total_count = market.get('total_holders_count', 0)
            top_holders = market.get('top_holders', [])
            print(f"   Total Holders: {total_count}")
            if top_holders:
                print(f"   Top {len(top_holders)} Holders:")
                for holder_idx, holder in enumerate(top_holders[:5], 1):  # Show top 5
                    proxy_wallet = holder.get('proxyWallet', 'N/A')
                    amount = holder.get('amount', 0)
                    outcome_index = holder.get('outcomeIndex', 'N/A')
                    name = holder.get('name', 'Anonymous')
                    pseudonym = holder.get('pseudonym', 'N/A')
                    bio = holder.get('bio', '')
                    
                    print(f"      {holder_idx}. {name} (@{pseudonym})")
                    print(f"         Wallet: {proxy_wallet}")
                    print(f"         Amount: {amount:,.2f} | Outcome: {outcome_index}")
                    if bio:
                        print(f"         Bio: {bio}")
                if len(top_holders) > 5:
                    print(f"      ... and {len(top_holders) - 5} more holders")
        
        print()


if __name__ == "__main__":
    import sys
    
    # Check if user wants to include holders data
    include_holders = "--with-holders" in sys.argv
    
    # Fetch top 10 markets
    print("Fetching top markets...")
    markets = get_top_markets(limit=10, include_holders=include_holders, holder_limit=10)
    
    # Print summary
    print_market_summary(markets)
    
    # Optionally print full JSON for first market
    if markets and "--json" in sys.argv:
        print(f"{'='*80}")
        print("SAMPLE MARKET (Full JSON):")
        print(f"{'='*80}")
        import json
        print(json.dumps(markets[0], indent=2))
    
    print(f"\n{'='*80}")
    print("Usage:")
    print("  python -m src.backend.getMarkets              # Basic market data")
    print("  python -m src.backend.getMarkets --with-holders  # Include top holders")
    print("  python -m src.backend.getMarkets --with-holders --json  # Include JSON output")
    print(f"{'='*80}")
