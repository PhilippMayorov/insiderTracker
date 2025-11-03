"""
Test script for insider trading detection
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.getMarkets import get_insider_markets, get_top_markets

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING INSIDER TRADING DETECTION")
    print("=" * 80)
    
    # Number of markets to fetch
    NUM_MARKETS = 20  # Increased to get more chances of finding insider markets
    
    # Fetch and filter insider markets directly
    print(f"\n1. Fetching top {NUM_MARKETS} markets and analyzing for insider trading potential...")
    insider_markets = get_insider_markets(limit=NUM_MARKETS, include_holders=True, holder_limit=10)
    print(f"   ✓ Found {len(insider_markets)} markets with insider potential")
    
    # Display results
    if insider_markets:
        print("\n" + "=" * 80)
        print("MARKETS WITH INSIDER TRADING POTENTIAL:")
        print("=" * 80)
        
        for idx, market in enumerate(insider_markets, 1):
            question = market.get('question', 'Unknown Market')
            volume = market.get('volume', 0)
            liquidity = market.get('liquidity', 0)
            insider_score = market.get('insider_score', 0.0)
            # total_holders = market.get('total_holders_count', 0)
            
            print(f"\n🚨 {idx}. [{insider_score:.2f}] {question}")
            print(f"   Volume: ${float(volume):,.2f}")
            print(f"   Liquidity: ${float(liquidity):,.2f}")
            print(f"   Market ID: {market.get('id', 'N/A')}")
            print(f"   Condition ID: {market.get('conditionId', 'N/A')}")
            
            # Display holder information
            total_holders = market.get('total_holders_count', 0)
            top_holders = market.get('top_holders', [])
            print(f"   Total Holders: {total_holders:,}")
            
            if top_holders:
                print(f"   Top {min(3, len(top_holders))} Holders:")
                for h_idx, holder in enumerate(top_holders[:3], 1):
                    name = holder.get('name', 'Anonymous')
                    pseudonym = holder.get('pseudonym', 'N/A')
                    wallet = holder.get('proxyWallet', 'N/A')
                    amount = holder.get('amount', 0)
                    outcome = holder.get('outcomeIndex', 'N/A')
                    bio = holder.get('bio', '')
                    
                    print(f"      {h_idx}. {name} (@{pseudonym})")
                    print(f"         Wallet: {wallet}")
                    print(f"         Amount: {amount:,.2f} | Outcome: {outcome}")
                    if bio:
                        print(f"         Bio: {bio}")
    else:
        print("\n⚠️  No markets with significant insider trading potential found.")
        print("   Try increasing NUM_MARKETS or checking different market categories.")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
