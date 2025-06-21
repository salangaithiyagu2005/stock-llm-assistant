# 📈 Stock LLM Assistant – Local + LSTM AI

A full offline, private stock assistant that:
- ✅ Uses **Ollama LLM** (e.g., `llama3.2`)
- ✅ Downloads and stores **10 years of stock history**
- ✅ Trains a **deep learning LSTM model** on OHLCV data (Open, High, Low, Close, Volume)
- ✅ Suggests trades and predicts next close price
- ✅ Fully customizable, runs on your laptop

---

## 📂 Folder Structure

```
.
├── app.py
├── llm_agent.py
├── model_context_provider.py
├── stock_data.py
├── stock_history.py
├── update_history.py
├── watchlist.json
├── requirements.txt
├── stock_history/
└── ml/
    ├── prepare_data.py
    ├── train_lstm_model.py
    └── predict.py
```

---

## 🧪 Requirements

- Python **3.11** (⛔ NOT 3.12+)
- Ollama installed (for local LLMs)
- Windows or Git Bash

---

## ✅ 1. Create and Activate Virtual Environment

### 💻 On Windows CMD:

```cmd
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
venv\Scripts\activate
```

### 🐧 On Git Bash / Linux / WSL:

```bash
/c/Users/YourName/AppData/Local/Programs/Python/Python311/python -m venv venv
source venv/Scripts/activate
```

---

## 📦 2. Install Requirements

```bash
pip install -r requirements.txt
```

> ✅ If TensorFlow fails, install it manually:
```bash
pip install tensorflow==2.15.0
```

---

## 📋 3. Define Watchlist

Create/edit `watchlist.json`:

```json
{
  "stocks": ["TCS.NS", "RELIANCE.NS", "INFY.NS"]
}
```

---

## 📥 4. Download 10-Year History

```bash
python update_history.py
```

> Updates all stocks in `stock_history/` as JSON

---

## 🧠 5. Train LSTM Model (per stock)

```bash
python ml/train_lstm_model.py
```

This trains a deep learning model using last **60 days** of:
- Open, High, Low, Close, Volume

Model is saved to:
```
ml/TCS_NS_lstm_model.h5
ml/TCS_NS_scaler.save
```

---

## 🔮 6. Predict Next Day Close

```bash
python ml/predict.py
```

Output:
```
Predicted next close price for TCS.NS: Rs.3854.12
```

---

## 🧠 7. Run GUI with LLM Suggestions

```bash
python app.py
```

- Click **🧠 Suggest Trade** to ask your LLM to analyze price/news/history
- Click **✅ Confirm Buy** to log trades into your personal context

---

## 🤖 Local LLM (Ollama Setup)

Make sure you’ve installed [Ollama](https://ollama.com) and downloaded a model:

```bash
ollama run llama3.2
ollama serve
```

You can list models:
```bash
ollama list
```

---

## 🔁 To Do / Expand

- [ ] Add chart display
- [ ] Backtesting support
- [ ] Fine-tune custom model using your JSON history
- [ ] Signal generation (Buy/Sell alert triggers)

---

## 💬 Need Help?

Paste your Python version and any error for quick help.