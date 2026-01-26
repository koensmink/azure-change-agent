import requests
from bs4 import BeautifulSoup

URL = "https://learn.microsoft.com/en-us/defender-endpoint/whats-new-in-microsoft-defender-endpoint"

def fetch_index():
    r = requests.get(URL, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for h in soup.select("main h2, main h3"):
        title = (h.get_text() or "").strip()
        if not title:
            continue
        items.append({"title": title, "url": URL})
    return items

def enrich_detail(idx: dict) -> dict:
    title = idx["title"]
    r = requests.get(URL, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
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
        "source": "defender_whatsnew",
        "source_uid": f"{URL}::{title}",
        "source_url": URL,
        "title": title[:300],
        "summary": None,
        "product": "Microsoft Defender for Endpoint",
        "tags": ["defender", "mde"],
        "release_stage": stage,
        "published_at": None,
        "updated_at": None,
        "body_text": text[:20000],
        "raw": {"page": URL},
    }
