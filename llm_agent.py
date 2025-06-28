import datetime
from model_context_provider import get_trade_context, get_news_summary
from ml.predict import predict_next_close, predict_multi, get_technicals
from llm_client import ask_llm_sync  # use your own file/module here

def suggest_trade(symbol: str, last_close: float) -> str:
    try:
        predicted_price = predict_next_close(symbol)
        predicted_week = predict_multi(symbol, days_ahead=5)
        predicted_month = predict_multi(symbol, days_ahead=20)
        technicals = get_technicals(symbol)
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
Predicted Next Week Close: ₹{predicted_week:.2f}
Predicted End-of-Month Close: ₹{predicted_month:.2f}

Technical Indicators:
- RSI: {technicals['RSI']}
- 20-day MA: {technicals['MA20']}
- 50-day MA: {technicals['MA50']}
- Support: {technicals['Support']}
- Resistance: {technicals['Resistance']}

Recent News:
{news}

Your Past Trades:
{past_trades}

---
INSTRUCTIONS:
You are advising a swing/position trader who is NOT a daily trader and prefers to hold and average down rather than exit quickly. Only recommend 'Exit' in extreme or long-term negative scenarios. If the prediction is negative, suggest if and how to average down, and under what conditions to consider exiting. Focus on patient, long-term strategies.

1. Analyze the above data and provide your recommendation in the following format:

Action: <Buy/Hold/Average/Exit> (first line, single word)
Confidence: <0-100> (second line, integer only)
Rationale: (2-3 sentences, concise, actionable, and specific for a non-daily trader)

2. Then, provide a summary table with these columns: Factor | Value | Impact (Positive/Negative/Neutral)
   - Include: Last Close, Predicted Next Close, Predicted Next Week, Predicted Month, RSI, MA20, MA50, Support, Resistance, Recent News Sentiment, Trade History Summary

3. Be direct, avoid generic disclaimers, and focus on actionable advice for a patient, non-daily trader.
"""

    # 🔍 DEBUG print before sending to LLM
    print("🧠 Sending prompt to LLM:\n", prompt)
    with open("llm_prompt_debug.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    try:
        response = ask_llm_sync(prompt)
        print("🤖 LLM Response:\n", response)
        with open("llm_response_debug.txt", "w", encoding="utf-8") as f:
            f.write(response)
        return response
    except Exception as e:
        return f"❌ LLM Error: {e}"
