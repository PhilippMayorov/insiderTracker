Below is a **fully updated version of your README**, with:

- New **“Insider / Informed Trader Alert”** features clearly documented (without accusatory language).
- Concrete, step-by-step guidance for integrating the **Hashdive (Hashmaps) API**, including configuration, rate limits, data flow, and where it fits in the pipeline.
- Clear separation between **data provider responsibilities** and **detector logic**, keeping the project compliance-aware and research-focused.

You can replace your existing `README.md` with the content below.

---

# PolyMarket Anomaly Detector — Project README

_(for GitHub Copilot Agent & Research Use)_

## 📘 Overview

This repository contains the **PolyMarket Anomaly Detector**, a local research and monitoring tool built in **Python** that detects and flags unusual, high-signal trading behavior on PolyMarket using **publicly available data only**.

The system is designed for research, market surveillance, and compliance analysis — not enforcement. It focuses on identifying statistical and behavioral anomalies, including whale activity, coordinated actors, timing-based anomalies, and potentially informed or privileged trading patterns, without making claims about intent or legality.

The architecture is modular, explainable, and reproducible, combining public APIs, enriched trade data, and on-chain signals.

---

## 🧱 Core Features

### Public Data Ingestion

- PolyMarket public endpoints
- Polygon on-chain data
- Hashdive (Hashmaps) API for enriched trades, OHLCV, and whale activity

### Anomaly Detection Engine

- Rule-based detectors
- Statistical baselines & z-scores
- Temporal and cross-market correlation logic

### Insider / Informed Trading Alerts (Non-Accusatory)

- Detects pre-resolution positioning, pre-news accumulation, and asymmetric timing advantages
- Labels alerts as **“Informed Timing Risk”** or **“Elevated Information Asymmetry”**
- Produces evidence bundles instead of judgments

### Feature & Signal Layer (Silver Tables)

- DuckDB + Polars feature views
- Wallet-level, market-level, and temporal features

### Risk Aggregation (“Risk Brain”)

- Combines detector outputs into unified, explainable scores

### Investigator UI

- Built in **FastAPI + Streamlit / PyWebIO**
- Drill-downs by wallet, market, and alert type

### Evidence Bundles

- CSV trade slices
- JSON summaries
- Price + timing charts for each alert

---

## 🚨 Insider / Informed Trading Alert Features

⚠️ **Important**: The system does **not** claim illegal insider trading.  
Alerts indicate statistically unusual timing or positioning patterns that may warrant further analysis.

### Example Alert Types

#### Pre-Resolution Accumulation

- Wallet accumulates a large position shortly before market resolution
- Especially when price impact is minimal at entry

#### Pre-Event Timing Advantage

- Trades occur shortly before major market-moving events (debates, court rulings, announcements)
- Compared against historical behavior of the same wallet

#### Asymmetric Risk Exposure

- Wallet takes large directional exposure with unusually low downside volatility
- Compared to contemporaneous traders

#### Cross-Market Information Signals

- Same wallet positions consistently ahead of correlated markets resolving

### Alert Output Includes

- Triggered detector IDs (e.g. `D7_TIMING_ASYMMETRY`)
- Risk score contribution
- Trade-level evidence (from Hashdive + on-chain)
- Market context (price, volume, liquidity)
- Clear non-accusatory language

---

## 🧩 Project Structure

```text
polymarket-anomaly-detector/
├── README.md
├── docker-compose.yml
├── requirements.txt
├── setup.py
├── .env.example
├── config/
│   ├── detectors.yaml
│   ├── pipeline.yaml
│   └── logging.yaml
│
├── data/
│   ├── bronze/          # Raw API & on-chain data (Parquet)
│   ├── silver/          # Feature tables (DuckDB views)
│   └── gold/            # Aggregated risk & alerts
│
├── src/
│   ├── api/             # FastAPI endpoints
│   ├── app_frontend/    # Streamlit / PyWebIO UI
│   ├── data/
│   │   ├── ingest_hashdive.py   # Hashdive API ingestion
│   │   ├── ingest_polymarket.py
│   │   └── ingest_chain.py
│   ├── features/
│   ├── detectors/
│   │   ├── d1_whale_trades.py
│   │   ├── d5_coordination.py
│   │   ├── d7_timing_asymmetry.py   # Insider-style timing detector
│   │   └── d9_pre_resolution.py
│   ├── risk/
│   ├── alerts/
│   ├── storage/
│   ├── utils/
│   ├── main.py
│   └── settings.py
│
├── tests/
├── notebooks/
└── scripts/
```

## 🔌 Hashdive (Hashmaps) API Integration Guide

The **Hashdive API** is the primary source of enriched PolyMarket trade data used by this system.

### Why Hashdive?

- Normalized trade history by wallet
- Market metadata enrichment
- OHLCV aggregates
- Whale trade detection
- Consistent pagination & formats

---

## ⚙️ Base Configuration

Add the following to your `.env` file:

```env
HASHDIVE_API_KEY=your_api_key_here
HASHDIVE_BASE_URL=https://hashdive.com/api
HASHDIVE_RATE_LIMIT_QPS=1
```

## 🚦 Rate Limits

1 request per second

60 requests per minute

Each request consumes 1 credit

Default: 1000 credits / month (PRO beta)

The ingestion layer includes built-in throttling and retry logic.

## 🔑 Key Endpoints Used

/get_trades

Used for:

Wallet-level trade reconstruction

Insider / timing detectors

Coordination analysis

Typical usage:

Backfill historical trades

Incremental polling every minute

/get_positions

Used for:

Current exposure snapshots

Pre-resolution accumulation detection

/get_ohlcv

Used for:

Price & volume context

Volatility normalization

Timing asymmetry baselines

/get_latest_whale_trades

Used for:

High-signal monitoring

Fast-path whale alerts

## 🧪 Example: Hashdive Ingestion Flow

def ingest_wallet_trades(wallet):
trades = hashdive.get_trades(wallet)
write_bronze(trades)
update_silver_features(trades)
