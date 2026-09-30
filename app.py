import os
import re
import sqlite3
from datetime import datetime
from functools import wraps
from urllib.parse import quote_plus, urlparse
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

try:
    import yfinance as yf
except Exception:
    yf = None

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "finwise.db")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "finwise-dev-secret-change-me")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            income REAL NOT NULL,
            expenses REAL NOT NULL,
            leftover REAL NOT NULL,
            savings REAL NOT NULL,
            emergency REAL NOT NULL,
            investment REAL NOT NULL,
            risk TEXT NOT NULL,
            investment_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("signin", next=request.path))
        return fn(*args, **kwargs)
    return wrapper


def latest_plan():
    if "user_id" not in session:
        return None
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM plans WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (session["user_id"],),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def money(value):
    return f"₹{value:,.0f}"


def allocation(income, expenses, invest=True):
    leftover = max(0.0, income - expenses)
    if not invest:
        return {
            "leftover": leftover,
            "savings": leftover * 0.60,
            "emergency": leftover * 0.40,
            "investment": 0.0,
        }
    return {
        "leftover": leftover,
        "savings": leftover * 0.20,
        "emergency": leftover * 0.50,
        "investment": leftover * 0.30,
    }


def load_stock_dataset():
    candidates = [
        os.path.join(BASE_DIR, "FINWISE", "stock_risk_with_price.csv"),
        os.path.join(BASE_DIR, "FINWISE", "all_stocks_with_risk.csv"),
        os.path.join(BASE_DIR, "FINWISE", "low_risk_filtered_stocks.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                rename = {}
                for c in df.columns:
                    key = c.strip().lower().replace("_", " ")
                    if key in {"company", "symbol", "stock"}:
                        rename[c] = "Company"
                    elif "current price" in key or key == "price":
                        rename[c] = "Current Price"
                    elif "volatility" in key or "std" in key:
                        rename[c] = "Volatility"
                    elif "risk" in key:
                        rename[c] = "Risk Level"
                df = df.rename(columns=rename)
                required = {"Company", "Current Price", "Volatility", "Risk Level"}
                if required.issubset(df.columns):
                    return df[list(required)].copy()
            except Exception:
                pass
    return pd.DataFrame(columns=["Company", "Current Price", "Volatility", "Risk Level"])


def live_stock_data(limit=40):
    """Best-effort live NSE data. Falls back to bundled CSV so the app still works offline."""
    bundled = load_stock_dataset()
    if yf is None:
        return bundled

    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
               "ITC.NS", "LT.NS", "SBIN.NS", "BHARTIARTL.NS", "MARUTI.NS",
               "HINDUNILVR.NS", "SUNPHARMA.NS", "AXISBANK.NS", "KOTAKBANK.NS"]
    rows = []
    for symbol in symbols[:limit]:
        try:
            data = yf.download(symbol, period="6mo", interval="1d",
                               progress=False, auto_adjust=False, threads=False)
            if data is None or data.empty:
                continue
            close = data["Close"]
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            returns = close.pct_change().dropna()
            vol = float(returns.std())
            price = float(close.iloc[-1])
            risk = "Low" if vol < 0.015 else "Medium" if vol < 0.03 else "High"
            rows.append({
                "Company": symbol.replace(".NS", ""),
                "Current Price": round(price, 2),
                "Volatility": round(vol, 5),
                "Risk Level": risk,
            })
        except Exception:
            continue

    live = pd.DataFrame(rows)
    if not live.empty:
        return live
    return bundled


def recommend_stocks(risk, budget, limit=10):
    df = live_stock_data()
    if df.empty:
        return []
    df["Current Price"] = pd.to_numeric(df["Current Price"], errors="coerce")
    df["Volatility"] = pd.to_numeric(df["Volatility"], errors="coerce")
    df = df.dropna(subset=["Current Price", "Volatility"])
    risk = risk.title()
    result = df[(df["Risk Level"].astype(str).str.title() == risk) &
                (df["Current Price"] <= float(budget))].copy()
    # Prefer lower volatility within the selected risk bucket.
    result = result.sort_values(["Volatility", "Current Price"])
    return result.head(limit).to_dict("records")


def extract_article_image(article_url):
    if not article_url:
        return ""

    try:
        response = requests.get(
            article_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
            allow_redirects=True,
        )
        response.raise_for_status()
        html = response.text
    except Exception:
        return ""

    patterns = [
        r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\']',
        r'<meta[^>]+itemprop=["\']image["\'][^>]+content=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            image_url = match.group(1).strip()
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            elif image_url.startswith("/"):
                parsed = urlparse(response.url)
                image_url = f"{parsed.scheme}://{parsed.netloc}{image_url}"
            return image_url
    return ""


def _parse_google_news_rss(xml_text, limit=12):
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    articles = []
    media_ns = "http://search.yahoo.com/mrss/"
    for item in root.findall(".//item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        published_at = (item.findtext("pubDate") or datetime.utcnow().isoformat()).strip()

        source_node = item.find("source")
        source_name = (source_node.text if source_node is not None and source_node.text else "Google News").strip()

        image_url = ""
        for candidate in [
            item.find(f"{{{media_ns}}}content"),
            item.find(f"{{{media_ns}}}thumbnail"),
            item.find("enclosure"),
        ]:
            if candidate is not None:
                image_url = (candidate.attrib.get("url") or candidate.attrib.get("href") or "").strip()
                if image_url:
                    break
        if not image_url:
            image_tag = item.find("image")
            if image_tag is not None:
                image_url = (image_tag.findtext("url") or "").strip()
        if not image_url and link:
            image_url = extract_article_image(link)

        if not title or not link:
            continue

        articles.append({
            "title": title,
            "description": description or "No summary available.",
            "url": link,
            "urlToImage": image_url,
            "source": {"name": source_name},
            "publishedAt": published_at,
        })

    return articles


def get_news(query="finance", limit=12):
    if NEWS_API_KEY:
        try:
            q = f"{query} AND (India OR NSE OR BSE OR Sensex OR Nifty OR RBI)"
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": q,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": limit,
                    "apiKey": NEWS_API_KEY,
                },
                timeout=8,
            )
            data = response.json()
            if data.get("status") == "ok":
                return data.get("articles", [])
        except Exception:
            pass

    search_terms = f"{query} finance India NSE BSE RBI"
    rss_url = (
        "https://news.google.com/rss/search?q="
        f"{quote_plus(search_terms)}&hl=en-IN&gl=IN&ceid=IN:en"
    )
    try:
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        articles = _parse_google_news_rss(response.text, limit=limit)
        if articles:
            return articles
    except Exception:
        pass

    return [
        {
            "title": "Live market updates are temporarily unavailable",
            "description": "Please refresh the page or check your internet connection. Recent finance news will appear here automatically when available.",
            "url": "https://www.google.com/search?q=finance+news",
            "urlToImage": "",
            "source": {"name": "FinWise"},
            "publishedAt": datetime.utcnow().isoformat(),
        }
    ]


@app.context_processor
def inject_globals():
    return {
        "logged_in": "user_id" in session,
        "username": session.get("username"),
        "current_year": datetime.now().year,
    }


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or len(password) < 6:
            flash("Enter all fields. Password must be at least 6 characters.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        else:
            try:
                conn = get_db()
                conn.execute(
                    "INSERT INTO users(username,email,password_hash,created_at) VALUES(?,?,?,?)",
                    (username, email, generate_password_hash(password), datetime.now().isoformat()),
                )
                conn.commit()
                conn.close()
                flash("Account created. Please sign in.", "success")
                return redirect(url_for("signin"))
            except sqlite3.IntegrityError:
                flash("Username or email already exists.", "danger")
    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? OR email=?",
            (identity, identity.lower()),
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!", "success")
            return redirect(request.args.get("next") or url_for("dashboard"))
        flash("Invalid username/email or password.", "danger")
    return render_template("signin.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("home"))


@app.route("/questionnaire")
@login_required
def questionnaire():
    return render_template("questionnaire.html")


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    try:
        income = float(request.form["income"])
        expenses = float(request.form["expenses"])
    except (KeyError, ValueError):
        flash("Please enter valid income and expense amounts.", "danger")
        return redirect(url_for("questionnaire"))

    if income < 0 or expenses < 0 or expenses > income:
        flash("Expenses must be positive and cannot exceed income.", "danger")
        return redirect(url_for("questionnaire"))

    invest = request.form.get("invest", "no") == "yes"
    risk = request.form.get("risk", "medium").lower()
    investment_type = request.form.get("investment_type", "stocks")
    amounts = allocation(income, expenses, invest)

    conn = get_db()
    conn.execute(
        """INSERT INTO plans
        (user_id,income,expenses,leftover,savings,emergency,investment,risk,investment_type,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            session["user_id"], income, expenses, amounts["leftover"],
            amounts["savings"], amounts["emergency"], amounts["investment"],
            risk, investment_type, datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("results"))


@app.route("/results")
@login_required
def results():
    plan = latest_plan()
    if not plan:
        return redirect(url_for("questionnaire"))
    stocks = recommend_stocks(plan["risk"], plan["investment"])
    return render_template("results.html", plan=plan, stocks=stocks)


@app.route("/get-stocks", methods=["POST"])
@login_required
def get_stocks():
    plan = latest_plan()
    if not plan:
        return redirect(url_for("questionnaire"))
    risk = request.form.get("risk", plan["risk"])
    budget = float(request.form.get("allocated_budget", plan["investment"]))
    stocks = recommend_stocks(risk, budget)
    return render_template("results.html", plan={**plan, "risk": risk, "investment": budget}, stocks=stocks)


@app.route("/dashboard")
@login_required
def dashboard():
    plan = latest_plan()
    return render_template("dashboard.html", plan=plan)


@app.route("/news")
def news():
    return render_template("news.html")


@app.route("/api/news")
def api_news():
    query = request.args.get("q", "finance")
    return jsonify({"articles": get_news(query)})


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "FinWise"})


@app.route("/api/stocks")
def api_stocks():
    risk = request.args.get("risk", "medium")
    budget = float(request.args.get("budget", "100000"))
    return jsonify({"stocks": recommend_stocks(risk, budget)})


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
