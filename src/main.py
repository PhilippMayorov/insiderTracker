"""
PolyMarket Anomaly Detector - Main Entry Point
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="PolyMarket Anomaly Detector",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🔍 PolyMarket Anomaly Detector")
    st.markdown("---")
    
    # Welcome message
    st.header("Welcome to the PolyMarket Anomaly Detection System")
    
    st.write("""
    This system detects and flags unusual, high-signal trading activity on PolyMarket 
    using **public data only**.
    """)
    
    # Features overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Data Ingestion")
        st.write("Fetches data from PolyMarket APIs and Polygon subgraphs")
        
    with col2:
        st.subheader("🎯 Anomaly Detection")
        st.write("10+ detectors for whale trades, timing anomalies, and more")
        
    with col3:
        st.subheader("📈 Visualization")
        st.write("Interactive dashboards for analysis and investigation")
    
    st.markdown("---")
    
    # Quick stats (placeholder)
    st.subheader("System Status")
    
    status_col1, status_col2, status_col3, status_col4 = st.columns(4)
    
    with status_col1:
        st.metric("Active Detectors", "10")
    
    with status_col2:
        st.metric("Markets Monitored", "0")
    
    with status_col3:
        st.metric("Alerts Today", "0")
    
    with status_col4:
        st.metric("System Health", "🟢 OK")
    
    st.markdown("---")
    
    # Getting started
    st.subheader("🚀 Getting Started")

    
    
    # st.write("""
    # 1. **Set up your environment**: Copy `.env.example` to `.env` and configure
    # 2. **Start services**: Run `docker-compose up -d` to start PostgreSQL and MinIO
    # 3. **Run detectors**: Execute `python src/main.py --run-all` to start detection
    # 4. **Explore results**: Use the sidebar to navigate to different analysis views
    # """)
    
    # Footer
    st.markdown("---")
    st.caption("PolyMarket Anomaly Detector v0.1.0 | Research Tool | Public Data Only")


if __name__ == "__main__":
    main()
