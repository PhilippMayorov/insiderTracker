# Trade History Fetch Feature

## Overview

This feature allows you to fetch and import all historical trades for a tracked wallet directly from the Hashdive API.

## How It Works

### 1. Database Updates

The `trades` table now includes additional fields from Hashdive's market_info:

- `market_question`: The full market question text
- `market_outcome`: The outcome (Yes/No)
- `market_tags`: JSON array of market tags
- `market_target_price`: Target price for the market
- `market_resolved`: Whether the market is resolved (0/1)
- `market_is_winner`: Whether this outcome won (0/1)
- `market_resolved_price`: The resolved price

### 2. Hashdive API Integration

The system now uses the correct Hashdive API endpoint:

- **URL**: `https://hashdive.com/api/get_trades`
- **Method**: GET
- **Parameters**:
  - `user_address`: Wallet address to query
  - `format`: json
- **Headers**:
  - `x-api-key`: Your Hashdive API key (from .env)

### 3. Using the Feature

#### From the Frontend (Streamlit):

1. Navigate to the "Tracked Insider Traders" section
2. Find the trader you want to fetch history for
3. Click the **"📥 Fetch Trades"** button next to their row
4. Wait for the import to complete
5. View the results showing:
   - Total trades found
   - New trades imported
   - Duplicate trades skipped

#### From the Backend API:

```bash
POST /favorites/{wallet_address}/fetch-history
```

Response:

```json
{
  "wallet_address": "0x...",
  "imported": 150,
  "skipped": 50,
  "total": 200,
  "message": "Successfully imported 150 trades (50 duplicates skipped)"
}
```

### 4. Migration

If you have an existing database, run the migration script first:

```powershell
python scripts/migrate_database.py
```

This will add the new columns to your existing `trades` table without losing data.

### 5. Deduplication

The system automatically handles duplicates:

- Each trade has a unique `trade_uid` (primary key)
- If a trade already exists in the database, it's skipped
- This allows you to safely re-run the fetch without creating duplicates

## Configuration

### Environment Variables

Make sure you have your Hashdive API key in `.env`:

```bash
HASHDIVE_API_KEY=your_api_key_here
HASHDIVE_API_URL=https://hashdive.com  # Default value
```

### API Rate Limits

Be aware of Hashdive API rate limits when fetching history for multiple wallets.

## Troubleshooting

### "Hashdive client not initialized"

Make sure the backend is running and fully started before clicking the fetch button.

### "Wallet not tracked"

You must add the wallet to your tracked list before fetching its history.

### No trades returned

- Verify the wallet address is correct
- Check that the wallet has trading activity on PolyMarket
- Verify your Hashdive API key is valid

### Database errors

Run the migration script if you see database schema errors:

```powershell
python scripts/migrate_database.py
```

## Data Format Example

Hashdive returns data in this format:

```
user_address, asset_id, side, price, shares, usd_amount, timestamp,
market_info.question, market_info.outcome, market_info.tags,
market_info.target_price, market_info.resolved, market_info.is_winner,
market_info.resolved_price
```

The system normalizes this to:

- `side`: 'b' → 'buy', 's' → 'sell'
- `share_type`: market_info.outcome ('Yes' or 'No')
- `market_name`: market_info.question
- `timestamp`: Converted to ISO format from "M/D/YYYY H:MM"
- All market_info fields stored separately
