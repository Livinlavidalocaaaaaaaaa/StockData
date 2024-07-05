import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Function to fetch stock data
def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    return df

# Function to calculate technical indicators
def add_indicators(df):
    # MACD
    df['MACD'] = ta.trend.macd_diff(df['Close'])
    
    # Rahul Mohinder Oscillator (RMO)
    df['RMO'] = ta.momentum.roc(df['Close'], window=10) - ta.momentum.roc(df['Close'], window=30)
    
    return df

# Streamlit app
def main():
    st.title('Dutch Stock Tickers with OHLC and Technical Indicators')

    # List of Dutch stock tickers (you can expand this list)
    dutch_tickers = ['ASML.AS', 'RDSA.AS', 'UNA.AS', 'AD.AS', 'INGA.AS']

    # Sidebar for user input
    selected_ticker = st.sidebar.selectbox('Select a Dutch stock ticker', dutch_tickers)
    
    # Fetch and display stock data
    df = get_stock_data(selected_ticker)
    df = add_indicators(df)

    # Display OHLC data
    st.subheader(f'OHLC Data for {selected_ticker}')
    st.dataframe(df[['Open', 'High', 'Low', 'Close']])

    # Display technical indicators
    st.subheader('Technical Indicators')
    st.dataframe(df[['MACD', 'RMO']])

    # Optional: Add charts
    st.subheader('Stock Price Chart')
    st.line_chart(df['Close'])

    st.subheader('MACD Chart')
    st.line_chart(df['MACD'])

    st.subheader('Rahul Mohinder Oscillator Chart')
    st.line_chart(df['RMO'])

if __name__ == '__main__':
    main()
