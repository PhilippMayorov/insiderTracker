"""
PolyMarket Trade Tracker - Streamlit Frontend
API Consumer (calls FastAPI backend)
"""
import streamlit as st
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")

# Page configuration
st.set_page_config(
    page_title="PolyMarket Trade Tracker",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# API Helper Functions
# ============================================================================

def api_get(endpoint: str, params: Dict = None) -> Optional[Dict]:
    """Make GET request to API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API GET error: {e}")
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, data: Dict) -> Optional[Dict]:
    """Make POST request to API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API POST error: {e}")
        st.error(f"API Error: {e}")
        return None


def api_patch(endpoint: str, data: Dict) -> Optional[Dict]:
    """Make PATCH request to API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.patch(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API PATCH error: {e}")
        st.error(f"API Error: {e}")
        return None


def api_delete(endpoint: str) -> bool:
    """Make DELETE request to API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"API DELETE error: {e}")
        st.error(f"API Error: {e}")
        return False


# ============================================================================
# Data Fetching Functions
# ============================================================================

def fetch_favorites() -> List[Dict]:
    """Fetch tracked wallets from API"""
    result = api_get("/favorites")
    return result if result else []


def fetch_trades(filters: Dict) -> Dict:
    """Fetch trades with filters from API"""
    result = api_get("/trades", params=filters)
    return result if result else {"items": [], "total_results": 0, "total_pages": 0}


def fetch_markets() -> List[str]:
    """Fetch distinct market names from API"""
    result = api_get("/markets")
    return result if result else []


# ============================================================================
# Utility Functions
# ============================================================================

def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as 'time ago' string"""
    try:
        # Parse ISO format timestamp (assuming UTC)
        trade_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Remove timezone info to compare with current local time
        if trade_time.tzinfo is not None:
            trade_time = trade_time.replace(tzinfo=None)
        
        # Get current time as naive datetime
        now = datetime.now()
        
        delta = now - trade_time
        
        # Handle negative delta (future timestamps)
        if delta.total_seconds() < 0:
            return "Just now"
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h ago"
        elif hours > 0:
            return f"{hours}h {minutes}m ago"
        else:
            return f"{minutes}m ago"
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return "Unknown"


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main Streamlit application"""
    
    st.title("🔎 PolyMarket Trade Tracker")
    
    # Check API health
    health = api_get("/health")
    if not health:
        st.error("⚠️ Cannot connect to backend API. Please ensure the backend is running.")
        st.code(f"Expected API URL: {API_BASE_URL}")
        st.info("Start the backend with: `uvicorn src.backend.main:app --reload --port 8080`")
        return
    
    # Show health status in sidebar
    with st.sidebar:
        st.subheader("System Status")
        if health.get("status") == "ok":
            st.success("✅ Backend Online")
        else:
            st.warning("⚠️ Backend Degraded")
        
        st.metric("Poller Status", "🟢 Running" if health.get("poller_running") else "🔴 Stopped")
        st.metric("Database", "🟢 Connected" if health.get("database_connected") else "🔴 Disconnected")
        
        st.markdown("---")
        st.markdown(f"**API Endpoint:** `{API_BASE_URL}`")
    
    # ========================================================================
    # Tracked Insider Traders Section
    # ========================================================================
    
    st.subheader("Tracked Insider Traders")
    st.caption("Manage your tracked wallet addresses and their details.")
    
    # Add new trader button
    if st.button("➕ Add New Trader", type="secondary"):
        st.session_state.show_add_form = not st.session_state.get('show_add_form', False)
    
    # Add new trader form
    if st.session_state.get('show_add_form', False):
        with st.form("add_trader_form", clear_on_submit=True):
            st.markdown("#### Add New Insider Trader")
            
            form_col1, form_col2, form_col3 = st.columns([2, 4, 2])
            
            with form_col1:
                new_name = st.text_input("Name", placeholder="Enter trader name")
            
            with form_col2:
                new_address = st.text_input("Wallet Address", placeholder="0x...")
            
            with form_col3:
                new_market = st.text_input("Main Market", placeholder="e.g., US Elections")
            
            submit_col1, submit_col2 = st.columns([1, 5])
            
            with submit_col1:
                submitted = st.form_submit_button("Add Trader", type="primary")
            
            with submit_col2:
                cancel = st.form_submit_button("Cancel")
            
            if submitted and new_name and new_address:
                result = api_post("/favorites", {
                    "wallet_address": new_address,
                    "custom_name": new_name,
                    "main_market": new_market or "Unknown",
                    "alerts_enabled": True
                })
                
                if result:
                    st.success(f"✅ Added trader: {new_name}")
                    st.session_state.show_add_form = False
                    st.rerun()
            
            if cancel:
                st.session_state.show_add_form = False
                st.rerun()
    
    st.markdown("")
    
    # Fetch and display tracked wallets
    favorites = fetch_favorites()
    
    if favorites:
        # Create table header
        col1, col2, col3, col4, col5 = st.columns([2, 4, 2, 0.8, 1.2])
        
        with col1:
            st.markdown("**Custom Name**")
        with col2:
            st.markdown("**User Address**")
        with col3:
            st.markdown("**Main Market Traded**")
        with col4:
            st.markdown("**Actions**")
        with col5:
            st.markdown("**Fetch History**")
        
        # Display each trader with edit and delete options
        traders_to_delete = []
        
        for i, fav in enumerate(favorites):
            col1, col2, col3, col4, col5 = st.columns([2, 4, 2, 0.8, 1.2])
            
            original_name = fav.get('custom_name', '')
            original_address = fav['wallet_address']
            original_market = fav.get('main_market', '')
            
            with col1:
                new_name = st.text_input(
                    "Name",
                    value=original_name,
                    key=f"name_{i}",
                    label_visibility="collapsed"
                )
            
            with col2:
                new_address = st.text_input(
                    "Address",
                    value=original_address,
                    key=f"address_{i}",
                    label_visibility="collapsed"
                )
            
            with col3:
                new_market = st.text_input(
                    "Market",
                    value=original_market,
                    key=f"market_{i}",
                    label_visibility="collapsed"
                )
            
            with col4:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this trader"):
                    traders_to_delete.append(i)
            
            with col5:
                if st.button("📥 Fetch Trades", key=f"fetch_{i}", help="Fetch trade history from Hashdive"):
                    with st.spinner(f"Fetching trades for {original_name or original_address[:8]}..."):
                        result = api_post(f"/favorites/{original_address}/fetch-history", {})
                        if result:
                            st.success(f"✅ {result.get('message', 'Trades imported successfully')}")
                            st.info(f"Imported: {result.get('imported', 0)} | Skipped: {result.get('skipped', 0)} | Total: {result.get('total', 0)}")
                            # Refresh the page to show new trades
                            st.rerun()
            
            # Check if values changed and update via API
            if (new_name != original_name or 
                new_address != original_address or 
                new_market != original_market):
                
                # If address changed, delete old and create new
                if new_address != original_address:
                    api_delete(f"/favorites/{original_address}")
                    api_post("/favorites", {
                        "wallet_address": new_address,
                        "custom_name": new_name,
                        "main_market": new_market,
                        "alerts_enabled": True
                    })
                else:
                    # Just update name/market
                    api_patch(f"/favorites/{original_address}", {
                        "custom_name": new_name,
                        "main_market": new_market
                    })
        
        # Delete traders after iteration
        if traders_to_delete:
            for idx in sorted(traders_to_delete, reverse=True):
                deleted_trader = favorites[idx]
                if api_delete(f"/favorites/{deleted_trader['wallet_address']}"):
                    st.success(f"🗑️ Deleted trader: {deleted_trader.get('custom_name', '')}")
            st.rerun()
    
    else:
        st.info("No traders tracked yet. Click 'Add New Trader' to get started.")
    
    st.markdown("---")
    
    # ========================================================================
    # Filters Section
    # ========================================================================
    
    st.markdown("### Filters")
    
    # Row 1: User and Purchase Side
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        filter_user = st.text_input(
            "Filter by User",
            placeholder="Paste wallet address here",
            key="filter_user",
            help="Enter a wallet address to filter trades"
        )
    
    with filter_col2:
        filter_side = st.selectbox(
            "Filter by Purchase Side",
            options=["All", "buy", "sell"],
            key="filter_side",
            help="Filter trades by buy or sell side"
        )
    
    # Row 2: Trade Size (Min to Max)
    trade_size_col1, trade_size_col2 = st.columns(2)
    
    with trade_size_col1:
        min_trade_size = st.number_input(
            "Min Trade Size (USD)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            key="min_trade_size"
        )
    
    with trade_size_col2:
        max_trade_size = st.number_input(
            "Max Trade Size (USD)",
            min_value=0.0,
            value=1000000.0,
            step=100.0,
            key="max_trade_size"
        )
    
    # Row 3: Market Name Filter
    filter_market = st.text_input(
        "Filter by Market Name",
        placeholder="Enter market name or keywords",
        key="filter_market",
        help="Search for specific market names"
    )
    
    # Row 4: Sort Controls
    st.markdown("### Sort Options")
    sort_col1, sort_col2 = st.columns(2)
    
    with sort_col1:
        sort_by = st.selectbox(
            "Sort By",
            options=[
                ("timestamp", "⏱️ Time (Most Recent)"),
                ("usd_amount", "💵 Trade Size"),
                ("price", "💰 Price"),
                ("shares", "📊 Shares"),
                ("side", "🔄 Side (Buy/Sell)"),
                ("share_type", "✅ Share Type (YES/NO)"),
                ("market", "📈 Market Name"),
                ("wallet", "👤 Wallet Address")
            ],
            format_func=lambda x: x[1],
            key="sort_by",
            index=0
        )
    
    with sort_col2:
        sort_order = st.selectbox(
            "Sort Order",
            options=[
                ("desc", "⬇️ Descending (High to Low / Recent to Old)"),
                ("asc", "⬆️ Ascending (Low to High / Old to Recent)")
            ],
            format_func=lambda x: x[1],
            key="sort_order",
            index=0
        )
    
    # Timezone info
    st.info("All trade timestamps have been converted to your local time zone: America/Toronto (current local time: 2026-01-12 11:05:15).")
    
    # Page controls
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
    
    # ========================================================================
    # Trades Table
    # ========================================================================
    
    st.markdown("---")
    
    # Build filter parameters
    filter_params = {
        "page": page_number,
        "page_size": 50
    }
    
    if filter_user:
        filter_params["wallet"] = filter_user
    
    if filter_side != "All":
        filter_params["side"] = filter_side
    
    if min_trade_size > 0:
        filter_params["min_usd"] = min_trade_size
    
    if max_trade_size < 1000000:
        filter_params["max_usd"] = max_trade_size
    
    if filter_market:
        filter_params["market"] = filter_market
    
    # Add sorting parameters (always include them)
    filter_params["sort_by"] = sort_by[0] if sort_by else "timestamp"
    filter_params["sort_order"] = sort_order[0] if sort_order else "desc"
    
    # Fetch trades
    trades_data = fetch_trades(filter_params)
    trades = trades_data.get("items", [])
    total_results = trades_data.get("total_results", 0)
    total_pages = trades_data.get("total_pages", 0)
    
    st.markdown(f"**Page {page_number} of {total_pages}** ({total_results} results)")
    
    if trades:
        # Table header with tooltips
        header_cols = st.columns([1.5, 0.7, 0.7, 3, 1, 0.8, 1.2, 2.5, 1.2])
        headers = [
            ("Timestamp", "Date and time of trade"),
            ("Side", "Buy or Sell"),
            ("Share Type", "YES or NO shares"),
            ("Market", "Market name - hover for full text"),
            ("Trade Size", "USD amount of trade"),
            ("Price", "Price per share"),
            ("Name", "Trader custom name"),
            ("User", "Wallet address - hover for full address"),
            ("Traded Shares", "Number of shares traded")
        ]
        
        for col, (header, tooltip) in zip(header_cols, headers):
            col.markdown(f"**{header}**", help=tooltip)
        
        # Display trades
        for trade in trades:
            trade_cols = st.columns([1.5, 0.7, 0.7, 3, 1, 0.8, 1.2, 2.5, 1.2])
            
            # Timestamp (show both formatted time and time ago)
            timestamp_str = trade.get('timestamp', '')
            if timestamp_str:
                try:
                    trade_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    formatted_time = trade_time.strftime('%Y-%m-%d %H:%M:%S')
                    time_ago = format_time_ago(timestamp_str)
                    trade_cols[0].markdown(f"{formatted_time}<br><small>{time_ago}</small>", unsafe_allow_html=True)
                except Exception as e:
                    trade_cols[0].text(timestamp_str)
            else:
                trade_cols[0].text("Unknown")
            
            # Side (Buy/Sell)
            side = trade.get('side', 'buy')
            if side.lower() == 'buy':
                trade_cols[1].markdown("🟢 **Buy**")
            else:
                trade_cols[1].markdown("🔴 **Sell**")
            
            # Share Type (YES/NO)
            share_type = trade.get('share_type', 'YES')
            if share_type and share_type.upper() == 'YES':
                trade_cols[2].markdown("✅ **YES**")
            else:
                trade_cols[2].markdown("❌ **NO**")
            
            # Market (with tooltip for full text)
            market_name = trade.get('market_name', 'Unknown Market')
            market_display = market_name[:50] + "..." if len(market_name) > 50 else market_name
            if len(market_name) > 50:
                # Use markdown with title attribute for hover tooltip
                trade_cols[3].markdown(
                    f'<div title="{market_name}">{market_display}</div>',
                    unsafe_allow_html=True
                )
            else:
                trade_cols[3].text(market_display)
            
            # Trade size
            trade_size = trade.get('usd_amount', 0) or 0
            trade_cols[4].text(f"${trade_size:,.2f}")
            
            # Price
            price = trade.get('price', 0) or 0
            trade_cols[5].text(f"${price:.2f}")
            
            # Name (get from favorites)
            wallet_addr = trade.get('wallet_address', '')
            wallet_name = "Unknown"
            for fav in favorites:
                if fav['wallet_address'] == wallet_addr:
                    wallet_name = fav.get('custom_name', wallet_addr[:8])
                    break
            trade_cols[6].markdown(f"**{wallet_name}**")
            
            # User address (with tooltip for full address)
            wallet_display = wallet_addr[:20] + "..." if len(wallet_addr) > 20 else wallet_addr
            trade_cols[7].markdown(
                f'<div title="{wallet_addr}"><code>{wallet_display}</code></div>',
                unsafe_allow_html=True
            )
            
            # Traded shares
            shares = trade.get('shares', 0) or 0
            trade_cols[8].text(f"{shares:,.2f}")
    
    else:
        st.info("No trades match your current filters. The backend is continuously polling for new trades.")
    
    # Footer
    if trades:
        st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
