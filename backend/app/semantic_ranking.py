
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "news_articles.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "semantic_ranked_news.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

USER_INTERESTS = [
    "Artificial intelligence and machine learning",
    "Technology and software",
    "Business and startups",
    "India news",
    "Sports and cricket",
    "Entertainment and movies",
    "World news and international affairs",
    "Finance and economy",
    "Science and research",
]


def rank_news_semantically():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"News file not found: {INPUT_FILE}. "
            "Run news_ingestion.py first."
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    if not articles:
        print("No articles found. Run news ingestion first.")
        return

    print("Loading the semantic embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Encoding your interest categories...")
    interest_embeddings = model.encode(
        USER_INTERESTS,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    article_texts = [
        f"{article.get('title', '')}. {article.get('summary', '')}"
        for article in articles
    ]

    print(f"Encoding {len(articles)} news articles...")
    article_embeddings = model.encode(
        article_texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    # Normalized embeddings: dot product gives cosine similarity.
    similarity_matrix = article_embeddings @ interest_embeddings.T

    for index, article in enumerate(articles):
        category_scores = similarity_matrix[index]
        best_category_index = int(category_scores.argmax())

        article["semantic_score"] = round(
            float(category_scores[best_category_index]), 4
        )
        article["best_matching_interest"] = USER_INTERESTS[
            best_category_index
        ]

    ranked_articles = sorted(
        articles,
        key=lambda article: article["semantic_score"],
        reverse=True,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(ranked_articles, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nArticles ranked: {len(ranked_articles)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nTop 5 semantically relevant articles:")

    for index, article in enumerate(ranked_articles[:5], start=1):
        print(f"\n{index}. {article.get('title', 'Untitled')}")
        print(f"   Similarity: {article['semantic_score']}")
        print(
            "   Best matching interest: "
            f"{article['best_matching_interest']}"
        )


if __name__ == "__main__":
    rank_news_semantically()
