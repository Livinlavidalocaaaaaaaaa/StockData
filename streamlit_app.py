import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# Inject custom CSS to manage overflow
st.markdown(
    """
    <style>
    .stApp {
        overflow: hidden;
    }
    .stMultiColumn {
        display: flex;
        flex-wrap: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
            
            if not df.empty:
                # 21 Day EMA
                ema_21 = EMAIndicator(df['Close'], window=21).ema_indicator()
                
                # MACD
                macd_indicator = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
                macd = macd_indicator.macd_diff()
                
                # RMO
                rmo, signal = calculate_rmo(df['Close'])
                
                # Momentum Oscillator
                momentum = calculate_momentum(df['Close'])
                
                # Stochastic Oscillator
                stoch = StochasticOscillator(df['High'], df['Low'], df['Close'])
                
                # RSI
                rsi = RSIIndicator(df['Close']).rsi()
                
                last_day = df.index[-1]
                prev_day = df.index[-2]
                
                # Calculate AoT for today and yesterday
                aot_columns = ['21 Day EMA', 'MACD', 'Exp. MACD', 'Volume', 'Momentum', 'Stochastic', 'RSI']
                today_values = [
                    1 if df.loc[last_day, 'Close'] > ema_21.iloc[-1] else 0,
                    1 if macd.iloc[-1] >= 0 else 0,
                    1 if macd.iloc[-1] > macd.iloc[-2] else 0,
                    1 if df.loc[last_day, 'Volume'] > df.loc[prev_day, 'Volume'] else 0,
                    1 if momentum.iloc[-1] > momentum.iloc[-2] else 0,
                    1 if stoch.stoch().iloc[-1] > stoch.stoch().iloc[-2] else 0,
                    1 if rsi.iloc[-1] > rsi.iloc[-2] else 0
                ]
                yesterday_values = [
                    1 if df.loc[prev_day, 'Close'] > ema_21.iloc[-2] else 0,
                    1 if macd.iloc[-2] >= 0 else 0,
                    1 if macd.iloc[-2] > macd.iloc[-3] else 0,
                    1 if df.loc[prev_day, 'Volume'] > df.loc[df.index[-3], 'Volume'] else 0,
                    1 if momentum.iloc[-2] > momentum.iloc[-3] else 0,
                    1 if stoch.stoch().iloc[-2] > stoch.stoch().iloc[-3] else 0,
                    1 if rsi.iloc[-2] > rsi.iloc[-3] else 0
                ]
                
                aot_today = sum(today_values) / len(aot_columns) * 100
                aot_yesterday = sum(yesterday_values) / len(aot_columns) * 100
                
                rmo_today = 1 if (rmo.iloc[-1] > signal.iloc[-1] or (rmo.iloc[-1] > 0 and rmo.iloc[-1] > rmo.iloc[-2])) else 0
                rmo_yesterday = 1 if (rmo.iloc[-2] > signal.iloc[-2] or (rmo.iloc[-2] > 0 and rmo.iloc[-2] > rmo.iloc[-3])) else 0
                
                data.append({
                    'Ticker': ticker,
                    'Open': round(df.loc[last_day, 'Open'], 5),
                    'High': round(df.loc[last_day, 'High'], 5),
                    'Low': round(df.loc[last_day, 'Low'], 5),
                    'Close': round(df.loc[last_day, 'Close'], 5),
                    '21 Day EMA': 1 if df.loc[last_day, 'Close'] > ema_21.iloc[-1] else 0,
                    'MACD': 1 if macd.iloc[-1] >= 0 else 0,
                    'Exp. MACD': 1 if macd.iloc[-1] > macd.iloc[-2] else 0,
                    'Volume': 1 if df.loc[last_day, 'Volume'] > df.loc[prev_day, 'Volume'] else 0,
                    'Momentum': 1 if momentum.iloc[-1] > momentum.iloc[-2] else 0,
                    'Stochastic': 1 if stoch.stoch().iloc[-1] > stoch.stoch().iloc[-2] else 0,
                    'RSI': 1 if rsi.iloc[-1] > rsi.iloc[-2] else 0,
                    'RMO': rmo_today,
                    'AoT': aot_today,
                    'AoT Change': 1 if aot_yesterday != 100 and aot_today == 100 else 0,
                    'RMO Change': 1 if rmo_yesterday == 0 and rmo_today == 1 else 0
                })
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {str(e)}")
    
    return pd.DataFrame(data)

def get_index_data(index_tickers, end_date):
    start_date = end_date - timedelta(days=100)  # Get 100 days of data for calculations
    data = []
    for ticker in index_tickers:
        try:
            index = yf.Ticker(ticker)
            df = index.history(start=start_date, end=end_date)
            
            if not df.empty:
                # RMO
                rmo, signal = calculate_rmo(df['Close'])
                
                # MACD
                macd_indicator = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
                macd = macd_indicator.macd_diff()
                
                last_day = df.index[-1]
                
                data.append({
                    'Ticker': ticker,
                    'Close': round(df.loc[last_day, 'Close'], 2),
                    'RMO': 1 if (rmo.iloc[-1] > signal.iloc[-1] or (rmo.iloc[-1] > 0 and rmo.iloc[-1] > rmo.iloc[-2])) else 0,
                    'MACD': 1 if macd.iloc[-1] >= 0 else 0
                })
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {str(e)}")
    
    return pd.DataFrame(data)

# Streamlit app
def main():
    st.title('Art Of Trading ')

    # Lists of biggest companies by country
    dutch_tickers = ['ASML.AS', 'REN.AS', 'UNA.AS', 'RDSA.AS', 'AD.AS', 'INGA.AS', 'PHIA.AS', 'KPN.AS', 'DSM.AS', 'RAND.AS', 'AKZA.AS', 'MT.AS', 'HEIA.AS', 'PRX.AS', 'WKL.AS', 'AGN.AS', 'NN.AS', 'ASRNL.AS', 'GLPG.AS', 'URW.AS']
    
    belgian_tickers = ['ABI.BR', 'KBC.BR', 'UCB.BR', 'SOLB.BR', 'GBLB.BR', 'COLR.BR', 'PROX.BR', 'ACKB.BR', 'GLPG.BR', 'ARGX.BR', 'UMI.BR', 'BEFB.BR', 'TESB.BR', 'APAM.BR', 'BPOST.BR', 'TNET.BR', 'SOF.BR', 'ONTEX.BR', 'AED.BR', 'BARCO.BR']
    
    french_tickers = ['AI.PA', 'AIR.PA', 'ALO.PA', 'BN.PA', 'BNP.PA', 'CA.PA', 'CAP.PA', 'CS.PA', 'DG.PA', 'ENGI.PA', 'KER.PA', 'LR.PA', 'MC.PA', 'ML.PA', 'OR.PA', 'ORA.PA', 'PUB.PA', 'RI.PA', 'SAF.PA', 'SAN.PA']
    
    german_tickers = ['ADS.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'BMW.DE', 'CON.DE', 'DAI.DE', 'DB1.DE', 'DBK.DE', 'DPW.DE', 'DTE.DE', 'EOAN.DE', 'FME.DE', 'FRE.DE', 'HEI.DE', 'HEN3.DE', 'IFX.DE', 'LIN.DE', 'MRK.DE', 'MUV2.DE']

    all_tickers = dutch_tickers + belgian_tickers + french_tickers + german_tickers

    # Add index tickers
    index_tickers = ['^GDAXI', '^AEX', '^FCHI']  # DAX, AEX, CAC 40

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
    df_stocks = get_stock_data(all_tickers, selected_date)
    df_indices = get_index_data(index_tickers, selected_date)

    # Apply conditional formatting
    def color_cells(val):
        if isinstance(val, (int, float)):
            if val == 1 or val == 100:
                return 'background-color: green'
            elif val == 0:
                return 'background-color: red'
        return ''
    
    # Display index data
    st.subheader(f'Index Data for {selected_date}')
    st.dataframe(df_indices.style.applymap(color_cells))
    
    # Display data for the selected date with formatting
    st.subheader(f'Stock Data for {selected_date}')
    st.dataframe(df_stocks.style.applymap(color_cells))



if __name__ == '__main__':
    main()
