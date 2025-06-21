import tkinter as tk
from tkinter import messagebox
from stock_data import get_price, get_moneycontrol_news
from model_context_provider import ModelContextProvider
from llm_agent import ask_llm

mcp = ModelContextProvider()
SYMBOL = "TCS.NS"
QUANTITY = 1

def suggest_trade():
    price = get_price(SYMBOL)
    news = get_moneycontrol_news(SYMBOL.split('.')[0])
    ctx = mcp.get_context_summary()
    prompt = (
        f"Past trades:\n{ctx}\n\n"
        f"Today: {SYMBOL}, current price: ₹{price}, news: {news}\n"
        "Suggest: BUY / HOLD / EXIT with reasoning."
    )
    result = ask_llm(prompt)
    txt.delete("1.0", tk.END)
    txt.insert(tk.END, result)

def confirm_buy():
    price = get_price(SYMBOL)
    news = get_moneycontrol_news(SYMBOL.split('.')[0])
    mcp.add_trade(SYMBOL, "BUY", price, QUANTITY, news=news)
    messagebox.showinfo("Trade Confirmed", f"BUY {SYMBOL} @ ₹{price} logged.")

app = tk.Tk()
app.title("Stock LLM Assistant")
app.geometry("600x400")

tk.Label(app, text="Stock LLM Assistant (Free & Local)", font=("Arial", 16)).pack(pady=10)
tk.Button(app, text="🧠 Suggest Trade", command=suggest_trade).pack(pady=5)
txt = tk.Text(app, height=10, width=70)
txt.pack(pady=10)
tk.Button(app, text="✅ Confirm Buy", command=confirm_buy).pack(pady=5)

app.mainloop()
