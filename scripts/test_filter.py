"""
Test script to verify the filtering by custom name works
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.db import SessionLocal, init_db
from src.backend import crud

# Initialize database
init_db()
db = SessionLocal()

try:
    print("=" * 60)
    print("Testing Trade Filtering by Custom Name: 'yourlocalcrusader'")
    print("=" * 60)
    
    # Test 1: Filter by custom name
    print("\n1️⃣  Filtering by custom name 'yourlocalcrusader':")
    trades, count = crud.get_trades(db, wallet_address="yourlocalcrusader", limit=10)
    print(f"   Found {count} trades")
    for i, trade in enumerate(trades[:3], 1):
        print(f"   {i}. {trade.market_name[:50]}... (${trade.usd_amount:.2f})")
    
    # Test 2: Filter by actual wallet address
    print("\n2️⃣  Filtering by wallet address '0x3950c02127380820f56205f5c1ed47cceb4ae272':")
    trades2, count2 = crud.get_trades(db, wallet_address="0x3950c02127380820f56205f5c1ed47cceb4ae272", limit=10)
    print(f"   Found {count2} trades")
    for i, trade in enumerate(trades2[:3], 1):
        print(f"   {i}. {trade.market_name[:50]}... (${trade.usd_amount:.2f})")
    
    # Verify they match
    print(f"\n✅ Results match: {count == count2}")
    
    # Test 3: Get all tracked wallets
    print("\n3️⃣  All tracked wallets:")
    wallets = crud.get_tracked_wallets(db, limit=10)
    for wallet in wallets:
        print(f"   - {wallet.custom_name} ({wallet.wallet_address[:10]}...)")
    
    print("\n" + "=" * 60)
    print("✅ Filter test completed successfully!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
