from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import models.models as models
from dependencies import engine, SessionLocal, Base
from apis.routes import router as api_router

app = FastAPI()

# Create DB tables
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app.include_router(api_router) 