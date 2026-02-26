# 📈 Stock Backtesting Tool

A Python-based stock backtesting engine that simulates a **Moving Average Crossover** trading strategy on historical price data and compares it against a buy-and-hold benchmark. Features both a terminal interface and an interactive Streamlit web dashboard.

---

## Features

- Downloads live historical data via **yfinance** (no API key needed)
- Implements the **Golden Cross / Death Cross** strategy (short MA vs long MA)
- Tracks portfolio value, trade log, win rate, and max drawdown
- Interactive **Streamlit web dashboard** with live controls
- Generates a **3-panel matplotlib chart** with dark theme:
  - Price + moving averages + buy/sell signals
  - Portfolio value vs buy-and-hold benchmark
  - Drawdown over time

---

## Web Dashboard

Run the interactive dashboard in your browser:
```bash
streamlit run app.py
```

The dashboard lets you:
- Enter any ticker symbol (AAPL, TSLA, MSFT, etc.)
- Set a custom date range and starting capital
- Adjust the short and long MA windows with sliders
- View live performance metrics and charts
- Browse the full trade log in an interactive table

---

## Terminal Usage
```bash
python main.py
```

Configure settings at the top of `main.py`:
```python
TICKER       = "AAPL"       # Any valid Yahoo Finance ticker
START_DATE   = "2020-01-01"
END_DATE     = "2024-12-31"
INITIAL_CASH = 10_000       # Starting portfolio in USD
SHORT_WINDOW = 20           # Fast moving average (days)
LONG_WINDOW  = 50           # Slow moving average (days)
```

---

## Setup
```bash
# Clone the repo
git clone https://github.com/ericcai903/stock-backtester.git
cd stock-backtester

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

---

## How the Strategy Works

| Signal | Condition |
|--------|-----------|
| **BUY** | Short MA crosses **above** Long MA (Golden Cross) |
| **SELL** | Short MA crosses **below** Long MA (Death Cross) |

The backtester simulates going **all-in on each buy** and **fully exiting on each sell** (no partial positions). This keeps the logic simple and easy to reason about.

---

## Project Structure
```
stock-backtester/
├── app.py           # Streamlit web dashboard
├── main.py          # Terminal entry point
├── backtester.py    # Core simulation engine
├── strategy.py      # MA Crossover signal generation
├── plot.py          # Matplotlib visualizations
├── requirements.txt
└── README.md
```

---

## Dependencies

- `yfinance` — historical stock data
- `pandas` — data manipulation
- `matplotlib` — charting
- `streamlit` — web dashboard