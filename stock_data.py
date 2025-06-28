import yfinance as yf
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import feedparser
import re
import urllib.parse

def get_price(symbol: str) -> float:
    data = yf.Ticker(symbol)
    hist = data.history(period="1d")
    return round(hist['Close'].iloc[-1], 2) if not hist.empty else None

def get_moneycontrol_news(symbol: str, days: int = 90) -> list:
    """
    Download news headlines for the last `days` days for the given symbol from Moneycontrol.
    Returns a list of dicts: [{"date": ..., "headline": ...}, ...]
    """
    url = f"https://www.moneycontrol.com/india/stockpricequote/{symbol.lower()}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.content, 'html.parser')
    news_items = []
    # This selector and date extraction may need adjustment if Moneycontrol changes layout
    for card in soup.select('.card'):
        title = card.select_one('.card-title')
        date_tag = card.select_one('.card-date, .card-subtitle')
        if title:
            headline = title.text.strip()
            # Try to extract date, fallback to today
            if date_tag and date_tag.text.strip():
                date_str = date_tag.text.strip()
                try:
                    # Try to parse date (adjust format as needed)
                    date = datetime.strptime(date_str, "%d %b %Y")
                except Exception:
                    date = datetime.today()
            else:
                date = datetime.today()
            # Only include news within the last `days`
            if (datetime.today() - date).days <= days:
                news_items.append({"date": date.strftime("%Y-%m-%d"), "headline": headline})
    return news_items

def get_yahoo_news(symbol: str, days: int = 90) -> list:
    """
    Fetch news headlines for the last `days` days for the given symbol from Yahoo Finance using yfinance.
    Returns a list of dicts: [{"date": ..., "headline": ...}, ...]
    """
    ticker = yf.Ticker(symbol)
    news_items = []
    try:
        news = ticker.news
        cutoff = datetime.now() - timedelta(days=days)
        for item in news:
            # Yahoo news items have 'title' and 'providerPublishTime' (unix timestamp)
            title = item.get('title')
            ts = item.get('providerPublishTime')
            if title and ts:
                date = datetime.fromtimestamp(ts)
                if date >= cutoff:
                    news_items.append({"date": date.strftime("%Y-%m-%d"), "headline": title})
    except Exception as e:
        print(f"Failed to fetch Yahoo news for {symbol}: {e}")
    return news_items

def get_google_news(symbol: str, days: int = 90) -> list:
    """
    Fetch news headlines for the last `days` days for the given symbol from Google News RSS.
    Returns a list of dicts: [{"date": ..., "headline": ...}, ...]
    """
    query = symbol.replace('.NS', '') + ' stock'
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}+when:90d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    news_items = []
    cutoff = datetime.now() - timedelta(days=days)
    for entry in feed.entries:
        title = entry.title
        # Try to parse date from published_parsed
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            date = datetime(*entry.published_parsed[:6])
        else:
            date = datetime.now()
        if date >= cutoff:
            # Remove HTML tags from title if any
            clean_title = re.sub('<.*?>', '', title)
            news_items.append({"date": date.strftime("%Y-%m-%d"), "headline": clean_title})
    return news_items

def download_all_news(watchlist_path='data/watchlist.json', news_path='data/news.json', days=90):
    """
    Download news for all stocks in the watchlist and save to news_path using Google News RSS.
    """
    if not os.path.exists(watchlist_path):
        print(f"Watchlist not found: {watchlist_path}")
        return
    with open(watchlist_path, 'r') as f:
        stocks = json.load(f).get('stocks', [])
    all_news = {}
    for symbol in stocks:
        print(f"Fetching Google News for {symbol}...")
        try:
            all_news[symbol] = get_google_news(symbol, days)
        except Exception as e:
            print(f"Failed to fetch news for {symbol}: {e}")
            all_news[symbol] = []
    with open(news_path, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, indent=2, ensure_ascii=False)
    print(f"News saved to {news_path}")
