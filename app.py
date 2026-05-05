import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Scalewrx - Upstak Analysis", layout="wide")

# 2. Upstak Branding - Dark Mode Professional with Green Accents
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #4ade80; }
    .stMetric { background-color: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .upstak-header { color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 800; border-left: 5px solid #4ade80; padding-left: 15px; margin-bottom: 20px; }
    .stSidebar { background-color: #000000; }
    .stDataFrame { background-color: #1a1c23; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 3. Logo Handling in Sidebar
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("UPSTAK.")
    
    st.divider()
    st.subheader("Executive Navigation")
    page = st.radio("Select Dashboard View", ["Operational Benchmarking", "Competitive Financial Analysis"])
    st.divider()
    if st.button("🔄 Refresh Market Data"):
        st.cache_data.clear()
        st.rerun()

# 4. Data Fetching (Live Peer Data)
@st.cache_data(ttl=3600)
def get_peer_data():
    tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']
    data_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Accurate Asset Turnover Logic
            total_rev = info.get('totalRevenue') or stock.financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in stock.financials.index else 0
            total_assets = info.get('totalAssets') or stock.balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in stock.balance_sheet.index else 1
            asset_turnover = float(total_rev) / float(total_assets) if total_assets > 0 else 0
            
            data_list.append({
                "Company": info.get('shortName', ticker),
                "Ticker": ticker,
                "Gross Margin (%)": round(info.get('grossMargins', 0) * 100, 2),
                "ROA (%)": round(info.get('returnOnAssets', 0) * 100, 2),
                "Asset Turnover (x)": round(asset_turnover, 2),
                "Current Ratio": round(info.get('currentRatio', 0), 2),
                "Inventory Turnover (x)": round(abs(stock.financials.loc['Cost Of Revenue'].iloc[0] / stock.balance_sheet.loc['Inventory'].iloc[0]), 2) if 'Inventory' in stock.balance_sheet.index else 0
            })
        except: continue
    return pd.DataFrame(data_list)

# 5. Header
st.markdown("<h1 class='upstak-header'>Competitive Analysis Dashboard <br><span style='color:#4ade80'>Scalewrx - Upstak</span></h1>", unsafe_allow_html=True)

# 6. Dashboard Pages
if page == "Operational Benchmarking":
    st.subheader("Internal Operational KPIs vs. Industry Standards")
    
    # 8 Key Performance Indicators (Custom Request)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("OEE (Effectiveness)", "84.2%", "↑ 7% vs Ind.")
    col2.metric("Cycle Time", "42.5s", "↓ 12% vs Ind.", delta_color="inverse")
    col3.metric("First Pass Yield", "99.1%", "↑ 4.2% vs Ind.")
    col4.metric("Production Downtime", "2.8%", "↓ 3.7% vs Ind.", delta_color="inverse")
    
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("AR/AP/Inv Days", "32/45/28", "Optimized")
    col6.metric("Cost Per Unit", "$12.45", "↓ $1.05", delta_color="inverse")
    col7.metric("Scrap Rate", "0.85%", "↓ 2.3%", delta_color="inverse")
    col8.metric("Safety (TRIR)", "0.32", "Best-in-Class")

    st.divider()

    # Visualizing the Performance Gap
    op_bench_data = pd.DataFrame({
        "Metric": ["OEE", "Cycle Time (inv)", "First Pass Yield", "Scrap Rate (inv)", "Downtime (inv)", "Safety (inv)"],
        "Scalewrx (Upstak)": [84, 92, 99, 98, 97, 100],
        "Industry Standard": [75, 80, 94, 90, 88, 85]
    })
    
    fig_op = px.line(op_bench_data, x="Metric", y=["Scalewrx (Upstak)", "Industry Standard"], 
                     markers=True, template="plotly_dark",
                     color_discrete_map={"Scalewrx (Upstak)": "#4ade80", "Industry Standard": "#64748b"},
                     title="Operational Gap Analysis (Standardized 0-100 Scale)")
    st.plotly_chart(fig_op, use_container_width=True)

else:
    # Competitive Financials Page
    df = get_peer_data()
    st.subheader("Public Market Comparative Analysis")
    
    # Allow user to pick which KPI to benchmark
    kpi_choice = st.selectbox("Select Peer Benchmark Metric", df.columns[2:])
    
    # Top Row Comparison
    st.write(f"### Peer Comparison: {kpi_choice}")
    p_cols = st.columns(len(df))
    for i, (idx, row) in enumerate(df.iterrows()):
        p_cols[i].metric(row['Ticker'], f"{row[kpi_choice]}")

    st.divider()

    # Graphs
    graph_col1, graph_col2 = st.columns(2)
    with graph_col1:
        fig_bar = px.bar(df.sort_values(kpi_choice, ascending=False), x='Ticker', y=kpi_choice, 
                         color='Ticker', template="plotly_dark",
                         color_discrete_sequence=px.colors.sequential.Greens_r,
                         title=f"Ranked {kpi_choice}")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with graph_col2:
        fig_scatter = px.scatter(df, x='Gross Margin (%)', y='ROA (%)', size='Asset Turnover (x)',
                                 text='Ticker', hover_name='Company', template="plotly_dark",
                                 color_discrete_sequence=["#4ade80"],
                                 title="Profitability vs. Efficiency Matrix")
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Detailed Peer Financial Dataset")
    st.dataframe(df, use_container_width=True, hide_index=True)

# Footer
st.markdown("<br><hr><center>© 2026 Upstak Intelligence | Proprietary Executive Dashboard for Scalewrx</center>", unsafe_allow_html=True)
