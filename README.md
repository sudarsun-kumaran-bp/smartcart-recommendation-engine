# SmartCart — AI Product Recommendation Engine

Natural language product search with explainable recommendations. No paid API. No ML training. 100% free.

[Python](https://www.python.org/) | [FastAPI](https://fastapi.tiangolo.com/) | [scikit-learn](https://scikit-learn.org/) | [MIT License](LICENSE)

## What it does

User types a natural language query → SmartCart returns the top 5 matching products with an AI-generated explanation for each recommendation.

### Example

**Query:** "best wireless earphones under 1000"

**Result 1:** boAt Rockerz 255 Pro — Rs.899 — Rating 4.3 — 19.8% match  
*Recommended because: matches your category (earphones), fits your budget (Rs.899 under Rs.1,000), highly rated by users.*

**Result 2:** Redmi Buds 4 Active — Rs.999 — Rating 4.1 — 14.2% match  
*Recommended because: matches features: tws, budget, earbuds, fits your budget.*

---

## Features

| Feature | Description |
|---------|-------------|
| Natural Language Search | Type queries like a human — no keyword tricks needed |
| Price Filter | Automatically detects "under Rs.1000", "below 500", "within 15000" |
| Explainable Results | Every recommendation comes with a human-readable reason |
| Match Score | Confidence percentage for each result |
| Secure | Rate limiting, input sanitisation (XSS/path traversal/code injection), SQL injection prevented via SQLAlchemy ORM |
| Web UI | Clean, responsive interface — works on mobile too |
| Swagger Docs | Full API documentation at /docs |

---

## How It Works

```
User Query: "gaming laptop under 70000"
         |
         v
  Input Sanitizer (security check)
         |
         v
  Price Filter Parser -> detects Rs.70,000 limit
         |
         v
  TF-IDF Vectorizer -> converts query + products to vectors
         |
         v
  Cosine Similarity -> ranks products by relevance
         |
         v
  Rule-based Explainer -> generates reasons per product
         |
         v
  JSON Response + Web UI display
```

---

## Project Structure

```
smartcart/
├── app/
│   ├── main.py              # FastAPI entry point + web UI serving
│   ├── core/
│   │   ├── recommender.py   # TF-IDF engine + explainer
│   │   └── security.py      # Rate limiting + input sanitisation
│   ├── routers/
│   │   └── search.py        # /search and /categories endpoints
│   └── data/
│       └── products.json    # 50+ product catalog
├── templates/
│   └── index.html           # Frontend web UI
├── requirements.txt
└── README.md
```

---


## Setup & Run

```bash
# 1. Enter project folder
cd smartcart

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start server
uvicorn app.main:app --reload

# 5. Open in browser
# Web UI  -> http://127.0.0.1:8000
# API docs -> http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Web UI |
| GET | /search?q=... | Search products |
| GET | /search?q=...&top_n=3 | Get top 3 results |
| GET | /categories | List all categories |
| GET | /health | Health check |
| GET | /docs | Swagger API docs |

### Example API call

```http
GET /search?q=budget+smartphone+under+15000&top_n=5
```

Response (abbreviated):
```json
{
  "query": "budget smartphone under 15000",
  "total_results": 3,
  "results": [
    {
      "id": 5,
      "name": "Realme Narzo 60 5G",
      "match_score": 22.4,
      "explanation": "Recommended because: fits your budget..."
    }
  ]
}
```

---

## Security

- Rate limiting — 30 requests/minute per IP (in‑memory; for production use Redis)
- Input sanitisation — blocks XSS, path traversal, and code injection patterns
- SQL injection safe — SQLAlchemy ORM with parameterised queries
- Secure HTTP headers — X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, etc.
- Query length limit — max 200 characters

---

## Future improvements (if scaling)

- Pre‑compute TF‑IDF vectors once at startup (already done)
- Replace in‑memory rate limiter with Redis for multi‑worker deployments
- Use a vector database (FAISS, Pinecone) for >10k products
- Add unit and integration tests
- Dockerise the application

---

## Resume Description

Built an explainable product recommendation engine using TF‑IDF retrieval and rule‑based reasoning, served via FastAPI with a responsive web UI. Features include natural language price parsing, cosine similarity ranking, match score confidence, and security middleware (rate limiting, input sanitisation, secure headers).

---

## Built by

Sudarsun Kumaran B P — ECE Final Year, SASTRA Deemed University  
[GitHub](https://github.com/sudarsun-kumaran-bp) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
```
