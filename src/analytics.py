import pandas as pd
import numpy as np

def calculate_metrics(df, resolved):
    """Calculate all trading performance metrics."""
    if "pnl" not in resolved:
        return None

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

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "longest_win_streak": longest_win_streak,
        "longest_loss_streak": longest_loss_streak,
        "avg_rr": avg_rr,
        "pnl_series": pnl_series,
        "equity": equity
    }

def get_best_worst_trades(df, resolved, n=5):
    """Get Top N winning and losing trades."""
    if "pnl" not in resolved:
        return None, None
        
    pnl_col = resolved["pnl"]
    best = df.assign(_pnl=pd.to_numeric(df[pnl_col], errors="coerce")).sort_values("_pnl", ascending=False).head(n)
    worst = df.assign(_pnl=pd.to_numeric(df[pnl_col], errors="coerce")).sort_values("_pnl").head(n)
    return best, worst
