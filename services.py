from sqlalchemy.orm import Session
from models.models import Portfolio, Stock, PortfolioValue, StockValue
import yfinance as yf
from datetime import date, datetime
from dependencies import SessionLocal

def create_portfolio(db: Session, name: str):
    portfolio = Portfolio(name=name)
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio

def get_portfolios(db: Session):
    return db.query(Portfolio).all()

def get_portfolio(db: Session, portfolio_id: int):
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

def add_stock_to_portfolio(db: Session, portfolio_id: int, ticker: str, shares: float):
    stock = Stock(ticker=ticker, shares=shares, portfolio_id=portfolio_id)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

def get_stocks_by_portfolio(db: Session, portfolio_id: int):
    return db.query(Stock).filter(Stock.portfolio_id == portfolio_id).all()

def get_portfolio_value(db: Session, portfolio_id: int, for_date: date = None):
    stocks = get_stocks_by_portfolio(db, portfolio_id)
    total_value = 0.0
    prices = {}
    if for_date is None:
        for_date = date.today()
    for stock in stocks:
        ticker = stock.ticker
        try:
            data = yf.Ticker(ticker)
            # Get last close price for the given date
            hist = data.history(start=for_date, end=for_date)
            if hist.empty:
                # fallback: get previous available close
                hist = data.history(end=for_date, period="5d")
                if not hist.empty:
                    price = hist.iloc[-1]["Close"]
                else:
                    price = None
            else:
                price = hist.iloc[-1]["Close"]
            prices[ticker] = price
            if price is not None:
                total_value += price * stock.shares
        except Exception:
            prices[ticker] = None
    return {"total_value": total_value, "prices": prices}

def store_portfolio_value(db: Session, portfolio_id: int, value: float, prices: dict, stocks: list, for_date: date = None):
    if for_date is None:
        for_date = date.today()
    existing = db.query(PortfolioValue).filter_by(portfolio_id=portfolio_id, date=for_date).first()
    stock_set = set((stock.ticker, stock.shares) for stock in stocks)
    if existing:
        # Check if stocks match
        existing_stocks = set((s.ticker, s.shares) for s in existing.stocks)
        if stock_set == existing_stocks:
            return existing
        # If stocks changed, delete old record and children
        db.query(StockValue).filter_by(portfolio_value_id=existing.id).delete()
        db.delete(existing)
        db.commit()
    pv = PortfolioValue(portfolio_id=portfolio_id, date=for_date, total_value=value)
    db.add(pv)
    db.flush()  # get pv.id
    for stock in stocks:
        ticker = stock.ticker
        shares = stock.shares
        stock_value = prices.get(ticker)
        sv = StockValue(portfolio_value_id=pv.id, ticker=ticker, shares=shares, value=stock_value)
        db.add(sv)
    db.commit()
    db.refresh(pv)
    return pv

def get_portfolio_values_by_date(db: Session, portfolio_id: int):
    return db.query(PortfolioValue).filter_by(portfolio_id=portfolio_id).order_by(PortfolioValue.date.desc()).all()

def delete_stock(db: Session, stock_id: int):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if stock:
        db.delete(stock)
        db.commit()
        return True
    return False

def delete_portfolio(db: Session, portfolio_id: int):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        db.delete(portfolio)
        db.commit()
        return True
    return False

def update_portfolio_name(db: Session, portfolio_id: int, new_name: str):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio:
        portfolio.name = new_name
        db.commit()
        db.refresh(portfolio)
        return portfolio
    return None 