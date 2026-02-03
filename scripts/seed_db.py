import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path to import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.database import init_db, save_trades_to_db

def generate_sample_trades(n=100):
    np.random.seed(42)
    markets = ["Bitcoin", "Ethereum", "BankNifty", "Nifty 50", "Apple", "Tesla", "Gold", "EUR/USD"]
    directions = ["Buy", "Sell"]
    
    start_date = datetime.now() - timedelta(days=365)
    data = []
    
    current_equity = 10000
    
    for i in range(n):
        trade_date = start_date + timedelta(days=i * 3 + np.random.randint(0, 3))
        market = np.random.choice(markets)
        direction = np.random.choice(directions)
        
        # Base prices
        if "Bitcoin" in market: base_price = 40000
        elif "Equity" in market or "Nifty" in market: base_price = 18000
        elif "Gold" in market: base_price = 2000
        else: base_price = 150
        
        entry = base_price + np.random.normal(0, base_price * 0.02)
        
        # RR and Outcome
        # 45% win rate, but higher RR
        is_win = np.random.random() < 0.45
        
        if is_win:
            rr = np.random.uniform(1.5, 4.0)
            risk = entry * 0.01 # 1% risk
            pnl = risk * rr
            exit_price = entry + (entry * 0.01 * rr) if direction == "Buy" else entry - (entry * 0.01 * rr)
            stop_loss = entry - (entry * 0.01) if direction == "Buy" else entry + (entry * 0.01)
            take_profit = exit_price
            notes = "Target hit. Followed setup."
        else:
            risk = entry * 0.01
            pnl = -risk
            exit_price = entry - (entry * 0.01) if direction == "Buy" else entry + (entry * 0.01)
            stop_loss = exit_price
            take_profit = entry + (entry * 0.02) if direction == "Buy" else entry - (entry * 0.02)
            notes = "Stop loss hit. Market reversed."
            
        data.append({
            "date": trade_date,
            "market": market,
            "direction": direction,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "exit_price": round(exit_price, 2),
            "quantity": 1,
            "pnl": round(pnl, 2),
            "notes": notes
        })
        
    df = pd.DataFrame(data)
    mapping = {
        'date': 'date', 'market': 'market', 'direction': 'direction', 
        'entry': 'entry', 'stop_loss': 'stop_loss', 'take_profit': 'take_profit',
        'exit_price': 'exit_price', 'quantity': 'quantity', 'pnl': 'pnl', 'notes': 'notes'
    }
    
    print(f"Generating {n} trades...")
    save_trades_to_db(df, mapping)
    print("Sample database 'trades.db' created successfully!")

if __name__ == "__main__":
    init_db()
    generate_sample_trades(120)
