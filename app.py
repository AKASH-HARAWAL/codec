import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# Set the page configuration
st.set_page_config(layout="wide")
st.title("📊 Real-Time Stock Market Dashboard")

# Sidebar input
symbol = st.sidebar.text_input("Enter Stock Symbol (e.g. AAPL)", value="AAPL").upper()
period = st.sidebar.selectbox("Select Time Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"])
interval = st.sidebar.selectbox("Select Interval", ["1m", "5m", "15m", "1h", "1d"])

try:
    data = yf.download(tickers=symbol, period=period, interval=interval)

    if not data.empty and len(data) > 1:
        close_prices = data['Close'].dropna()

        # Latest price and percent change
        latest_price = float(close_prices.iloc[-1])
        previous_price = float(close_prices.iloc[-2])
        price_change = ((latest_price - previous_price) / previous_price) * 100

        st.subheader(f"Live Stock Data: {symbol}")
        st.metric(label="Latest Price", value=f"${latest_price:.2f}", delta=f"{price_change:.2f}%")

        # Plot stock price with Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=close_prices, mode='lines', name='Close Price'))
        fig.update_layout(title=f"{symbol} Price Chart", xaxis_title="Time", yaxis_title="Price", height=500)
        st.plotly_chart(fig, use_container_width=True)

        data['SMA_20'] = close_prices.rolling(window=20).mean()
        data['EMA_20'] = close_prices.ewm(span=20, adjust=False).mean()
        st.line_chart(data[['Close', 'SMA_20', 'EMA_20']])

    else:
        st.error("No data available for the given symbol or time period. Try changing the interval or period.")
except Exception as e:
    st.error(f"An error occurred: {e}")
