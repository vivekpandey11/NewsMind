
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"

KEYWORD_FILE = DATA_DIR / "ranked_news.json"
SEMANTIC_FILE = DATA_DIR / "semantic_ranked_news.json"
OUTPUT_FILE = DATA_DIR / "ranking_evaluation.json"


def load_articles(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_rankings():
    keyword_articles = load_articles(KEYWORD_FILE)
    semantic_articles = load_articles(SEMANTIC_FILE)

    keyword_top_5 = keyword_articles[:5]
    semantic_top_5 = semantic_articles[:5]

    keyword_top_links = {
        article.get("link") for article in keyword_top_5
    }
    semantic_top_links = {
        article.get("link") for article in semantic_top_5
    }

    common_links = keyword_top_links & semantic_top_links
    union_links = keyword_top_links | semantic_top_links

    overlap_count = len(common_links)
    overlap_percentage = (
        overlap_count / len(union_links) * 100
        if union_links else 0
    )

    report = {
        "keyword_article_count": len(keyword_articles),
        "semantic_article_count": len(semantic_articles),
        "top_k": 5,
        "common_top_articles": overlap_count,
        "top_k_jaccard_overlap": round(overlap_percentage, 2),
        "common_articles": [
            article.get("title", "Untitled")
            for article in keyword_top_5
            if article.get("link") in common_links
        ],
        "manual_evaluation": [
            {
                "title": article.get("title", "Untitled"),
                "link": article.get("link", ""),
                "keyword_rank": next(
                    (
                        rank
                        for rank, item in enumerate(
                            keyword_articles, start=1
                        )
                        if item.get("link") == article.get("link")
                    ),
                    None,
                ),
                "semantic_rank": next(
                    (
                        rank
                        for rank, item in enumerate(
                            semantic_articles, start=1
                        )
                        if item.get("link") == article.get("link")
                    ),
                    None,
                ),
                "relevance_label": None,
            }
            for article in semantic_top_5
        ],
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("RANKING EVALUATION")
    print(f"Keyword articles: {len(keyword_articles)}")
    print(f"Semantic articles: {len(semantic_articles)}")
    print(f"Common articles in top 5: {overlap_count}")
    print(f"Top-5 Jaccard overlap: {overlap_percentage:.2f}%")

    print("\nArticles common to both top-5 lists:")
    if common_links:
        for title in report["common_articles"]:
            print(f"- {title}")
    else:
        print("None")

    print(f"\nEvaluation report saved to: {OUTPUT_FILE}")
    print(
        "\nNext, we will manually label the top articles "
        "to evaluate actual relevance."
    )


if __name__ == "__main__":
    evaluate_rankings()
