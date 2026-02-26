"""
strategy.py — Trading strategy definitions.

A strategy receives a DataFrame of price data and returns a Series of signals:
    +1  = BUY
     0  = HOLD
    -1  = SELL
"""

import pandas as pd


class MovingAverageCrossover:
    """
    Golden Cross / Death Cross strategy.

    BUY  when the short-term MA crosses ABOVE the long-term MA.
    SELL when the short-term MA crosses BELOW the long-term MA.
    """

    def __init__(self, short_window: int = 20, long_window: int = 50):
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        self.short_window = short_window
        self.long_window  = long_window
        self.name = f"MA Crossover ({short_window}/{long_window})"

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parameters
        ----------
        df : DataFrame with at least a 'Close' column, DatetimeIndex.

        Returns
        -------
        df : original DataFrame with added columns:
               short_ma, long_ma, signal, position
        """
        data = df.copy()

        # Compute moving averages
        data["short_ma"] = data["Close"].rolling(window=self.short_window).mean()
        data["long_ma"]  = data["Close"].rolling(window=self.long_window).mean()

        # Raw signal: 1 when short > long, 0 otherwise
        data["signal"] = 0
        data.loc[data["short_ma"] > data["long_ma"], "signal"] = 1

        # Position = difference of signal to detect crossover events
        # +1 → just crossed up (BUY), -1 → just crossed down (SELL), 0 → no change
        data["position"] = data["signal"].diff()

        return data
