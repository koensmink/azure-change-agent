import hashlib
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def stable_url(url: str) -> str:
    """Remove tracking params and normalize."""
    try:
        p = urlparse(url)
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if k.lower() not in ("utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content")]
        new_q = urlencode(q)
        return urlunparse((p.scheme, p.netloc, p.path.rstrip("/"), p.params, new_q, ""))
    except Exception:
        return url

def text_norm(s: str | None) -> str:
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s).strip()
    return s

def make_event_id(source: str, source_uid: str, url: str) -> str:
    base = f"{source}|{source_uid or stable_url(url)}"
    return "sha256:" + hashlib.sha256(base.encode()).hexdigest()

def make_content_hash(payload: dict) -> str:
    """
    Hash over normalized fields that should trigger 'CHANGED' when they change.
    """
    parts = [
        text_norm(payload.get("title")),
        text_norm(payload.get("summary")),
        text_norm(payload.get("product")),
        text_norm(payload.get("release_stage")),
        text_norm(payload.get("published_at")),
        text_norm(payload.get("updated_at")),
        " ".join(sorted([text_norm(t).lower() for t in (payload.get("tags") or [])])),
        text_norm(payload.get("body_text")),
    ]
    base = "|".join(parts)
    return "sha256:" + hashlib.sha256(base.encode()).hexdigest()
