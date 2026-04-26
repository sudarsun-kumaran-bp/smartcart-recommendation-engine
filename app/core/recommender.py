import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
    """Rule-based explainer for each recommendation."""
    query_lower = query.lower()
    reasons = []
    tags = product_dict['tags'] if isinstance(product_dict['tags'], list) else product_dict['tags'].split(',')

    if product_dict['category'].lower() in query_lower:
        reasons.append(f"matches your category ({product_dict['category']})")

    if product_dict['brand'].lower() in query_lower:
        reasons.append(f"matches your preferred brand ({product_dict['brand']})")

    matched_tags = [t.strip() for t in tags if t.strip() in query_lower]
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
    Main search:
    1. Query SQLite via SQLAlchemy
    2. Apply price filter
    3. TF-IDF + cosine similarity
    4. Return ranked results with explanations
    """
    from app.models import Product

    # Step 1: Fetch all products from DB
    price_limit = parse_price_filter(query)

    if price_limit:
        # SQL WHERE clause — price filter in the database
        db_products = db.query(Product).filter(Product.price <= price_limit).all()
        if not db_products:
            db_products = db.query(Product).all()  # fallback
    else:
        db_products = db.query(Product).all()

    if not db_products:
        return []

    # Convert ORM objects to dicts
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

    # Step 2: Build TF-IDF corpus
    corpus = []
    for p in products:
        text = f"{p['name']} {p['category']} {p['brand']} {p['description']} {' '.join(p['tags'])}"
        corpus.append(text.lower())

    corpus.append(query.lower())  # query is last

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except Exception:
        return []

    query_vector = tfidf_matrix[-1]
    product_vectors = tfidf_matrix[:-1]
    scores = cosine_similarity(query_vector, product_vectors).flatten()

    # Step 3: Rank and return top N
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
