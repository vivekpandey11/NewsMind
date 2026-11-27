
import json
import re
import math
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NEWS_FILE = PROJECT_ROOT / "data" / "processed" / "news_articles.json"

# Common words that do not add much search relevance.
STOP_WORDS = {
    "the", "is", "are", "was", "were", "a", "an", "and",
    "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "about", "as", "it", "its",
    "this", "that", "these", "those", "be", "been",
    "what", "which", "who", "when", "where", "why",
    "how", "can", "could", "would", "should", "do",
    "does", "did", "has", "have", "had", "will",
    "latest", "news"
}

# Lightweight in-memory cache.
_cached_mtime = None
_cached_articles = []
_cached_tokens = []
_cached_doc_freq = Counter()
_cached_avg_length = 0


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def get_article_data():
    global _cached_mtime
    global _cached_articles
    global _cached_tokens
    global _cached_doc_freq
    global _cached_avg_length

    if not NEWS_FILE.exists():
        raise FileNotFoundError(
            "News file not found. Run news_ingestion.py first."
        )

    current_mtime = NEWS_FILE.stat().st_mtime_ns

    if _cached_mtime != current_mtime:
        print("Loading news articles and building lightweight search index...")

        with NEWS_FILE.open("r", encoding="utf-8") as file:
            articles = json.load(file)

        if not isinstance(articles, list):
            raise ValueError("News data must be a list of articles.")

        article_tokens = []
        doc_freq = Counter()

        for article in articles:
            text = (
                f"{article.get('title', '')} "
                f"{article.get('summary', '')}"
            )

            tokens = tokenize(text)
            article_tokens.append(tokens)

            doc_freq.update(set(tokens))

        total_length = sum(len(tokens) for tokens in article_tokens)

        _cached_articles = articles
        _cached_tokens = article_tokens
        _cached_doc_freq = doc_freq
        _cached_avg_length = (
            total_length / len(article_tokens)
            if article_tokens else 0
        )
        _cached_mtime = current_mtime

    return (
        _cached_articles,
        _cached_tokens,
        _cached_doc_freq,
        _cached_avg_length,
    )


def retrieve_news(query: str, top_k: int = 3) -> list[dict]:
    query = query.strip()

    if not query or top_k < 1:
        return []

    articles, documents, doc_freq, avg_length = get_article_data()

    if not articles or not documents:
        return []

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    query_counts = Counter(query_tokens)
    total_docs = len(documents)

    k1 = 1.5
    b = 0.75

    results = []

    for index, article in enumerate(articles):
        document = documents[index]

        if not document:
            continue

        term_counts = Counter(document)
        doc_length = len(document)
        score = 0.0

        for term, query_count in query_counts.items():
            frequency = term_counts.get(term, 0)

            if frequency == 0:
                continue

            document_frequency = doc_freq.get(term, 0)

            idf = math.log(
                1 + (
                    total_docs - document_frequency + 0.5
                ) / (document_frequency + 0.5)
            )

            length_norm = (
                1 - b + b * doc_length / avg_length
                if avg_length else 1
            )

            denominator = frequency + k1 * length_norm

            term_score = (
                idf * frequency * (k1 + 1) / denominator
            )

            score += term_score * query_count

        if score <= 0:
            continue

        # Normalize score to a convenient 0-1 range.
        similarity = score / (score + 5)

        results.append({
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "link": article.get("link", ""),
            "summary": article.get("summary", ""),
            "similarity": round(similarity, 4),
            "_score": score,
        })

    results.sort(
        key=lambda item: item["_score"],
        reverse=True
    )

    for result in results:
        result.pop("_score")

    return results[:top_k]


if __name__ == "__main__":
    question = input("What news topic do you want to explore? ")
    results = retrieve_news(question)

    for index, article in enumerate(results, start=1):
        print(f"\n{index}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Similarity: {article['similarity']}")
        print(f"   Summary: {article['summary']}")
        print(f"   Link: {article['link']}")
