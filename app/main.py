from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.routers import search
from app.core.security import add_security_headers
from app.database import engine, Base, SessionLocal
from app.core.recommender import init_recommender
import os

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartCart — AI Product Recommendation API",
    description="""
## SmartCart

Natural language product search with explainable AI recommendations.

**Database:** SQLite via SQLAlchemy ORM

**Search Engine:** TF-IDF + Cosine Similarity

### Example queries
- `best earphones under 1000`
- `gaming laptop RTX`
- `budget smartphone 5G under 15000`
- `smartwatch with calling feature`
""",
    version="2.0.0",
)

# ─── Startup event: pre‑compute TF‑IDF vectors ─────────────────
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        init_recommender(db)
        print("✅ Recommender initialised with pre‑computed TF‑IDF vectors")
    except Exception as e:
        print(f"⚠️ Failed to initialise recommender: {e}")
    finally:
        db.close()

# ─── Middleware ────────────────────────────────────────────────
app.middleware("http")(add_security_headers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────
app.include_router(search.router, tags=["🔍 Search"])

# ─── Serve frontend HTML ───────────────────────────────────────
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "../templates/index.html")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
