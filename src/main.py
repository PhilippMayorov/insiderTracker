"""
PolyMarket Anomaly Detector - Main Entry Point
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the backend modules
from backend.getEvents import get_top_events
from backend.getMarkets import get_top_markets, get_insider_markets


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
    
    # Insider Trading Detection Section
    st.subheader("🚨 Insider Trading Detection")
    
    st.write("""
    This detector analyzes market headlines to identify those with potential for insider trading.
    It looks for markets involving:
    - Product releases and announcements
    - Regulatory decisions (SEC, FDA approvals)
    - Political/monetary policy events
    - Corporate mergers and acquisitions
    """)
    
    # Button to fetch and analyze markets for insider trading
    if st.button("🔍 Detect Insider Trading Potential Markets", type="secondary", use_container_width=True, key="detect_insider"):
        with st.spinner("Fetching and analyzing markets for insider trading potential..."):
            insider_markets = get_insider_markets(limit=10, include_holders=True, holder_limit=10)
            
            if insider_markets:
                st.success(f"🚨 Found {len(insider_markets)} markets with insider trading potential!")
                st.markdown("---")
                
                # Display insider markets in an organized way
                for idx, market in enumerate(insider_markets, 1):
                    # Create an expander for each market
                    with st.expander(f"🚨 #{idx} - {market.get('question', 'Unknown Market')}", expanded=(idx <= 2)):
                        # Create columns for better layout
                        info_col1, info_col2 = st.columns(2)
                        
                        with info_col1:
                            st.metric("💰 Volume", f"${float(market.get('volume', 0)):,.2f}")
                        
                        with info_col2:
                            st.metric("💧 Liquidity", f"${float(market.get('liquidity', 0)):,.2f}")
                        
                        # Highlight why this might be insider-sensitive
                        st.warning("⚠️ **Potential Insider Risk**: This market involves events where privileged information may exist.")
                        
                        # Additional information
                        st.markdown("**Details:**")
                        st.write(f"🔗 **Slug:** `{market.get('market_slug', 'N/A')}`")
                        
                        # Outcome prices
                        outcome_prices = market.get('outcomePrices', [])
                        
                        if outcome_prices and len(outcome_prices) >= 2:
                            try:
                                price_col1, price_col2 = st.columns(2)
                                with price_col1:
                                    yes_price = float(str(outcome_prices[0]))
                                    st.metric("✅ Yes Price", f"${yes_price:.4f}")
                                with price_col2:
                                    no_price = float(str(outcome_prices[1]))
                                    st.metric("❌ No Price", f"${no_price:.4f}")
                            except (ValueError, TypeError, IndexError) as e:
                                st.write(f"Outcome Prices: {outcome_prices}")
                        
                        # Additional market info
                        if market.get('description'):
                            st.write(f"📝 **Description:** {market.get('description')}")
                        
                        # Display end date if available
                        if market.get('endDate'):
                            st.write(f"⏰ **End Date:** {market.get('endDate')}")
                        
                        # Display event info if available
                        if market.get('groupItemTitle'):
                            st.write(f"📂 **Event:** {market.get('groupItemTitle')}")
                        
                        # Display insider score
                        if 'insider_score' in market:
                            insider_score = market['insider_score']
                            st.metric("🎯 Insider Risk Score", f"{insider_score:.2f}", 
                                     help="Score from 0.0 (low risk) to 1.0 (high risk)")
                        
                        # Display holder information if available
                        if 'top_holders' in market and market.get('top_holders'):
                            st.markdown("---")
                            st.subheader("👥 Top Holders Analysis")
                            
                            total_holders = market.get('total_holders_count', 0)
                            top_holders = market['top_holders']
                            
                            holder_col1, holder_col2 = st.columns(2)
                            with holder_col1:
                                st.metric("Total Holders", f"{total_holders:,}")
                            with holder_col2:
                                st.metric("Top Holders Shown", len(top_holders))
                            
                            # Display top holders in a table-like format
                            st.markdown("**🐋 Top Holders:**")
                            for h_idx, holder in enumerate(top_holders[:5], 1):
                                wallet = holder.get('proxyWallet', 'N/A')
                                amount = holder.get('amount', 0)
                                outcome_idx = holder.get('outcomeIndex', 'N/A')
                                pseudonym = holder.get('pseudonym', 'Anonymous')
                                
                                with st.container():
                                    h_col1, h_col2, h_col3 = st.columns([3, 2, 1])
                                    with h_col1:
                                        st.write(f"**{h_idx}.** `{wallet[:16]}...`")
                                        if pseudonym and pseudonym != 'Anonymous':
                                            st.caption(f"👤 {pseudonym}")
                                    with h_col2:
                                        st.write(f"**Amount:** {amount:,}")
                                    with h_col3:
                                        outcome_label = "✅ Yes" if outcome_idx == 0 else "❌ No" if outcome_idx == 1 else "?"
                                        st.write(outcome_label)
                            
                            if len(top_holders) > 5:
                                st.caption(f"... and {len(top_holders) - 5} more holders shown in data")
                        elif 'total_holders_count' in market:
                            st.info(f"ℹ️ Total Holders: {market['total_holders_count']} (detailed data not loaded)")
            else:
                st.info("ℹ️ No markets with significant insider trading potential found in current top markets.")
    
    st.markdown("---")
    
    # Create two columns for Events and Markets
    events_col, markets_col = st.columns(2)
    
    # Top Events Section
    with events_col:
        st.subheader("📋 Top PolyMarket Events")
        
        # Button to fetch events
        if st.button("🔄 Fetch Top 10 Events", type="primary", use_container_width=True, key="fetch_events"):
            with st.spinner("Fetching events from PolyMarket..."):
                events = get_top_events(limit=10)
                
                if events:
                    st.success(f"✅ Successfully fetched {len(events)} events!")
                    st.markdown("---")
                    
                    # Display events in an organized way
                    for idx, event in enumerate(events, 1):
                        # Create an expander for each event
                        with st.expander(f"#{idx} - {event.get('title', 'Unknown Event')}", expanded=(idx == 1)):
                            # Create columns for better layout
                            info_col1, info_col2, info_col3 = st.columns(3)
                            
                            with info_col1:
                                st.metric("💰 Volume", f"${float(event.get('volume', 0)):,.2f}")
                            
                            with info_col2:
                                st.metric("💧 Liquidity", f"${float(event.get('liquidity', 0)):,.2f}")
                            
                            with info_col3:
                                market_count = len(event.get('markets', []))
                                st.metric("📊 Markets", market_count)
                            
                            # Additional information
                            st.markdown("**Details:**")
                            st.write(f"🔗 **Slug:** `{event.get('slug', 'N/A')}`")
                            
                            # Display description if available
                            if event.get('description'):
                                st.write(f"📝 **Description:** {event.get('description')}")
                            
                            # Display start and end dates if available
                            col_date1, col_date2 = st.columns(2)
                            with col_date1:
                                if event.get('startDate'):
                                    st.write(f"🟢 **Start:** {event.get('startDate')}")
                            with col_date2:
                                if event.get('endDate'):
                                    st.write(f"🔴 **End:** {event.get('endDate')}")
                            
                            # Show markets if available
                            if event.get('markets'):
                                st.markdown("**Markets:**")
                                for market in event.get('markets', [])[:3]:  # Show first 3 markets
                                    st.write(f"  • {market.get('question', 'N/A')}")
                                if len(event.get('markets', [])) > 3:
                                    st.write(f"  ... and {len(event.get('markets', [])) - 3} more markets")
                else:
                    st.error("❌ Failed to fetch events. Please check your connection and try again.")
    
    # Top Markets Section
    with markets_col:
        st.subheader("🎲 Top PolyMarket Markets")
        
        # Button to fetch markets
        if st.button("🔄 Fetch Top 10 Markets", type="primary", use_container_width=True, key="fetch_markets"):
            with st.spinner("Fetching markets from PolyMarket..."):
                markets = get_top_markets(limit=10)
                
                if markets:
                    st.success(f"✅ Successfully fetched {len(markets)} markets!")
                    st.markdown("---")
                    
                    # Display markets in an organized way
                    for idx, market in enumerate(markets, 1):
                        # Create an expander for each market
                        with st.expander(f"#{idx} - {market.get('question', 'Unknown Market')}", expanded=(idx == 1)):
                            # Create columns for better layout
                            info_col1, info_col2 = st.columns(2)
                            
                            with info_col1:
                                st.metric("💰 Volume", f"${float(market.get('volume', 0)):,.2f}")
                            
                            with info_col2:
                                st.metric("💧 Liquidity", f"${float(market.get('liquidity', 0)):,.2f}")
                            
                            # Additional information
                            st.markdown("**Details:**")
                            st.write(f"🔗 **Slug:** `{market.get('market_slug', 'N/A')}`")
                            
                            # Outcome prices
                            outcome_prices = market.get('outcomePrices', [])

                            if outcome_prices and len(outcome_prices) >= 2:
                                try:
                                    price_col1, price_col2 = st.columns(2)
                                    with price_col1:
                                        yes_price = float(str(outcome_prices[0]))
                                        st.metric("✅ Yes Price", f"${yes_price:.4f}")
                                    with price_col2:
                                        no_price = float(str(outcome_prices[1]))
                                        st.metric("❌ No Price", f"${no_price:.4f}")
                                except (ValueError, TypeError, IndexError) as e:
                                    st.write(f"Outcome Prices: {outcome_prices}")
                            
                            # Additional market info
                            if market.get('description'):
                                st.write(f"📝 **Description:** {market.get('description')}")
                            
                            # Display end date if available
                            if market.get('endDate'):
                                st.write(f"⏰ **End Date:** {market.get('endDate')}")
                            
                            # Display event info if available
                            if market.get('groupItemTitle'):
                                st.write(f"📂 **Event:** {market.get('groupItemTitle')}")
                else:
                    st.error("❌ Failed to fetch markets. Please check your connection and try again.")
    
    st.markdown("---")
    
    # Getting started
    st.subheader("🚀 Getting Started")    
    
    st.write("""
    1. Click **"Detect Insider Trading Potential Markets"** to find markets with insider risk
    2. Click **"Fetch Top 10 Events"** or **"Fetch Top 10 Markets"** for general data
    3. Expand any item to see detailed information
    4. Monitor volume, liquidity, prices, and market activity
    5. Review flagged markets for unusual patterns
    """)
    
    # Footer
    st.markdown("---")
    st.caption("PolyMarket Anomaly Detector v0.1.0 | Research Tool | Public Data Only")


if __name__ == "__main__":
    main()
