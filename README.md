# PolyMarket Anomaly Detector

A local research tool built in Python that detects and flags unusual, high-signal trading activity on PolyMarket using **public data only**.

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/polymarket-anomaly-detector.git
cd polymarket-anomaly-detector
cp .env.example .env
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

### 4. Run the Streamlit UI

```bash
streamlit run src/main.py
```

Visit http://localhost:8501 to see the application.

## 📁 Project Structure

See [copilot-instructions.md](.github/copilot-instructions.md) for detailed architecture information.

## 🔧 Development

- **API**: `uvicorn src.api.main:app --reload`
- **Tests**: `pytest -v`
- **Detectors**: `python src/main.py --run-all`

## 📚 Documentation

- [Architecture Guide](.github/copilot-instructions.md)
- [Configuration](config/)
- [API Documentation](docs/api.md) _(coming soon)_

## 🛡️ Ethics & Privacy

- Uses **public data only**
- No deanonymization attempts
- Labels behavior as "unusual" or "atypical", not "malicious"
- Designed for research and compliance analysis

## 📄 License

MIT License © 2025
