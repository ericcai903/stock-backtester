"""
app.py — Streamlit web dashboard for the Stock Backtester.

Run with:
    streamlit run app.py
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from backtester import Backtester
from strategy import MovingAverageCrossover

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Backtester",
    page_icon="📈",
    layout="wide",
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("📈 Stock Backtesting Dashboard")
st.markdown("Simulate a **Moving Average Crossover** strategy on any stock and compare it to buy & hold.")
st.divider()

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    ticker = st.text_input("Ticker Symbol", value="AAPL").upper().strip()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.Timestamp("2020-01-01"))
    with col2:
        end_date = st.date_input("End Date", value=pd.Timestamp("2024-12-31"))

    initial_cash = st.number_input(
        "Starting Capital ($)", min_value=100, max_value=1_000_000,
        value=10_000, step=1000
    )

    st.subheader("Moving Average Windows")
    short_window = st.slider("Short MA (days)", min_value=5, max_value=100, value=20)
    long_window  = st.slider("Long MA (days)",  min_value=10, max_value=300, value=50)

    if short_window >= long_window:
        st.error("Short MA must be less than Long MA!")
        st.stop()

    run = st.button("🚀 Run Backtest", use_container_width=True, type="primary")

# ── Main area ─────────────────────────────────────────────────────────────────
if not run:
    st.info("👈 Configure your settings in the sidebar and click **Run Backtest** to get started.")
    st.stop()

# Run backtest
with st.spinner(f"Downloading {ticker} data and running backtest…"):
    try:
        strategy = MovingAverageCrossover(short_window=short_window, long_window=long_window)
        bt = Backtester(
            ticker=ticker,
            start=str(start_date),
            end=str(end_date),
            initial_cash=initial_cash
        )
        results = bt.run(strategy)
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()

m   = results["metrics"]
data      = results["data"]
portfolio = results["portfolio"]
buy_hold  = results["buy_hold"]
trades    = results["trades"]

# ── Metrics row ───────────────────────────────────────────────────────────────
st.subheader(f"Results for {ticker}  •  {start_date} → {end_date}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Final Value",      f"${m['final_value']:,.0f}")
c2.metric("Strategy Return",  f"{m['strategy_return']:+.1f}%",
          delta=f"{m['strategy_return'] - m['buy_hold_return']:+.1f}% vs B&H")
c3.metric("Buy & Hold Return",f"{m['buy_hold_return']:+.1f}%")
c4.metric("Max Drawdown",     f"{m['max_drawdown']:.1f}%")
c5.metric("Win Rate",         f"{m['win_rate']:.0f}%",
          help=f"{m['num_buys']} buys / {m['num_sells']} sells")

st.divider()

# ── Charts ────────────────────────────────────────────────────────────────────
buys  = [t for t in trades if t["type"] == "BUY"]
sells = [t for t in trades if t["type"] == "SELL"]

fig, axes = plt.subplots(3, 1, figsize=(14, 11), gridspec_kw={"height_ratios": [3, 2, 1.5]})
fig.patch.set_facecolor("#0f1117")
for ax in axes:
    ax.set_facecolor("#1a1d27")
    ax.tick_params(colors="#aaaaaa")
    ax.spines[:].set_color("#333344")
    ax.yaxis.label.set_color("#cccccc")
    ax.xaxis.label.set_color("#cccccc")
    ax.title.set_color("#eeeeee")

# Panel 1 — Price + MAs + signals
ax1 = axes[0]
ax1.plot(data.index, data["Close"],    color="#4fc3f7", lw=1.2, label="Close Price", alpha=0.9)
ax1.plot(data.index, data["short_ma"], color="#ffb74d", lw=1.4, label=f"{short_window}-day MA", linestyle="--")
ax1.plot(data.index, data["long_ma"],  color="#ef5350", lw=1.4, label=f"{long_window}-day MA",  linestyle="--")
for t in buys:
    ax1.scatter(t["date"], t["price"], marker="^", color="#00e676", s=100, zorder=5)
for t in sells:
    ax1.scatter(t["date"], t["price"], marker="v", color="#ff5252", s=100, zorder=5)
ax1.scatter([], [], marker="^", color="#00e676", s=80, label="BUY")
ax1.scatter([], [], marker="v", color="#ff5252", s=80, label="SELL")
ax1.set_title(f"{ticker} — Price & Signals")
ax1.set_ylabel("Price (USD)")
ax1.legend(loc="upper left", framealpha=0.3, labelcolor="white", facecolor="#1a1d27")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha="right")

# Panel 2 — Portfolio vs B&H
ax2 = axes[1]
ax2.plot(portfolio.index, portfolio.values, color="#ba68c8", lw=1.8,
         label=f"Strategy  ({m['strategy_return']:+.1f}%)")
ax2.plot(buy_hold.index, buy_hold.values,   color="#4db6ac", lw=1.8,
         linestyle="--", label=f"Buy & Hold ({m['buy_hold_return']:+.1f}%)")
ax2.axhline(y=portfolio.iloc[0], color="#555566", lw=1, linestyle=":")
ax2.set_title("Portfolio Value vs. Buy & Hold")
ax2.set_ylabel("Value (USD)")
ax2.legend(loc="upper left", framealpha=0.3, labelcolor="white", facecolor="#1a1d27")
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right")

# Panel 3 — Drawdown
ax3 = axes[2]
rolling_max = portfolio.cummax()
drawdown    = (portfolio - rolling_max) / rolling_max * 100
ax3.fill_between(drawdown.index, drawdown.values, 0, color="#ef5350", alpha=0.5)
ax3.plot(drawdown.index, drawdown.values, color="#ef5350", lw=1)
ax3.axhline(0, color="#555566", lw=0.8)
ax3.set_title(f"Drawdown  (Max: {m['max_drawdown']:.1f}%)")
ax3.set_ylabel("Drawdown (%)")
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=30, ha="right")

plt.tight_layout()
st.pyplot(fig)

st.divider()

# ── Trade log ─────────────────────────────────────────────────────────────────
st.subheader("📋 Trade Log")

if trades:
    trade_df = pd.DataFrame([
        {
            "Date"   : t["date"].date(),
            "Action" : t["type"],
            "Price"  : f"${t['price']:.2f}",
            "Shares" : f"{t['shares']:.4f}",
        }
        for t in trades
    ])
    st.dataframe(
        trade_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Action": st.column_config.TextColumn(
                "Action",
                help="BUY or SELL signal"
            )
        }
    )
else:
    st.info("No trades were executed in this period.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ This tool is for educational purposes only and does not constitute financial advice.")
