import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Manufacturing Benchmark Dashboard", layout="wide")

st.title("🏭 Top 5 Manufacturing KPIs Benchmarking")
st.write("Data sourced live from Yahoo Finance. Benchmarking top global manufacturing firms.")

# Define the tickers for the Top 5 Manufacturing Companies
tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']

@st.cache_data(ttl=3600)
def get_data(ticker_list):
    data_list = []
    for ticker in ticker_list:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        # Operational & Financial KPI Calculation
        # 1. Gross Profit Margin
        gp_margin = info.get('grossMargins', 0) * 100
        
        # 2. Return on Assets (ROA)
        roa = info.get('returnOnAssets', 0) * 100
        
        # 3. Revenue Growth (YoY)
        rev_growth = info.get('revenueGrowth', 0) * 100
        
        # 4. Asset Turnover (Revenue / Total Assets)
        total_rev = info.get('totalRevenue', 1)
        total_assets = info.get('totalAssets', 1)
        asset_turnover = total_rev / total_assets
        
        # 5. Inventory Turnover (Cost of Goods Sold / Inventory)
        # Using simplified estimate from financial statements
        cogs = financials.loc['Cost Of Revenue'].iloc[0] if 'Cost Of Revenue' in financials.index else 0
        inventory = balance_sheet.loc['Inventory'].iloc[0] if 'Inventory' in balance_sheet.index else 1
        inv_turnover = abs(cogs / inventory) if inventory != 0 else 0

        data_list.append({
            "Company": info.get('shortName', ticker),
            "Ticker": ticker,
            "Gross Margin (%)": round(gp_margin, 2),
            "ROA (%)": round(roa, 2),
            "Revenue Growth (%)": round(rev_growth, 2),
            "Asset Turnover (x)": round(asset_turnover, 2),
            "Inventory Turnover (x)": round(inv_turnover, 2)
        })
    return pd.DataFrame(data_list)

try:
    with st.spinner('Fetching live market data...'):
        df = get_data(tickers)

    # Sidebar Metrics
    st.sidebar.header("Benchmark Filters")
    selected_metric = st.sidebar.selectbox("Select KPI for Comparison", df.columns[2:])

    # Layout: Top Row Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [col1, col2, col3, col4, col5]
    for i, ticker in enumerate(tickers):
        with metrics[i]:
            val = df.loc[df['Ticker'] == ticker, selected_metric].values[0]
            st.metric(label=ticker, value=val)

    # Visualizations
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(f"Ranked: {selected_metric}")
        fig = px.bar(df, x='Company', y=selected_metric, color='Company', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Financial Strength: ROA vs Gross Margin")
        fig2 = px.scatter(df, x='Gross Margin (%)', y='ROA (%)', size='Asset Turnover (x)', 
                          hover_name='Company', text='Ticker', color='Company')
        st.plotly_chart(fig2, use_container_width=True)

    # Raw Data Table
    st.subheader("Comparative Benchmarking Data")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data: {e}. Please ensure you have an active internet connection.")
