# models.py
from pymongo import MongoClient

# connect to local MongoDB server
client = MongoClient("mongodb://localhost:27017/")

# create or access database
db = client["flight_tracker"]

# create or access collection
flights_collection = db["flights"]



from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class PriceSample(BaseModel):
    timestamp: datetime
    price: float

class RouteCreate(BaseModel):
    source: str
    destination: str
    airline: Optional[str] = None
    flight_date: date
    interval_days: int = 7
    tracking_start: Optional[date] = None

class Route(RouteCreate):
    id: str
    price_history: List[PriceSample] = []
