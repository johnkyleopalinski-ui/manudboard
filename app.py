import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Manufacturing KPI Benchmark", layout="wide")

st.title("🏭 Manufacturing Sector Benchmarking Dashboard")
st.markdown("""
This dashboard compares the top 5 global manufacturing public companies using live financial data.
*KPIs are updated in real-time via Yahoo Finance.*
""")

# 2. Define Tickers
tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']

# 3. Data Fetching Function with Robust Logic
@st.cache_data(ttl=3600)  # Caches data for 1 hour to prevent "Too Many Requests" errors
def get_clean_data(ticker_list):
    all_data = []
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # --- Robust Calculation Logic ---
            
            # Gross Margin
            gm = info.get('grossMargins', 0)
            
            # ROA
            roa = info.get('returnOnAssets', 0)
            
            # Revenue Growth
            rev_growth = info.get('revenueGrowth', 0)
            
            # Asset Turnover (Fixed Logic)
            total_rev = info.get('totalRevenue')
            total_assets = info.get('totalAssets')
            if total_rev and total_assets and total_assets > 0:
                asset_turnover = float(total_rev) / float(total_assets)
            else:
                asset_turnover = 0.0
                
            # Current Ratio
            curr_ratio = info.get('currentRatio', 0)

            data = {
                "Company": info.get('shortName', ticker),
                "Ticker": ticker,
                "Gross Margin (%)": round(gm * 100, 2) if gm else 0,
                "ROA (%)": round(roa * 100, 2) if roa else 0,
                "Revenue Growth (%)": round(rev_growth * 100, 2) if rev_growth else 0,
                "Asset Turnover (x)": round(asset_turnover, 2),
                "Current Ratio": round(curr_ratio, 2) if curr_ratio else 0
            }
            all_data.append(data)
        except Exception as e:
            st.warning(f"Could not pull data for {ticker}: {e}")
            continue
            
    return pd.DataFrame(all_data)

# 4. Main Application Logic
try:
    with st.spinner('Fetching live market data...'):
        df = get_clean_data(tickers)

    if not df.empty:
        # --- Sidebar ---
        st.sidebar.header("Dashboard Controls")
        selected_kpi = st.sidebar.selectbox(
            "Select KPI for Benchmarking", 
            ["Gross Margin (%)", "ROA (%)", "Revenue Growth (%)", "Asset Turnover (x)", "Current Ratio"]
        )
        
        if st.sidebar.button("Force Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        # --- Top Row: Key Metrics ---
        st.subheader(f"Current Comparison: {sel
