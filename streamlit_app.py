import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta

# Function to fetch stock data and calculate indicators
def get_stock_data(tickers, date):
    data = []
    for ticker in tickers:
        try:
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
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {str(e)}")
    
    return pd.DataFrame(data)

# Streamlit app
def main():
    st.title('European Stock Tickers with OHLC and Technical Indicators')

    # Lists of biggest companies by country
    dutch_tickers = ['ASML.AS', 'REN.AS', 'UNA.AS', 'RDSA.AS', 'AD.AS', 'INGA.AS', 'PHIA.AS', 'KPN.AS', 'DSM.AS', 'RAND.AS', 'AKZA.AS', 'MT.AS', 'HEIA.AS', 'PRX.AS', 'WKL.AS', 'AGN.AS', 'NN.AS', 'ASRNL.AS', 'GLPG.AS', 'URW.AS']
    
    belgian_tickers = ['ABI.BR', 'KBC.BR', 'UCB.BR', 'SOLB.BR', 'GBLB.BR', 'COLR.BR', 'PROX.BR', 'ACKB.BR', 'GLPG.BR', 'ARGX.BR', 'UMI.BR', 'BEFB.BR', 'TESB.BR', 'APAM.BR', 'BPOST.BR', 'TNET.BR', 'SOF.BR', 'ONTEX.BR', 'AED.BR', 'BARCO.BR']
    
    french_tickers = ['AI.PA', 'AIR.PA', 'ALO.PA', 'BN.PA', 'BNP.PA', 'CA.PA', 'CAP.PA', 'CS.PA', 'DG.PA', 'ENGI.PA', 'KER.PA', 'LR.PA', 'MC.PA', 'ML.PA', 'OR.PA', 'ORA.PA', 'PUB.PA', 'RI.PA', 'SAF.PA', 'SAN.PA']
    
    german_tickers = ['ADS.DE', 'ALV.DE', 'BAS.DE', 'BAYN.DE', 'BMW.DE', 'CON.DE', 'DAI.DE', 'DB1.DE', 'DBK.DE', 'DPW.DE', 'DTE.DE', 'EOAN.DE', 'FME.DE', 'FRE.DE', 'HEI.DE', 'HEN3.DE', 'IFX.DE', 'LIN.DE', 'MRK.DE', 'MUV2.DE']

    all_tickers = dutch_tickers + belgian_tickers + french_tickers + german_tickers

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
    df = get_stock_data(all_tickers, selected_date)

    # Display data for the selected date
    st.subheader(f'Stock Data for {selected_date}')
    st.table(df)

if __name__ == '__main__':
    main()
