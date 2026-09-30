from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__, static_folder="static", template_folder="template")

API_KEY = "05abeb0fce2248a1a92c119913d5e6d1"  # Your API Key
BASE_URL = "https://newsapi.org/v2/everything"

@app.route("/")
def home():
    """Serve the main HTML page."""
    return render_template("newsweb.html")  # Ensure `newsweb.html` is inside `templates/`

@app.route("/fetch-news")
def fetch_news():
    """Fetch news based on category."""
    category = request.args.get("category", "finance")
    query = f"{category} AND (India OR NSE OR BSE OR Sensex OR Nifty OR RBI)"
    url = f"{BASE_URL}?q={query}&sortBy=publishedAt&language=en&pageSize=20&page=1&apiKey={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()
        if data.get("status") == "ok":
            return jsonify(data)  # Send news data to frontend
        else:
            return jsonify({"error": data.get("message", "Failed to fetch news")}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)