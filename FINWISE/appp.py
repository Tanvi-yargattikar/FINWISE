from flask import Flask, render_template, request
import pandas as pd
import random
import yfinance as yf
import numpy as np

print("Running THIS version: appp.py")  # in appp.py


app = Flask(__name__)

# 1. Fetch NSE symbols
def fetch_random_symbols(n=100):  # Increased to 100
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    symbols = [symbol + '.NS' for symbol in symbols]
    return random.sample(symbols, n)

# 2. Get stock price and volatility
def calculate_stock_risk_and_price(symbols):
    stock_data = []

    for symbol in symbols:
        try:
            data = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if data.empty:
                continue
            data['Returns'] = data['Close'].pct_change()
            std_dev = np.std(data['Returns'].dropna())
            risk_level = "Low" if std_dev < 0.015 else "Medium" if std_dev < 0.03 else "High"
            current_price = round(data['Close'].iloc[-1], 2)
            stock_data.append({
                'Company': symbol.replace('.NS', ''),
                'Current Price': current_price,
                'Volatility': round(std_dev, 5),
                'Risk Level': risk_level
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return pd.DataFrame(stock_data)

# 3. Filter by risk and budget
def filter_stocks(df, user_risk, budget):
    filtered_df = df[df['Risk Level'] == user_risk]
    budget_filtered_df = filtered_df[filtered_df['Current Price'].astype(float) <= budget]
    return budget_filtered_df

# 4. Main questionnaire form
@app.route("/")
def home():
    return render_template("Finwise.html")

# 5. Process form, calculate allocation, redirect
@app.route("/submit", methods=["POST"])
def submit():
    income = float(request.form.get("income", 0))
    expenses = float(request.form.get("expenses", 0))
    leftover = income - expenses

    # Allocation rules
    emergency = round(leftover * 0.3, 2)
    savings = round(leftover * 0.2, 2)
    goal = round(leftover * 0.2, 2)
    investment = round(leftover * 0.3, 2)

    invest_choice = request.form.get("invest")
    risk = request.form.get("risk")
    investment_type = request.form.get("investment_type")

    stocks = []

    if invest_choice == "yes":
        if investment_type in ["stocks", "both"] and risk:
            risk = risk.capitalize()  # Match "Low", "Medium", "High"
            symbols = fetch_random_symbols()
            stock_df = calculate_stock_risk_and_price(symbols)
            recommended_stocks = filter_stocks(stock_df, risk, investment)

            print("Risk preference:", risk)
            print("Allocated investment:", investment)
            print("Recommended stocks:\n", recommended_stocks)

            stocks = recommended_stocks.to_dict(orient="records")

    return render_template("result.html",
                           leftover=leftover,
                           emergency=emergency,
                           savings=savings,
                           goal=goal,
                           investment=investment,
                           stocks=stocks)

if __name__ == "__main__":
    app.run(debug=True)


