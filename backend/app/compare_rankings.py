
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

KEYWORD_FILE = DATA_DIR / "ranked_news.json"
SEMANTIC_FILE = DATA_DIR / "semantic_ranked_news.json"
OUTPUT_FILE = DATA_DIR / "ranking_comparison.json"


def load_articles(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def compare_rankings():
    keyword_articles = load_articles(KEYWORD_FILE)
    semantic_articles = load_articles(SEMANTIC_FILE)

    keyword_ranks = {
        article["link"]: rank
        for rank, article in enumerate(keyword_articles, start=1)
    }

    semantic_ranks = {
        article["link"]: rank
        for rank, article in enumerate(semantic_articles, start=1)
    }
    keyword_by_link = {
        article["link"]: article
        for article in keyword_articles
    }

    semantic_by_link = {
        article["link"]: article
        for article in semantic_articles
    }

    # Compare every unique article across both ranking lists.
    all_articles = {}

    for article in keyword_articles + semantic_articles:
        link = article.get("link", "")
        if link:
            all_articles[link] = article

    comparison = []

    for link, article in all_articles.items():
        keyword_rank = keyword_ranks.get(link)
        semantic_rank = semantic_ranks.get(link)

        comparison.append({
            "title": article.get("title", "Untitled"),
            "link": link,
            "keyword_rank": keyword_rank,
            "semantic_rank": semantic_rank,
            "rank_change": (
                keyword_rank - semantic_rank
                if keyword_rank is not None and semantic_rank is not None
                else None
            ),
            "keyword_score": keyword_by_link.get(link, {}).get(
                "relevance_score"
            ),
            "semantic_score": semantic_by_link.get(link, {}).get(
                "semantic_score"
            ),
            "best_matching_interest": article.get(
                "best_matching_interest"
            ),
            "matched_interests": article.get("matched_interests", []),
        })

    comparison.sort(
        key=lambda item: (
            item["semantic_rank"] is None,
            item["semantic_rank"] or float("inf"),
        )
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    common_articles = set(keyword_ranks) & set(semantic_ranks)

    print(f"Keyword articles: {len(keyword_articles)}")
    print(f"Semantic articles: {len(semantic_articles)}")
    print(f"Common articles: {len(common_articles)}")
    print(f"Saved comparison to: {OUTPUT_FILE}")

    print("\nTOP 5 — RANKING COMPARISON")

    for item in comparison[:5]:
        print(f"\n{item['title']}")
        print(f"  Keyword rank: {item['keyword_rank']}")
        print(f"  Semantic rank: {item['semantic_rank']}")
        print(f"  Keyword score: {item['keyword_score']}")
        print(f"  Semantic score: {item['semantic_score']}")
        print(
            f"  Rank change (+ = moved up): {item['rank_change']}"
        )


if __name__ == "__main__":
    compare_rankings()
