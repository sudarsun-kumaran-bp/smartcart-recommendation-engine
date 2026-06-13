import logging
from fastapi import APIRouter, Query, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.recommender import search_products
from app.core.security import sanitize_query, rate_limit_check
from app.database import get_db
from app.models import Product
from pydantic import BaseModel
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class ProductOut(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: int
    rating: float
    match_score: float
    explanation: str
    tags: List[str]


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[ProductOut]


@router.get("/search", response_model=SearchResponse)
def search(
    request: Request,
    q: str = Query(..., description="e.g. 'best earphones under 1000'"),
    top_n: Optional[int] = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_check)
):
    """Search products using natural language. Results ranked by TF-IDF cosine similarity."""
    clean_query = sanitize_query(q)
    try:
        results = search_products(clean_query, db=db, top_n=top_n)
    except Exception as e:
        logger.error(f"Search failed for query '{clean_query}': {e}")
        raise HTTPException(status_code=500, detail="Internal search error")
    return {"query": clean_query, "total_results": len(results), "results": results}


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all product categories from the database."""
    categories = db.query(Product.category).distinct().order_by(Product.category).all()
    return {"categories": [c[0] for c in categories]}


@router.get("/products/count")
def product_count(db: Session = Depends(get_db)):
    """Total number of products in the database."""
    count = db.query(Product).count()
    return {"total_products": count}


@router.get("/health")
def health():
    return {"status": "ok", "service": "SmartCart API", "database": "SQLite"}
