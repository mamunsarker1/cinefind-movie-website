
import json
import os
import re
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone

SOURCE_URL = "https://southfreak.club/"
OUTPUT = "data/movies.json"

# সাধারণ ওয়েবসাইটের পেজ বাদ দেওয়ার তালিকা
EXCLUDE = {
    "about", "about-us", "contact", "contact-us",
    "disclaimer", "dmca", "privacy-policy", "terms",
    "how-to-download", "category", "tag", "author",
    "page", "search", "feed", "wp-admin", "wp-login"
}

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
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=30) as response:
        html = response.read(4_000_000).decode("utf-8", "replace")

    parser = LinkParser()
    parser.feed(html)

    source_host = urlparse(SOURCE_URL).netloc
    movies = []
    seen = set()

    for item in parser.links:
        title = re.sub(r"\s+", " ", item["text"]).strip()
        link = urljoin(SOURCE_URL, item["href"])
        parsed = urlparse(link)
        path_parts = [p.lower() for p in parsed.path.strip("/").split("/") if p]

        if parsed.netloc != source_host:
            continue
        if len(title) < 3 or len(title) > 160:
            continue
        if link.rstrip("/") == SOURCE_URL.rstrip("/"):
            continue
        if any(part in EXCLUDE for part in path_parts):
            continue
        if parsed.path.rstrip("/") in ("", "/"):
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
        raise RuntimeError(
            "No eligible links found. Keeping existing movie data."
        )

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "movies": movies[:250]
        }, f, ensure_ascii=False, indent=2)

    print(f"Saved {min(len(movies), 250)} candidate links.")

if __name__ == "__main__":
    main()
