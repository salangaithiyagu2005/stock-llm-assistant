import os
import json
import joblib
import numpy as np
from tensorflow.keras.models import load_model
from prepare_data import load_stock_data_for_prediction

def predict_next_close(symbol: str, window: int = 60) -> float:
    import pandas as pd
    import numpy as np
    import json
    import joblib
    from tensorflow.keras.models import load_model

    print(f"\n🔮 Predicting next close for {symbol}...")

    # Load data
    with open(f"stock_history/{symbol}.json", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data).T.astype(float).tail(window)
    if len(df) < window:
        raise ValueError("Not enough data for prediction window")

    model_path = f"ml/{symbol.replace('.', '_')}_lstm_model.h5"
    scaler_path = f"ml/{symbol.replace('.', '_')}_scaler.save"
    model = load_model(model_path)
    scaler = joblib.load(scaler_path)

    # Scale and reshape input
    scaled_input = scaler.transform(df.values)
    X = np.reshape(scaled_input, (1, scaled_input.shape[0], scaled_input.shape[1]))

    # Predict (returns scaled close price)
    scaled_pred = model.predict(X, verbose=0)

    # Create dummy row to inverse scale (padding with 0s except for close)
    dummy_row = np.zeros((1, df.shape[1]))
    dummy_row[0][3] = scaled_pred  # 'close' is at index 3

    # Inverse transform to get original price scale
    unscaled_row = scaler.inverse_transform(dummy_row)
    predicted_close = unscaled_row[0][3]

    return float(predicted_close)


if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "TCS.NS"

    try:
        price = predict_next_close(symbol)
        print(f"📈 Predicted next close price for {symbol}: ₹{price:.2f}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
