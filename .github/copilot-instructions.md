# PolyMarket Trade Tracker

_A lightweight tracking and alerting system for monitoring specific PolyMarket wallets_

---

## 📘 Overview

This repository contains the **PolyMarket Trade Tracker**, a simple monitoring tool built in **Python** that tracks a predefined list of PolyMarket trader wallets and sends **email alerts whenever a new trade is detected**.

The system uses **publicly available data only**, sourced from the **Hashdive (Hashmaps) API**, and is intended for personal monitoring, research, and notification purposes.

There is **no analysis, scoring, or labeling of behavior** — the system only answers one question:

> **“Did a tracked wallet make a new trade?”**

---

## 🎯 What This Project Does

- Track a **manually defined list of PolyMarket wallet addresses**
- Poll for **new trades** using the Hashdive API
- Detect **previously unseen trades**
- Send an **email notification** when a new trade occurs
- Store basic trade history locally to prevent duplicate alerts

---

## 🚫 What This Project Does NOT Do

- ❌ No insider trading detection
- ❌ No anomaly detection or risk scoring
- ❌ No behavioral classification
- ❌ No market predictions
- ❌ No enforcement or interpretation

---

## 🧱 Core Features

### Wallet Tracking

- Track any number of PolyMarket wallets
- Wallets are defined explicitly by the user
- Each wallet is treated independently

### Trade Monitoring

- Uses Hashdive’s enriched `/get_trades` endpoint
- Polls on a configurable interval
- Detects new trades via trade ID or timestamp comparison

### Email Alerts

- Sends an email when a tracked wallet places a new trade
- Includes:
  - Wallet address
  - Market name
  - Side (YES / NO)
  - Price
  - Size
  - Timestamp

---

## 🧩 Project Structure (Simplified)

```text
polymarket-trade-tracker/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── wallets.yaml        # List of tracked wallets
│
├── data/
│   └── trades.db           # Local SQLite or DuckDB store
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
│   └── main.py             # Entry point
│
└── scripts/
    └── run_tracker.py
```
