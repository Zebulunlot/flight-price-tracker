from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["flight_tracker"]
    print("✅ MongoDB connection successful!")
    print("Databases:", client.list_database_names())
except Exception as e:
    print("❌ Connection failed:", e)
