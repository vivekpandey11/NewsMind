import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Reuse the existing interest profile
from backend.app.relevance_ranking import USER_INTERESTS


# --------------------------------------------------
# Configuration
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("newsmind.digest")

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NEWS_FILE = PROJECT_ROOT / "data" / "processed" / "ranked_news.json"
CACHE_FILE = PROJECT_ROOT / "data" / "processed" / "daily_digest.json"
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

GEMINI_MODEL = "gemini-3.8-flash"

MAX_ATTEMPTS = 3
MAX_ARTICLES = 8


# --------------------------------------------------
# Select personalized articles
# --------------------------------------------------

def get_digest_articles(limit: int = MAX_ARTICLES) -> list[dict]:

    if not NEWS_FILE.exists():
        raise FileNotFoundError(
            "Ranked news file not found. "
            "Run relevance_ranking.py first."
        )

    with NEWS_FILE.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    if not isinstance(articles, list):
        raise ValueError("Ranked news file must contain a list.")

    # Only include articles matching at least one user interest.
    relevant_articles = [
        article
        for article in articles
        if article.get("relevance_score", 0) > 0
        and article.get("matched_interests")
    ]

    # Highest relevance score first.
    relevant_articles.sort(
        key=lambda article: article.get("relevance_score", 0),
        reverse=True,
    )

    return relevant_articles[:limit]


# --------------------------------------------------
# Generate digest using Gemini
# --------------------------------------------------

def generate_digest_text(articles: list[dict]) -> str:

    if client is None:
        raise RuntimeError(
            "Gemini API key is not configured. Check your .env file."
        )

    article_context = []

    for index, article in enumerate(articles, start=1):
        article_context.append(
            f"""
Article {index}
Title: {article.get('title', 'Untitled')}
Publisher: {article.get('source', 'Unknown')}
Summary: {article.get('summary', 'No summary available.')}
Matched interests: {', '.join(article.get('matched_interests', []))}
Relevance score: {article.get('relevance_score', 0)}
Original link: {article.get('link', '')}
"""
        )

    context = "\n".join(article_context)

    interests = ", ".join(USER_INTERESTS.keys())

    prompt = f"""
You are NewsMind, a personalized AI news editor.

Create a useful daily news digest for a reader interested in:
{interests}

Use ONLY the supplied articles. Do not introduce outside facts.

Instructions:

1. Start with a short, engaging introduction.
2. Organize stories under relevant interest categories.
3. Select the most important stories from the supplied articles.
4. Give each story:
   - A clear headline.
   - A concise summary in approximately 2-3 sentences.
   - A short explanation of why it matters to this reader.
   - Its publisher and original URL.
5. Avoid repeating the same story.
6. Do not invent facts, statistics, or developments.
7. If an article has insufficient information, do not make unsupported claims.
8. Use readable Markdown.
9. Keep the entire digest concise and informative.

ARTICLE CONTEXT:
{context}
"""

    last_error = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty digest.")

            return response.text

        except Exception as exc:
            last_error = exc
            error_text = str(exc)

            status_code = getattr(exc, "code", None)
            if callable(status_code):
                try:
                    status_code = status_code()
                except Exception:
                    status_code = None

            retryable = (
                status_code in (429, 500, 502, 503, 504)
                or any(
                    code in error_text
                    for code in (
                        "429",
                        "500",
                        "502",
                        "503",
                        "504",
                        "RESOURCE_EXHAUSTED",
                        "UNAVAILABLE",
                        "INTERNAL",
                    )
                )
            )

            if not retryable or attempt == MAX_ATTEMPTS - 1:
                logger.exception("Gemini digest generation failed.")
                raise

            wait_seconds = 2 ** (attempt + 1)

            logger.warning(
                "Temporary Gemini error. Retrying in %s seconds.",
                wait_seconds,
            )

            time.sleep(wait_seconds)

    raise last_error or RuntimeError("Digest generation failed.")


# --------------------------------------------------
# Main digest function
# --------------------------------------------------

def create_daily_digest() -> dict:

    today = datetime.now().astimezone().date().isoformat()

    # Check whether today's digest already exists.
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r", encoding="utf-8") as file:
                cached_digest = json.load(file)

            if cached_digest.get("digest_date") == today:
                logger.info("Returning cached daily digest.")
                return cached_digest

        except (json.JSONDecodeError, OSError):
            logger.warning("Could not read digest cache. Regenerating.")

    # Generate a fresh digest if today's cache is unavailable.
    articles = get_digest_articles()

    if not articles:
        return {
            "status": "empty",
            "message": "No relevant articles are available for your interests.",
            "article_count": 0,
            "digest": "",
            "articles": [],
        }

    digest_text = generate_digest_text(articles)

    selected_articles = [
        {
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "link": article.get("link", ""),
            "summary": article.get("summary", ""),
            "relevance_score": article.get("relevance_score", 0),
            "matched_interests": article.get("matched_interests", []),
        }
        for article in articles
    ]

    result = {
        "status": "success",
        "digest_date": today,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(selected_articles),
        "digest": digest_text,
        "articles": selected_articles,
    }

    # Save today's digest for future requests.
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    logger.info("Daily digest generated and cached successfully.")

    return result

# --------------------------------------------------
# Run directly for testing
# --------------------------------------------------

if __name__ == "__main__":

    print("Generating your personalized NewsMind digest...\n")

    try:
        result = create_daily_digest()

        print("Status:", result["status"])
        print("Articles selected:", result["article_count"])
        print("\n" + result["digest"])

    except Exception as exc:
        print("Digest generation failed:", type(exc).__name__, str(exc))
