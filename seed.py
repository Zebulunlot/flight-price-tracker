# seed.py
import uuid, random, datetime, json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "flighttracker")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db['routes']

# create 10 sample routes
samples = []
templates = [
    ("LHE","JED","PIA"), ("LHE","BKK","Thai"), ("SIN","BKK","SingaporeAir"),
    ("LHR","JFK","BritishAirways"), ("DXB","LAX","Emirates"), ("DEL","SYD","AirIndia"),
    ("KHI","DXB","Emirates"), ("MNL","HKG","Cathay"), ("DOH","CDG","QatarAirways"),
    ("BOM","SFO","AirIndia")
]
flight_dates = ["2026-01-01","2026-02-20","2026-03-15","2026-01-15","2026-12-25","2026-04-10","2026-02-01","2026-03-30","2026-05-05","2026-06-18"]

def make_price_history(start_date, end_date, step_days=7, base_price=700):
    hist=[]
    dt = start_date
    price = base_price
    while dt <= end_date:
        noise = random.uniform(-0.08,0.08)
        price = max(30, price*(1+noise))
        hist.append({"timestamp": dt.isoformat(), "price": round(price,2)})
        dt = dt + datetime.timedelta(days=step_days)
    return hist

for (src,dst,air),fd in zip(templates, flight_dates):
    id = str(uuid.uuid4())
    fdate = datetime.datetime.fromisoformat(fd).date()
    tracking_start = fdate - datetime.timedelta(days=180)
    # make price history up to now or few samples
    end = min(datetime.datetime.utcnow().date(), fdate - datetime.timedelta(days=1))
    hist = make_price_history(tracking_start, end, step_days=random.choice([1,7,14]), base_price=random.randint(200,1200))
    doc = {
        "_id": id, "source":src, "destination":dst, "route":f"{src}->{dst}",
        "airline":air, "flight_date": fd, "tracking_start": tracking_start.isoformat(),
        "interval_days": random.choice([1,7,14]), "price_history": hist
    }
    samples.append(doc)

coll.delete_many({})   # clear
coll.insert_many(samples)
print("Seeded", len(samples), "routes")
# Optional export
with open("seeded_flights.json","w") as f:
    json.dump(samples, f, indent=2)
print("Exported seeded_flights.json")
