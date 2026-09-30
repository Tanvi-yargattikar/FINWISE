import yfinance as yf
import pandas as pd
import numpy as np

def get_stock_data():
    df = pd.read_csv('stock_risk_with_price.csv')
    return df.to_dict(orient='records')

def fetch_symbols():
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    symbols = [symbol + '.NS' for symbol in symbols]
    return symbols[:100]  # Limit to first 100 for faster testing

def calculate_volatility_and_price(symbols):
    stock_data = []

    for symbol in symbols:
        try:
            data = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if data.empty:
                continue

            # Calculate daily returns
            data['Returns'] = data['Close'].pct_change()
            std_dev = np.std(data['Returns'].dropna())

            # Classify risk level
            if std_dev < 0.015:
                risk_level = "Low"
            elif std_dev < 0.03:
                risk_level = "Medium"
            else:
                risk_level = "High"

            # Get latest close price
            current_price = data['Close'].iloc[-1]

            # Store results
            stock_data.append({
                'Company': symbol.replace('.NS', ''),
                'Current Price': round(current_price, 2),
                'Volatility': round(std_dev, 5),
                'Risk Level': risk_level
            })

        except Exception as e:
            print(f"Error with {symbol}: {e}")

    return pd.DataFrame(stock_data)

if __name__ == "__main__":
    symbols = fetch_symbols()
    result_df = calculate_volatility_and_price(symbols)

    print(result_df.head(20))  # Print top 20 results
    result_df.to_csv('stock_risk_with_price.csv', index=False)
    print("Saved to stock_risk_with_price.csv")
def get_stock_data():
    df = pd.read_csv('stock_risk_with_price.csv')
    return df.to_dict(orient='records')

