import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY_HERE'  # 🔁 Replace this with your Alpha Vantage key

def get_price_history(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=compact'
    
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error fetching data for {symbol}")
        return None

    # Convert data to DataFrame
    df = pd.DataFrame(data["Time Series (Daily)"]).T
    df = df.astype(float)
    df['close'] = df['4. close']
    df = df[['close']]
    df.index = pd.to_datetime(df.index)

    return df
if __name__ == "__main__":
    print("Running the script...")  # 👈 Just for checking
    df = get_price_history("RELIANCE.BSE")

    if df is not None:
        print(df.head())  # Display first few rows
    else:
        print("No data received.")

