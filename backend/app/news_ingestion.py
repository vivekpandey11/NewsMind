import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import feedparser

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "news_articles.json"

FEEDS = {
    "BBC News": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "NPR News": "https://feeds.npr.org/1001/rss.xml",
}

TRACKING_PARAMS = {
    "fbclid", "gclid", "mc_cid", "mc_eid"
}


def normalize_url(url):
    if not url:
        return ""

    parts = urlsplit(url.strip())

    # Remove common tracking parameters
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query)
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_PARAMS
    ]

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/"),
        urlencode(query),
        ""  # Remove fragments
    ))


def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def fetch_news(limit_per_feed=5):
    articles = []

    for source, url in FEEDS.items():
        print(f"Fetching from {source}...")

        try:
            feed = feedparser.parse(url)

            if getattr(feed, "bozo", False) and not feed.entries:
                print(f"Feed unavailable or invalid: {source}")
                continue

            for entry in feed.entries[:limit_per_feed]:
                title = clean_text(entry.get("title", ""))
                link = normalize_url(entry.get("link", ""))

                if not title or not link:
                    continue

                articles.append({
                    "title": title,
                    "source": source,
                    "link": link,
                    "published": entry.get(
                        "published",
                        entry.get("updated", "Date unavailable")
                    ),
                    "summary": clean_text(entry.get("summary", "")),
                })

        except Exception as exc:
            print(f"{source} failed: {type(exc).__name__}")

    # Remove duplicate URLs while preserving the first occurrence
    unique_articles = []
    seen_urls = set()

    for article in articles:
        if article["link"] in seen_urls:
            continue

        seen_urls.add(article["link"])
        unique_articles.append(article)

    return unique_articles


if __name__ == "__main__":
    news = fetch_news()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(news, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\nArticles fetched and cleaned: {len(news)}")
    print(f"Unique URLs: {len({a['link'] for a in news})}")
    print(f"Saved to: {OUTPUT_FILE}")

    for index, article in enumerate(news, start=1):
        print(f"\n{index}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Published: {article['published']}")
        print(f"   Link: {article['link']}")
