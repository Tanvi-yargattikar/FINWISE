from flask import Flask, request, render_template, url_for
import pandas as pd
import random
import yfinance as yf
import numpy as np

print("🔥 Running THIS version: app.py")  # in app.py


# Initialize Flask App
app = Flask(__name__)

#route for landing page 
@app.route('/')
def Finwise():
    return render_template("Finwise.html")

# Route for the Questionnaire Page
@app.route('/que')
def que():
    return render_template("que.html")

@app.route('/test')
def test():
    return "<h1>Hello, Flask is Working!</h1>"

# Stock analysis functions
def fetch_random_symbols(n=100):
    url = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
    df = pd.read_csv(url)
    symbols = df['SYMBOL'].tolist()
    symbols = [symbol + '.NS' for symbol in symbols]
    
    random_symbols = random.sample(symbols, n)
    return random_symbols

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

def filter_stocks_by_risk_and_budget(df, risk_level, budget):
    # Filter by risk level
    filtered_df = df[df['Risk Level'] == risk_level]

    # Convert price to float in case it's string
    filtered_df['Current Price'] = filtered_df['Current Price'].astype(float)

    # Filter by budget
    budget_filtered_df = filtered_df[filtered_df['Current Price'] <= budget]

    return budget_filtered_df

# Route to Process the Form Submission and show results with stock recommendations
@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get User Input
        income = int(request.form['income'])
        expenses = int(request.form['expenses'])
        leftover = income - expenses

        # Allocating leftover income
        savings = leftover * 0.2
        emergency = leftover * 0.5
        investment = leftover * 0.3
        
        
        # Default risk level is Medium, but you could add this to your form if you want
        risk_level = "Medium"
        
        # Get stock recommendations if there's investment amount
        stocks = []
        if investment > 0:
            try:
                symbols = fetch_random_symbols()
                stock_df = calculate_stock_risk_and_price(symbols)
                result_df = filter_stocks_by_risk_and_budget(stock_df, risk_level, investment)
                stocks = result_df.head(10).to_dict('records')
            except Exception as e:
                print(f"Error getting stock recommendations: {e}")

        return render_template("result.html", 
                               leftover=leftover,
                               emergency=emergency,
                               savings=savings,
                               investment=investment,
                            
                               stocks=stocks,
                               risk=risk_level
                              )
    except ValueError:
        return "Invalid input! Please enter numeric values for income and expenses."

# Route to refresh stock recommendations
@app.route('/get-stocks', methods=['POST'])
def get_stocks():
    try:
        # Get the investment budget and risk from the form
        risk_level = request.form['risk']
        investment = float(request.form['allocated_budget'])
        
        # Calculate other financial values (assuming you need these for the template)
        # These would typically come from session data or be recalculated
        leftover = investment / 0.3  # Since investment is 30% of leftover
        savings = leftover * 0.2
        emergency = leftover * 0.5
        
        
        # Get new stock recommendations
        symbols = fetch_random_symbols()
        stock_df = calculate_stock_risk_and_price(symbols)
        result_df = filter_stocks_by_risk_and_budget(stock_df, risk_level, investment)
        stocks = result_df.head(10).to_dict('records')
        
        return render_template("result.html", 
                              leftover=leftover,
                              emergency=emergency,
                              savings=savings,
                              investment=investment,
                        
                              stocks=stocks,
                              risk=risk_level
                             )
    except Exception as e:
        return f"Error refreshing stock recommendations: {e}"

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)