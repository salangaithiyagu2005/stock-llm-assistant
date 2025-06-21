import json
from datetime import datetime
from typing import Optional, List

class ModelContextProvider:
    def __init__(self, storage_file='trade_log.json'):
        self.storage_file = storage_file
        try:
            with open(self.storage_file, 'r') as f:
                self.trades = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.trades = []

    def save(self):
        with open(self.storage_file, 'w') as f:
            json.dump(self.trades, f, indent=2)

    def add_trade(self, symbol: str, action: str, price: float, quantity: int, status: str = "open", news: Optional[List[str]] = None, note: Optional[str] = None):
        trade = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol.upper(),
            "action": action.upper(),
            "price": round(price, 2),
            "quantity": quantity,
            "status": status,
            "news": news or [],
            "note": note
        }
        self.trades.append(trade)
        self.save()

    def close_trade(self, symbol: str, exit_price: float):
        for trade in reversed(self.trades):
            if trade["symbol"] == symbol.upper() and trade["status"] == "open":
                trade["exit_price"] = round(exit_price, 2)
                trade["status"] = "closed"
                trade["profit"] = round((exit_price - trade["price"]) * trade["quantity"], 2)
                break
        self.save()

    def get_recent_trades(self, n=5):
        return self.trades[-n:]

    def get_context_summary(self, n=5):
        trades = self.get_recent_trades(n)
        context = []
        for t in trades:
            summary = (
                f"{t['date']} - {t['symbol']} {t['action']} @ {t['price']} x {t['quantity']}"
                + (f" -> EXIT @ {t['exit_price']}, P&L: ₹{t['profit']}" if t.get("exit_price") else "")
            )
            context.append(summary)
        return "\n".join(context)
