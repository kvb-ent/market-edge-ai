import streamlit as st
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
import yfinance as yf

# --- CONFIG ---
TICKERS = ['TSLA', 'AAPL', 'ETH-USD', 'BTC-USD', 'SOL-USD']
TIMEFRAMES = {
    '1d': '1d',
    '4h': '60m',
    '1h': '60m',
    '30m': '30m',
    '5m': '5m'
}
LOOKBACK = 200  # candles to fetch per timeframe

# --- FUNCTIONS ---
def fetch_data(ticker, interval, lookback):
    try:
        data = yf.download(ticker, period='60d', interval=interval)
        return data.tail(lookback)
    except Exception as e:
        return None

def analyze_signals(df):
    close_series = df['Close'].squeeze()
    df['EMA21'] = EMAIndicator(close_series, window=21).ema_indicator()
    df['EMA50'] = EMAIndicator(close_series, window=50).ema_indicator()
    df['EMA90'] = EMAIndicator(close_series, window=90).ema_indicator()
    df['EMA180'] = EMAIndicator(close_series, window=180).ema_indicator()

    close_series = df['Close'].squeeze() 
    df[''] = RSIIndicator(close_series, window=14).rsi()
    macd = MACD(close_series)
    df['MACD'] = macd.macd()
    df['MACD_Hist'] = macd.macd_diff()
    df.dropna(inplace=True)
    return df

def detect_setup(df):
    if df is None or df.empty or len(df) < 2:
        return "⚠️ Not enough data to generate signal"

    required_cols = ['RSI', 'MACD_Hist', 'EMA21', 'EMA50', 'Close']
    for col in required_cols:
        if col not in df.columns:
            return f"⚠️ Missing indicator: {col}"

    latest = df.iloc[-1]
    prior = df.iloc[-2]

    try:
        if (
            latest['RSI'] < 40 and
            prior['MACD_Hist'] < 0 and latest['MACD_Hist'] > 0 and
            latest['Close'] > latest['EMA21'] > latest['EMA50']
        ):
            return "📈 Bullish Reversal Signal"
        elif (
            latest['RSI'] > 60 and
            prior['MACD_Hist'] > 0 and latest['MACD_Hist'] < 0 and
            latest['Close'] < latest['EMA21'] < latest['EMA50']
        ):
            return "📉 Bearish Reversal Signal"
        else:
            return "No clear setup"
    except KeyError:
        return "⚠️ Missing required data in last candles"



# --- UI ---
st.title("🧠 Market Edge AI - Mini Version")
st.write("This scans 5 symbols across multiple timeframes using MACD, RSI, and EMAs.")

for ticker in TICKERS:
    st.subheader(ticker)
    for tf_name, tf_code in TIMEFRAMES.items():
        st.markdown(f"**Timeframe: {tf_name}**")
        df = fetch_data(ticker, tf_code, LOOKBACK)
        if df is not None and not df.empty:
            df = analyze_signals(df)
            signal = detect_setup(df)
            st.write(signal)
        else:
            st.write("Data not available.")
