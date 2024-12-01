import streamlit as st
import requests
import pandas as pd
import numpy as np

# Fetch real-time crypto data
def fetch_crypto_data(symbol, interval='1h', limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    # Convert to DataFrame
    columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
               'Close Time', 'Quote Asset Volume', 'Number of Trades', 
               'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore']
    df = pd.DataFrame(data, columns=columns)

    # Clean and convert to numeric
  for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
      df[col] = pd.to_numeric(df[col], errors='coerce')
      
    df.dropna(subset = ['Close'], inplace = True)
    return df

# RSI Calculation
def calculate_rsi(data, period=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# Moving Average
def calculate_moving_averages(data, short_window=9, long_window=21):
    data['Short MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long MA'] = data['Close'].rolling(window=long_window).mean()
    return data

# Generate Buy/Sell Signals
def generate_signals(data):
    if data.empty:
        print("No data available for signal generation")
        return data
    data['Signal'] = 0
    # Buy Signal: RSI < 30 and Price > Short MA
    data.loc[(data['RSI'] < 30) & (data['Close'] > data['Short MA']), 'Signal'] = 1
    # Sell Signal: RSI > 70 and Price < Short MA
    data.loc[(data['RSI'] > 70) & (data['Close'] < data['Short MA']), 'Signal'] = -1
    return data

# Streamlit App
st.title("Real-Time Crypto Analysis")
symbol = st.text_input("Enter Crypto Symbol (e.g., BTCUSDT):", value="BTCUSDT")

if st.button("Analyze"):
    data = fetch_crypto_data(symbol)
    data = calculate_rsi(data)
    data = calculate_moving_averages(data)
    data = generate_signals(data)

    # Display Data
    st.write(data[['Close', 'RSI', 'Short MA', 'Long MA', 'Signal']])

    # Plot
    st.line_chart(data[['Close', 'Short MA', 'Long MA']])
