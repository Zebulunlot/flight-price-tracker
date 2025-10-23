# ✈️ Flight Price Tracker System

This project is a **Flight Ticket Price Tracking System** that tracks and compares flight ticket prices over time using FastAPI and MongoDB.  
It was developed as part of the **Mini Project (Sample Paper C)**.

---

## 🚀 Overview

The system:
- Tracks flight prices for various routes.
- Stores and updates ticket data over time.
- Allows searching and ranking flights using a hybrid scoring algorithm (TF-IDF + Price Drop + Recency).

---

## 🧠 Features

- Add and view flight routes.
- Track price changes for each route.
- Search for flights using text queries.
- Rank results using a **hybrid relevance algorithm**.
- Auto-update data using a scheduler.

---

## 🏗️ Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | FastAPI (Python) |
| Database | MongoDB |
| Scheduler | APScheduler |
| ML / Ranking | Scikit-learn (TF-IDF + Cosine Similarity) |
| Language | Python 3.10+ |

---

## 📂 Folder Structure

