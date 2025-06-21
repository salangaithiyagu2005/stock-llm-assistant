import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def load_stock_data(symbol: str, window: int = 60):
    path = f"stock_history/{symbol}.json"
    with open(path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data).T.astype(float)
    df = df[["open", "high", "low", "close", "volume"]]

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)

    X, y = [], []
    for i in range(window, len(df)):
        X.append(scaled[i - window:i])
        y.append(scaled[i][3])  # Close price

    return np.array(X), np.array(y), scaler

def load_stock_data_for_prediction(symbol: str, window: int = 60):
    path = f"stock_history/{symbol}.json"
    with open(path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data).T.astype(float).tail(window)
    df = df[["open", "high", "low", "close", "volume"]]

    return df.values
