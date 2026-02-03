from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    market = Column(String(50))
    direction = Column(String(10))
    entry = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    exit_price = Column(Float)
    quantity = Column(Float)
    pnl = Column(Float)
    notes = Column(Text)

# SQLite for portability
DB_URL = "sqlite:///trades.db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_trades_to_db(df, resolved):
    """Save a dataframe of trades to the SQLite database."""
    init_db()
    session = SessionLocal()
    
    # Map resolved columns back to DB schema
    for _, row in df.iterrows():
        trade = Trade(
            date=row.get(resolved.get('date')) if pd.notnull(row.get(resolved.get('date'))) else None,
            market=str(row.get(resolved.get('market'), 'Unknown')),
            direction=str(row.get(resolved.get('direction'), 'Unknown')),
            entry=float(row.get(resolved.get('entry'), 0)),
            stop_loss=float(row.get(resolved.get('stop_loss'), 0)),
            take_profit=float(row.get(resolved.get('take_profit'), 0)),
            exit_price=float(row.get(resolved.get('exit_price'), 0)),
            quantity=float(row.get(resolved.get('quantity'), 1)),
            pnl=float(row.get(resolved.get('pnl'), 0)),
            notes=str(row.get(resolved.get('notes'), ''))
        )
        session.add(trade)
    
    session.commit()
    session.close()

def load_trades_from_db():
    """Load all trades from the SQLite database as a dataframe."""
    init_db()
    return pd.read_sql("SELECT * FROM trades", engine)
