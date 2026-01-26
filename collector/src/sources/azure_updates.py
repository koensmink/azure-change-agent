import requests
from bs4 import BeautifulSoup

INDEX = "https://azure.microsoft.com/en-us/updates/"

def fetch_index():
    r = requests.get(INDEX, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for a in soup.select("a"):
        href = a.get("href") or ""
        text = (a.get_text() or "").strip()
        if "/updates/" not in href:
            continue
        if href.startswith("/"):
            href = "https://azure.microsoft.com" + href
        if not text:
            text = "Azure update"
        items.append({"title": text, "url": href})

    uniq = {i["url"]: i for i in items}
    return list(uniq.values())

def enrich_detail(idx: dict) -> dict:
    url = idx["url"]
    r = requests.get(url, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text(" ", strip=True)

    # Heuristic stage detection
    hay = text.lower()
    stage = "Unknown"
    if "generally available" in hay or "general availability" in hay:
        stage = "GA"
    elif "preview" in hay:
        stage = "Preview"
    elif "retire" in hay or "retirement" in hay or "deprecated" in hay:
        stage = "Retirement"

    title = idx["title"]
    # attempt: use page title if better
    h1 = soup.select_one("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)

    return {
        "source": "azure_updates",
        "source_uid": url,
        "source_url": url,
        "title": title[:300],
        "summary": None,
        "product": "Azure",
        "tags": ["azure"],
        "release_stage": stage,
        "published_at": None,
        "updated_at": None,
        "body_text": text[:20000],
        "raw": {"page": url},
    }
