# app.py
# POP Backtester - Streamlit Dashboard (mobile friendly)
# - Works with manual filters (sliders, inputs)
# - Optional GPT helper if you add OPENAI_API_KEY in Streamlit secrets

import os
import json
import time
import pandas as pd
import numpy as np
import streamlit as st

# ===============================
# Placeholder POP backtester
# Replace this with your real backtester logic
# ===============================
def demo_run_backtest(params: dict) -> dict:
    np.random.seed(42)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=60)
    equity = pd.Series(
        10000 + np.cumsum(np.random.randn(len(dates)) * 50),
        index=dates,
        name="Equity"
    )
    trades = pd.DataFrame({
        "Date": np.random.choice(dates, size=15, replace=False),
        "Ticker": np.random.choice(["AAPL","TSLA","NVDA","PLTR","AMD","SIDU","BURU"], size=15),
        "Entry": np.round(np.random.uniform(1, 100, size=15), 2),
        "Exit":  np.round(np.random.uniform(1, 110, size=15), 2),
        "PnL%":  np.round(np.random.uniform(-15, 25, size=15), 2)
    }).sort_values("Date")
    metrics = {
        "Total Return %": round((equity.iloc[-1] / equity.iloc[0] - 1) * 100, 2),
        "Win Rate %": round((trades["PnL%"] > 0).mean() * 100, 1),
        "Avg Trade %": round(trades["PnL%"].mean(), 2),
        "Max Drawdown %": round((equity.cummax() - equity).max() / equity.cummax().max() * 100, 2),
        "Trades": int(len(trades))
    }
    return {"trades": trades, "metrics": metrics, "equity": equity}

# ===============================
# Optional GPT helper
# ===============================
USE_GPT = False
try:
    from openai import OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        client = OpenAI()
        USE_GPT = True
except Exception:
    client = None
    USE_GPT = False

SYSTEM_PROMPT = """
You translate plain English into a JSON object of POP backtest parameters.
Fields: GapPct (number), MinRVOL (number), MaxFloat (millions), PriceMax (number),
DateStart (YYYY-MM-DD), DateEnd (YYYY-MM-DD).
Only output valid JSON with those keys (omit if not specified).
"""

def gpt_to_params(nl: str) -> dict:
    if not USE_GPT or client is None:
        return {}
    try:
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": nl}
            ],
            temperature=0.1
        )
        text = chat.choices[0].message.content
        return json.loads(text)
    except Exception as e:
        st.warning(f"GPT error: {e}")
        return {}
