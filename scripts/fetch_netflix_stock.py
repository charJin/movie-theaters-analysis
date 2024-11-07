import os
import yfinance as yf
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
tickers = ['NFLX', 'AMC', 'CNK', 'IMAX']
start_date = '2007-01-01'
end_date = '2024-07-31'

for ticker in tickers:
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)
    stock_data.reset_index(inplace=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, f'{ticker.lower()}_stock_data.csv')
    stock_data.to_csv(file_path)
    print(f"{ticker} stock data successfully saved to {file_path}")