import pandas as pd

def fetch_symbols():
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    symbols = [symbol + '.NS' for symbol in symbols]
    return symbols

 
if __name__ == "__main__":
    stock_symbols = fetch_symbols()
    print(stock_symbols[:100])  # Just show first 10 to avoid too much output
 