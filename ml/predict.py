import os
import json
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

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

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    if not symbol:
        print("Usage: python predict.py <SYMBOL>")
    else:
        price = predict_next_close(symbol)
        print(f"📈 Predicted next close for {symbol}: ₹{price:.2f}")
