import streamlit as st
import pandas as pd
import pandas_ta as ta
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
    df['EMA21'] = ta.ema(df['Close'], length=21)
    df['EMA50'] = ta.ema(df['Close'], length=50)
    df['EMA90'] = ta.ema(df['Close'], length=90)
    df['EMA180'] = ta.ema(df['Close'], length=180)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_Hist'] = macd['MACDh_12_26_9']
    df.dropna(inplace=True)
    return df

def detect_setup(df):
    latest = df.iloc[-1]
    prior = df.iloc[-2]
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
