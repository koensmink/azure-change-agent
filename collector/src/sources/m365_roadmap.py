import requests
import feedparser

ROADMAP_API = "https://www.microsoft.com/releasecommunications/api/v1/m365"  # widely referenced
ROADMAP_RSS = "https://www.microsoft.com/microsoft-365/RoadmapFeatureRSS"     # RSS feed

def fetch_index():
    # Try API first
    try:
        r = requests.get(ROADMAP_API, timeout=30, headers={"Accept": "application/json"})
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return {"mode": "api", "items": data}
    except Exception:
        pass

    # Fallback to RSS
    d = feedparser.parse(ROADMAP_RSS)
    return {"mode": "rss", "items": getattr(d, "entries", [])}

def enrich_detail(item: dict, mode: str) -> dict:
    if mode == "api":
        title = item.get("Title") or item.get("title") or "Untitled"
        status = (item.get("Status") or item.get("status") or "").strip()
        stage = "Unknown"
        if status.lower() == "launched":
            stage = "GA"
        elif status.lower() in ("rolling out", "in development"):
            stage = "Planned"

        source_uid = str(item.get("Id") or item.get("id") or title)
        url = item.get("MoreInfoLink") or item.get("moreInfoLink") or item.get("PublicDisclosureLink") or ROADMAP_API

        summary = item.get("Description") or item.get("description")
        product = None
        # Some responses contain product containers/tags; keep lightweight
        tags = []
        if item.get("Tags"):
            tags += [str(t) for t in item.get("Tags", [])]
        if item.get("Products"):
            tags += [str(p) for p in item.get("Products", [])]

        published = item.get("LastModified") or item.get("lastModified")
        updated = item.get("LastModified") or item.get("lastModified")
        body = summary or ""

        return {
            "source": "m365_roadmap",
            "source_uid": source_uid,
            "source_url": url or ROADMAP_API,
            "title": str(title)[:300],
            "summary": summary,
            "product": product or "Microsoft 365 Roadmap",
            "tags": list(dict.fromkeys([t for t in tags if t])),
            "release_stage": stage,
            "published_at": published,
            "updated_at": updated,
            "body_text": body,
            "raw": {"roadmap_api": item},
        }

    # RSS mode
    title = getattr(item, "title", None) or item.get("title") or "Untitled"
    url = getattr(item, "link", None) or item.get("link") or ROADMAP_RSS
    source_uid = url
    summary = getattr(item, "summary", None) or item.get("summary")
    published = getattr(item, "published", None) or item.get("published")
    updated = getattr(item, "updated", None) or item.get("updated")

    # RSS usually contains both launched and not; infer stage via title/summary keywords
    hay = f"{title} {summary or ''}".lower()
    stage = "Unknown"
    if "launched" in hay or "generally available" in hay or "general availability" in hay:
        stage = "GA"
    elif "rolling out" in hay:
        stage = "Planned"
    elif "preview" in hay:
        stage = "Preview"

    return {
        "source": "m365_roadmap",
        "source_uid": source_uid,
        "source_url": url,
        "title": str(title)[:300],
        "summary": summary,
        "product": "Microsoft 365 Roadmap",
        "tags": [],
        "release_stage": stage,
        "published_at": published,
        "updated_at": updated,
        "body_text": summary or "",
        "raw": {"roadmap_rss": dict(item)},
    }
