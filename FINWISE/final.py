import pandas as pd
import random
import yfinance as yf
import numpy as np

# STEP 1: Fetch 100 Random Indian Stock Symbols
def fetch_random_symbols(n=1000):
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    symbols = [symbol + '.NS' for symbol in symbols]
    
    random_symbols = random.sample(symbols, n)
    return random_symbols

# STEP 2: Calculate Risk & Price for Each Stock
def calculate_stock_risk_and_price(symbols):
    stock_data = []

    for symbol in symbols:
        try:
            data = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if data.empty:
                continue

            # Daily returns and volatility
            data['Returns'] = data['Close'].pct_change()
            std_dev = np.std(data['Returns'].dropna())

            # Classify risk
            if std_dev < 0.015:
                risk_level = "Low"
            elif std_dev < 0.03:
                risk_level = "Medium"
            else:
                risk_level = "High"

            # Get just the numeric current price value
            current_price = round(data['Close'].iloc[-1], 2)

            stock_data.append({
                'Company': symbol.replace('.NS', ''),
                'Current Price': current_price,
                'Volatility': round(std_dev, 5),
                'Risk Level': risk_level
            })

        except Exception as e:
            print(f"Error with {symbol}: {e}")
    
    return pd.DataFrame(stock_data)

# STEP 3: Filter stocks based on user risk level and budget
def filter_stocks_by_risk_and_budget(df, risk_level, budget):
    # Filter by risk level
    filtered_df = df[df['Risk Level'] == risk_level]

    # Convert price to float in case it's string
    filtered_df['Current Price'] = filtered_df['Current Price'].astype(float)

    # Filter by budget
    budget_filtered_df = filtered_df[filtered_df['Current Price'] <= budget]

    return budget_filtered_df

# MAIN EXECUTION
if __name__ == "__main__":
    print("Fetching stock symbols...")
    symbols = fetch_random_symbols()

    print("Calculating stock risk and price...")
    stock_df = calculate_stock_risk_and_price(symbols)
    
    # Set display options to show clean output
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 100)
    pd.set_option('display.float_format', '{:.2f}'.format)

    print("\n--- All Analyzed Stocks ---")
    print(stock_df.head(10))

    # Get user input
    user_risk = input("\nEnter your risk preference (Low / Medium / High): ").capitalize()
    user_budget = float(input("Enter your max investment per stock (INR): "))

    result = filter_stocks_by_risk_and_budget(stock_df, user_risk, user_budget)

    print(f"\n--- Recommended {user_risk} Risk Stocks under ₹{user_budget} ---")
    print(result.head(10))

    # Optional: Save results
    stock_df.to_csv("all_stocks_with_risk.csv", index=False)
    result.to_csv(f"{user_risk.lower()}_risk_filtered_stocks.csv", index=False)
    print("\nData saved to CSV files.")