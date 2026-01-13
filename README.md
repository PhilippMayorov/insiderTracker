# PolyMarket Trade Tracker

A professional-grade tracking and alerting system for monitoring PolyMarket wallets. Features a **FastAPI backend** with background polling and a **Streamlit frontend** for an intuitive web interface.

## 🎯 Key Features

- ✅ **FastAPI REST API** - Scalable backend with automatic API documentation
- ✅ **Streamlit Web UI** - Clean, intuitive interface for wallet management
- ✅ **Background Polling** - Continuously monitors tracked wallets (even when UI is closed)
- ✅ **Email Alerts** - Instant notifications for new trades
- ✅ **Trade History** - SQLite database with full trade history
- ✅ **Advanced Filters** - Filter by wallet, side, trade size, and market
- ✅ **Real-time Updates** - Live trade data from Hashdive API

## 🏗️ Architecture

**Backend (FastAPI):**

- Owns SQLite database
- Background polling service
- Trade deduplication
- Email alerts
- REST API endpoints

**Frontend (Streamlit):**

- Web-based UI
- Wallet management
- Trade visualization
- Real-time system status

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/polymarket-trade-tracker.git
cd polymarket-trade-tracker
python -m venv venv
venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**Required Configuration (.env):**

```bash
# Database
DATABASE_URL=sqlite:///./src/data/tracker.db

# Email Alerts
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com

# Hashdive API (optional - for better rate limits)
HASHDIVE_API_KEY=your-api-key-here
HASHDIVE_API_URL=https://api.hashdive.io

# Polling Configuration
POLL_INTERVAL_SECONDS=60
INITIAL_LOOKBACK_DAYS=7
MIN_TRADE_SIZE_USD=100
```

### 3. Start Backend Server

Open **Terminal 1** and run:

```bash
uvicorn src.backend.main:app --reload --port 8080
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8080
INFO:     Application startup complete.
```

### 4. Start Frontend UI

Open **Terminal 2** and run:

```bash
# Windows PowerShell
$env:API_BASE_URL="http://localhost:8080"
streamlit run src/frontend/app.py

# Linux/Mac
API_BASE_URL=http://localhost:8080 streamlit run src/frontend/app.py
```

### 5. Access the Application

- **Frontend UI:** http://localhost:8501
- **API Documentation:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

## 📁 Project Structure

````
insiderTracker/
├── src/                          # All source code
│   ├── backend/                  # FastAPI Backend
│   │   ├── main.py              # FastAPI app + REST endpoints
│   │   ├── db.py                # SQLAlchemy database setup
│   │   ├── models.py            # ORM models (TrackedWallet, Trade, AlertLog)
│   │   ├── crud.py              # Database CRUD operations
│   │   ├── hashdive.py          # Hashdive API client
│   │   ├── poller.py            # Background polling service
│   │   ├── emailer.py           # SMTP email notifications
│   │   └── settings.py          # Environment configuration
│   │
│   ├── frontend/                # Streamlit Frontend
│   │   └── app.py               # Web UI (API consumer)
│   │
│   └── data/                    # Database Storage
│       └── tracker.db           # SQLite database (auto-created)
│
├── config/                      # Configuration
│   └── wallets.yaml            # Optional: initial wallet list
│
├── scripts/                     # Utility scripts
│   └── run_tracker.py
│
├── venv/                        # Virtual environment
├── .env                         # Environment variables (create from .env.example)
├──💡 How It Works

### Data Flow

1. **Add Wallets** - Use Streamlit UI to add wallet addresses to track
2. **Background Polling** - Backend polls Hashdive API every 60 seconds
3. **Trade Detection** - New trades are automatically detected via deduplication
4. **Email Alerts** - Notifications sent for trades meeting size threshold
5. **View Trades** - Browse and filter trade history in the web UI

### Key Components

**Backend (Always Running):**
- REST API server (FastAPI)
- Async background poller
- SQLite database with WAL mode
- Trade deduplication via unique IDs
- SMTP email notifications

**Frontend (On-Demand):**
- Streamlit web interface
- Wallet CRUD operations
- Trade filtering and search
- Real-time system status
- Paginated Alerts

Email notifications include:

- Wallet address and custom name
- Market name and asset ID
- Side (Buy / Sell)
- Price and shares traded
- Total USD amount
- Timestamp

**Alert Conditions:**
- Trade meets `MIN_TRADE_SIZE_USD` threshold
- Alerts are enabled for the wallet
- Trade is new (not a duplicate)

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Database
DATABASE_URL=sqlite:///./src/data/tracker.db

# Email (Gmail recommended)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password      # Use Gmail App Password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_USE_TLS=true

# Hashdive API
HASHDIVE_API_KEY=optional-api-key
HASHDIVE_API_URL=https://api.hashdive.io

# Polling Settings
POLL_INTERVAL_SECONDS=60              # Background poll frequency
INITIAL_LOOKBACK_DAYS=7               # How far back to check for trades
MIN_TRADE_SIZE_USD=100                # Minimum trade size for alerts

# Logging
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR

# Frontend
API_BASE_URL=http://localhost:8080    # Backend API endpoint
````

### Gmail App Password Setup

1. Enable 2-Factor Authentication on Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and your device
4. Copy the 16-digit password
5. Use this in `EMAIL_PASSWORD` (not your regular password)

## 🔌 REST API Endpoints

The backend provides a full REST API:

**Wallet Management:**

- `GET /favorites` - List tracked wallets
- `POST /favorites` - Add new wallet
- `PATCH /favorites/{address}` - Update wallet
- `DELETE /favorites/{address}` - Remove wallet

**Trade Queries:**

- `GET /trades` - Query trades with filters
- `GET /markets` - Get distinct market names

**System:**

- `GET /health` - Health check and poller status
- `POST /poller/run-once` - Trigger manual poll
  **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup guide with troubleshooting
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture and design decisions
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[API Docs](http://localhost:8080/docs)** - Interactive API documentation (when running)

## 🛠️ Development

### Running in Development Mode

```bash
# Terminal 1: Backend with auto-reload
uvicorn src.backend.main:app --reload --port 8080

# Terminal 2: Frontend with auto-reload
streamlit run src/frontend/app.py
```

### Testing

```bash
# Test Python syntax
python -m py_compile src/backend/main.py
python -m py_compile src/frontend/app.py

# Test API health
curl http://localhost:8080/health

# Test manual poll
curl -X POST http://localhost:8080/poller/run-once
```

### Debug Logging

```bash
# In .env file
LOG_LEVEL=DEBUG

# Backend will show detailed logs
```

## 🐛 Troubleshooting

**Backend won't start:**

- Check port 8080 is available
- Verify `.env` file exists and has valid settings
- Check Python version (3.8+ required)

**Frontend can't connect:**

- Ensure backend is running first
- Verify `API_BASE_URL` environment variable
- Check firewall settings

**No trades appearing:**

- Wait 60 seconds for first poll cycle
- Check backend logs for errors
- Verify wallet addresses are valid
- Check Hashdive API is accessible

**Emails not sending:**

- Use Gmail App Password (not regular password)
- Verify SMTP settings in `.env`
- Check `alerts_enabled=true` for wallet
- Ensure trade meets `MIN_TRADE_SIZE_USD`

## 🚀 Production Deployment

For production use:

1. **Use PostgreSQL** instead of SQLite for better concurrency
2. **Process Manager** - Use systemd, supervisor, or Docker
3. **Reverse Proxy** - Nginx or Traefik for HTTPS
4. **Environment** - Use proper secrets management (not .env file)
5. **Monitoring** - Set up logging and alerting
6. **Backups** - Regular database backups

Example systemd service:

```ini
[Unit]
Description=PolyMarket Trade Tracker Backend
After=network.target

[Service]
Type=simple
User=polymarket
WorkingDirectory=/opt/polymarket-tracker
Environment="PATH=/opt/polymarket-tracker/venv/bin"
ExecStart=/opt/polymarket-tracker/venv/bin/uvicorn src.backend.main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🎯 Success Checklist

Before first use, verify:

- ✅ Backend starts without errors
- ✅ Frontend connects to backend
- ✅ Can add/edit/delete wallets via UI
- ✅ Trades appear after ~60 seconds
- ✅ Email test successful
- ✅ Database created in `src/data/tracker.db`
- ✅ Health endpoint returns status: `curl http://localhost:8080/health`
