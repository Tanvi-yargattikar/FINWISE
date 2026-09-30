from flask import Flask, jsonify
import requests

app = Flask(__name__)

NEWS_API_KEY = "4b7036d9f02945cebbcda9f024bf71ba"

@app.route("/")
def raw_api():
    try:
        # Make a request to News API
        url = f"https://newsapi.org/v2/everything?q=finance&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        # Return the raw JSON directly to the browser
        return jsonify({
            "status": data.get("status"),
            "total_results": data.get("totalResults"),
            "articles_count": len(data.get("articles", [])),
            "first_article_title": data.get("articles", [{}])[0].get("title", "No title") if data.get("articles") else "No articles"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True) 
    from flask import Flask, jsonify
import requests

app = Flask(__name__)

NEWS_API_KEY = "4b7036d9f02945cebbcda9f024bf71ba"

@app.route("/")
def raw_api():
    try:
        # Make a request to News API
        url = f"https://newsapi.org/v2/everything?q=finance&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        # Return the raw JSON directly to the browser
        return jsonify({
            "status": data.get("status"),
            "total_results": data.get("totalResults"),
            "articles_count": len(data.get("articles", [])),
            "first_article_title": data.get("articles", [{}])[0].get("title", "No title") if data.get("articles") else "No articles"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
