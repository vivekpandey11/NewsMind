import json
from pathlib import Path
from functools import lru_cache

from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NEWS_FILE = PROJECT_ROOT / "data" / "processed" / "news_articles.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Load the embedding model only once per process.
@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    print("Loading Sentence Transformer model...")
    return SentenceTransformer(MODEL_NAME)


# Cache article data and embeddings until the news file changes.
_cached_mtime = None
_cached_articles = []
_cached_embeddings = None


def get_article_data():
    global _cached_mtime, _cached_articles, _cached_embeddings

    if not NEWS_FILE.exists():
        raise FileNotFoundError(
            "News file not found. Run news_ingestion.py first."
        )

    current_mtime = NEWS_FILE.stat().st_mtime_ns

    if (
        _cached_mtime != current_mtime
        or _cached_embeddings is None
    ):
        print("Loading news articles and preparing embeddings...")

        with NEWS_FILE.open("r", encoding="utf-8") as file:
            articles = json.load(file)

        if not articles:
            _cached_mtime = current_mtime
            _cached_articles = []
            _cached_embeddings = None
            return _cached_articles, _cached_embeddings

        model = get_model()

        article_texts = [
            f"{article.get('title', '')}. {article.get('summary', '')}"
            for article in articles
        ]

        embeddings = model.encode(
            article_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        _cached_articles = articles
        _cached_embeddings = embeddings
        _cached_mtime = current_mtime

    return _cached_articles, _cached_embeddings


def retrieve_news(query: str, top_k: int = 3) -> list[dict]:
    query = query.strip()

    if not query:
        return []

    if top_k < 1:
        return []

    articles, article_embeddings = get_article_data()

    if not articles or article_embeddings is None:
        return []

    model = get_model()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]

    similarities = article_embeddings @ query_embedding

    ranked_indices = similarities.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:
        article = articles[int(index)]

        results.append({
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "link": article.get("link", ""),
            "summary": article.get("summary", ""),
            "similarity": round(float(similarities[index]), 4),
        })

    return results


if __name__ == "__main__":
    question = input("What news topic do you want to explore? ")
    results = retrieve_news(question)

    for index, article in enumerate(results, start=1):
        print(f"\n{index}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Similarity: {article['similarity']}")
        print(f"   Summary: {article['summary']}")
        print(f"   Link: {article['link']}")
