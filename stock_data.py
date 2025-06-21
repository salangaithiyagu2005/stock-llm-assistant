import yfinance as yf
import requests
from bs4 import BeautifulSoup

def get_price(symbol: str) -> float:
    data = yf.Ticker(symbol)
    hist = data.history(period="1d")
    return round(hist['Close'].iloc[-1], 2) if not hist.empty else None

def get_moneycontrol_news(symbol: str) -> list:
    url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol.lower()}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    headlines = soup.select('.card .card-title')
    return [h.text.strip() for h in headlines[:3]]
