# update_history.py

import os
import json
import yfinance as yf
from datetime import datetime

WATCHLIST_FILE = "watchlist.json"
HISTORY_DIR = "stock_history"

if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            data = json.load(f)
            return data.get("stocks", [])
    return []

def download_and_update(symbol):
    try:
        path = os.path.join(HISTORY_DIR, f"{symbol}.json")
        existing_data = {}

        if os.path.exists(path):
            with open(path, "r") as f:
                existing_data = json.load(f)

        start = "2013-01-01"
        end = datetime.today().strftime("%Y-%m-%d")
        data = yf.download(symbol, start=start, end=end)
        if data.empty:
            print(f"⚠️ No data for {symbol}")
            return

        for index, row in data.iterrows():
            day = index.strftime("%Y-%m-%d")
            if day not in existing_data:
                existing_data[day] = {
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                }

        with open(path, "w") as f:
            json.dump(existing_data, f, indent=2)

        print(f"✅ Updated {symbol}")

    except Exception as e:
        print(f"❌ Failed to update {symbol}: {e}")

if __name__ == "__main__":
    symbols = load_watchlist()
    if not symbols:
        print("❌ No stocks in watchlist.json")
    for sym in symbols:
        download_and_update(sym)
