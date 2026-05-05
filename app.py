import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from PIL import Image
import os

# 1. Page Configuration & Theme
st.set_page_config(page_title="Scalewrx - Upstak Analysis", layout="wide")

# Custom CSS for a high-end Dark/Modern look to match the logo
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #4ade80; }
    .stMetric { background-color: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .upstak-header { color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; border-left: 5px solid #4ade80; padding-left: 15px; margin-bottom: 20px; }
    .stSidebar { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

# 2. Logo Handling
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        # Fallback if logo isn't uploaded yet
        st.title("UPSTAK.")
    
    st.divider()
    page = st.radio("Executive Navigation", ["Operational Performance", "Competitive Financials"])

# 3. Header
st.markdown("<h1 class='upstak-header'>Competitive Analysis Dashboard <br><span style='color:#4ade80'>Scalewrx - Upstak</span></h1>", unsafe_allow_html=True)

# 4. Data Fetching Logic (Financials)
@st.cache_data(ttl=3600)
def get_bench_data():
    tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']
    data = []
    for t in tickers:
        try:
            s = yf.Ticker(t)
            info = s.info
            data.append({
                "Company": info.get('shortName', t),
                "Ticker": t,
                "Gross Margin (%)": round(info.get('grossMargins', 0) * 100, 2),
                "ROA (%)": round(info.get('returnOnAssets', 0) * 100, 2),
                "Asset Turnover (x)": round(float(info.get('totalRevenue', 0)) / float(info.get('totalAssets', 1)), 2),
                "Current Ratio": round(info.get('currentRatio', 0), 2)
            })
        except: continue
    return pd.DataFrame(data)

# 5. Dashboard Pages
if page == "Operational Performance":
    st.subheader("Internal Manufacturing Benchmarks")
    
    # Row 1: Production KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("OEE", "84.2%", "↑ 2.1%")
    c2.metric("Cycle Time", "42.5s", "↓ 3.2s", delta_color="inverse")
    c3.metric("First Pass Yield", "99.1%", "↑ 0.5%")
    c4.metric("Downtime", "2.8%", "↓ 1.4%", delta_color="inverse")
    
    # Row 2: Financial Ops & Safety
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Inventory Days", "28 Days", "Target: 30")
    c6.metric("Cost Per Unit", "$12.45", "↓ $0.80", delta_color="inverse")
    c7.metric("Scrap Rate", "0.85%", "↓ 0.2%", delta_color="inverse")
    c8.metric("Safety (TRIR)", "0.32", "Best-in-Class")

    st.divider()
    
    # Visual Gap Analysis
    op_data = pd.DataFrame({
        "Metric": ["OEE", "Yield", "Downtime (Inv)", "Scrap (Inv)", "Safety (Inv)"],
        "Scalewrx": [84, 99, 97, 99, 100],
        "Industry Standard": [75, 94, 92, 96, 90]
    })
    fig = px.line(op_data, x="Metric", y=["Scalewrx", "Industry Standard"], 
                  template="plotly_dark", color_discrete_sequence=["#4ade80", "#64748b"],
                  title="Performance Maturity Model")
    st.plotly_chart(fig, use_container_width=True)

else:
    df = get_bench_data()
    st.subheader("Market Peer Analysis")
    
    kpi = st.selectbox("Select Benchmark KPI", df.columns[2:])
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.bar(df, x='Ticker', y=kpi, color='Ticker', template="plotly_dark",
                      color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        fig2 = px.scatter(df, x='Gross Margin (%)', y='ROA (%)', size='Asset Turnover (x)', 
                          hover_name='Company', template="plotly_dark", color_discrete_sequence=["#4ade80"])
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)

# Footer
st.markdown("<br><hr><center>© 2026 Upstak Intelligence | Proprietary Executive Dashboard</center>", unsafe_allow_html=True)
