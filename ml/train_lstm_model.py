import os
import json
import joblib
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

# Import from the ml package
from ml.prepare_data import load_stock_data

def train_model(symbol: str, window=60, epochs=20, batch_size=32):
    print(f"\n🔁 Training model for {symbol}...")

    # Load data and scaler
    try:
        X, y, scaler = load_stock_data(symbol, window=window)
    except Exception as e:
        print(f"❌ Failed to load data for {symbol}: {e}")
        return

    if X.size == 0:
        print(f"❌ Not enough data to train for {symbol}.")
        return

    # Define LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(50))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mean_squared_error")

    # Train
    model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    # Prepare directories
    trained_dir = os.path.join(os.path.dirname(__file__), "trained_models")
    os.makedirs(trained_dir, exist_ok=True)

    # File paths
    safe_name = symbol.replace(".", "_").replace("/", "_")
    model_path = os.path.join(trained_dir, f"{safe_name}_lstm_model.h5")
    scaler_path = os.path.join(trained_dir, f"{safe_name}_scaler.save")

    # Save model and scaler
    try:
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        print(f"✅ Model saved to {model_path}")
        print(f"✅ Scaler saved to {scaler_path}")
    except Exception as e:
        print(f"❌ Failed to save model/scaler for {symbol}: {e}")

if __name__ == "__main__":
    # Load watchlist.json from project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    watchlist_path = os.path.join(project_root, "watchlist.json")
    if not os.path.exists(watchlist_path):
        print(f"❌ watchlist.json not found at {watchlist_path}")
    else:
        with open(watchlist_path, "r") as f:
            try:
                symbols = json.load(f).get("stocks", [])
            except Exception as e:
                print(f"❌ Failed to parse watchlist.json: {e}")
                symbols = []
        if not symbols:
            print("❌ No symbols in watchlist.json to train.")
        else:
            for symbol in symbols:
                train_model(symbol, window=60)
