import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

# ──────────────────────────────────────────────────────────────
# Global pre‑computed data (initialised once)
# ──────────────────────────────────────────────────────────────

_vectorizer = None
_product_vectors = None
_all_products = None   # list of dicts with all product data


def init_recommender(db_session):
    """
    Call this once on application startup to pre‑compute TF‑IDF vectors.
    This avoids recomputing the entire matrix on every search request.
    """
    global _vectorizer, _product_vectors, _all_products
    from app.models import Product

    products_db = db_session.query(Product).all()
    if not products_db:
        _all_products = []
        _product_vectors = None
        _vectorizer = None
        return

    # Build product dictionary list and text corpus
    _all_products = []
    corpus = []
    for p in products_db:
        prod_dict = {
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "price": p.price,
            "rating": p.rating,
            "description": p.description,
            "tags": p.tags.split(",") if isinstance(p.tags, str) else []
        }
        _all_products.append(prod_dict)

        # Text used for TF‑IDF: name + category + brand + description + tags
        text = f"{p.name} {p.category} {p.brand} {p.description} {' '.join(prod_dict['tags'])}"
        corpus.append(text.lower())

    # Fit vectorizer and transform all products
    _vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    _product_vectors = _vectorizer.fit_transform(corpus)


def parse_price_filter(query: str):
    """Extract budget constraint from natural language query."""
    query_lower = query.lower()
    patterns = [
        r'under\s*₹?\s*(\d+)',
        r'below\s*₹?\s*(\d+)',
        r'less than\s*₹?\s*(\d+)',
        r'within\s*₹?\s*(\d+)',
        r'budget\s*₹?\s*(\d+)',
        r'max\s*₹?\s*(\d+)',
        r'upto\s*₹?\s*(\d+)',
        r'up to\s*₹?\s*(\d+)',
        r'₹\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return int(match.group(1))
    return None


def generate_explanation(product_dict, query, match_score):
    """Rule‑based explainer for each recommendation."""
    query_lower = query.lower()
    reasons = []
    tags = product_dict['tags']  # already a list

    if product_dict['category'].lower() in query_lower:
        reasons.append(f"matches your category ({product_dict['category']})")

    if product_dict['brand'].lower() in query_lower:
        reasons.append(f"matches your preferred brand ({product_dict['brand']})")

    matched_tags = [t.strip() for t in tags if t.strip().lower() in query_lower]
    if matched_tags:
        reasons.append(f"matches features: {', '.join(matched_tags[:3])}")

    if product_dict['rating'] >= 4.5:
        reasons.append("top-rated product (4.5+)")
    elif product_dict['rating'] >= 4.2:
        reasons.append("highly rated by users")

    price_limit = parse_price_filter(query)
    if price_limit and product_dict['price'] <= price_limit:
        reasons.append(f"fits your budget (₹{product_dict['price']:,} under ₹{price_limit:,})")
    elif product_dict['price'] < 1000:
        reasons.append("budget-friendly option")
    elif product_dict['price'] > 20000:
        reasons.append("premium quality product")

    if match_score > 0.5:
        reasons.append("strong keyword match with your query")
    elif match_score > 0.2:
        reasons.append("relevant to your search")

    if not reasons:
        reasons.append(f"relevant {product_dict['category']} with good ratings")

    return "Recommended because: " + ", ".join(reasons) + "."


def search_products(query: str, db, top_n: int = 5):
    """
    Main search using pre‑computed TF‑IDF vectors (if available).
    Falls back to on‑the‑fly computation if not initialised.
    """
    global _vectorizer, _product_vectors, _all_products

    # 1. If pre‑computed data missing, compute on the fly (fallback)
    if _vectorizer is None or _all_products is None:
        return _search_products_fallback(query, db, top_n)

    # 2. Parse price filter
    price_limit = parse_price_filter(query)

    # 3. Filter products by price (using pre‑loaded _all_products)
    filtered_products = []
    for p in _all_products:
        if price_limit is None or p['price'] <= price_limit:
            filtered_products.append(p)

    # No products within budget → return empty (no fallback)
    if not filtered_products:
        return []

    # 4. Build corpus for filtered products + query (still need to vectorise filtered set)
    #    Note: we cannot directly use _product_vectors because we filtered.
    #    For simplicity and correctness, we transform the filtered products.
    #    For larger datasets, you would filter after scoring using _product_vectors.
    corpus = []
    for p in filtered_products:
        text = f"{p['name']} {p['category']} {p['brand']} {p['description']} {' '.join(p['tags'])}"
        corpus.append(text.lower())
    corpus.append(query.lower())

    # Transform using the existing (global) vectorizer – do NOT refit!
    tfidf_matrix = _vectorizer.transform(corpus)
    query_vector = tfidf_matrix[-1]
    product_vectors = tfidf_matrix[:-1]
    scores = cosine_similarity(query_vector, product_vectors).flatten()

    # 5. Rank and return top N
    top_indices = np.argsort(scores)[::-1][:top_n]
    results = []
    for idx in top_indices:
        p = filtered_products[idx]
        score = float(scores[idx])
        results.append({
            "id": p["id"],
            "name": p["name"],
            "brand": p["brand"],
            "category": p["category"],
            "price": p["price"],
            "rating": p["rating"],
            "match_score": round(score * 100, 1),
            "explanation": generate_explanation(p, query, score),
            "tags": p["tags"]
        })
    return results


def _search_products_fallback(query: str, db, top_n: int = 5):
    """
    Original on‑the‑fly computation (used when pre‑computed data is not available).
    This also has the price fallback removed.
    """
    from app.models import Product

    price_limit = parse_price_filter(query)

    if price_limit:
        db_products = db.query(Product).filter(Product.price <= price_limit).all()
    else:
        db_products = db.query(Product).all()

    if not db_products:
        return []

    products = []
    for p in db_products:
        products.append({
            "id": p.id,
            "name": p.name,
            "brand": p.brand,
            "category": p.category,
            "price": p.price,
            "rating": p.rating,
            "description": p.description,
            "tags": p.tags.split(",")
        })

    corpus = []
    for p in products:
        text = f"{p['name']} {p['category']} {p['brand']} {p['description']} {' '.join(p['tags'])}"
        corpus.append(text.lower())
    corpus.append(query.lower())

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except Exception:
        return []

    query_vector = tfidf_matrix[-1]
    product_vectors = tfidf_matrix[:-1]
    scores = cosine_similarity(query_vector, product_vectors).flatten()

    top_indices = np.argsort(scores)[::-1][:top_n]

    results = []
    for idx in top_indices:
        p = products[idx]
        score = float(scores[idx])
        results.append({
            "id": p["id"],
            "name": p["name"],
            "brand": p["brand"],
            "category": p["category"],
            "price": p["price"],
            "rating": p["rating"],
            "match_score": round(score * 100, 1),
            "explanation": generate_explanation(p, query, score),
            "tags": p["tags"]
        })
    return results
