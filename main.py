# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os, uuid, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from fetcher import fetch_current_price
from utils import compute_hybrid_scores
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI","mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME","flighttracker")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db['routes']

app = FastAPI(title="Flight Price Tracker MVP")

@app.post("/routes")
def create_route(payload: dict):
    payload["_id"] = payload.get("_id", str(uuid.uuid4()))
    coll.insert_one(payload)
    return {"status":"ok","id":payload["_id"]}

@app.get("/routes/{route_id}")
def get_route(route_id: str):
    doc = coll.find_one({"_id": route_id}, {"_id":1,"source":1,"destination":1,"airline":1,"flight_date":1,"price_history":1})
    if not doc: raise HTTPException(404,"not found")
    # convert ObjectId to str
    return doc

@app.get("/routes/{route_id}/prices")
def get_prices(route_id: str, start: str=None, end: str=None):
    doc = coll.find_one({"_id": route_id})
    if not doc: raise HTTPException(404,"not found")
    ph = doc.get("price_history",[])
    if start:
        ph = [p for p in ph if p["timestamp"] >= start]
    if end:
        ph = [p for p in ph if p["timestamp"] <= end]
    return {"prices": ph}

@app.get("/search")
def search(q: str = Query(None), source: str = Query(None), destination: str = Query(None), airline: str = Query(None), top_k: int = 5):
    # structured filter
    query = {}
    if source: query["source"] = source
    if destination: query["destination"] = destination
    if airline: query["airline"] = {"$regex": airline, "$options":"i"}
    candidates = list(coll.find(query))
    if not candidates:
        candidates = list(coll.find({}))  # fallback to full set
    # compute hybrid scores and return top K
    scored = compute_hybrid_scores(candidates, q or "")
    results = []
    for s, doc in scored[:top_k]:
        results.append({
            "id": doc["_id"],
            "route": doc["route"],
            "airline": doc.get("airline"),
            "flight_date": doc.get("flight_date"),
            "latest_price": doc.get("price_history")[-1]["price"] if doc.get("price_history") else None,
            "score": round(s,4)
        })
    return {"results": results}

# Scheduler job: fetch and append price for every route every X seconds (demo)
def polling_job():
    for doc in coll.find({}):
        rid = doc["_id"]
        new_price, ts = fetch_current_price(doc)
        coll.update_one({"_id": rid}, {"$push": {"price_history": {"timestamp": ts, "price": new_price}}})
    print("Polling job ran:", datetime.datetime.utcnow().isoformat())

scheduler = BackgroundScheduler()
scheduler.add_job(polling_job, 'interval', seconds=60)   # for demo every 60s; change to minutes for real
scheduler.start()

# graceful shutdown
import atexit
atexit.register(lambda: scheduler.shutdown())
