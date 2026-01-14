"""
Script to add NEW test trades with share_type for all tracked wallets
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
    "Will SpaceX successfully land humans on Mars?",
    "Will the S&P 500 close above 5000 in 2024?",
    "Will OpenAI release GPT-5 in 2024?",
    "Will there be a nuclear weapons test in 2024?",
    "Will gas prices exceed $5 per gallon in 2024?",
    "Will the Supreme Court overturn Roe v Wade?",
    "Will Netflix stock hit $500 in 2024?",
    "Will Meta launch a Twitter competitor?",
    "Will California experience major earthquake in 2024?",
    "Will global temperatures hit record highs?",
]

def generate_new_test_trades(wallet_address: str, start_idx: int = 100, num_trades: int = 5):
    """Generate NEW random test trades for a given wallet"""
    trades = []
    
    for i in range(num_trades):
        # Randomize trade parameters
        side = random.choice(["buy", "sell"])
        share_type = random.choice(["YES", "NO"])
        price = round(random.uniform(0.10, 0.95), 2)
        usd_amount = round(random.uniform(500, 15000), 2)
        shares = round(usd_amount / price, 2)
        hours_ago = random.randint(1, 72)
        market_name = random.choice(MARKET_NAMES)
        
        trade = {
            "trade_uid": f"test_trade_{wallet_address}_{start_idx + i:03d}",
            "wallet_address": wallet_address,
            "asset_id": f"0x{random.randint(100000, 999999):x}",
            "market_name": market_name,
            "side": side,
            "share_type": share_type,
            "price": price,
            "usd_amount": usd_amount,
            "shares": shares,
            "timestamp": (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat(),
            "raw": {"hashdive_enriched": True}
        }
        trades.append(trade)
    
    return trades

try:
    wallets = crud.get_tracked_wallets(db, limit=1000)
    
    if not wallets:
        print("⚠️  No tracked wallets found.")
        sys.exit(0)
    
    print("=" * 70)
    print(f"📊 Adding NEW trades with share_type for {len(wallets)} wallets")
    print("=" * 70)
    
    total_added = 0
    
    for wallet in wallets:
        wallet_address = wallet.wallet_address
        custom_name = wallet.custom_name or wallet_address[:10]
        
        print(f"\n🔄 Processing: {custom_name} ({wallet_address[:10]}...)")
        
        # Generate new test trades starting from index 100 to avoid conflicts
        test_trades = generate_new_test_trades(wallet_address, start_idx=100, num_trades=5)
        
        added_count = 0
        
        for trade_data in test_trades:
            result = crud.create_trade(db, trade_data)
            if result:
                added_count += 1
                total_added += 1
                print(f"   ✅ {trade_data['side'].upper()} {trade_data['share_type']} ${trade_data['usd_amount']:.0f} - {trade_data['market_name'][:40]}...")
        
        if added_count > 0:
            print(f"   ✨ Added {added_count} new trades")
    
    print("\n" + "=" * 70)
    print(f"🎉 Successfully added {total_added} NEW trades with share_type!")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
