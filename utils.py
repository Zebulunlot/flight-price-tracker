# utils.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
from typing import List

# We'll build TF-IDF at runtime from DB docs (simple)
def build_tfidf(corpus):
    vec = TfidfVectorizer().fit(corpus)
    mat = vec.transform(corpus)
    return vec, mat

def compute_hybrid_scores(candidates, query_text, weights=None):
    if weights is None:
        weights = {'text':0.5, 'price_drop':0.3, 'recency':0.2}
    # build corpus text
    texts = [f"{c['route']} {c.get('airline','')} {c.get('flight_date','')}" for c in candidates]
    vec, mat = build_tfidf(texts)
    qvec = vec.transform([query_text]) if query_text else None
    text_scores = cosine_similarity(qvec, mat)[0] if qvec is not None else np.zeros(len(candidates))
    # price drop
    price_drop = []
    for c in candidates:
        prices = [p['price'] for p in c.get('price_history',[])]
        if not prices: price_drop.append(0)
        else:
            mx, mn = max(prices), min(prices)
            price_drop.append((mx-mn)/mx if mx>0 else 0)
    # normalize lists
    def normalize(arr):
        a = np.array(arr, dtype=float)
        if a.max() - a.min() < 1e-9:
            return np.zeros_like(a)
        return (a - a.min())/(a.max()-a.min())
    pd_norm = normalize(price_drop)
    # recency: 1/(1+days_since_latest)
    recency = []
    for c in candidates:
        if c.get('price_history'):
            latest_ts = datetime.fromisoformat(c['price_history'][-1]['timestamp'])
            days = (datetime.utcnow() - latest_ts).total_seconds()/86400
            recency.append(1.0/(1.0+max(0,days)))
        else:
            recency.append(0)
    r_norm = normalize(recency)
    final_scores = []
    for i,c in enumerate(candidates):
        s = weights['text']*float(text_scores[i]) + weights['price_drop']*float(pd_norm[i]) + weights['recency']*float(r_norm[i])
        final_scores.append((s,c))
    final_scores.sort(key=lambda x: x[0], reverse=True)
    return final_scores
