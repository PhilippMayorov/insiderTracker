# PolyMarket Anomaly Detector — Project README (for GitHub Copilot Agent)

## 📘 Overview

This repository contains the **PolyMarket Anomaly Detector**, a local research tool built in **Python** (front-end + back-end) that detects and flags unusual, high-signal trading activity on PolyMarket using **public data only**.

The system is designed for research, monitoring, and compliance analysis—not enforcement. It’s built to be modular, explainable, and reproducible, using public APIs and on-chain data to identify patterns such as whale trades, coordinated actors, timing anomalies, and liquidity shocks.
---

## 🧱 Core Features

- **Public Data Ingestion** from PolyMarket APIs and Polygon subgraphs.
- **Anomaly Detection Engine** using rule-based, statistical, and graph correlation detectors.
- **Feature & Signal Layer** (Silver tables) built with DuckDB/Polars.
- **Risk Aggregation (Risk Brain)** combining detector outputs into unified scores.
- **Investigator UI** built in **Python (FastAPI + PyWebIO/Streamlit)** for analysis & visualization.
- **Evidence Bundles** for each alert: CSVs, JSON summaries, and charts.

---

## 🧩 Project Structure

```
polymarket-anomaly-detector/
├── README.md                     # This file
├── docker-compose.yml             # Local container orchestration
├── requirements.txt               # Python dependencies
├── setup.py                       # Package installer config
├── .env.example                   # Example environment variables
├── config/                        # YAML configs for detectors, risk, and system
│   ├── detectors.yaml
│   ├── pipeline.yaml
│   └── logging.yaml
│
├── data/                          # Local data storage (Bronze, Silver, Gold)
│   ├── bronze/                    # Raw API and on-chain dumps (Parquet)
│   ├── silver/                    # Cleaned feature tables (DuckDB views)
│   └── gold/                      # Aggregated and scored signals
│
├── src/                           # Main Python source code
│   ├── api/                       # FastAPI REST endpoints
│   ├── app_frontend/              # Streamlit or PyWebIO UI components
│   ├── data/                      # Data ingestion & ETL scripts
│   ├── features/                  # Feature computation (Silver Layer)
│   ├── detectors/                 # D1–D10 anomaly detectors
│   ├── risk/                      # Risk aggregation engine
│   ├── alerts/                    # Alert generation and evidence
│   ├── storage/                   # Database models and persistence
│   ├── utils/                     # Helper modules (logging, config, math)
│   ├── main.py                    # CLI entry point
│   └── settings.py                # Environment configuration
│
├── tests/                         # Unit and integration tests
│   ├── fixtures/                  # Synthetic test data
│   ├── test_detectors.py
│   ├── test_api.py
│   ├── test_etl.py
│   └── test_ui.py
│
├── notebooks/                     # Jupyter notebooks for research
│   ├── backtesting.ipynb
│   ├── calibration.ipynb
│   └── exploratory.ipynb
│
└── scripts/                       # Utility CLI scripts
    ├── run_all_detectors.py
    ├── backfill_data.py
    └── export_evidence.py
```

---

## 🐍 Python Tech Stack

| Component         | Technology                          |
| ----------------- | ----------------------------------- |
| **Back-end API**  | FastAPI (async REST)                |
| **Front-end UI**  | Streamlit / PyWebIO (Python-native) |
| **Data Engine**   | DuckDB + Polars + SQLAlchemy        |
| **Database**      | PostgreSQL 16                       |
| **Storage**       | MinIO (S3-compatible)               |
| **Visualization** | Plotly / Matplotlib                 |
| **Testing**       | pytest + faker + httpx              |

---

## ⚙️ Setup & Installation

### 1️⃣ Clone & Initialize

```bash
git clone https://github.com/yourusername/polymarket-anomaly-detector.git
cd polymarket-anomaly-detector
cp .env.example .env
```

### 2️⃣ Build Containers

```bash
docker-compose up -d
```

### 3️⃣ Install Python Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4️⃣ Run Database Migrations

```bash
python -m src.storage.db migrate
```

### 5️⃣ Launch API & UI

```bash
uvicorn src.api.main:app --reload
streamlit run src.app_frontend.dashboard.py
```

API will run at `http://localhost:8080`
UI will run at `http://localhost:8501`

---

## 🚨 Running the Detector Pipeline

```bash
python src/main.py --run-all
```

This executes the full workflow:

1. Fetch market and trade data (ETL)
2. Build Silver features
3. Run all D1–D10 detectors
4. Aggregate scores and create alerts
5. Push results to Postgres + UI

---

## 🧪 Testing

```bash
pytest -v --maxfail=1 --disable-warnings
```

Synthetic test cases for each detector are included in `tests/fixtures/`.

---

## 🛡️ Ethics & Privacy

- Uses **public data only** (PolyMarket APIs, public subgraphs, Polygon RPC).
- Avoids labeling behavior as malicious; uses “unusual”, “atypical”, or “elevated”.
- No attempt at deanonymization or enforcement.

---

## 🤖 GitHub Copilot Agent Guide

Copilot can assist with:

- Adding new detectors using the base `Detector` class.
- Generating FastAPI endpoints for new data or analytics routes.
- Building Streamlit/PyWebIO dashboards.
- Writing SQLAlchemy models or schema migrations.
- Expanding test coverage for detectors or pipelines.

**Prompt Examples:**

- “Add a detector that identifies sudden liquidity inflows to a wallet.”
- “Build a Streamlit chart that plots top whale trades by market.”
- “Generate a FastAPI endpoint to list alerts by level.”

---

## 📚 License

MIT License © 2025 PolyMarket Surveillance Architect
