  from fastapi import FastAPI, Query
from .db import init_db, query_events
from .digest import build_digest
from .config import DEFAULT_GA_ONLY

app = FastAPI(title="Microsoft Changes Collector", version="1.0")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/events")
def events(
    since: str | None = Query(None, description="ISO8601 timestamp"),
    security_only: bool = Query(False),
    ga_only: bool = Query(DEFAULT_GA_ONLY),
    limit: int = Query(100, ge=1, le=500),
):
    return {"items": query_events(since_iso=since, security_only=security_only, ga_only=ga_only, limit=limit)}

@app.get("/digest")
def digest(
    hours: int = Query(24, ge=1, le=168),
    security_only: bool = Query(True),
    ga_only: bool = Query(DEFAULT_GA_ONLY),
    limit: int = Query(200, ge=1, le=500),
):
    return build_digest(hours=hours, security_only=security_only, ga_only=ga_only, limit=limit)
