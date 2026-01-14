"""SQLAlchemy ORM Models"""
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.backend.db import Base


class TrackedWallet(Base):
    """Tracked wallet addresses with custom names"""
    __tablename__ = "tracked_wallets"
    
    wallet_address = Column(String, primary_key=True, index=True)
    custom_name = Column(String, nullable=True)
    main_market = Column(String, nullable=True)  # Added for Streamlit UI
    alerts_enabled = Column(Integer, nullable=False, default=1)
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    
    # Relationship
    trades = relationship("Trade", back_populates="wallet", cascade="all, delete-orphan")


class Trade(Base):
    """Individual trades from tracked wallets"""
    __tablename__ = "trades"
    
    trade_uid = Column(String, primary_key=True)
    wallet_address = Column(String, ForeignKey("tracked_wallets.wallet_address"), nullable=False, index=True)
    asset_id = Column(String, nullable=True)
    market_name = Column(String, nullable=True, index=True)
    side = Column(String, nullable=True)  # buy / sell (b / s from Hashdive)
    share_type = Column(String, nullable=True)  # YES / NO
    price = Column(Float, nullable=True)
    usd_amount = Column(Float, nullable=True, index=True)
    shares = Column(Float, nullable=True)
    timestamp = Column(String, nullable=False, index=True)
    
    # Market info fields from Hashdive
    market_question = Column(Text, nullable=True)  # market_info.question
    market_outcome = Column(String, nullable=True)  # market_info.outcome (Yes/No)
    market_tags = Column(Text, nullable=True)  # market_info.tags (stored as JSON string)
    market_target_price = Column(Float, nullable=True)  # market_info.target_price
    market_resolved = Column(Integer, nullable=True)  # market_info.resolved (0/1)
    market_is_winner = Column(Integer, nullable=True)  # market_info.is_winner (0/1)
    market_resolved_price = Column(Float, nullable=True)  # market_info.resolved_price
    
    raw_json = Column(Text, nullable=True)  # Store full trade data as JSON
    created_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    
    # Relationship
    wallet = relationship("TrackedWallet", back_populates="trades")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_trades_wallet_time', 'wallet_address', 'timestamp'),
    )


class AlertLog(Base):
    """Log of sent email alerts"""
    __tablename__ = "alert_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_uid = Column(String, nullable=False, unique=True, index=True)
    wallet_address = Column(String, nullable=False)
    sent_to = Column(String, nullable=False)
    sent_at = Column(String, nullable=False, default=lambda: datetime.utcnow().isoformat())
    status = Column(String, nullable=False)  # success / failed
    error_message = Column(Text, nullable=True)
