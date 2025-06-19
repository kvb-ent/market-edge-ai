# Market Edge AI: Streamlit App (Stocks + Crypto + GPT-Style Trade Ideas)

import streamlit as st
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Market Edge AI", layout="wide")
st.title("📊 Market Edge AI Dashboard")

# --- Constants ---
POLYGON_API_KEY = "P4f_PZiyHRfBw_xx3VSBpx30mG29Qu4r"
DEFAULT_TICKERS = ["SPY", "QQQ", "TSLA", "AAPL", "NVDA"]
DEFAULT_COINS = ["bitcoin", "ethereum", "solana", "ripple", "chainlink"]

# --- User Input ---
st.sidebar.header("🔧 Settings")
custom_stock = st.sidebar.text_input("Add a Stock Ticker", value="")
custom_crypto = st.sidebar.text_input("Add a Crypto Symbol (e.g. dogecoin)", value="")
run_scan = st.sidebar.button("Run Scan")

# --- Stock Data from Polygon ---
def get_stock_data(ticker):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{(datetime.now() - timedelta(days=30)).date()}/{datetime.now().date()}?adjusted=true&sort=asc&limit=30&apiKey={POLYGON_API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        results = r.json().get("results", [])
        df = pd.DataFrame(results)
        df["t"] = pd.to_datetime(df["t"], unit='ms')
        return df
    else:
        return pd.DataFrame()

# --- Crypto Data from CoinGecko ---
def get_crypto_data():
    ids = ','.join(DEFAULT_COINS + ([custom_crypto] if custom_crypto else []))
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    r = requests.get(url)
    return r.json()

# --- GPT Trade Idea Logic (Simplified) ---
def generate_trade_idea(change):
    if change < -3:
        return "BUY: Oversold dip. Strong potential for rebound. Target +8%"
    elif change > 3:
        return "WAIT: Already pumped. Watch for cooldown."
    else:
        return "HOLD: Stable range. No clear setup yet."

# --- Display Stock Charts ---
if run_scan:
    st.subheader("📈 Stock Trade Ideas")
    tickers = DEFAULT_TICKERS + ([custom_stock.upper()] if custom_stock else [])
    for ticker in tickers:
        df = get_stock_data(ticker)
        if not df.empty:
            st.markdown(f"**{ticker}**")
            st.line_chart(df.set_index("t")["c"], height=200)
            recent_change = ((df["c"].iloc[-1] - df["o"].iloc[-1]) / df["o"].iloc[-1]) * 100
            st.caption(f"Change Today: {recent_change:.2f}%")
            st.success(generate_trade_idea(recent_change))
        else:
            st.warning(f"No data found for {ticker}")

    st.subheader("₿ Crypto Trade Ideas")
    data = get_crypto_data()
    for coin in DEFAULT_COINS + ([custom_crypto] if custom_crypto else []):
        if coin in data:
            price = data[coin]["usd"]
            change = data[coin]["usd_24h_change"]
            st.markdown(f"**{coin.capitalize()}**: ${price:.2f} ({change:+.2f}% 24h)")
            st.success(generate_trade_idea(change))
        else:
            st.warning(f"No data found for {coin}")
