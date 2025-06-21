import os
import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def load_stock_data(symbol, window=60):
    file_path = os.path.join("stock_history", f"{symbol}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Stock history for {symbol} not found")

    with open(file_path, "r") as f:
        raw_data = json.load(f)

    data = list(raw_data.values())
    if len(data) <= window:
        return np.array([]), np.array([]), None

    features = ["open", "high", "low", "close", "volume"]
    dataset = np.array([[day[feat] for feat in features] for day in data], dtype=np.float32)

    scaler = MinMaxScaler()
    dataset_scaled = scaler.fit_transform(dataset)

    X, y = [], []
    for i in range(window, len(dataset_scaled)):
        X.append(dataset_scaled[i - window:i])
        y.append(dataset_scaled[i][3])  # Close price index = 3

    return np.array(X), np.array(y), scaler
