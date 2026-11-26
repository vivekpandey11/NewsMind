import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "news_articles.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "ranked_news.json"

# NewsMind user's interest profile.
# Each category contains keywords and alternative phrases.
USER_INTERESTS = {
    "AI & Machine Learning": [
        "artificial intelligence", "AI", "machine learning",
        "ML", "generative AI", "large language model",
        "LLM", "neural network", "deep learning"
    ],
    "Technology": [
        "technology", "tech", "software", "cybersecurity",
        "cloud computing", "smartphone", "semiconductor",
        "robotics", "social media"
    ],
    "Business & Startups": [
        "business", "startup", "startups", "entrepreneur",
        "funding", "venture capital", "company", "corporate",
        "IPO", "merger", "acquisition"
    ],
    "India News": [
        "India", "Indian", "New Delhi", "Mumbai", "Bengaluru",
        "Gwalior", "Rupee"
    ],
    "Sports": [
        "sports", "sport", "cricket", "football", "tennis",
        "Olympics", "tournament", "athlete", "championship"
    ],
    "Entertainment": [
        "entertainment", "film", "films", "movie", "movies",
        "actor", "actress", "music", "celebrity",
        "Netflix", "streaming"
    ],
    "World News": [
        "international", "global", "world", "war", "conflict",
        "diplomacy", "geopolitical", "president", "government"
    ],
    "Finance & Economy": [
        "finance", "economy", "economic", "inflation",
        "stock market", "stocks", "shares", "banking",
        "GDP", "interest rates", "trade", "budget"
    ],
    "Science & Research": [
        "science", "scientific", "research", "study",
        "scientist", "discovery", "experiment", "space",
        "NASA", "climate", "medical research"
    ],
}

TITLE_WEIGHT = 3
SUMMARY_WEIGHT = 1


def contains_phrase(text, phrase):
    """Match a whole word or phrase, ignoring letter case."""
    pattern = r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)"
    return re.search(pattern, text.lower()) is not None


def calculate_relevance(article):
    title = article.get("title", "") or ""
    summary = article.get("summary", "") or ""

    score = 0
    matched_interests = []

    for category, keywords in USER_INTERESTS.items():
        title_match = any(
            contains_phrase(title, keyword)
            for keyword in keywords
        )

        summary_match = any(
            contains_phrase(summary, keyword)
            for keyword in keywords
        )

        # Count each category only once per article.
        if title_match:
            score += TITLE_WEIGHT
            matched_interests.append(category)
        elif summary_match:
            score += SUMMARY_WEIGHT
            matched_interests.append(category)

    return score, matched_interests


def rank_news():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"News file not found: {INPUT_FILE}. "
            "Run news_ingestion.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    for article in articles:
        score, matched = calculate_relevance(article)
        article["relevance_score"] = score
        article["matched_interests"] = matched

    # Python's sort preserves original order when scores are tied.
    ranked_articles = sorted(
        articles,
        key=lambda article: article["relevance_score"],
        reverse=True,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(ranked_articles, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Articles ranked: {len(ranked_articles)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nTop 5 articles for your interest profile:")

    for index, article in enumerate(ranked_articles[:5], start=1):
        print(f"\n{index}. {article.get('title', 'Untitled')}")
        print(f"   Score: {article['relevance_score']}")
        print(
            "   Matched interests: "
            + (
                ", ".join(article["matched_interests"])
                or "None"
            )
        )


if __name__ == "__main__":
    rank_news()
