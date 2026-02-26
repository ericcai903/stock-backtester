"""
backtester.py — Core backtesting engine.

Downloads historical price data via yfinance and simulates trades
based on signals from a strategy object.
"""

import yfinance as yf
import pandas as pd


class Backtester:
    def __init__(self, ticker: str, start: str, end: str, initial_cash: float = 10_000):
        self.ticker       = ticker.upper()
        self.start        = start
        self.end          = end
        self.initial_cash = initial_cash

    # ── Data ─────────────────────────────────────────────────────────────────

    def _fetch_data(self) -> pd.DataFrame:
        print(f"  Downloading {self.ticker} data from Yahoo Finance…")
        df = yf.download(self.ticker, start=self.start, end=self.end, progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError(f"No data returned for ticker '{self.ticker}'. Check the symbol and date range.")
        # Flatten MultiIndex columns if present (yfinance ≥ 0.2.x)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        print(f"  {len(df)} trading days loaded ({self.start} → {self.end})\n")
        return df

    # ── Simulation ────────────────────────────────────────────────────────────

    def run(self, strategy) -> dict:
        """
        Simulate the strategy and return a results dict containing:
          - data        : annotated price DataFrame
          - trades      : list of trade dicts
          - portfolio   : daily portfolio value Series
          - buy_hold    : daily buy-and-hold value Series
          - metrics     : summary statistics dict
        """
        df = self._fetch_data()
        df = strategy.generate_signals(df)

        cash      = self.initial_cash
        shares    = 0
        trades    = []
        portfolio = []

        for date, row in df.iterrows():
            price = float(row["Close"])

            # BUY signal
            if row["position"] == 1 and cash > 0:
                shares = cash / price
                cash   = 0
                trades.append({"date": date, "type": "BUY", "price": price, "shares": shares})

            # SELL signal
            elif row["position"] == -1 and shares > 0:
                cash   = shares * price
                proceeds = cash
                trades.append({"date": date, "type": "SELL", "price": price, "shares": shares, "proceeds": proceeds})
                shares = 0

            # Daily portfolio value
            total = cash + shares * price
            portfolio.append({"date": date, "value": total})

        # Close any open position at the last price
        if shares > 0:
            last_price = float(df["Close"].iloc[-1])
            cash = shares * last_price
            shares = 0

        final_value = cash

        # Build time series
        portfolio_series = pd.DataFrame(portfolio).set_index("date")["value"]

        # Buy-and-hold benchmark
        first_price = float(df["Close"].dropna().iloc[0])
        shares_bh   = self.initial_cash / first_price
        buy_hold    = df["Close"] * shares_bh

        # ── Metrics ──────────────────────────────────────────────────────────
        strategy_return = (final_value - self.initial_cash) / self.initial_cash * 100
        bh_return       = (float(buy_hold.iloc[-1]) - self.initial_cash) / self.initial_cash * 100

        # Max drawdown
        rolling_max = portfolio_series.cummax()
        drawdown    = (portfolio_series - rolling_max) / rolling_max
        max_drawdown = float(drawdown.min()) * 100

        # Win rate
        sell_trades = [t for t in trades if t["type"] == "SELL"]
        buy_trades  = [t for t in trades if t["type"] == "BUY"]
        wins = 0
        for i, sell in enumerate(sell_trades):
            if i < len(buy_trades):
                if sell["price"] > buy_trades[i]["price"]:
                    wins += 1
        win_rate = (wins / len(sell_trades) * 100) if sell_trades else 0

        metrics = {
            "final_value"      : final_value,
            "strategy_return"  : strategy_return,
            "buy_hold_return"  : bh_return,
            "max_drawdown"     : max_drawdown,
            "total_trades"     : len(trades),
            "win_rate"         : win_rate,
            "num_buys"         : len(buy_trades),
            "num_sells"        : len(sell_trades),
        }

        return {
            "data"      : df,
            "trades"    : trades,
            "portfolio" : portfolio_series,
            "buy_hold"  : buy_hold,
            "metrics"   : metrics,
            "strategy"  : strategy,
        }

    # ── Output ────────────────────────────────────────────────────────────────

    def print_summary(self, results: dict):
        m = results["metrics"]
        print("PERFORMANCE SUMMARY")
        print("-" * 40)
        print(f"  Starting Capital  : ${self.initial_cash:>10,.2f}")
        print(f"  Final Value       : ${m['final_value']:>10,.2f}")
        print(f"  Strategy Return   : {m['strategy_return']:>+9.2f}%")
        print(f"  Buy & Hold Return : {m['buy_hold_return']:>+9.2f}%")
        print(f"  Max Drawdown      : {m['max_drawdown']:>9.2f}%")
        print(f"  Total Trades      : {m['total_trades']:>10}")
        print(f"  Win Rate          : {m['win_rate']:>9.1f}%")
        print("-" * 40)

        print("\nTRADE LOG")
        print("-" * 40)
        for t in results["trades"]:
            tag = "▲ BUY " if t["type"] == "BUY" else "▼ SELL"
            print(f"  {tag}  {t['date'].date()}  ${t['price']:>8.2f}  ({t['shares']:.4f} shares)")
        print()
