import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def load_stock_data_for_prediction(symbol, window=60):
    path = f"stock_history/{symbol}.json"
    with open(path, "r") as f:
        data = json.load(f)

    df = list(data.items())[-window:]
    rows = []

    for _, values in df:
        rows.append([
            values["open"],
            values["high"],
            values["low"],
            values["close"],
            values["volume"]
        ])

    return np.array(rows)