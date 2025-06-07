from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, DateTime
from sqlalchemy.orm import relationship
from dependencies import Base

class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    stocks = relationship("Stock", back_populates="portfolio", cascade="all, delete-orphan")

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    shares = Column(Float)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio", back_populates="stocks")

class PortfolioValue(Base):
    __tablename__ = "portfolio_values"
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    date = Column(Date, index=True)
    total_value = Column(Float)
    stocks = relationship("StockValue", back_populates="portfolio_value", cascade="all, delete-orphan")
    portfolio = relationship("Portfolio")

class StockValue(Base):
    __tablename__ = "stock_values"
    id = Column(Integer, primary_key=True, index=True)
    portfolio_value_id = Column(Integer, ForeignKey("portfolio_values.id"))
    ticker = Column(String, index=True)
    shares = Column(Float)
    value = Column(Float)
    portfolio_value = relationship("PortfolioValue", back_populates="stocks") 