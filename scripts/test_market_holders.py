#!/usr/bin/env python3
"""
Test script for fetching markets with top holders data
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.getMarkets import get_top_markets, get_insider_markets

def test_basic_markets():
    """Test fetching markets without holders"""
    print("=" * 80)
    print("TEST 1: Fetching markets WITHOUT holder data")
    print("=" * 80)
    
    markets = get_top_markets(limit=3, include_holders=False)
    
    print(f"\nFetched {len(markets)} markets")
    for idx, market in enumerate(markets, 1):
        print(f"\n{idx}. {market.get('question', 'Unknown')[:60]}...")
        print(f"   Volume: ${float(market.get('volume', 0)):,.2f}")
        print(f"   Has holders data: {'top_holders' in market}")


def test_markets_with_holders():
    """Test fetching markets with holders"""
    print("\n" + "=" * 80)
    print("TEST 2: Fetching markets WITH holder data")
    print("=" * 80)
    
    markets = get_top_markets(limit=3, include_holders=True, holder_limit=5)
    
    print(f"\nFetched {len(markets)} markets with holder data")
    for idx, market in enumerate(markets, 1):
        print(f"\n{idx}. {market.get('question', 'Unknown')[:60]}...")
        print(f"   Volume: ${float(market.get('volume', 0)):,.2f}")
        print(f"   Total Holders: {market.get('total_holders_count', 0)}")
        
        top_holders = market.get('top_holders', [])
        if top_holders:
            print(f"   Top {len(top_holders)} Holders:")
            for h_idx, holder in enumerate(top_holders[:3], 1):
                wallet = holder.get('proxyWallet', 'N/A')
                amount = holder.get('amount', 0)
                print(f"      {h_idx}. {wallet[:12]}... | Amount: {amount}")


def test_insider_markets_with_holders():
    """Test fetching insider-sensitive markets with holders"""
    print("\n" + "=" * 80)
    print("TEST 3: Fetching INSIDER markets WITH holder data")
    print("=" * 80)
    
    insider_markets = get_insider_markets(limit=20, include_holders=True, holder_limit=10)
    
    print(f"\nFound {len(insider_markets)} insider-sensitive markets")
    for idx, market in enumerate(insider_markets, 1):
        score = market.get('insider_score', 0.0)
        print(f"\n{idx}. [{score:.2f}] {market.get('question', 'Unknown')[:60]}...")
        print(f"   Volume: ${float(market.get('volume', 0)):,.2f}")
        print(f"   Total Holders: {market.get('total_holders_count', 0)}")
        
        top_holders = market.get('top_holders', [])
        if top_holders:
            print(f"   Top 3 Holders:")
            for h_idx, holder in enumerate(top_holders[:3], 1):
                wallet = holder.get('proxyWallet', 'N/A')
                amount = holder.get('amount', 0)
                print(f"      {h_idx}. {wallet[:12]}... | Amount: {amount}")


if __name__ == "__main__":
    print("\n🧪 TESTING MARKET HOLDERS FUNCTIONALITY\n")
    
    # Run tests
    test_basic_markets()
    test_markets_with_holders()
    test_insider_markets_with_holders()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
