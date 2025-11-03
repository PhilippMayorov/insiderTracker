"""
Fetch top 10 events from PolyMarket API
"""
import requests
from typing import List, Dict, Any


def get_top_events(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch top events from PolyMarket Gamma API
    
    Args:
        limit: Number of events to return (default: 10)
        
    Returns:
        List of event dictionaries containing event information
    """
    url = "https://gamma-api.polymarket.com/events"
    
    try:
        # Add parameters to limit results
        params = {
            "limit": limit,
            "archived": False  # Only get active events
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        events = response.json()
        
        # Return top events (API returns them sorted by volume/popularity)
        if isinstance(events, list):
            return events[:limit]
        else:
            # If response is paginated or has a different structure
            return events.get('data', [])[:limit] if isinstance(events, dict) else []
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return []


def print_event_summary(events: List[Dict[str, Any]]) -> None:
    """
    Print a formatted summary of events
    
    Args:
        events: List of event dictionaries
    """
    if not events:
        print("No events found")
        return
    
    print(f"\n{'='*80}")
    print(f"TOP {len(events)} POLYMARKET EVENTS")
    print(f"{'='*80}\n")
    
    for idx, event in enumerate(events, 1):
        title = event.get('title', 'Unknown Event')
        slug = event.get('slug', 'N/A')
        volume = event.get('volume', 0)
        liquidity = event.get('liquidity', 0)
        market_count = len(event.get('markets', []))
        
        print(f"{idx}. {title}")
        print(f"   Slug: {slug}")
        print(f"   Volume: ${float(volume):,.2f}")
        print(f"   Liquidity: ${float(liquidity):,.2f}")
        print(f"   Markets: {market_count}")
        print()


if __name__ == "__main__":
    # Fetch top 10 events
    events = get_top_events(limit=10)
    
    # Print summary
    print_event_summary(events)
    
    # Optionally print full JSON for first event
    # if events:
    #     print(f"{'='*80}")
    #     print("SAMPLE EVENT (Full JSON):")
    #     print(f"{'='*80}")
    #     import json
    #     print(json.dumps(events[0], indent=2))