"""
Test script to verify sorting functionality
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.db import SessionLocal, init_db
from src.backend import crud

init_db()
db = SessionLocal()

try:
    print("=" * 80)
    print("🧪 Testing Sorting Functionality")
    print("=" * 80)
    
    # Test 1: Sort by timestamp (most recent first - default)
    print("\n1️⃣  Sort by TIMESTAMP (descending - most recent first):")
    trades, _ = crud.get_trades(db, sort_by="timestamp", sort_order="desc", limit=5)
    for i, trade in enumerate(trades, 1):
        print(f"   {i}. {trade.timestamp[:19]} | {trade.market_name[:40]}...")
    
    # Test 2: Sort by USD amount (highest first)
    print("\n2️⃣  Sort by USD AMOUNT (descending - highest first):")
    trades, _ = crud.get_trades(db, sort_by="usd_amount", sort_order="desc", limit=5)
    for i, trade in enumerate(trades, 1):
        print(f"   {i}. ${trade.usd_amount:>9,.2f} | {trade.market_name[:40]}...")
    
    # Test 3: Sort by USD amount (lowest first)
    print("\n3️⃣  Sort by USD AMOUNT (ascending - lowest first):")
    trades, _ = crud.get_trades(db, sort_by="usd_amount", sort_order="asc", limit=5)
    for i, trade in enumerate(trades, 1):
        print(f"   {i}. ${trade.usd_amount:>9,.2f} | {trade.market_name[:40]}...")
    
    # Test 4: Sort by side
    print("\n4️⃣  Sort by SIDE (descending - sell before buy):")
    trades, _ = crud.get_trades(db, sort_by="side", sort_order="desc", limit=5)
    for i, trade in enumerate(trades, 1):
        print(f"   {i}. {trade.side.upper():4s} | ${trade.usd_amount:>8,.2f} | {trade.market_name[:35]}...")
    
    # Test 5: Sort by share_type
    print("\n5️⃣  Sort by SHARE TYPE (descending - YES before NO):")
    trades, _ = crud.get_trades(db, sort_by="share_type", sort_order="desc", limit=5)
    for i, trade in enumerate(trades, 1):
        icon = "✅" if trade.share_type == "YES" else "❌"
        print(f"   {i}. {icon} {trade.share_type:3s} | {trade.side.upper():4s} | {trade.market_name[:35]}...")
    
    # Test 6: Sort by price
    print("\n6️⃣  Sort by PRICE (ascending - lowest first):")
    trades, _ = crud.get_trades(db, sort_by="price", sort_order="asc", limit=5)
    for i, trade in enumerate(trades, 1):
        print(f"   {i}. ${trade.price:.2f} | {trade.market_name[:40]}...")
    
    # Test 7: Sort by shares
    print("\n7️⃣  Sort by SHARES (descending - most shares first):")
    trades, _ = crud.get_trades(db, sort_by="shares", sort_order="desc", limit=5)
    for i, trade in enumerate(trades, 1):
        print(f"   {i}. {trade.shares:>10,.2f} shares | ${trade.usd_amount:>8,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ All sorting tests completed successfully!")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
