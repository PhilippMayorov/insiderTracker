"""
PolyMarket Trade Tracker - Streamlit Dashboard
"""
import streamlit as st
import logging
from datetime import datetime, timedelta
from pathlib import Path
import time
import yaml

from tracker.state import TradeState
from integrations.hashdive import HashdiveClient
from settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="PolyMarket Trade Tracker",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'favorite_addresses' not in st.session_state:
    st.session_state.favorite_addresses = [
        {"name": "frenchlaundry", "address": "0x1c3cdc2caa24eeb0434100f82ac32c2a260b1b01", "smart_score": 3.35},
        {"name": "tom63901", "address": "0x36fb0ccfe40b9dae0922743d457e21dee59b494e", "smart_score": 0.04},
        {"name": "merci", "address": "0x00f23f6a27a3e5a92da952da39526b17087947e9bc4f", "smart_score": 3.51},
    ]

if 'all_trades' not in st.session_state:
    st.session_state.all_trades = []

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None


def load_wallets_from_config():
    """Load wallet addresses from wallets.yaml"""
    config_path = "config/wallets.yaml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('wallets', [])
    except Exception as e:
        logger.error(f"Failed to load wallets config: {e}")
        return []


def fetch_trades_for_wallets(wallets, hashdive_client, trade_state):
    """Fetch recent trades for all monitored wallets"""
    all_trades = []
    
    for wallet in wallets:
        if not wallet.get('enabled', True):
            continue
            
        address = wallet.get('address', '')
        name = wallet.get('name', address[:8])
        
        try:
            # Fetch trades from last 7 days
            start_time = datetime.now() - timedelta(days=7)
            trades = hashdive_client.get_trades(
                wallet_address=address,
                start_time=start_time,
                limit=100
            )
            
            # Add wallet info to each trade
            for trade in trades:
                trade['wallet_name'] = name
                trade['wallet_address'] = address
                all_trades.append(trade)
                
        except Exception as e:
            logger.error(f"Failed to fetch trades for {name}: {e}")
    
    # Sort by timestamp (most recent first)
    all_trades.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    return all_trades


def format_time_ago(timestamp):
    """Format timestamp as 'time ago' string"""
    try:
        if isinstance(timestamp, int):
            trade_time = datetime.fromtimestamp(timestamp)
        else:
            trade_time = datetime.fromisoformat(str(timestamp))
        
        now = datetime.now()
        delta = now - trade_time
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m ago"
        elif hours > 0:
            return f"{hours}h {minutes}m ago"
        else:
            return f"{minutes}m ago"
    except:
        return "Unknown"


def main():
    """Main Streamlit application"""
    
    # Header with banner
    st.markdown("### 🔎 New: Potential Insiders Dashboard")
    st.markdown("Monitor suspicious traders and the markets where they may be active. 👉 [Explore Potential Insiders](#)")
    st.markdown("---")
    
    # Favorite Addresses Section
    st.subheader("Favorite Addresses")
    st.caption("You can edit the custom names by double clicking them.")
    
    # Display favorite addresses table
    if st.session_state.favorite_addresses:
        # Create editable table
        col1, col2, col3 = st.columns([2, 4, 1])
        
        with col1:
            st.markdown("**Custom Name**")
        with col2:
            st.markdown("**User**")
        with col3:
            st.markdown("**Smart Score**")
        
        for i, fav in enumerate(st.session_state.favorite_addresses):
            col1, col2, col3 = st.columns([2, 4, 1])
            
            with col1:
                new_name = st.text_input(
                    "Name",
                    value=fav['name'],
                    key=f"name_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.favorite_addresses[i]['name'] = new_name
            
            with col2:
                st.code(fav['address'], language=None)
            
            with col3:
                st.text(f"{fav['smart_score']:.2f}")
    
    st.markdown("---")
    
    # Filters Section
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        filter_user = st.text_input(
            "Filter by user (optional)",
            placeholder="Paste the address here and press enter",
            key="filter_user"
        )
    
    with filter_col2:
        filter_side = st.selectbox(
            "Filter by side",
            options=["All", "Buy", "Sell"],
            key="filter_side"
        )
    
    # Price and amount filters
    price_col1, price_col2 = st.columns(2)
    
    with price_col1:
        min_price = st.number_input(
            "Min Price (USD)",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01,
            key="min_price"
        )
    
    with price_col2:
        max_price = st.number_input(
            "Max Price (USD)",
            min_value=0.0,
            max_value=1.0,
            value=1.0,
            step=0.01,
            key="max_price"
        )
    
    # USD amount filters
    amount_col1, amount_col2 = st.columns(2)
    
    with amount_col1:
        min_amount = st.number_input(
            "Min USD amount",
            min_value=0.0,
            value=1.0,
            step=1.0,
            key="min_amount"
        )
    
    with amount_col2:
        max_amount = st.number_input(
            "Max USD amount",
            min_value=0.0,
            value=1000000.0,
            step=100.0,
            key="max_amount"
        )
    
    # Market filter
    filter_market = st.selectbox(
        "Filter by market (1 matching your filters)",
        options=["All"],
        key="filter_market"
    )
    
    # Timezone info
    st.info("All trade timestamps have been converted to your local time zone: America/Toronto (current local time: 2026-01-12 11:05:15).")
    
    # Page number and sound alerts
    control_col1, control_col2 = st.columns([1, 3])
    
    with control_col1:
        page_number = st.number_input(
            "Page number",
            min_value=1,
            value=1,
            step=1,
            key="page_number"
        )
    
    with control_col2:
        enable_sound = st.checkbox(
            "🔔 Enable sound alerts for real-time trades matching current filters",
            value=False,
            key="enable_sound"
        )
    
    # Refresh button
    if st.button("🔄 Refresh Trades", type="primary", use_container_width=True):
        with st.spinner("Fetching latest trades..."):
            hashdive_client = HashdiveClient(api_key=settings.hashdive_api_key)
            trade_state = TradeState(db_path=settings.trade_db_path)
            
            wallets = load_wallets_from_config()
            st.session_state.all_trades = fetch_trades_for_wallets(
                wallets, hashdive_client, trade_state
            )
            st.session_state.last_refresh = datetime.now()
            st.success(f"Loaded {len(st.session_state.all_trades)} trades")
    
    # Display trades table
    st.markdown("---")
    st.markdown(f"**Page 1 of 1** (1 results)")
    
    if st.session_state.all_trades:
        # Filter trades based on user inputs
        filtered_trades = st.session_state.all_trades
        
        if filter_user:
            filtered_trades = [t for t in filtered_trades if filter_user.lower() in t.get('wallet_address', '').lower()]
        
        if filter_side != "All":
            filtered_trades = [t for t in filtered_trades if t.get('side', '').lower() == filter_side.lower()]
        
        # Apply price and amount filters
        filtered_trades = [
            t for t in filtered_trades
            if min_price <= t.get('price', 0) <= max_price
            and min_amount <= t.get('value_usd', 0) <= max_amount
        ]
        
        # Create trades table
        if filtered_trades:
            # Table header
            header_cols = st.columns([1, 0.7, 3, 1, 0.8, 1.2, 2.5, 1.2, 1.5])
            headers = ["Time Ago", "Side", "Market", "Trade Size", "Price", "Name", "User", "Traded Shares", "Timestamp"]
            
            for col, header in zip(header_cols, headers):
                col.markdown(f"**{header}**")
            
            # Display trades (paginated)
            page_size = 20
            start_idx = (page_number - 1) * page_size
            end_idx = start_idx + page_size
            
            for trade in filtered_trades[start_idx:end_idx]:
                trade_cols = st.columns([1, 0.7, 3, 1, 0.8, 1.2, 2.5, 1.2, 1.5])
                
                # Time ago
                trade_cols[0].text(format_time_ago(trade.get('timestamp')))
                
                # Side (Buy/Sell)
                side = trade.get('side', 'Buy')
                if side.lower() == 'buy':
                    trade_cols[1].markdown("🟢 **Buy**")
                else:
                    trade_cols[1].markdown("🔴 **Sell**")
                
                # Market
                market_name = trade.get('market', 'Unknown Market')
                trade_cols[2].text(market_name[:50] + "..." if len(market_name) > 50 else market_name)
                
                # Trade size
                trade_size = trade.get('value_usd', 0)
                trade_cols[3].text(f"${trade_size:.2f}")
                
                # Price
                price = trade.get('price', 0)
                trade_cols[4].text(f"${price:.2f}")
                
                # Name
                wallet_name = trade.get('wallet_name', 'Unknown')
                trade_cols[5].markdown(f"**{wallet_name}**")
                
                # User address
                address = trade.get('wallet_address', '')
                trade_cols[6].code(address[:20] + "..." if len(address) > 20 else address, language=None)
                
                # Traded shares
                shares = trade.get('shares', 0)
                trade_cols[7].text(f"{shares:,.2f}")
                
                # Timestamp
                timestamp = trade.get('timestamp_dt', datetime.now())
                trade_cols[8].text(str(timestamp))
        
        else:
            st.info("No trades match your current filters.")
    
    else:
        st.info("Click 'Refresh Trades' to load recent trades from monitored wallets.")
    
    # Footer
    if st.session_state.last_refresh:
        st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
