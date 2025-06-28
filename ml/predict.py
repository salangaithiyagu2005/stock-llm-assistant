import os
import json
import joblib
import numpy as np
import pandas as pd
import pandas_ta as ta
from tensorflow.keras.models import load_model
import datetime

def predict_next_close(symbol: str, window: int = 60) -> float:
    print(f"\n🔮 Predicting next close for {symbol}...")

    safe_name = symbol.replace(".", "_").replace("/", "_")
    model_path = os.path.join("ml", "trained_models", f"{safe_name}_lstm_model.h5")
    scaler_path = os.path.join("ml", "trained_models", f"{safe_name}_scaler.save")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Model or scaler not found for {symbol} at {model_path} / {scaler_path}")

    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    # Load last `window` days from stock_history
    path = os.path.join("stock_history", f"{symbol}.json")
    with open(path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data).T.astype(float).sort_index().tail(window)
    if len(df) < window:
        raise ValueError(f"Not enough data ({len(df)}) for prediction window {window}")

    arr = df[["open", "high", "low", "close", "volume"]].values
    scaled_input = scaler.transform(arr)
    X = np.reshape(scaled_input, (1, scaled_input.shape[0], scaled_input.shape[1]))

    scaled_pred = model.predict(X, verbose=0)
    # Inverse-scale only the close value
    dummy = np.zeros((1, arr.shape[1]))
    dummy[0][3] = scaled_pred  # index 3 is 'close'
    unscaled = scaler.inverse_transform(dummy)
    predicted_close = unscaled[0][3]

    return float(predicted_close)

def predict_multi(symbol: str, days_ahead: int = 5, window: int = 60) -> float:
    """
    Predict the close price N days ahead using recursive LSTM prediction.
    """
    safe_name = symbol.replace(".", "_").replace("/", "_")
    model_path = os.path.join("ml", "trained_models", f"{safe_name}_lstm_model.h5")
    scaler_path = os.path.join("ml", "trained_models", f"{safe_name}_scaler.save")
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Model or scaler not found for {symbol} at {model_path} / {scaler_path}")
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)
    path = os.path.join("stock_history", f"{symbol}.json")
    with open(path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data).T.astype(float).sort_index()
    arr = df[["open", "high", "low", "close", "volume"]].values
    window_data = arr[-window:].copy()
    for _ in range(days_ahead):
        scaled_input = scaler.transform(window_data)
        X = np.reshape(scaled_input, (1, scaled_input.shape[0], scaled_input.shape[1]))
        scaled_pred = model.predict(X, verbose=0)
        dummy = np.zeros((1, arr.shape[1]))
        dummy[0][3] = scaled_pred  # index 3 is 'close'
        unscaled = scaler.inverse_transform(dummy)
        next_close = unscaled[0][3]
        # Roll window: add predicted close, keep other values same as last day
        last_row = window_data[-1].copy()
        last_row[3] = next_close
        window_data = np.vstack([window_data[1:], last_row])
    return float(next_close)

def get_technicals(symbol: str, window: int = 60) -> dict:
    """
    Calculate RSI, 20/50-day moving averages, support/resistance for the stock.
    """
    path = os.path.join("stock_history", f"{symbol}.json")
    with open(path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data).T.astype(float).sort_index()
    close = df["close"]
    rsi = ta.rsi(close, length=14).iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    support = close.rolling(20).min().iloc[-1]
    resistance = close.rolling(20).max().iloc[-1]
    return {
        "RSI": round(rsi, 2) if not pd.isna(rsi) else None,
        "MA20": round(ma20, 2) if not pd.isna(ma20) else None,
        "MA50": round(ma50, 2) if not pd.isna(ma50) else None,
        "Support": round(support, 2) if not pd.isna(support) else None,
        "Resistance": round(resistance, 2) if not pd.isna(resistance) else None,
    }

def save_prediction(symbol, window, price, week, month, technicals):
    today = datetime.date.today().isoformat()
    out = {
        "date": today,
        "symbol": symbol,
        "window": window,
        "predicted_next_close": price,
        "predicted_next_week": week,
        "predicted_month": month,
        "technicals": technicals
    }
    os.makedirs("predictions", exist_ok=True)
    fname = f"predictions/{symbol}_predictions.json"
    if os.path.exists(fname):
        with open(fname, "r") as f:
            all_preds = json.load(f)
    else:
        all_preds = []
    all_preds.append(out)
    with open(fname, "w") as f:
        json.dump(all_preds, f, indent=2)

def check_and_retrain(symbol, window):
    """
    Check yesterday's prediction vs actual, retrain if error is large.
    """
    import numpy as np
    fname = f"predictions/{symbol}_predictions.json"
    path = os.path.join("stock_history", f"{symbol}.json")
    if not os.path.exists(fname) or not os.path.exists(path):
        return
    with open(fname, "r") as f:
        preds = json.load(f)
    with open(path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data).T.astype(float).sort_index()
    # Find last prediction with a matching date in actuals
    for pred in reversed(preds):
        pred_date = pred["date"]
        if pred_date in df.index:
            actual = df.loc[pred_date]["close"]
            predicted = pred["predicted_next_close"]
            error = abs(actual - predicted)
            if error > max(2, 0.03 * actual):  # >₹2 or >3% error
                print(f"Retraining suggested: {pred_date} prediction error {error:.2f}")
                # Here you would call your training script, e.g.:
                # os.system(f"python -m ml.train_lstm_model {symbol} {window}")
            break

def log_llm_training_example(symbol, window, price, week, month, technicals, actual_close=None, action=None, rationale=None):
    """
    Log a training example for LLM fine-tuning. Includes prompt, actual result, and your action/rationale if available.
    """
    today = datetime.date.today().isoformat()
    prompt = f"Stock: {symbol}\nDate: {today}\nWindow: {window}\nPredicted Next Close: ₹{price:.2f}\nPredicted Next Week: ₹{week:.2f}\nPredicted Month: ₹{month:.2f}\nRSI: {technicals['RSI']}\nMA20: {technicals['MA20']}\nMA50: {technicals['MA50']}\nSupport: {technicals['Support']}\nResistance: {technicals['Resistance']}\n"
    if actual_close is not None:
        prompt += f"Actual Close: ₹{actual_close:.2f}\n"
    response = ""
    if action:
        response += f"Action: {action}\n"
    if rationale:
        response += f"Rationale: {rationale}\n"
    entry = {"prompt": prompt.strip(), "response": response.strip()}
    os.makedirs("llm_finetune_data", exist_ok=True)
    fname = f"llm_finetune_data/{symbol}_finetune.jsonl"
    with open(fname, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# --- Automated logging of actual close and retraining action ---
def log_actual_and_action(symbol, window):
    """
    After prediction, log the actual close and retraining suggestion for LLM fine-tuning.
    """
    # Load last prediction
    pred_file = f"predictions/{symbol}_predictions.json"
    if not os.path.exists(pred_file):
        return
    with open(pred_file, "r") as f:
        preds = json.load(f)
    if not preds:
        return
    last_pred = preds[-1]
    # Load actual close
    path = os.path.join("stock_history", f"{symbol}.json")
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data).T.astype(float).sort_index()
    pred_date = last_pred["date"]
    if pred_date in df.index:
        actual = df.loc[pred_date]["close"]
        predicted = last_pred["predicted_next_close"]
        error = abs(actual - predicted)
        retrain = error > max(2, 0.03 * actual)
        action = "Retrain" if retrain else "NoRetrain"
        rationale = f"Prediction error: {error:.2f} (actual: {actual:.2f}, predicted: {predicted:.2f})"
        log_llm_training_example(
            symbol, window, predicted, last_pred["predicted_next_week"], last_pred["predicted_month"],
            last_pred["technicals"], actual_close=actual, action=action, rationale=rationale
        )

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    window = 60  # Default window
    if len(sys.argv) > 2:
        try:
            window = int(sys.argv[2])
        except Exception:
            print("Invalid window size, using default 60.")
    if not symbol:
        print("Usage: python predict.py <SYMBOL> [WINDOW]")
    else:
        price = predict_next_close(symbol, window=window)
        week = predict_multi(symbol, days_ahead=5, window=window)
        month = predict_multi(symbol, days_ahead=20, window=window)
        technicals = get_technicals(symbol, window=window)
        print(f"\n📈 Predicted next close for {symbol} (window={window}): ₹{price:.2f}")
        print(f"📅 Predicted next week close: ₹{week:.2f}")
        print(f"📆 Predicted end-of-month close: ₹{month:.2f}")
        print(f"\nTechnical Indicators:")
        for k, v in technicals.items():
            print(f"  {k}: {v}")
        save_prediction(symbol, window, price, week, month, technicals)
        check_and_retrain(symbol, window)
        # Log for LLM fine-tuning (no actual/action/rationale yet)
        log_llm_training_example(symbol, window, price, week, month, technicals)
        # Automated: log actual close and retraining action for LLM
        log_actual_and_action(symbol, window)
