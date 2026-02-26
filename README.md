<<<<<<< HEAD
# 📈 Stock Backtesting Tool

A Python-based stock backtesting engine that simulates a **Moving Average Crossover** trading strategy on historical price data and compares it against a buy-and-hold benchmark.

---

## Features

- Downloads live historical data via **yfinance** (no API key needed)
- Implements the **Golden Cross / Death Cross** strategy (short MA vs long MA)
- Tracks portfolio value, trade log, win rate, and max drawdown
- Generates a **3-panel matplotlib chart** with dark theme:
  - Price + moving averages + buy/sell signals
  - Portfolio value vs buy-and-hold benchmark
  - Drawdown over time

---

## Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/stock-backtester.git
cd stock-backtester

# Install dependencies
pip install -r requirements.txt

# Run the backtest
python main.py
```

---

## Configuration

Edit the top of `main.py` to change any parameter:

```python
TICKER       = "AAPL"       # Any valid Yahoo Finance ticker
START_DATE   = "2020-01-01"
END_DATE     = "2024-12-31"
INITIAL_CASH = 10_000       # Starting portfolio in USD
SHORT_WINDOW = 20           # Fast moving average (days)
LONG_WINDOW  = 50           # Slow moving average (days)
```

---

## How the Strategy Works

| Signal | Condition |
|--------|-----------|
| **BUY** | Short MA crosses **above** Long MA (Golden Cross) |
| **SELL** | Short MA crosses **below** Long MA (Death Cross) |

The backtester simulates going **all-in on each buy** and **fully exiting on each sell** (no partial positions). This keeps the logic simple and easy to reason about.

---

## Example Output

```
=====================================================
  Stock Backtester — Moving Average Crossover
=====================================================
  Ticker     : AAPL
  Period     : 2020-01-01 → 2024-12-31
  MA Windows : 20-day / 50-day
  Capital    : $10,000.00
=====================================================

PERFORMANCE SUMMARY
----------------------------------------
  Starting Capital  :  $10,000.00
  Final Value       :  $18,243.17
  Strategy Return   :     +82.43%
  Buy & Hold Return :    +291.12%
  Max Drawdown      :     -18.34%
  Total Trades      :          14
  Win Rate          :      57.1%
----------------------------------------
```

---

## Project Structure

```
stock-backtester/
├── main.py          # Entry point & configuration
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

