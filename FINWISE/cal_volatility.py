import yfinance as yf
import pandas as pd
import numpy as np

# Step 1: Get 100 symbols from NSE
def fetch_symbols():
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    symbols = [symbol + '.NS' for symbol in symbols]
    return symbols[:100]  # LIMIT to 100

symbols = fetch_symbols()

# Step 2: Get historical prices and calculate volatility
risk_data = {}

for symbol in symbols:
    try:
        data = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if data.empty:
            continue
        data['Returns'] = data['Close'].pct_change()
        std_dev = np.std(data['Returns'].dropna())
        risk_data[symbol] = std_dev
    except Exception as e:
        print(f"Error with {symbol}: {e}")

# Step 3: Create a DataFrame of symbol vs volatility
risk_df = pd.DataFrame(list(risk_data.items()), columns=['Symbol', 'Volatility'])
risk_df = risk_df.sort_values(by='Volatility')

# Print top 10 for now
print(risk_df.head(100))

# Optional: Save to CSV for future use
risk_df.to_csv('stock_volatility.csv', index=False)
