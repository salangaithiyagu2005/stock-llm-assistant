import datetime
from model_context_provider import get_trade_context, get_news_summary
from ml.predict import predict_next_close
from llm_client import ask_llm_sync  # use your own file/module here

def suggest_trade(symbol: str, last_close: float) -> str:
    try:
        predicted_price = predict_next_close(symbol)
    except Exception as e:
        return f"⚠️ Prediction error: {e}"

    past_trades = get_trade_context()
    news = get_news_summary(symbol)
    today = datetime.date.today().isoformat()

    prompt = f"""
Date: {today}
Stock: {symbol}
Last Close: ₹{last_close}
Predicted Next Close (LSTM): ₹{predicted_price:.2f}

Recent News:
{news}

Your Past Trades:
{past_trades}

What action should I take? (Buy / Hold / Exit)
Explain briefly in simple language.
"""

    # 🔍 DEBUG print before sending to LLM
    print("🧠 Sending prompt to LLM:\n", prompt)

    try:
        response = ask_llm_sync(prompt)
        print("🤖 LLM Response:\n", response)
        return response
    except Exception as e:
        return f"❌ LLM Error: {e}"
