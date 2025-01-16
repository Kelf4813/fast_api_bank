from fastapi import FastAPI

from app.api import include_router
from app.database import get_db

db = get_db()
app = FastAPI()
include_router(app)
