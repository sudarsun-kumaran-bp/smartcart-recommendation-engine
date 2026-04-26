# 🛒 SmartCart — AI Product Recommendation Engine

> Natural language product search with explainable recommendations. No paid API. No ML training. 100% free.

![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-F7931E?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🔍 What it does

User types a natural language query → SmartCart returns the top 5 matching products with an AI-generated explanation for each recommendation.

**Example:**
```
Query: "best wireless earphones under 1000"

Result 1: boAt Rockerz 255 Pro — ₹899 — ⭐ 4.3 — 19.8% match
Recommended because: matches your category (earphones), fits your budget (₹899 under ₹1,000), highly rated by users.

Result 2: Redmi Buds 4 Active — ₹999 — ⭐ 4.1 — 14.2% match
Recommended because: matches features: tws, budget, earbuds, fits your budget.
```

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔍 Natural Language Search | Type queries like a human — no keyword tricks needed |
| 💰 Price Filter | Automatically detects "under ₹1000", "below 500", "within 15000" |
| 🧠 Explainable Results | Every recommendation comes with a human-readable reason |
| 📊 Match Score | Confidence percentage for each result |
| 🔒 Secure | Rate limiting, input sanitization, XSS/SQL injection protection |
| 🌐 Web UI | Clean, responsive interface — works on mobile too |
| 📚 Swagger Docs | Full API documentation at `/docs` |

---

## 🏗️ How It Works

```
User Query: "gaming laptop under 70000"
         │
         ▼
  Input Sanitizer (security check)
         │
         ▼
  Price Filter Parser → detects ₹70,000 limit
         │
         ▼
  TF-IDF Vectorizer → converts query + products to vectors
         │
         ▼
  Cosine Similarity → ranks products by relevance
         │
         ▼
  Rule-based Explainer → generates reasons per product
         │
         ▼
  JSON Response + Web UI display
```

---

## 📁 Project Structure

```
smartcart/
├── app/
│   ├── main.py              # FastAPI entry point + web UI serving
│   ├── core/
│   │   ├── recommender.py   # TF-IDF engine + explainer
│   │   └── security.py      # Rate limiting + input sanitization
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

## ⚙️ Setup & Run

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
# Web UI  → http://127.0.0.1:8000
# API docs → http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web UI |
| GET | `/search?q=...` | Search products |
| GET | `/search?q=...&top_n=3` | Get top 3 results |
| GET | `/categories` | List all categories |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger API docs |

### Example API call
```
GET /search?q=budget+smartphone+under+15000&top_n=5
```

---

## 🔒 Security

- **Rate limiting** — 30 requests/minute per IP
- **Input sanitization** — blocks XSS, SQL injection, path traversal
- **Secure headers** — X-Content-Type-Options, X-Frame-Options, XSS-Protection
- **Query length limit** — max 200 characters

---

## 📝 Resume Description

> Built an explainable product recommendation engine using TF-IDF retrieval and rule-based reasoning, served via FastAPI with a responsive web UI. Features include natural language price parsing, cosine similarity ranking, match score confidence, and security middleware (rate limiting, input sanitization, secure headers).

---


## 👨‍💻 Built by

**Sudarsun Kumaran B P** — ECE Final Year, SASTRA Deemed University
