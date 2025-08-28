# streamlit_app.py — fixed, self-contained
import streamlit as st
import pandas as pd
import chardet
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import tempfile
import os

st.set_page_config(page_title="TradeInsight", layout="wide", initial_sidebar_state="expanded")
st.title("📊 TradeInsight - Trading Journal")
st.write("Upload your trades CSV (reasonable headers). Click **Get Analysis** to compute performance metrics, visualizations and export a PDF report.")

# ------------------------
# File upload & read
# ------------------------
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv", "txt"])
if uploaded_file is None:
    st.info("⬆️ Upload a CSV to begin. Use the included `trade_log_template.csv` as a template.")
    st.stop()

raw = uploaded_file.read()
enc = chardet.detect(raw)["encoding"] or "utf-8"
uploaded_file.seek(0)
try:
    df = pd.read_csv(uploaded_file, encoding=enc)
except Exception:
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

# ------------------------
# Normalize columns & mapping
# ------------------------
def normalize_columns(df_in):
    df2 = df_in.copy()
    df2.columns = df2.columns.str.lower().str.strip()
    df2.columns = df2.columns.str.replace(" ", "_")
    df2.columns = df2.columns.str.replace(".", "", regex=False)
    return df2

df = normalize_columns(df)

col_map = {
    "date": ["date", "trade_date", "trade date", "timestamp", "time"],
    "market": ["market", "market_type", "symbol", "instrument"],
    "direction": ["direction", "side", "buy/sell"],
    "entry": ["entry", "entry_price", "entryprice", "entry_price", "entry price"],
    "stop_loss": ["stop_loss", "stoploss", "sl", "stop_loss_price", "stop"],
    "take_profit": ["take_profit", "takeprofit", "tp", "target", "take_profit_price"],
    "exit_price": ["exit_price", "exitprice", "exit", "exit_price"],
    "pnl": ["pnl", "profit", "pl", "profit_loss", "profit/loss"],
    "risk_reward": ["risk_reward", "rr", "riskreward", "risk:reward", "risk_reward_ratio"],
    "quantity": ["quantity", "qty", "size"],
    "notes": ["notes", "note", "comment"]
}

resolved = {}
for std, candidates in col_map.items():
    for c in candidates:
        if c in df.columns:
            resolved[std] = c
            break

st.subheader("Preview of uploaded file")
st.dataframe(df.head(50))

# Ensure date numeric parsing where possible
if "date" in resolved:
    df[resolved["date"]] = pd.to_datetime(df[resolved["date"]], errors="coerce")

# Ensure numeric columns for known fields
for ncol in ["entry", "stop_loss", "take_profit", "exit_price", "pnl", "risk_reward", "quantity"]:
    if ncol in resolved:
        df[resolved[ncol]] = pd.to_numeric(df[resolved[ncol]], errors="coerce")

# Compute pnl if not present but exit/entry/quantity present
if "pnl" not in resolved and {"entry", "exit_price", "quantity"}.issubset(resolved.keys()):
    df["computed_pnl"] = (df[resolved["exit_price"]] - df[resolved["entry"]]) * df[resolved["quantity"]]
    resolved["pnl"] = "computed_pnl"

# Compute risk_reward if missing and entry/tp/sl present
if "risk_reward" not in resolved and {"entry", "stop_loss", "take_profit"}.issubset(resolved.keys()):
    try:
        df["computed_rr"] = (df[resolved["take_profit"]] - df[resolved["entry"]]).abs() / (df[resolved["entry"]] - df[resolved["stop_loss"]]).abs()
        resolved["risk_reward"] = "computed_rr"
    except Exception:
        pass

# fallback quantity
if "quantity" not in resolved:
    df["_quantity_fallback"] = 1
    resolved["quantity"] = "_quantity_fallback"

# ------------------------
# Utility: save matplotlib fig to temp png and return path
# ------------------------
def save_fig_temp(fig, suffix=".png"):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    fig.savefig(tmp.name, bbox_inches="tight")
    tmp.close()
    return tmp.name

# ------------------------
# Main Analysis Button (all visuals & PDF happen inside)
# ------------------------
if st.button("📈 Get Analysis"):
    st.subheader("🔍 Metrics & Insights")

    if "pnl" not in resolved:
        st.error("Couldn't find or compute PnL. Please include PnL column or provide entry/exit/quantity.")
        st.stop()

    pnl_col = resolved["pnl"]
    pnl_series = pd.to_numeric(df[pnl_col], errors="coerce").fillna(0)

    total_trades = int(pnl_series.size)
    wins_mask = pnl_series > 0
    losses_mask = pnl_series <= 0
    wins = int(wins_mask.sum())
    losses = int(losses_mask.sum())
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0.0
    avg_win = pnl_series[wins_mask].mean() if wins > 0 else 0.0
    avg_loss = abs(pnl_series[losses_mask].mean()) if losses > 0 else 0.0
    expectancy = (win_rate/100 * avg_win) - ((100 - win_rate)/100 * avg_loss)
    gross_profit = pnl_series[pnl_series > 0].sum()
    gross_loss = abs(pnl_series[pnl_series < 0].sum()) or 1e-9
    profit_factor = gross_profit / gross_loss
    mean_return = pnl_series.mean()
    std_return = pnl_series.std(ddof=0) or 1e-9
    sharpe = mean_return / std_return
    equity = pnl_series.cumsum()
    peak = equity.cummax()
    drawdown = (equity - peak)
    max_drawdown = drawdown.min()

    def longest_streak(mask):
        max_s = cur = 0
        for v in mask:
            if v:
                cur += 1
                max_s = max(max_s, cur)
            else:
                cur = 0
        return max_s

    longest_win_streak = longest_streak(wins_mask)
    longest_loss_streak = longest_streak(~wins_mask)

    avg_rr = None
    if "risk_reward" in resolved:
        try:
            avg_rr = float(pd.to_numeric(df[resolved["risk_reward"]], errors="coerce").dropna().mean())
        except Exception:
            avg_rr = None

    # show KPI metrics
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Trades", f"{total_trades}")
    k2.metric("Win Rate", f"{win_rate:.2f}%")
    k3.metric("Avg Win", f"{avg_win:.2f}")
    k4.metric("Avg Loss", f"{avg_loss:.2f}")

    k5, k6, k7, k8 = st.columns(4)
    k5.metric("Expectancy / trade", f"{expectancy:.2f}")
    k6.metric("Profit Factor", f"{profit_factor:.2f}")
    k7.metric("Sharpe (mean/std)", f"{sharpe:.2f}")
    k8.metric("Max Drawdown", f"{max_drawdown:.2f}")

    with st.expander("What these metrics mean (brief)"):
        st.write("""
        - **Win Rate:** % of trades that were profitable.
        - **Avg Win / Avg Loss:** Mean PnL of winning vs losing trades.
        - **Expectancy:** Expected PnL per trade (positive is good).
        - **Profit Factor:** Gross profit / gross loss.
        - **Sharpe:** Mean PnL / Std PnL (simple risk-adjusted measure).
        - **Max Drawdown:** Largest drop from peak equity.
        """)

    # --- Create Matplotlib charts and save to temp files ---
    temp_images = []  # will collect paths to include in PDF

    # 1) Equity curve (matplotlib)
    fig1, ax1 = plt.subplots(figsize=(8, 3.5))
    ax1.plot(equity.values, linewidth=2, color="tab:blue")
    ax1.set_title("Equity Curve (Cumulative PnL)")
    ax1.set_xlabel("Trade #")
    ax1.set_ylabel("Cumulative PnL")
    ax1.grid(True, linestyle="--", alpha=0.4)
    st.pyplot(fig1)
    st.caption("Purpose: Shows account growth and drawdown periods. A steady upward curve is ideal.")
    temp_images.append(save_fig_temp(fig1))

    # 2) Win vs Loss bar
    df["_outcome"] = np.where(pnl_series > 0, "Win", "Loss")
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    df["_outcome"].value_counts().reindex(["Win", "Loss"], fill_value=0).plot(kind="bar", ax=ax2, color=["green", "red"])
    ax2.set_title("Win vs Loss Counts")
    ax2.set_ylabel("Number of Trades")
    st.pyplot(fig2)
    st.caption("Purpose: Quick view of how many trades result in profit vs loss.")
    temp_images.append(save_fig_temp(fig2))

    # 3) PnL distribution histogram
    fig3, ax3 = plt.subplots(figsize=(6, 3))
    ax3.hist(pnl_series, bins=30, color="purple", alpha=0.7)
    ax3.set_title("PnL Distribution (per trade)")
    ax3.set_xlabel("PnL")
    ax3.set_ylabel("Frequency")
    st.pyplot(fig3)
    st.caption("Purpose: Shows whether losses or wins dominate and if there are fat-tail events.")
    temp_images.append(save_fig_temp(fig3))

    # 4) Market breakdown (safe check)
    market_col = resolved.get("market")
    if market_col and market_col in df.columns:
        fig4, ax4 = plt.subplots(figsize=(7, 3))
        df[market_col].value_counts().plot(kind="bar", ax=ax4, color="orange")
        ax4.set_title("Trades by Market")
        ax4.set_xlabel("Market")
        ax4.set_ylabel("Count")
        st.pyplot(fig4)
        st.caption("Purpose: Shows which markets you trade more and might need focus.")
        temp_images.append(save_fig_temp(fig4))
    else:
        st.info("No market column found — skipping Market breakdown chart.")

    # 5) Risk-Reward scatter (if rr present)
    rr_col = resolved.get("risk_reward")
    if rr_col and rr_col in df.columns:
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        ax5.scatter(df[rr_col], pnl_series, alpha=0.7, c=np.where(pnl_series > 0, "green", "red"))
        ax5.set_xlabel("Risk:Reward")
        ax5.set_ylabel("PnL")
        ax5.set_title("Risk:Reward vs PnL")
        st.pyplot(fig5)
        st.caption("Purpose: Check whether higher risk:reward correlates with positive PnL.")
        temp_images.append(save_fig_temp(fig5))
    else:
        st.info("No Risk:Reward column available — skipping R:R scatter.")

    # 6) Monthly PnL (if date exists)
    if "date" in resolved and resolved["date"] in df.columns:
        df["_date_parsed"] = pd.to_datetime(df[resolved["date"]], errors="coerce")
        if df["_date_parsed"].notna().sum() > 0:
            monthly = df.groupby(pd.Grouper(key="_date_parsed", freq="M")).agg(monthly_pnl=(pnl_col, lambda x: pd.to_numeric(x).sum()))
            fig6 = px.bar(monthly.reset_index(), x=" _date_parsed" if False else monthly.reset_index().columns[0], y="monthly_pnl", title="Monthly PnL")
            st.plotly_chart(fig6, use_container_width=True)
            st.caption("Purpose: Shows month-to-month performance and seasonality.")
            # Also save a matplotlib fallback for PDF
            fig6_mpl, ax6 = plt.subplots(figsize=(8, 3))
            ax6.bar(monthly.reset_index().iloc[:,0].astype(str), monthly["monthly_pnl"])
            ax6.set_title("Monthly PnL")
            ax6.set_ylabel("PnL")
            ax6.set_xticklabels(monthly.reset_index().iloc[:,0].astype(str), rotation=45, ha="right")
            temp_images.append(save_fig_temp(fig6_mpl))
    else:
        st.info("No date column found — skipping monthly PnL chart.")

    # Table of best/worst trades
    st.subheader("Best & Worst Trades")
    best = df.assign(_pnl=pd.to_numeric(df[pnl_col], errors="coerce")).sort_values("_pnl", ascending=False).head(5)
    worst = df.assign(_pnl=pd.to_numeric(df[pnl_col], errors="coerce")).sort_values("_pnl").head(5)
    st.write("Top 5 winning trades")
    preview_cols = []
    for key in ["date", "market", "entry", "exit_price", "pnl"]:
        if key in resolved and resolved[key] in df.columns:
            preview_cols.append(resolved[key])
    if preview_cols:
        st.dataframe(best[preview_cols].head(5))
        st.dataframe(worst[preview_cols].head(5))
    else:
        st.dataframe(best.head(5))
        st.dataframe(worst.head(5))

    st.success("Analysis complete. Use the charts and metrics to identify patterns and areas to improve.")
    # ------------------------
    # PDF generation (reportlab, in-memory) — automatic
    # ------------------------
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    flowables = []

    flowables.append(Paragraph("TradeInsight - Performance Report", styles["Title"]))
    flowables.append(Spacer(1, 8))
    # KPIs summary
    flowables.append(Paragraph(f"Total Trades: {total_trades}", styles["Normal"]))
    flowables.append(Paragraph(f"Win Rate: {win_rate:.2f}%", styles["Normal"]))
    flowables.append(Paragraph(f"Total PnL: {float(pnl_series.sum()):.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Expectancy: {expectancy:.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Profit Factor: {profit_factor:.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Sharpe (mean/std): {sharpe:.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Max Drawdown: {max_drawdown:.2f}", styles["Normal"]))
    flowables.append(Spacer(1, 12))

    # Add charts into the PDF
    for img_path in temp_images:
        try:
            flowables.append(RLImage(img_path, width=450, height=250))
            flowables.append(Spacer(1, 12))
        except Exception:
            pass

    doc.build(flowables)
    buffer.seek(0)

    st.download_button(
        "📥 Download PDF Report",
        data=buffer,
        file_name="trade_report.pdf",
        mime="application/pdf"
    )

    # cleanup temp images
    for p in temp_images:
        try:
            os.remove(p)
        except Exception:
            pass
