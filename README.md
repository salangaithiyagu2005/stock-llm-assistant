# Stock LLM Assistant

A fully local, free stock trading assistant using Ollama and Tkinter.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/stock-llm-assistant.git
cd stock-llm-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Features

- Suggests trades using LLM (llama3.2 in Ollama)
- Remembers past trades
- Uses yfinance + Moneycontrol
- Works entirely offline
