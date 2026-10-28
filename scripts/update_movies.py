import json
import re
import os
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone

SOURCE_URL = "https://southfreak.club/"
OUTPUT = "data/movies.json"

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.current = {"href": attrs["href"], "text": ""}

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += " " + data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current)
            self.current = None

def main():
    request = Request(
        SOURCE_URL,
        headers={"User-Agent": "CineFind listing indexer/1.0"}
    )
    with urlopen(request, timeout=20) as response:
        html = response.read(3_000_000).decode("utf-8", "replace")

    parser = LinkParser()
    parser.feed(html)

    source_host = urlparse(SOURCE_URL).netloc
    movies = []
    seen = set()

    for item in parser.links:
        title = re.sub(r"\s+", " ", item["text"]).strip()
        link = urljoin(SOURCE_URL, item["href"])

        if len(title) < 3 or len(title) > 160:
            continue
        if urlparse(link).netloc != source_host:
            continue
        if link.rstrip("/") == SOURCE_URL.rstrip("/"):
            continue
        if link in seen:
            continue

        seen.add(link)
        movies.append({
            "title": title,
            "category": "Other",
            "year": "",
            "source_url": link,
            "description": "Visit the original source page.",
            "published_at": ""
        })

    if not movies:
        raise RuntimeError("No listings found; keeping the existing data.")

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "movies": movies[:250]
        }, f, ensure_ascii=False, indent=2)

    print(f"Saved {min(len(movies), 250)} listing links.")

if __name__ == "__main__":
    main()
