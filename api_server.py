# api_server.py - US Sector Rotation Backend
# FastAPI + yfinance: Fetches S&P 500 sector ETF data and calculates money flow

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
import json
from datetime import datetime, timedelta
import os

app = FastAPI(title="US Sector Rotation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 11 SPDR S&P 500 Sector ETFs
SECTORS = {
    "XLK":  {"name": "Technology",             "name_zh": "科技"},
    "XLF":  {"name": "Financials",             "name_zh": "金融"},
    "XLV":  {"name": "Health Care",            "name_zh": "醫療"},
    "XLY":  {"name": "Consumer Disc.",         "name_zh": "非必需消費"},
    "XLC":  {"name": "Communication",          "name_zh": "通訊"},
    "XLI":  {"name": "Industrials",            "name_zh": "工業"},
    "XLP":  {"name": "Consumer Staples",       "name_zh": "必需消費"},
    "XLE":  {"name": "Energy",                 "name_zh": "能源"},
    "XLU":  {"name": "Utilities",              "name_zh": "公用事業"},
    "XLRE": {"name": "Real Estate",            "name_zh": "房地產"},
    "XLB":  {"name": "Materials",              "name_zh": "原材料"},
    "SPY":  {"name": "S&P 500 (Benchmark)",    "name_zh": "S&P 500"},
}

def calc_money_flow(ticker_data):
    """Calculate money flow proxy: (close - open) * volume per day"""
    df = ticker_data.copy()
    df["money_flow"] = (df["Close"] - df["Open"]) * df["Volume"]
    return df

@app.get("/api/sectors")
def get_sectors():
    """Return sector bubble chart data for the last 30 days"""
    results = []
    end = datetime.today()
    start = end - timedelta(days=45)

    for ticker, meta in SECTORS.items():
        if ticker == "SPY":
            continue
        try:
            df = yf.download(ticker, start=start.strftime("%Y-%m-%d"),
                             end=end.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            if df.empty:
                continue

            df = calc_money_flow(df)

            # Recent 5-day trend (Y axis)
            recent5 = df["money_flow"].tail(5).sum() / 1e6  # in millions
            # Recent 20-day cumulative (bubble size)
            recent20 = df["money_flow"].tail(20).sum() / 1e6
            # Latest day flow (X axis)
            latest_flow = df["money_flow"].iloc[-1] / 1e6

            # 5-day price change %
            price_change_5d = 0
            if len(df) >= 5:
                price_change_5d = (df["Close"].iloc[-1] / df["Close"].iloc[-5] - 1) * 100

            # 20-day price change %
            price_change_20d = 0
            if len(df) >= 20:
                price_change_20d = (df["Close"].iloc[-1] / df["Close"].iloc[-20] - 1) * 100

            # Quadrant classification
            if recent5 > 0 and latest_flow > 0:
                quadrant = "rising"       # 漲潮
            elif recent5 > 0 and latest_flow <= 0:
                quadrant = "rotating"     # 輪動
            elif recent5 <= 0 and latest_flow > 0:
                quadrant = "watching"     # 翻望
            else:
                quadrant = "falling"      # 退潮

            results.append({
                "ticker": ticker,
                "name": meta["name"],
                "name_zh": meta["name_zh"],
                "x": round(float(latest_flow), 2),         # X: latest day money flow (M$)
                "y": round(float(recent5), 2),             # Y: 5-day trend
                "size": round(abs(float(recent20)), 2),    # Bubble size: 20-day abs flow
                "price_change_5d": round(float(price_change_5d), 2),
                "price_change_20d": round(float(price_change_20d), 2),
                "quadrant": quadrant,
                "close": round(float(df["Close"].iloc[-1]), 2),
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue

    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sectors": results
    }

@app.get("/api/market_breadth")
def get_market_breadth():
    """SPY benchmark + advancing/declining ratio of 11 sectors"""
    try:
        spy = yf.download("SPY", period="5d", progress=False, auto_adjust=True)
        spy_change = round(float((spy["Close"].iloc[-1] / spy["Close"].iloc[-2] - 1) * 100), 2)
    except:
        spy_change = 0

    return {
        "spy_change": spy_change,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

# Serve static frontend
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
