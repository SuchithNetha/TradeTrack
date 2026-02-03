import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import tempfile
import os

def save_fig_temp(fig, suffix=".png"):
    """Save a matplotlib figure to a temporary file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    fig.savefig(tmp.name, bbox_inches="tight")
    tmp.close()
    return tmp.name

def plot_equity_curve(metrics):
    """Plot cumulative PnL."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(metrics["equity"].values, linewidth=2, color="tab:blue")
    ax.set_title("Equity Curve (Cumulative PnL)")
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Cumulative PnL")
    ax.grid(True, linestyle="--", alpha=0.4)
    return fig

def plot_win_loss_dist(df, pnl_series):
    """Plot win vs loss counts."""
    df_temp = df.copy()
    df_temp["_outcome"] = np.where(pnl_series > 0, "Win", "Loss")
    fig, ax = plt.subplots(figsize=(6, 3))
    df_temp["_outcome"].value_counts().reindex(["Win", "Loss"], fill_value=0).plot(kind="bar", ax=ax, color=["green", "red"])
    ax.set_title("Win vs Loss Counts")
    ax.set_ylabel("Number of Trades")
    return fig

def plot_pnl_dist(pnl_series):
    """Plot PnL distribution histogram."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(pnl_series, bins=30, color="purple", alpha=0.7)
    ax.set_title("PnL Distribution (per trade)")
    ax.set_xlabel("PnL")
    ax.set_ylabel("Frequency")
    return fig

def plot_market_breakdown(df, resolved):
    """Plot trades by market."""
    market_col = resolved.get("market")
    if market_col and market_col in df.columns:
        fig, ax = plt.subplots(figsize=(7, 3))
        df[market_col].value_counts().plot(kind="bar", ax=ax, color="orange")
        ax.set_title("Trades by Market")
        ax.set_xlabel("Market")
        ax.set_ylabel("Count")
        return fig
    return None

def plot_rr_vs_pnl(df, resolved, pnl_series):
    """Plot Risk-Reward vs PnL."""
    rr_col = resolved.get("risk_reward")
    if rr_col and rr_col in df.columns:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(df[rr_col], pnl_series, alpha=0.7, c=np.where(pnl_series > 0, "green", "red"))
        ax.set_xlabel("Risk:Reward")
        ax.set_ylabel("PnL")
        ax.set_title("Risk:Reward vs PnL")
        return fig
    return None

def plot_monthly_pnl(df, resolved, pnl_col):
    """Plot Monthly PnL using Plotly and a Matplotlib fallback."""
    if "date" in resolved and resolved["date"] in df.columns:
        df["_date_parsed"] = pd.to_datetime(df[resolved["date"]], errors="coerce")
        if df["_date_parsed"].notna().sum() > 0:
            monthly = df.groupby(pd.Grouper(key="_date_parsed", freq="M")).agg(monthly_pnl=(pnl_col, lambda x: pd.to_numeric(x).sum()))
            
            # Plotly Chart
            fig_plotly = px.bar(monthly.reset_index(), x=monthly.reset_index().columns[0], y="monthly_pnl", title="Monthly PnL")
            
            # Matplotlib Fallback for PDF
            fig_mpl, ax = plt.subplots(figsize=(8, 3))
            ax.bar(monthly.reset_index().iloc[:,0].astype(str), monthly["monthly_pnl"])
            ax.set_title("Monthly PnL")
            ax.set_ylabel("PnL")
            ax.set_xticklabels(monthly.reset_index().iloc[:,0].astype(str), rotation=45, ha="right")
            
            return fig_plotly, fig_mpl
    return None, None
