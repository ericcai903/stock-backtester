"""
plot.py — Visualization for backtest results using matplotlib.

Produces a 3-panel chart:
  1. Price + Moving Averages + Buy/Sell signals
  2. Portfolio Value vs Buy-and-Hold benchmark
  3. Drawdown over time
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def plot_results(results: dict, ticker: str, short_window: int, long_window: int):
    data      = results["data"]
    portfolio = results["portfolio"]
    buy_hold  = results["buy_hold"]
    trades    = results["trades"]
    metrics   = results["metrics"]

    buys  = [t for t in trades if t["type"] == "BUY"]
    sells = [t for t in trades if t["type"] == "SELL"]

    # ── Figure layout ─────────────────────────────────────────────────────────
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [3, 2, 1.5]})
    fig.suptitle(
        f"{ticker} — Moving Average Crossover Backtest  "
        f"({short_window}-day / {long_window}-day)",
        fontsize=14, fontweight="bold", y=0.98
    )
    fig.patch.set_facecolor("#0f1117")
    for ax in axes:
        ax.set_facecolor("#1a1d27")
        ax.tick_params(colors="#aaaaaa")
        ax.spines[:].set_color("#333344")
        ax.yaxis.label.set_color("#cccccc")
        ax.xaxis.label.set_color("#cccccc")
        ax.title.set_color("#eeeeee")

    # ── Panel 1: Price + MAs + signals ───────────────────────────────────────
    ax1 = axes[0]
    ax1.plot(data.index, data["Close"],    color="#4fc3f7", lw=1.2, label="Close Price", alpha=0.9)
    ax1.plot(data.index, data["short_ma"], color="#ffb74d", lw=1.4, label=f"{short_window}-day MA", linestyle="--")
    ax1.plot(data.index, data["long_ma"],  color="#ef5350", lw=1.4, label=f"{long_window}-day MA",  linestyle="--")

    # Buy markers
    for t in buys:
        ax1.axvline(t["date"], color="#00e676", alpha=0.15, lw=1)
        ax1.scatter(t["date"], t["price"], marker="^", color="#00e676", s=100, zorder=5)

    # Sell markers
    for t in sells:
        ax1.axvline(t["date"], color="#ff5252", alpha=0.15, lw=1)
        ax1.scatter(t["date"], t["price"], marker="v", color="#ff5252", s=100, zorder=5)

    # Legend entries for signals
    ax1.scatter([], [], marker="^", color="#00e676", s=80, label="BUY signal")
    ax1.scatter([], [], marker="v", color="#ff5252", s=80, label="SELL signal")

    ax1.set_title("Price Chart with Moving Averages & Trade Signals")
    ax1.set_ylabel("Price (USD)")
    ax1.legend(loc="upper left", framealpha=0.3, labelcolor="white", facecolor="#1a1d27")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha="right")

    # ── Panel 2: Portfolio vs Buy & Hold ──────────────────────────────────────
    ax2 = axes[1]
    ax2.plot(portfolio.index, portfolio.values, color="#ba68c8", lw=1.8,
             label=f"Strategy  ({metrics['strategy_return']:+.1f}%)")
    ax2.plot(buy_hold.index, buy_hold.values,   color="#4db6ac", lw=1.8,
             linestyle="--", label=f"Buy & Hold ({metrics['buy_hold_return']:+.1f}%)")
    ax2.axhline(y=portfolio.iloc[0], color="#555566", lw=1, linestyle=":")

    ax2.set_title("Portfolio Value vs. Buy & Hold Benchmark")
    ax2.set_ylabel("Portfolio Value (USD)")
    ax2.legend(loc="upper left", framealpha=0.3, labelcolor="white", facecolor="#1a1d27")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right")

    # ── Panel 3: Drawdown ─────────────────────────────────────────────────────
    ax3 = axes[2]
    rolling_max = portfolio.cummax()
    drawdown    = (portfolio - rolling_max) / rolling_max * 100
    ax3.fill_between(drawdown.index, drawdown.values, 0, color="#ef5350", alpha=0.5)
    ax3.plot(drawdown.index, drawdown.values, color="#ef5350", lw=1)
    ax3.axhline(0, color="#555566", lw=0.8)

    ax3.set_title(f"Strategy Drawdown  (Max: {metrics['max_drawdown']:.1f}%)")
    ax3.set_ylabel("Drawdown (%)")
    ax3.set_xlabel("Date")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=30, ha="right")

    # ── Stats box ─────────────────────────────────────────────────────────────
    stats_text = (
        f"Final Value: ${metrics['final_value']:,.0f}\n"
        f"Strategy:  {metrics['strategy_return']:+.1f}%\n"
        f"B&H:       {metrics['buy_hold_return']:+.1f}%\n"
        f"Trades:    {metrics['total_trades']}\n"
        f"Win Rate:  {metrics['win_rate']:.0f}%"
    )
    fig.text(
        0.82, 0.93, stats_text,
        transform=fig.transFigure,
        fontsize=9, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#1a1d27", edgecolor="#4fc3f7", alpha=0.9),
        color="#eeeeee", family="monospace"
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_path = "backtest_results.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"  Chart saved → {output_path}")
    plt.show()
