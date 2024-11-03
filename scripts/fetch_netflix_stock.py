import os
import yfinance as yf
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
ticker_symbol = 'NFLX'
start_date = '2014-01-01'
end_date = '2024-07-31'

netflix_data = yf.download(ticker_symbol, start=start_date, end=end_date)
# Drop any multi-level index (like 'Ticker') if it exists
if isinstance(netflix_data.columns, pd.MultiIndex):
    netflix_data.columns = netflix_data.columns.get_level_values(0)

# Reset index so that 'Date' becomes a regular column
netflix_data.reset_index(inplace=True)

os.makedirs(DATA_DIR, exist_ok=True)
file_path = os.path.join(DATA_DIR, 'netflix_stock_data.csv')
netflix_data.to_csv(file_path)
print(f"Netflix Data successfully saved to {file_path}")