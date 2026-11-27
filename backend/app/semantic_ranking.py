
import json
import re
import math
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "news_articles.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "semantic_ranked_news.json"


USER_INTERESTS = {
    "Artificial intelligence and machine learning": [
        "artificial intelligence", "machine learning", "deep learning",
        "generative ai", "chatgpt", "openai", "google gemini",
        "large language models", "neural networks", "robotics",
        "automation", "ai model", "computer vision"
    ],
    "Technology and software": [
        "technology", "software", "smartphone", "mobile phone",
        "cybersecurity", "data breach", "cloud computing",
        "microsoft", "google", "apple", "meta", "internet",
        "digital platform", "social media", "startup technology"
    ],
    "Business and startups": [
        "business", "startup", "entrepreneur", "company",
        "corporate", "ceo", "investment", "funding",
        "acquisition", "market", "revenue", "profit",
        "economic growth", "stock market"
    ],
    "India news": [
        "india", "indian", "new delhi", "modi", "parliament",
        "supreme court", "indian government", "rupee",
        "mumbai", "bengaluru", "election india",
        "indian politics", "indian economy"
    ],
    "Sports and cricket": [
        "sports", "cricket", "football", "soccer", "ipl",
        "world cup", "test match", "odi", "t20",
        "olympics", "athlete", "championship", "tournament",
        "tennis", "basketball"
    ],
    "Entertainment and movies": [
        "entertainment", "movie", "film", "bollywood",
        "hollywood", "actor", "actress", "celebrity",
        "music", "television", "streaming", "netflix",
        "box office", "cinema"
    ],
    "World news and international affairs": [
        "world", "international", "global", "ukraine",
        "russia", "israel", "palestine", "iran", "united states",
        "trump", "war", "conflict", "attack", "military",
        "terrorism", "diplomacy", "ceasefire", "peace talks",
        "middle east", "europe", "paris", "jordan"
    ],
    "Finance and economy": [
        "finance", "economy", "inflation", "gdp",
        "interest rates", "central bank", "rbi",
        "banking", "stock market", "shares", "bonds",
        "currency", "rupee", "dollar", "recession",
        "fiscal policy", "monetary policy"
    ],
    "Science and research": [
        "science", "research", "scientist", "discovery",
        "space", "nasa", "astronomy", "physics",
        "biology", "chemistry", "climate change",
        "environment", "medical research", "experiment"
    ],
}


STOPWORDS = {
    "the", "is", "are", "was", "were", "a", "an", "and", "or",
    "of", "to", "in", "on", "for", "with", "by", "from", "at",
    "as", "it", "this", "that", "has", "have", "had", "be",
    "been", "will", "after", "before", "over", "into", "about",
    "their", "they", "them", "its", "who", "what", "when",
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [word for word in words if word not in STOPWORDS]


def build_tfidf(documents):
    tokenized = [tokenize(doc) for doc in documents]
    total_docs = len(tokenized)

    document_frequency = Counter()

    for words in tokenized:
        document_frequency.update(set(words))

    vectors = []

    for words in tokenized:
        word_counts = Counter(words)
        total_words = len(words)
        vector = {}

        for word, count in word_counts.items():
            tf = count / total_words if total_words else 0

            idf = math.log(
                (1 + total_docs) / (1 + document_frequency[word])
            ) + 1

            vector[word] = tf * idf

        vectors.append(vector)

    return vectors


def cosine_similarity(vector_a, vector_b):
    common_words = set(vector_a) & set(vector_b)

    dot_product = sum(
        vector_a[word] * vector_b[word]
        for word in common_words
    )

    norm_a = math.sqrt(
        sum(value ** 2 for value in vector_a.values())
    )

    norm_b = math.sqrt(
        sum(value ** 2 for value in vector_b.values())
    )

    if not norm_a or not norm_b:
        return 0.0

    return dot_product / (norm_a * norm_b)


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

    print("Building lightweight TF-IDF ranking...")

    interest_names = list(USER_INTERESTS.keys())

    interest_documents = [
        " ".join(keywords)
        for keywords in USER_INTERESTS.values()
    ]

    article_texts = [
        f"{article.get('title', '')} {article.get('summary', '')}"
        for article in articles
    ]

    all_documents = interest_documents + article_texts

    all_vectors = build_tfidf(all_documents)

    interest_vectors = all_vectors[:len(interest_names)]
    article_vectors = all_vectors[len(interest_names):]

    for index, article in enumerate(articles):

        scores = [
            cosine_similarity(
                article_vectors[index],
                interest_vector
            )
            for interest_vector in interest_vectors
        ]

        best_index = scores.index(max(scores))
        best_score = scores[best_index]

        article["semantic_score"] = round(best_score, 4)

        article["best_matching_interest"] = (
            interest_names[best_index]
            if best_score > 0
            else "No clear match"
        )

    ranked_articles = sorted(
        articles,
        key=lambda article: article["semantic_score"],
        reverse=True,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(
            ranked_articles,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print(f"\nArticles ranked: {len(ranked_articles)}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTOP 5 INTEREST-BASED ARTICLES")

    for index, article in enumerate(ranked_articles[:5], start=1):

        print(f"\n{index}. {article.get('title', 'Untitled')}")
        print(f"   Similarity: {article['semantic_score']}")
        print(
            f"   Best matching interest: "
            f"{article['best_matching_interest']}"
        )


if __name__ == "__main__":
    rank_news_semantically()
