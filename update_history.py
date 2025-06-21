import json
from stock_history import get_stock_history

def update_all_stock_history():
    with open("watchlist.json", "r") as f:
        watchlist = json.load(f)["stocks"]

    for symbol in watchlist:
        print(f"📥 Updating history for {symbol}")
        try:
            get_stock_history(symbol, years=10)
            print(f"✅ Done: {symbol}")
        except Exception as e:
            print(f"❌ Failed: {symbol} -> {e}")

if __name__ == "__main__":
    update_all_stock_history()
