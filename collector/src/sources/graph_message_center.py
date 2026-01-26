import requests
from datetime import datetime, timezone, timedelta
from dateutil import parser as dtp

from ..config import GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_ENDPOINT, SOURCE_LOOKBACK_DAYS

TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

def _get_token():
    if not (GRAPH_TENANT_ID and GRAPH_CLIENT_ID and GRAPH_CLIENT_SECRET):
        raise RuntimeError("Graph credentials missing: GRAPH_TENANT_ID/GRAPH_CLIENT_ID/GRAPH_CLIENT_SECRET")

    url = TOKEN_URL.format(tenant_id=GRAPH_TENANT_ID)
    data = {
        "client_id": GRAPH_CLIENT_ID,
        "client_secret": GRAPH_CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default",
    }
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def fetch_index():
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # Pull recent-ish messages; Graph supports $top and paging.
    # We'll do a simple first page pull; you can expand paging if needed.
    url = f"{GRAPH_ENDPOINT}/admin/serviceAnnouncement/messages?$top=200"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("value", [])

def enrich_detail(msg: dict) -> dict:
    # msg is already "detail enough"; treat it as detail record
    title = msg.get("title") or "Untitled"
    body = ""
    body_obj = msg.get("body", {})
    if isinstance(body_obj, dict):
        body = body_obj.get("content", "") or ""

    published = msg.get("startDateTime") or msg.get("createdDateTime")
    updated = msg.get("lastModifiedDateTime")

    # Stage heuristics: Message center doesn't always say GA; keep Unknown unless clearly stated
    stage = "Unknown"
    hay = f"{title} {msg.get('category','')} {body}".lower()
    if "general availability" in hay or "generally available" in hay or "ga" in hay:
        stage = "GA"
    elif "public preview" in hay or "preview" in hay:
        stage = "Preview"
    elif "retire" in hay or "retirement" in hay or "deprecated" in hay:
        stage = "Retirement"

    tags = []
    if msg.get("category"):
        tags.append(msg["category"])
    if msg.get("tags"):
        tags += [str(t) for t in msg.get("tags", [])]

    # stable id
    source_uid = msg.get("id") or ""

    # There's no single public URL; keep source_url as a synthetic link to Graph item
    source_url = f"{GRAPH_ENDPOINT}/admin/serviceAnnouncement/messages/{source_uid}" if source_uid else "graph://serviceAnnouncement/messages"

    return {
        "source": "graph_message_center",
        "source_uid": source_uid,
        "source_url": source_url,
        "title": title[:300],
        "summary": (msg.get("services") and f"Services: {', '.join(msg.get('services', []))}") or None,
        "product": "Microsoft 365 (Message Center)",
        "tags": list(dict.fromkeys([t for t in tags if t])),
        "release_stage": stage,
        "published_at": published,
        "updated_at": updated,
        "body_text": body,
        "raw": {"graph": msg},
    }
