import pandas as pd
import chardet
import io

def normalize_columns(df_in):
    """Normalize column names for consistency."""
    df2 = df_in.copy()
    df2.columns = df2.columns.str.lower().str.strip()
    df2.columns = df2.columns.str.replace(" ", "_").str.replace(".", "", regex=False)
    return df2

def get_column_mapping():
    """Returns the standard column mapping."""
    return {
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

def resolve_columns(df):
    """Resolve dataframe columns to standard names."""
    col_map = get_column_mapping()
    resolved = {}
    for std, candidates in col_map.items():
        for c in candidates:
            if c in df.columns:
                resolved[std] = c
                break
    return resolved

def process_data(df):
    """Process and clean the dataframe."""
    df = normalize_columns(df)
    resolved = resolve_columns(df)
    
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
        
    return df, resolved

def load_csv(uploaded_file):
    """Load and detect encoding for a CSV file."""
    raw = uploaded_file.read()
    enc = chardet.detect(raw)["encoding"] or "utf-8"
    uploaded_file.seek(0)
    try:
        df = pd.read_csv(uploaded_file, encoding=enc)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    return df
