# FinWise — Complete Integrated Project

FinWise is a Flask-based personal finance web app that connects:
- Sign up / sign in / logout
- Financial questionnaire
- Automatic income allocation
- Risk-based stock recommendations
- Dashboard
- Finance news with optional NewsAPI integration
- SQLite database for users and saved plans
- Bundled CSV fallback so stock recommendations still work when live market data is unavailable

## 1. Setup

### Windows
```powershell
cd FinWise_Complete
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS / Linux
```bash
cd FinWise_Complete
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Optional: put your NewsAPI key in `.env`:
```env
NEWS_API_KEY=your_key_here
```

## 2. Run
```bash
python app.py
```

Open:
`http://127.0.0.1:5000`

The SQLite database (`finwise.db`) is created automatically.

## 3. Project flow

Home → Sign up / Sign in → Questionnaire → Financial Results → Stock Recommendations → Dashboard / News.

## 4. Notes
- Stock prices are fetched from Yahoo Finance on a best-effort basis. If live data is unavailable, FinWise falls back to the bundled CSV dataset.
- News is fetched through NewsAPI only when `NEWS_API_KEY` is configured; otherwise the app shows a helpful fallback.
- This project is for educational purposes and is not financial advice.
