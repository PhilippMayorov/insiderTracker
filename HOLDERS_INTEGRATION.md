# Market Holders Integration

## Overview

Added functionality to fetch top holders for each PolyMarket market using the PolyMarket Data API endpoint `/holders`.

---

## 🔧 New Functions

### 1. `get_market_holders(condition_id, limit=100000, min_balance=1)`

Fetches top holders for a specific market.

**Parameters:**

- `condition_id` (str): The condition ID (token) for the market
- `limit` (int): Maximum number of holders to return (default: 100000)
- `min_balance` (int): Minimum balance threshold (default: 1)

**Returns:**

- `List[Dict]`: List of holder dictionaries, or `None` if error

**Example:**

```python
holders = get_market_holders("0x123abc...", limit=100, min_balance=1)
```

---

### 2. `enrich_markets_with_holders(markets, holder_limit=10)`

Enriches market data with top holders information.

**Parameters:**

- `markets` (List[Dict]): List of market dictionaries
- `holder_limit` (int): Number of top holders to include per market (default: 10)

**Returns:**

- `List[Dict]`: Markets enriched with `top_holders` and `total_holders_count` fields

**Example:**

```python
enriched = enrich_markets_with_holders(markets, holder_limit=5)
```

---

## 📊 Updated Functions

### `get_top_markets(limit=10, include_holders=False, holder_limit=10)`

**New Parameters:**

- `include_holders` (bool): Whether to fetch and include top holders data (default: False)
- `holder_limit` (int): Number of top holders to include per market (default: 10)

**Example:**

```python
# Without holders
markets = get_top_markets(limit=10)

# With top 5 holders per market
markets = get_top_markets(limit=10, include_holders=True, holder_limit=5)
```

---

### `get_insider_markets(limit=10, include_holders=False, holder_limit=10)`

**Updated Parameters:**

- `limit` (int): Number of markets to fetch (default: 10)
- `include_holders` (bool): Whether to fetch and include top holders data (default: False)
- `holder_limit` (int): Number of top holders to include per market (default: 10)

**Example:**

```python
# Get insider markets with holder data
insider_markets = get_insider_markets(limit=20, include_holders=True, holder_limit=10)

for market in insider_markets:
    print(f"Market: {market['question']}")
    print(f"Insider Score: {market['insider_score']}")
    print(f"Total Holders: {market['total_holders_count']}")
    print(f"Top Holders: {len(market['top_holders'])}")
```

---

## 🔍 Holder Data Structure

Each holder in the `top_holders` array contains:

```python
{
    "proxyWallet": "0x56687bf447db6ff4a1...",  # Wallet address
    "bio": "<string>",                         # User bio
    "asset": "<string>",                       # Asset info
    "pseudonym": "<string>",                   # User pseudonym
    "amount": 123,                             # Holdings amount
    "displayUsernamePublic": true,             # Display setting
    "outcomeIndex": 123,                       # Outcome index (0 or 1)
    "name": "<string>",                        # Display name
    "profileImage": "<string>",                # Profile image URL
    "profileImageOptimized": "<string>"        # Optimized image URL
}
```

---

## 📝 Usage Examples

### Example 1: Basic Markets with Holders

```python
from src.backend.getMarkets import get_top_markets

markets = get_top_markets(limit=5, include_holders=True, holder_limit=10)

for market in markets:
    print(f"\nMarket: {market['question']}")
    print(f"Total Holders: {market['total_holders_count']}")

    for idx, holder in enumerate(market['top_holders'][:3], 1):
        print(f"  {idx}. {holder['proxyWallet'][:12]}... - Amount: {holder['amount']}")
```

---

### Example 2: Insider Markets with Whale Detection

```python
from src.backend.getMarkets import get_insider_markets

# Get insider markets with holder data
insider_markets = get_insider_markets(limit=20, include_holders=True, holder_limit=50)

for market in insider_markets:
    insider_score = market['insider_score']
    total_holders = market['total_holders_count']
    top_holders = market['top_holders']

    # Calculate whale concentration (top holder percentage)
    if top_holders and total_holders > 0:
        top_holder_amount = top_holders[0]['amount']
        print(f"🚨 [{insider_score:.2f}] {market['question']}")
        print(f"   Whale Alert: Top holder has {top_holder_amount} units")
        print(f"   Total Holders: {total_holders}")
```

---

## 🧪 Testing

Run the test script:

```bash
python scripts/test_market_holders.py
```

Or test directly:

```bash
# Basic markets without holders
python -m src.backend.getMarkets

# Markets with top holders
python -m src.backend.getMarkets --with-holders

# Markets with holders and JSON output
python -m src.backend.getMarkets --with-holders --json
```

---

## 🔗 API Endpoint Reference

**PolyMarket Data API - Holders Endpoint:**

```
GET https://data-api.polymarket.com/holders
```

**Query Parameters:**

- `limit` (integer): Maximum number of results
- `market` (string[]): Comma-separated list of condition IDs (required)
- `minBalance` (integer): Minimum balance threshold

**Response:**
Returns an array of holder objects with wallet addresses, amounts, and metadata.

---

## ⚠️ Notes

1. **Performance**: Fetching holders for multiple markets can be slow. Use `include_holders=False` when not needed.

2. **Rate Limiting**: The API may have rate limits. Consider adding delays between requests for large batches.

3. **Condition IDs**: Make sure markets have a valid `conditionId` or `condition_id` field.

4. **Privacy**: All data is public and available through PolyMarket's APIs.

---

## 🎯 Integration with Streamlit UI

The `get_insider_markets()` function is used in `src/main.py`. To display holders in the UI, update the Streamlit code:

```python
insider_markets = get_insider_markets(limit=10, include_holders=True, holder_limit=10)

for market in insider_markets:
    with st.expander(f"Market: {market['question']}"):
        st.metric("Total Holders", market['total_holders_count'])

        if market['top_holders']:
            st.subheader("Top Holders")
            for idx, holder in enumerate(market['top_holders'][:5], 1):
                st.write(f"{idx}. {holder['proxyWallet'][:12]}... - {holder['amount']}")
```

---

## 📁 Files Modified

- `src/backend/getMarkets.py` - Added holder fetching functionality
- `scripts/test_market_holders.py` - New test script
- `HOLDERS_INTEGRATION.md` - This documentation

---

## ✅ Summary

You can now:

- ✅ Fetch top holders for any market
- ✅ Enrich market data with holder information
- ✅ Detect whale concentration in insider-sensitive markets
- ✅ Analyze holder patterns across markets
