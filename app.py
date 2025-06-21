import tkinter as tk
from tkinter import ttk, messagebox
from llm_agent import suggest_trade
from ml.predict import predict_next_close
import json


class StockLLMAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📈 Stock LLM Assistant")
        self.root.geometry("800x500")
        self.root.resizable(True, True)

        self.symbol_var = tk.StringVar()
        self.result_text = tk.Text(root, wrap=tk.WORD, height=20, width=100)
        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Stock Symbol:").pack(side=tk.LEFT)
        ttk.Entry(frame, textvariable=self.symbol_var, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="🧠 Suggest Trade", command=self.suggest_trade).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="❌ Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def suggest_trade(self):
        symbol = self.symbol_var.get().strip()
        if not symbol:
            messagebox.showwarning("Missing", "Please enter a stock symbol (e.g., TCS.NS)")
            return

        try:
            predicted = predict_next_close(symbol)
            last_close = self.get_last_close(symbol)
            prompt = suggest_trade(symbol, last_close)
            prompt += f"\n\n🧠 Predicted Close: ₹{predicted:.2f}"

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, prompt)
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"❌ Error: {e}")

    def get_last_close(self, symbol):
        with open(f"stock_history/{symbol}.json", "r") as f:
            data = json.load(f)
        last_day = sorted(data.keys())[-1]
        return float(data[last_day]["close"])

if __name__ == "__main__":
    root = tk.Tk()
    app = StockLLMAssistantApp(root)
    root.mainloop()
