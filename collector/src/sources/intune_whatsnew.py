import requests
from bs4 import BeautifulSoup

URL = "https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/whats-new"

def fetch_index():
    # single page acts as index; we'll treat headings as items
    r = requests.get(URL, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    items = []
    for h in soup.select("main h2, main h3"):
        title = (h.get_text() or "").strip()
        if not title:
            continue
        anchor = h.find("a")
        frag = ""
        if anchor and anchor.get("id"):
            frag = "#" + anchor["id"]
        items.append({"title": title, "url": URL + frag})
    return items

def enrich_detail(idx: dict) -> dict:
    # For simplicity: detail is still the main page; body_text is extracted section text is hard without heavy parsing.
    title = idx["title"]
    url = idx["url"]

    r = requests.get(URL, timeout=30, headers={"User-Agent": "ms-changes-collector/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text(" ", strip=True)

    hay = f"{title} {text}".lower()
    stage = "GA"
    if "preview" in hay or "public preview" in hay:
        stage = "Preview"

    return {
        "source": "intune_whatsnew",
        "source_uid": url,
        "source_url": url,
        "title": title[:300],
        "summary": None,
        "product": "Microsoft Intune",
        "tags": ["intune"],
        "release_stage": stage,
        "published_at": None,
        "updated_at": None,
        "body_text": text[:20000],
        "raw": {"page": URL},
    }
