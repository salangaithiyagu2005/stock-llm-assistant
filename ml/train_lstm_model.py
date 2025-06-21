import os
import json
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from prepare_data import load_stock_data

def train_model(symbol: str, window=60):
    print(f"\n🔁 Training model for {symbol}...")

    # Load data and scale
    X, y, scaler = load_stock_data(symbol, window=window)

    # Define LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(50))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(X, y, epochs=20, batch_size=32, verbose=0)

    # Save model and scaler
    model_path = f"ml/{symbol.replace('.', '_')}_lstm_model.h5"
    scaler_path = f"ml/{symbol.replace('.', '_')}_scaler.save"

    model.save(model_path)
    joblib.dump(scaler, scaler_path)

    print(f"✅ Model saved to {model_path}")
    print(f"✅ Scaler saved to {scaler_path}")

if __name__ == "__main__":
    with open("watchlist.json", "r") as f:
        symbols = json.load(f)["stocks"]

    for symbol in symbols:
        try:
            train_model(symbol)
        except Exception as e:
            print(f"❌ Failed to train {symbol}: {e}")
