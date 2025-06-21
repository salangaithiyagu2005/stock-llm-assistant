import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from llm_agent import suggest_trade
from ml.predict import predict_next_close
import json
import subprocess
import os
import sys

WATCHLIST_FILE = "watchlist.json"

class StockLLMAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📈 Stock LLM Assistant")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)

        self.symbol_var = tk.StringVar()
        self.result_text = tk.Text(root, wrap=tk.WORD, height=20, width=120)
        self.build_ui()
        self.load_watchlist()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.X)

        # Dropdown for symbol
        ttk.Label(frame, text="Stock Symbol:").pack(side=tk.LEFT)
        self.symbol_dropdown = ttk.Combobox(frame, textvariable=self.symbol_var, state="readonly", width=20)
        self.symbol_dropdown.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame, text="🧠 Suggest Trade", command=self.suggest_trade).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="⚙️ Manage Stocks", command=self.manage_stocks_popup).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="🚀 Start Ollama", command=self.start_ollama).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="📥 Download", command=self.download_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="🔁 Train", command=self.train_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="❌ Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def load_watchlist(self):
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, "r") as f:
                data = json.load(f)
                stocks = data.get("stocks", [])
                self.symbol_dropdown['values'] = stocks
                if stocks:
                    self.symbol_dropdown.current(0)

    def _get_stocks(self):
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, "r") as f:
                return json.load(f).get("stocks", [])
        return []

    def _save_stocks(self, stocks):
        with open(WATCHLIST_FILE, "w") as f:
            json.dump({"stocks": stocks}, f, indent=2)

    def manage_stocks_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Manage Watchlist")
        popup.geometry("400x250")
        popup.transient(self.root)

        entry_var = tk.StringVar()
        entry = ttk.Entry(popup, textvariable=entry_var, width=30)
        entry.pack(pady=10)

        listbox = tk.Listbox(popup)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Populate list
        stocks = self._get_stocks()
        for stock in stocks:
            listbox.insert(tk.END, stock)

        def add():
            val = entry_var.get().strip().upper()
            if val and val not in stocks:
                stocks.append(val)
                listbox.insert(tk.END, val)
                entry_var.set("")

        def remove():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                del stocks[index]
                listbox.delete(index)

        def save_and_close():
            self._save_stocks(stocks)
            self.load_watchlist()
            popup.destroy()

        # Buttons
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="➕ Add", command=add).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="➖ Remove", command=remove).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✅ Save", command=save_and_close).pack(side=tk.LEFT, padx=5)

    def suggest_trade(self):
        symbol = self.symbol_var.get().strip()
        if not symbol:
            messagebox.showwarning("Missing", "Please select a stock symbol")
            return
        try:
            predicted = predict_next_close(symbol)
            last_close = self.get_last_close(symbol)
            response = suggest_trade(symbol, last_close)
            response += f"\n\n🧠 Predicted Close: ₹{predicted:.2f}"
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, response)
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"❌ Error: {e}")

    def get_last_close(self, symbol):
        with open(f"stock_history/{symbol}.json", "r") as f:
            data = json.load(f)
        last_day = sorted(data.keys())[-1]
        return float(data[last_day]["close"])


    def start_ollama(self):
        try:
            subprocess.Popen(["ollama", "serve"])
            messagebox.showinfo("🧠 Ollama Started", "Ollama server is running in background.")
        except Exception as e:
            messagebox.showerror("❌ Ollama Error", str(e))

    def download_history(self):
        try:
            subprocess.run(["python", "update_history.py"], check=True)
            messagebox.showinfo("Success", "Downloaded stock history.")
        except Exception as e:
            messagebox.showerror("Download Failed", str(e))

    def train_model(self):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ml.train_lstm_model"],
                capture_output=True,
                text=True,
                check=True
            )
            messagebox.showinfo("✅ Training Complete", result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("❌ Training Failed", e.stderr or e.stdout)
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = StockLLMAssistantApp(root)
    root.mainloop()
