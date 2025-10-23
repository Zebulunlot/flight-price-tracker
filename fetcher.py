# fetcher.py
import random, datetime

def fetch_current_price(route):
    """Mock: returns a float price based on last price + noise"""
    # route is dict with price_history list
    if route.get('price_history'):
        last = route['price_history'][-1]['price']
    else:
        last = random.randint(200,1200)
    # small random change
    change = random.uniform(-0.05, 0.05)
    new_price = max(20, last * (1 + change))
    return round(new_price, 2), datetime.datetime.utcnow().isoformat()
