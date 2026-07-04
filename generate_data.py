# generate_data.py
# Run by GitHub Actions to produce static JSON for GitHub Pages deployment
# Output: static/data/sectors.json, static/data/breadth.json

import yfinance as yf
import json
import os
from datetime import datetime, timedelta

SECTORS = {
    "XLK":  {"name": "Technology",        "name_zh": "科技"},
    "XLF":  {"name": "Financials",        "name_zh": "金融"},
    "XLV":  {"name": "Health Care",       "name_zh": "醫療"},
    "XLY":  {"name": "Consumer Disc.",    "name_zh": "非必需消費"},
    "XLC":  {"name": "Communication",     "name_zh": "通訊"},
    "XLI":  {"name": "Industrials",       "name_zh": "工業"},
    "XLP":  {"name": "Consumer Staples",  "name_zh": "必需消費"},
    "XLE":  {"name": "Energy",            "name_zh": "能源"},
    "XLU":  {"name": "Utilities",         "name_zh": "公用事業"},
    "XLRE": {"name": "Real Estate",       "name_zh": "房地產"},
    "XLB":  {"name": "Materials",         "name_zh": "原材料"},
}

os.makedirs("static/data", exist_ok=True)

end = datetime.today()
start = end - timedelta(days=45)

results = []
for ticker, meta in SECTORS.items():
    try:
        df = yf.download(ticker, start=start.strftime("%Y-%m-%d"),
                         end=end.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
        if df.empty:
            print(f"  Skipping {ticker}: no data")
            continue

        df["money_flow"] = (df["Close"] - df["Open"]) * df["Volume"]

        recent5  = float(df["money_flow"].tail(5).sum()) / 1e6
        recent20 = float(df["money_flow"].tail(20).sum()) / 1e6
        latest   = float(df["money_flow"].iloc[-1]) / 1e6

        pc5  = float((df["Close"].iloc[-1] / df["Close"].iloc[-5]  - 1) * 100) if len(df) >= 5  else 0
        pc20 = float((df["Close"].iloc[-1] / df["Close"].iloc[-20] - 1) * 100) if len(df) >= 20 else 0

        if recent5 > 0 and latest > 0:
            quadrant = "rising"
        elif recent5 > 0 and latest <= 0:
            quadrant = "rotating"
        elif recent5 <= 0 and latest > 0:
            quadrant = "watching"
        else:
            quadrant = "falling"

        results.append({
            "ticker": ticker,
            "name": meta["name"],
            "name_zh": meta["name_zh"],
            "x": round(latest, 2),
            "y": round(recent5, 2),
            "size": round(abs(recent20), 2),
            "price_change_5d": round(pc5, 2),
            "price_change_20d": round(pc20, 2),
            "quadrant": quadrant,
            "close": round(float(df["Close"].iloc[-1]), 2),
        })
        print(f"  OK {ticker}: x={latest:.1f}M y={recent5:.1f}M quadrant={quadrant}")
    except Exception as e:
        print(f"  ERROR {ticker}: {e}")

with open("static/data/sectors.json", "w") as f:
    json.dump({"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
               "sectors": results}, f)
print(f"Saved {len(results)} sectors to static/data/sectors.json")

# SPY breadth
try:
    spy = yf.download("SPY", period="5d", progress=False, auto_adjust=True)
    spy_change = round(float((spy["Close"].iloc[-1] / spy["Close"].iloc[-2] - 1) * 100), 2)
except:
    spy_change = 0

with open("static/data/breadth.json", "w") as f:
    json.dump({"spy_change": spy_change,
               "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC")}, f)
print(f"S&P 500 change: {spy_change}%")
