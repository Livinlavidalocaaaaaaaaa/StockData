import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

# Function to fetch stock data and calculate indicators
def get_stock_data(tickers, date):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        df = stock.history(start=date, end=date + timedelta(days=1))
        
        if not df.empty:
            # Calculate MACD
            close_series = stock.history(start=date - timedelta(days=33), end=date)['Close']
            macd = ta.trend.macd_diff(close_series).iloc[-1]
            
            # Calculate Rahul Mohinder Oscillator (RMO)
            rmo = (ta.momentum.roc(close_series, window=10) - ta.momentum.roc(close_series, window=30)).iloc[-1]
            
            data.append({
                'Ticker': ticker,
                'Open': round(df['Open'].iloc[0], 5),
                'High': round(df['High'].iloc[0], 5),
                'Low': round(df['Low'].iloc[0], 5),
                'Close': round(df['Close'].iloc[0], 5),
                'MACD': 1 if macd >= 0 else 0,
                'RMO': 1 if rmo >= 0 else 0
            })
    
    return pd.DataFrame(data)

# Streamlit app
def main():
    st.title('Dutch Stock Tickers with OHLC and Technical Indicators')

    # List of Dutch stock tickers
    dutch_tickers = ['ASML.AS', 'RDSA.AS', 'UNA.AS', 'AD.AS', 'INGA.AS']

    # Date range for data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)  # One year of data

    # Date selector
    selected_date = st.date_input(
        "Select a date",
        min_value=start_date,
        max_value=end_date,
        value=end_date
    )

    # Fetch data for selected date
    df = get_stock_data(dutch_tickers, selected_date)

    # Display data for the selected date
    st.subheader(f'Stock Data for {selected_date}')
    st.table(df)

if __name__ == '__main__':
    main()
