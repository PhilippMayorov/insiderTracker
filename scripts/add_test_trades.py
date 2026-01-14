"""
Script to add test trade data for ALL tracked wallets in the database
"""
from datetime import datetime, timedelta
import sys
import os
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.db import SessionLocal, init_db
from src.backend import crud

# Initialize database
init_db()
db = SessionLocal()

# Sample market names pool
MARKET_NAMES = [
    "Will Trump win 2024 presidential election?",
    "Will Israel strike Iran by February 2024?",
    "Will Bitcoin hit $100k in 2024?",
    "Will AI replace human jobs by 2030?",
    "Will there be a recession in 2024?",
    "Will Democrats win the Senate in 2024?",
    "Will the Fed cut interest rates in Q1 2024?",
    "Will Tesla stock hit $300 in 2024?",
    "Will Ethereum merge to proof-of-stake succeed?",
    "Will China invade Taiwan by 2025?",
    "Will a new COVID variant emerge in 2024?",
    "Will the US ban TikTok in 2024?",
    "Will SpaceX land on Mars by 2026?",
    "Will Apple release VR headset in 2024?",
    "Will inflation drop below 3% in 2024?",
]

def generate_test_trades_for_wallet(wallet_address: str, num_trades: int = 5):
    """Generate random test trades for a given wallet"""
    trades = []
    
    for i in range(num_trades):
        # Randomize trade parameters
        side = random.choice(["buy", "sell"])
        price = round(random.uniform(0.10, 0.95), 2)
        usd_amount = round(random.uniform(500, 15000), 2)
        shares = round(usd_amount / price, 2)
        hours_ago = random.randint(1, 72)  # 1 to 72 hours ago
        market_name = random.choice(MARKET_NAMES)
        
        trade = {
            "trade_uid": f"test_trade_{wallet_address}_{i+1:03d}",
            "wallet_address": wallet_address,
            "asset_id": f"0x{random.randint(100000, 999999):x}",
            "market_name": market_name,
            "side": side,
            "price": price,
            "usd_amount": usd_amount,
            "shares": shares,
            "timestamp": (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat(),
            "raw": {"hashdive_enriched": True}
        }
        trades.append(trade)
    
    return trades


try:
    # Get all tracked wallets
    wallets = crud.get_tracked_wallets(db, limit=1000)
    
    if not wallets:
        print("⚠️  No tracked wallets found in the database.")
        print("   Please add wallets via the UI first.")
        sys.exit(0)
    
    print("=" * 70)
    print(f"📊 Found {len(wallets)} tracked wallets")
    print("=" * 70)
    
    total_added = 0
    total_skipped = 0
    
    for wallet in wallets:
        wallet_address = wallet.wallet_address
        custom_name = wallet.custom_name or wallet_address[:10]
        
        print(f"\n🔄 Processing: {custom_name} ({wallet_address[:10]}...)")
        
        # Generate test trades for this wallet
        test_trades = generate_test_trades_for_wallet(wallet_address, num_trades=5)
        
        added_count = 0
        skipped_count = 0
        
        for trade_data in test_trades:
            result = crud.create_trade(db, trade_data)
            if result:
                added_count += 1
                total_added += 1
                print(f"   ✅ Added: {trade_data['side'].upper()} ${trade_data['usd_amount']:.0f} - {trade_data['market_name'][:40]}...")
            else:
                skipped_count += 1
                total_skipped += 1
        
        if added_count > 0:
            print(f"   ✨ Added {added_count} new trades for {custom_name}")
        if skipped_count > 0:
            print(f"   ⏭️  Skipped {skipped_count} existing trades")
    
    print("\n" + "=" * 70)
    print(f"🎉 SUMMARY:")
    print(f"   • Processed {len(wallets)} wallets")
    print(f"   • Added {total_added} new trades")
    print(f"   • Skipped {total_skipped} existing trades")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error adding trades: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
