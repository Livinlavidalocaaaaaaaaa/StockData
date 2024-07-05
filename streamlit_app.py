import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# Function to fetch stock data and calculate indicators
def get_stock_data(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    
    # Calculate MACD
    df['MACD'] = ta.trend.macd_diff(df['Close'])
    
    # Calculate Rahul Mohinder Oscillator (RMO)
    df['RMO'] = ta.momentum.roc(df['Close'], window=10) - ta.momentum.roc(df['Close'], window=30)
    
    # Reset index to make Date a column
    df = df.reset_index()
    
    # Add Ticker column
    df['Ticker'] = ticker
    
    # Select and reorder columns
    df = df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'MACD', 'RMO']]
    
    # Rename columns to match desired format
    df.columns = ['Date', 'Ticker', 'O', 'H', 'L', 'C', 'MACD', 'RMO']
    
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

    # Display data in the requested format
    st.subheader(f'Stock Data for {selected_ticker}')
    st.dataframe(df)

    # Optional: Add charts
    st.subheader('Stock Price Chart')
    st.line_chart(df.set_index('Date')['C'])

    st.subheader('MACD Chart')
    st.line_chart(df.set_index('Date')['MACD'])

    st.subheader('Rahul Mohinder Oscillator Chart')
    st.line_chart(df.set_index('Date')['RMO'])

if __name__ == '__main__':
    main()
