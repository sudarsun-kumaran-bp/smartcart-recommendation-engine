"""
Run this once to populate the SQLite database from products.json.
Usage: python seed_db.py
"""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import Product

def seed():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if already seeded
    existing = db.query(Product).count()
    if existing > 0:
        print(f"Database already has {existing} products. Skipping seed.")
        db.close()
        return

    # Load JSON
    json_path = os.path.join(os.path.dirname(__file__), "app/data/products.json")
    with open(json_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    # Insert into DB
    for p in products:
        product = Product(
            id=p["id"],
            name=p["name"],
            brand=p["brand"],
            category=p["category"],
            price=p["price"],
            rating=p["rating"],
            description=p["description"],
            tags=",".join(p["tags"])
        )
        db.add(product)

    db.commit()
    db.close()
    print(f"✅ Seeded {len(products)} products into smartcart.db")

if __name__ == "__main__":
    seed()
