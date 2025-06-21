import os
import json
import yfinance as yf
import pandas as pd

def get_stock_history(symbol, years=10):
    path = f"stock_history/{symbol}.json"
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=10)

    os.makedirs("stock_history", exist_ok=True)

    # Load existing data if available
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        existing_dates = set(pd.to_datetime(data.keys()))
    else:
        data = {}
        existing_dates = set()

    # Download historical data
    df = yf.download(symbol, start=start, end=end)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.index = pd.to_datetime(df.index).normalize()

    for date in df.index:
        if date in existing_dates:
            continue
        row = df.loc[date]
        data[str(date.date())] = {
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return data
