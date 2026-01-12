# PolyMarket Trade Tracker

A lightweight tracking and alerting system for monitoring specific PolyMarket wallets. Track trades from predefined wallets and receive email notifications when new trades are detected.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/polymarket-trade-tracker.git
cd polymarket-trade-tracker
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and add your configuration:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
TO_EMAILS=recipient1@example.com,recipient2@example.com

# Hashdive API (optional)
HASHDIVE_API_KEY=your-api-key

# Trade Filters
MIN_TRADE_SIZE_USD=100
```

### 3. Configure Wallets

Edit `config/wallets.yaml` to add wallet addresses you want to track:

```yaml
wallets:
  - address: "0x1234567890123456789012345678901234567890"
    name: "Wallet 1"
    enabled: true
```

### 4. Install Dependencies

```bash
python -m venv venv
venv\Scripts\Activate.ps1  # On Windows PowerShell
# source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

### 5. Run the Tracker

```bash
# Test email configuration
python src/main.py --test-email

# Run once (single poll)
python src/main.py --once

# Run continuously (recommended for production)
python src/main.py
```

## 📁 Project Structure

```
polymarket-trade-tracker/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── wallets.yaml        # List of tracked wallets
│
├── data/
│   └── trades.db           # Local SQLite trade history
│
├── src/
│   ├── tracker/
│   │   ├── poller.py       # Polls Hashdive for new trades
│   │   ├── state.py        # Tracks last-seen trades
│   │   └── alerts.py       # Email alert logic
│   ├── integrations/
│   │   └── hashdive.py     # Hashdive API client
│   ├── email/
│   │   └── smtp.py         # Email sender
│   ├── settings.py         # Configuration
│   └── main.py             # Entry point
│
└── scripts/
    └── run_tracker.py      # Helper runner script
```

## 🎯 What This Does

- ✅ Track predefined PolyMarket wallet addresses
- ✅ Poll for new trades using the Hashdive API
- ✅ Detect previously unseen trades
- ✅ Send email notifications when new trades occur
- ✅ Store basic trade history locally to prevent duplicate alerts

## 🚫 What This Does NOT Do

- ❌ No insider trading detection
- ❌ No anomaly detection or risk scoring
- ❌ No behavioral classification
- ❌ No market predictions
- ❌ No enforcement or interpretation

## 📧 Email Notifications

Email alerts include:

- Wallet address and name
- Market name
- Side (YES / NO)
- Price and Size
- Total Value (USD)
- Timestamp

## ⚙️ Configuration Options

### Wallet Configuration (`config/wallets.yaml`)

```yaml
wallets:
  - address: "0x..."
    name: "Descriptive Name"
    enabled: true

polling:
  interval_seconds: 60
  initial_lookback_hours: 24

filters:
  min_trade_size_usd: 100
```

### Environment Variables (`.env`)

See `.env.example` for all available configuration options.

## 🔧 Command Line Options

```bash
python src/main.py --help

Options:
  --once         Run once and exit (instead of continuous polling)
  --test-email   Test email configuration and exit
  --config PATH  Path to wallets configuration file
```

## 📚 Documentation

- [Architecture Guide](.github/copilot-instructions.md)
- [Configuration](config/)

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest -v

# Run with debug logging
LOG_LEVEL=DEBUG python src/main.py --once
```

## 📝 Notes

- This tool uses **publicly available data only** from the Hashdive API
- Designed for personal monitoring, research, and notification purposes
- No analysis or interpretation of trading behavior is performed

---

**PolyMarket Trade Tracker** - Simple wallet monitoring with email alerts
