from fastapi import Request, HTTPException
from collections import defaultdict
import time
import re

# ─── Rate Limiter ─────────────────────────────────────────────
# Simple in-memory rate limiter: max 30 requests per minute per IP

RATE_LIMIT = 30          # max requests
RATE_WINDOW = 60         # per 60 seconds

request_counts = defaultdict(list)


def rate_limit_check(request: Request):
    ip = request.client.host
    now = time.time()

    # Remove old timestamps outside the window
    request_counts[ip] = [t for t in request_counts[ip] if now - t < RATE_WINDOW]

    if len(request_counts[ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please slow down and try again in a minute."
        )

    request_counts[ip].append(now)


# ─── Input Sanitizer ─────────────────────────────────────────
MAX_QUERY_LENGTH = 200
BLOCKED_PATTERNS = [
    r'<script.*?>',        # XSS
    r'javascript:',        # JS injection
    r'SELECT.*FROM',       # SQL injection
    r'DROP\s+TABLE',       # SQL drop
    r'INSERT\s+INTO',      # SQL insert
    r'--',                 # SQL comment
    r'\.\./\.\.',          # Path traversal
    r'eval\(',             # Code eval
    r'exec\(',             # Code exec
]


def sanitize_query(query: str) -> str:
    """Sanitize and validate search query."""
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    query = query.strip()

    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Maximum {MAX_QUERY_LENGTH} characters allowed."
        )

    # Check for injection patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Invalid characters detected in query."
            )

    # Strip HTML tags
    query = re.sub(r'<[^>]+>', '', query)

    return query


# ─── Secure Headers Middleware ────────────────────────────────
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store"
    return response
