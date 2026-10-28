
import json
import os
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from datetime import datetime, timezone

SOURCE_URL = "https://southfreak.club/"
OUTPUT = "data/movies.json"
MAX_MOVIES = 100

EXCLUDE = {
    "about", "about-us", "contact", "contact-us",
    "disclaimer", "dmca", "privacy-policy", "terms",
    "how-to-download", "category", "tag", "author",
    "page", "search", "feed", "wp-admin", "wp-login"
}


def fetch_html(url):
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urlopen(request, timeout=25) as response:
        return response.read(2500000).decode(
            "utf-8", "replace"
        )


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None
        self.images = []
        self.meta_images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and attrs.get("href"):
            self.current = {
                "href": attrs["href"],
                "text": ""
            }

        if tag == "img":
            src = (
                attrs.get("data-src")
                or attrs.get("data-lazy-src")
                or attrs.get("src")
                or attrs.get("srcset", "").split(",")[0].split(" ")[0]
            )
            if src:
                self.images.append(src)

        if tag == "meta":
            key = (
                attrs.get("property")
                or attrs.get("name")
                or ""
            ).lower()

            if key in ("og:image", "twitter:image"):
                if attrs.get("content"):
                    self.meta_images.append(attrs["content"])

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += " " + data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current)
            self.current = None


def get_poster(page_url):
    try:
        parser = PageParser()
        parser.feed(fetch_html(page_url))

        for raw in parser.meta_images + parser.images:
            image_url = urljoin(page_url, raw.strip())
            parsed = urlparse(image_url)

            if parsed.scheme not in ("http", "https"):
                continue

            if not re.search(
                r"\.(jpg|jpeg|png|webp)(\?|$)",
                parsed.path,
                re.I
            ):
                continue

            if any(word in parsed.path.lower()
                   for word in ("logo", "icon", "avatar", "banner")):
                continue

            return image_url

    except Exception as error:
        print(f"Poster not found: {page_url} ({error})")

    return ""


def main():
    parser = PageParser()
    parser.feed(fetch_html(SOURCE_URL))

    source_host = urlparse(SOURCE_URL).netloc
    movies = []
    seen = set()

    for item in parser.links:
        title = re.sub(r"\s+", " ", item["text"]).strip()
        link = urljoin(SOURCE_URL, item["href"])
        parsed = urlparse(link)
        path = parsed.path.strip("/")
        slug = path.split("/")[-1].lower() if path else ""

        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc != source_host or not path:
            continue
        if not title or len(title) < 3 or len(title) > 160:
            continue
        if slug in EXCLUDE:
            continue
        if any(part in ("category", "tag", "author", "page")
               for part in path.lower().split("/")):
            continue
        if link in seen:
            continue

        seen.add(link)
        movies.append({
            "title": title,
            "category": "Other",
            "year": "",
            "source_url": link,
            "poster_url": "",
            "description": "Visit the original source page.",
            "published_at": ""
        })

        if len(movies) >= MAX_MOVIES:
            break

    if not movies:
        raise RuntimeError(
            "No movie listings found; existing data was kept."
        )

    for index, movie in enumerate(movies, start=1):
        movie["poster_url"] = get_poster(movie["source_url"])
        print(
            f"{index}/{len(movies)}: "
            f"{movie['title']} - "
            f"{'Poster found' if movie['poster_url'] else 'No poster found'}"
        )

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump({
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "movies": movies
        }, file, ensure_ascii=False, indent=2)

    print(f"Updated {len(movies)} listings.")


if __name__ == "__main__":
    main()
