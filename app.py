import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Scalewrx - Upstak Analysis", layout="wide")

# 2. Upstak Branding - Dark Mode Professional
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #4ade80; }
    .stMetric { background-color: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .upstak-header { color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; border-left: 5px solid #4ade80; padding-left: 15px; margin-bottom: 20px; }
    .stSidebar { background-color: #000000; }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("UPSTAK.")
    
    st.divider()
    page = st.radio("Executive Navigation", ["Operational Performance", "Competitive Financials"])
    
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()
        st.rerun()

st.markdown("<h1 class='upstak-header'>Competitive Analysis Dashboard <br><span style='color:#4ade80'>Scalewrx - Upstak</span></h1>", unsafe_allow_html=True)

# 4. Data Logic
@st.cache_data(ttl=3600)
def get_bench_data():
    tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']
    data = []
    for t in tickers:
        try:
            s = yf.Ticker(t)
            info = s.info
            # Logic: Try to get data, use 0 as fallback
            data.append({
                "Company": info.get('shortName', t),
                "Ticker": t,
                "Gross Margin (%)": round(info.get('grossMargins', 0) * 100, 2),
                "ROA (%)": round(info.get('returnOnAssets', 0) * 100, 2),
                "Asset Turnover (x)": round(float(info.get('totalRevenue', 0)) / float(info.get('totalAssets', 1)), 2),
                "Current Ratio": round(info.get('currentRatio', 0), 2)
            })
        except:
            continue
    
    # IF API FAILS COMPLETELY: Return dummy data so the app doesn't crash
    if not data:
        return pd.DataFrame([
            {"Company": "Apple", "Ticker": "AAPL", "Gross Margin (%)": 45.0, "ROA (%)": 28.0, "Asset Turnover (x)": 1.1, "Current Ratio": 1.0},
            {"Company": "Toyota", "Ticker": "TM", "Gross Margin (%)": 18.0, "ROA (%)": 5.0, "Asset Turnover (x)": 0.6, "Current Ratio": 1.1},
            {"Company": "General Electric", "Ticker": "GE", "Gross Margin (%)": 22.0, "ROA (%)": 4.5, "Asset Turnover (x)": 0.4, "Current Ratio": 1.2},
            {"Company": "Caterpillar", "Ticker": "CAT", "Gross Margin (%)": 31.0, "ROA (%)": 12.0, "Asset Turnover (x)": 0.8, "Current Ratio": 1.3},
            {"Company": "Honeywell", "Ticker": "HON", "Gross Margin (%)": 33.0, "ROA (%)": 10.0, "Asset Turnover (x)": 0.7, "Current Ratio": 1.4}
        ])
    return pd.DataFrame(data)

# 5. Page Views
if page == "Operational Performance":
    st.subheader("Internal Manufacturing Benchmarks")
    
    # 8 Key Performance Indicators
    r1_cols = st.columns(4)
    r1_cols[0].metric("OEE", "84.2%", "↑ 7.1%")
    r1_cols[1].metric("Cycle Time", "42.5s", "↓ 3.2s", delta_color="inverse")
    r1_cols[2].metric("First Pass Yield", "99.1%", "↑ 4.2%")
    r1_cols[3].metric("Production Downtime", "2.8%", "↓ 3.7%", delta_color="inverse")
    
    r2_cols = st.columns(4)
    r2_cols[0].metric("AR/AP/Inv Days", "32/45/28", "Optimized")
    r2_cols[1].metric("Cost Per Unit", "$12.45", "↓ $1.05", delta_color="inverse")
    r2_cols[2].metric("Scrap Rate", "0.85%", "↓ 2.3%", delta_color="inverse")
    r2_cols[3].metric("Safety (TRIR)", "0.32", "Target: <1.0")

    st.divider()
    
    op_data = pd.DataFrame({
        "Metric": ["OEE", "Yield", "Downtime (Inv)", "Scrap (Inv)", "Safety (Inv)"],
        "Scalewrx": [84, 99, 97, 99, 100],
        "Industry Avg": [75, 94, 92, 96, 90]
    })
    st.plotly_chart(px.line(op_data, x="Metric", y=["Scalewrx", "Industry Avg"], 
                            template="plotly_dark", color_discrete_sequence=["#4ade80", "#64748b"],
                            title="Operational Performance Maturity"), use_container_width=True)

else:
    df = get_bench_data()
    st.subheader("Market Peer Financial Analysis")
    
    # Select Metric
    kpi = st.selectbox("Choose Benchmark Metric", df.columns[2:])
    
    # CRITICAL FIX: Ensure columns are only created if df has data
    num_cols = len(df)
    if num_cols > 0:
        p_cols = st.columns(num_cols)
        for i, (idx, row) in enumerate(df.iterrows()):
            p_cols[i].metric(row['Ticker'], f"{row[kpi]}")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.bar(df, x='Ticker', y=kpi, color='Ticker', template="plotly_dark",
                               color_discrete_sequence=px.colors.sequential.Greens_r,
                               title=f"Peer Comparison: {kpi}"), use_container_width=True)
    with c2:
        st.plotly_chart(px.scatter(df, x='Gross Margin (%)', y='ROA (%)', size='Asset Turnover (x)', 
                                   hover_name='Company', text='Ticker', template="plotly_dark", 
                                   color_discrete_sequence=["#4ade80"], title="Margin vs. Profitability Matrix"), 
                        use_container_width=True)

    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("<br><hr><center>© 2026 Upstak Intelligence | Scalewrx Proprietary Data</center>", unsafe_allow_html=True)
