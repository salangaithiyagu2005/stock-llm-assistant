import os
import json

TRADE_LOG_PATH = "data/trade_log.json"
NEWS_PATH = "data/news.json"

def safe_load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                return default
            data = json.loads(content)
            return data
    except Exception as e:
        print(f"⚠️ Failed to load {path}: {e}")
        return default

def get_trade_context() -> str:
    trades = safe_load_json(TRADE_LOG_PATH, [])

    if not isinstance(trades, list) or not trades:
        return "No past trades found."

    summary = []
    for trade in trades:
        summary.append(
            f"{trade['date']} - {trade['action']} {trade['symbol']} at ₹{trade['price']}"
        )
    return "\n".join(summary)

def get_news_summary(symbol: str) -> str:
    news = safe_load_json(NEWS_PATH, {})

    if not isinstance(news, dict):
        return f"No news found for {symbol}."

    stock_news = news.get(symbol, [])
    if not stock_news:
        return f"No news found for {symbol}."

    return "\n".join(f"- {item}" for item in stock_news)
