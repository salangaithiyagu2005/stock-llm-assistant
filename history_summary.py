import json
import os
from statistics import mean, stdev

def summarize_stock_history(symbol: str, days: int = 30):
    path = os.path.join("stock_history", f"{symbol}.json")
    if not os.path.exists(path):
        return f"No history available for {symbol}"

    with open(path, "r") as f:
        data = json.load(f)

    recent = list(data.items())[-days:]
    if not recent:
        return f"No data found in last {days} days"

    closes = [day[1]["close"] for day in recent]
    highs = [day[1]["high"] for day in recent]
    lows = [day[1]["low"] for day in recent]

    summary = {
        "last_close": closes[-1],
        "30d_avg": round(mean(closes), 2),
        "30d_high": max(highs),
        "30d_low": min(lows),
        "volatility": round(stdev(closes), 2) if len(closes) > 1 else 0.0,
        "last_date": recent[-1][0]
    }

    return (
        f"{symbol} summary as of {summary['last_date']}:\n"
        f"- Last Close: Rs.{summary['last_close']}\n"
        f"- 30-day Avg Close: Rs.{summary['30d_avg']}\n"
        f"- High: Rs.{summary['30d_high']}, Low: Rs.{summary['30d_low']}\n"
        f"- Volatility (std dev): {summary['volatility']}\n"
    )
