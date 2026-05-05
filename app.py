import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Manufacturing Benchmark", layout="wide")

st.title("🏭 Top 5 Manufacturing KPIs")

# Strategy: Use a specific list of tickers
tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']

@st.cache_data(ttl=3600)  # This saves the data for 1 hour so you don't hit the limit
def get_benchmarking_data(ticker_list):
    all_data = []
    for ticker in ticker_list:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            
            # Pulling specific metrics directly to minimize server hits
            data = {
                "Company": info.get('shortName', ticker),
                "Ticker": ticker,
                "Gross Margin (%)": round(info.get('grossMargins', 0) * 100, 2),
                "ROA (%)": round(info.get('returnOnAssets', 0) * 100, 2),
                "Revenue Growth (%)": round(info.get('revenueGrowth', 0) * 100, 2),
                "Asset Turnover (x)": round(info.get('totalRevenue', 0) / info.get('totalAssets', 1), 2),
                "Current Ratio": round(info.get('currentRatio', 0), 2)
            }
            all_data.append(data)
        except Exception:
            # Fallback if one specific ticker fails
            continue
    return pd.DataFrame(all_data)

# Main logic
try:
    df = get_benchmarking_data(tickers)
    
    if df.empty:
        st.error("Yahoo Finance is currently rate-limiting requests. Please wait 5 minutes and click 'Refresh'.")
        if st.button("Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    else:
        # Displaying the Dashboard
        metric_to_plot = st.sidebar.selectbox("Select KPI", df.columns[2:])
        
        cols = st.columns(5)
        for i, row in df.iterrows():
            cols[i].metric(row['Ticker'], f"{row[metric_to_plot]}")

        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(df, x='Ticker', y=metric_to_plot, color='Company', title=f"Ranked {metric_to_plot}")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.scatter(df, x='Gross Margin (%)', y='ROA (%)', size='Asset Turnover (x)', hover_name='Company', title="Margin vs. Efficiency")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.subheader("Comparison Table")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.warning("Connection issue. Please try again in a few minutes.")
    if st.button("Retry"):
        st.rerun()
