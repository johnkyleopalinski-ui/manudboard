import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Manufacturing KPI Benchmark", layout="wide")

st.title("🏭 Manufacturing Sector Benchmarking Dashboard")

tickers = ['AAPL', 'TM', 'GE', 'CAT', 'HON']

@st.cache_data(ttl=3600) 
def get_clean_data(ticker_list):
    all_data = []
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 1. Basic Stats from Info
            gm = info.get('grossMargins', 0)
            roa = info.get('returnOnAssets', 0)
            rev_growth = info.get('revenueGrowth', 0)
            curr_ratio = info.get('currentRatio', 0)

            # 2. Robust Asset Turnover Logic
            # We try info first, then fall back to the Financials/Balance Sheet
            total_rev = info.get('totalRevenue')
            total_assets = info.get('totalAssets')

            # Fallback: Pull from Financial Statements if Info is empty
            if not total_rev or not total_assets:
                # Get annual financials
                df_fin = stock.financials
                df_bs = stock.balance_sheet
                
                if not df_fin.empty and 'Total Revenue' in df_fin.index:
                    total_rev = df_fin.loc['Total Revenue'].iloc[0]
                
                if not df_bs.empty and 'Total Assets' in df_bs.index:
                    total_assets = df_bs.loc['Total Assets'].iloc[0]

            # Final Calculation
            if total_rev and total_assets and total_assets > 0:
                asset_turnover = float(total_rev) / float(total_assets)
            else:
                asset_turnover = 0.0

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
        except Exception:
            continue
            
    return pd.DataFrame(all_data)

try:
    with st.spinner('Accessing Financial Statements...'):
        df = get_clean_data(tickers)

    if not df.empty:
        st.sidebar.header("Dashboard Controls")
        selected_kpi = st.sidebar.selectbox(
            "Select KPI for Benchmarking", 
            ["Gross Margin (%)", "ROA (%)", "Revenue Growth (%)", "Asset Turnover (x)", "Current Ratio"]
        )
        
        if st.sidebar.button("Force Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.subheader(f"Current Comparison: {selected_kpi}")
        cols = st.columns(len(df))
        for i, (idx, row) in enumerate(df.iterrows()):
            cols[i].metric(label=row['Ticker'], value=row[selected_kpi])

        st.divider()

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.write(f"### {selected_kpi} Ranking")
            df_sorted = df.sort_values(by=selected_kpi, ascending=False)
            fig1 = px.bar(df_sorted, x='Ticker', y=selected_kpi, color='Ticker', text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            st.write("### Margin vs. Efficiency (ROA)")
            # Safety check: if all turnovers are 0, use a fixed size for the dots
            size_col = 'Asset Turnover (x)' if df['Asset Turnover (x)'].sum() > 0 else None
            fig2 = px.scatter(
                df, 
                x='Gross Margin (%)', 
                y='ROA (%)', 
                size=size_col, 
                color='Ticker',
                hover_name='Company',
                text='Ticker',
                size_max=40
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Raw Benchmarking Data")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data as CSV", data=csv, file_name="mfg_benchmarks.csv", mime='text/csv')

    else:
        st.error("Data unavailable. Please wait 5 minutes for the API rate limit to reset.")

except Exception as e:
    st.error(f"An error occurred: {e}")
