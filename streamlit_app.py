import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import datetime, timedelta

def calculate_rmo(close, sto_period=6, mto_period=10, lto_period=14, signal_period=3):
    sto = close.diff(sto_period)
    mto = close.diff(mto_period)
    lto = close.diff(lto_period)
    
    rmo = (sto + mto + lto) / 3
    signal = rmo.ewm(span=signal_period, adjust=False).mean()
    
    return rmo, signal

def calculate_momentum(close, period=14):
    return close / close.shift(period) * 100

def get_stock_data(tickers, end_date):
    start_date = end_date - timedelta(days=101)  # Get 101 days of data for calculations
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            
            if not df.empty and len(df) > 1:
                # Calculate indicators (similar to before, but for two days)
                ema_21 = EMAIndicator(df['Close'], window=21).ema_indicator()
                macd_indicator = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
                macd = macd_indicator.macd_diff()
                rmo, signal = calculate_rmo(df['Close'])
                momentum = calculate_momentum(df['Close'])
                stoch = StochasticOscillator(df['High'], df['Low'], df['Close'])
                rsi = RSIIndicator(df['Close']).rsi()
                
                for i in [-2, -1]:  # Calculate for yesterday and today
                    day = df.index[i]
                    prev_day = df.index[i-1]
                    
                    indicators = {
                        '21 Day EMA': 1 if df.loc[day, 'Close'] > ema_21.iloc[i] else 0,
                        'MACD': 1 if macd.iloc[i] >= 0 else 0,
                        'Exp. MACD': 1 if macd.iloc[i] > macd.iloc[i-1] else 0,
                        'Volume': 1 if df.loc[day, 'Volume'] > df.loc[prev_day, 'Volume'] else 0,
                        'Momentum': 1 if momentum.iloc[i] > momentum.iloc[i-1] else 0,
                        'Stochastic': 1 if stoch.stoch().iloc[i] > stoch.stoch().iloc[i-1] else 0,
                        'RSI': 1 if rsi.iloc[i] > rsi.iloc[i-1] else 0,
                    }
                    
                    aot = sum(indicators.values()) / len(indicators) * 100
                    rmo_value = 1 if (rmo.iloc[i] > signal.iloc[i] or (rmo.iloc[i] > 0 and rmo.iloc[i] > rmo.iloc[i-1])) else 0
                    
                    data_point = {
                        'Ticker': ticker,
                        'Date': day.date(),
                        'Open': round(df.loc[day, 'Open'], 5),
                        'High': round(df.loc[day, 'High'], 5),
                        'Low': round(df.loc[day, 'Low'], 5),
                        'Close': round(df.loc[day, 'Close'], 5),
                        **indicators,
                        'AoT': aot,
                        'RMO': rmo_value,
                    }
                    data.append(data_point)
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {str(e)}")
    
    return pd.DataFrame(data)

def style_dataframe(df):
    def color_cells(val):
        color = 'green' if val == 1 else 'red' if val == 0 else 'white'
        return f'background-color: {color}'
    
    styled = df.style.applymap(color_cells, subset=[col for col in df.columns if col not in ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'AoT']])
    
    def color_aot(val):
        return 'background-color: green' if val == 100 else ''
    
    styled = styled.applymap(color_aot, subset=['AoT'])
    
    return styled

# Streamlit app
def main():
    st.title('European Stock Tickers with OHLC and Technical Indicators')

    # ... (keep the ticker lists as they were) ...

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

    # Fetch data for selected date and the day before
    df = get_stock_data(all_tickers, selected_date)
    
    # Separate today's and yesterday's data
    df_today = df[df['Date'] == selected_date].copy()
    df_yesterday = df[df['Date'] == selected_date - timedelta(days=1)].copy()
    
    # Calculate AoT Change and RMO Change
    df_today['AoT Change'] = ((df_today['AoT'] == 100) & (df_yesterday['AoT'] != 100)).astype(int)
    df_today['RMO Change'] = ((df_today['RMO'] == 1) & (df_yesterday['RMO'] == 0)).astype(int)
    
    # Reorder columns
    columns_order = ['Ticker', 'Open', 'High', 'Low', 'Close', '21 Day EMA', 'MACD', 'Exp. MACD', 'Volume', 'Momentum', 'Stochastic', 'RSI', 'RMO', 'AoT', 'AoT Change', 'RMO Change']
    df_display = df_today[columns_order]
    
    # Display data for the selected date
    st.subheader(f'Stock Data for {selected_date}')
    
    # Add filter buttons
    st.write("Filter by:")
    cols = st.columns(len(columns_order))
    filters = {}
    for i, col in enumerate(columns_order):
        with cols[i]:
            if col not in ['Ticker', 'Open', 'High', 'Low', 'Close', 'AoT']:
                filters[col] = st.checkbox(col, key=f"filter_{col}")
    
    # Apply filters
    for col, filter_on in filters.items():
        if filter_on:
            df_display = df_display[df_display[col] == 1]
    
    # Display the styled dataframe
    st.dataframe(style_dataframe(df_display), width=1200, height=600)

if __name__ == '__main__':
    main()
