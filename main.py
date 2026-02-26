"""
Stock Backtesting Tool — Moving Average Crossover Strategy
Run: python main.py
"""

from backtester import Backtester
from strategy import MovingAverageCrossover
from plot import plot_results

# ── Configuration ────────────────────────────────────────────────────────────
TICKER       = "AAPL"          # Stock symbol to backtest
START_DATE   = "2020-01-01"
END_DATE     = "2024-12-31"
INITIAL_CASH = 10_000          # Starting portfolio value in USD
SHORT_WINDOW = 20              # Fast moving average (days)
LONG_WINDOW  = 50              # Slow moving average (days)
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*55}")
    print(f"  Stock Backtester — Moving Average Crossover")
    print(f"{'='*55}")
    print(f"  Ticker     : {TICKER}")
    print(f"  Period     : {START_DATE} → {END_DATE}")
    print(f"  MA Windows : {SHORT_WINDOW}-day / {LONG_WINDOW}-day")
    print(f"  Capital    : ${INITIAL_CASH:,.2f}")
    print(f"{'='*55}\n")

    # 1. Define strategy
    strategy = MovingAverageCrossover(short_window=SHORT_WINDOW, long_window=LONG_WINDOW)

    # 2. Run backtest
    bt = Backtester(ticker=TICKER, start=START_DATE, end=END_DATE, initial_cash=INITIAL_CASH)
    results = bt.run(strategy)

    # 3. Print summary
    bt.print_summary(results)

    # 4. Plot
    plot_results(results, ticker=TICKER, short_window=SHORT_WINDOW, long_window=LONG_WINDOW)


if __name__ == "__main__":
    main()
