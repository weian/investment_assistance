from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import services
from dependencies import SessionLocal
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    portfolios = services.get_portfolios(db)
    return templates.TemplateResponse("home.html", {"request": request, "portfolios": portfolios})

@router.post("/add-portfolio")
def add_portfolio(name: str = Form(...), db: Session = Depends(get_db)):
    services.create_portfolio(db, name)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/portfolio/{portfolio_id}")
def portfolio_detail(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = services.get_portfolio(db, portfolio_id)
    stocks = services.get_stocks_by_portfolio(db, portfolio_id)
    value_info = request.query_params.get("show_value")
    date_str = request.query_params.get("date")
    value = None
    prices = None
    used_date = None
    if value_info:
        if date_str:
            try:
                used_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except Exception:
                used_date = None
        result = services.get_portfolio_value(db, portfolio_id, used_date)
        value = result["total_value"]
        prices = result["prices"]
        services.store_portfolio_value(db, portfolio_id, value, prices, stocks, used_date)
    return templates.TemplateResponse("portfolio.html", {"request": request, "portfolio": portfolio, "stocks": stocks, "value": value, "prices": prices, "used_date": used_date, "date_str": date_str})

@router.get("/portfolio/{portfolio_id}/history")
def portfolio_history(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = services.get_portfolio(db, portfolio_id)
    values = services.get_portfolio_values_by_date(db, portfolio_id)
    return templates.TemplateResponse("history.html", {"request": request, "portfolio": portfolio, "values": values})

@router.post("/portfolio/{portfolio_id}/add-stock")
def add_stock(portfolio_id: int, ticker: str = Form(...), shares: float = Form(...), db: Session = Depends(get_db)):
    services.add_stock_to_portfolio(db, portfolio_id, ticker, shares)
    return RedirectResponse(url=f"/portfolio/{portfolio_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/portfolio/{portfolio_id}/delete-stock/{stock_id}")
def delete_stock(portfolio_id: int, stock_id: int, db: Session = Depends(get_db)):
    success = services.delete_stock(db, stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock not found")
    return RedirectResponse(url=f"/portfolio/{portfolio_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete-portfolio/{portfolio_id}")
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    success = services.delete_portfolio(db, portfolio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/portfolio/{portfolio_id}/update-name")
def update_portfolio_name(portfolio_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    updated = services.update_portfolio_name(db, portfolio_id, name)
    if not updated:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return RedirectResponse(url=f"/portfolio/{portfolio_id}", status_code=status.HTTP_303_SEE_OTHER) 