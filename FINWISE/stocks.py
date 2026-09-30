import requests  # 🔹 used to make API requests to the internet

# 🔐 Replace this with your real Alpha Vantage API key
API_KEY = "M6AZSFYKR1TH8WD7"

# 📦 This function fetches live stock price
def get_indian_stock_price(symbol):
    # 🔗 This is the API URL to get the current price of a stock
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"

    # 🌐 Send a GET request to the API
    response = requests.get(url)

    # 🔍 Get the JSON response (structured data)
    data = response.json()

    # 🧠 Extract the stock price from the response
    try:
        price = data["Global Quote"]["05. price"]
        return float(price)
    except KeyError:
        return "Price not found or API limit exceeded"

# ✅ Example: Get price of RELIANCE and TCS
print("RELIANCE.BSE:", get_indian_stock_price("RELIANCE.BSE"))
print("TCS.BSE:", get_indian_stock_price("TCS.BSE"))
