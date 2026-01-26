import requests
from bs4 import BeautifulSoup

URL = "https://learn.microsoft.com/en-us/entra/fundamentals/whats-new"

def fetch_index():
    r = requests.get(URL, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("main a"):
        href = a.get("href") or ""
        title = (a.get_text() or "").strip()
        if not title or not href:
            continue
        if href.startswith("/"):
            href = "https://learn.microsoft.com" + href
        if "/entra/" not in href:
            continue
        items.append({"title": title, "url": href})
    # Dedup by url
    uniq = {i["url"]: i for i in items}
    return list(uniq.values())

def enrich_detail(idx: dict) -> dict:
    url = idx["url"]
    title = idx["title"]

    r = requests.get(url, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text(" ", strip=True)

    hay = f"{title} {text}".lower()
    stage = "Unknown"
    if "generally available" in hay or "general availability" in hay:
        stage = "GA"
    elif "preview" in hay:
        stage = "Preview"

    return {
        "source": "entra_whatsnew",
        "source_uid": url,
        "source_url": url,
        "title": title[:300],
        "summary": None,
        "product": "Microsoft Entra",
        "tags": ["entra", "identity"],
        "release_stage": stage,
        "published_at": None,
        "updated_at": None,
        "body_text": text[:20000],
        "raw": {"page": url},
    }
