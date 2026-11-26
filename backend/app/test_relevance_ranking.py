from relevance_ranking import calculate_relevance


def test_ai_and_india_news():
    article = {
        "title": "AI breakthroughs announced by Indian startups",
        "summary": "",
    }

    score, matched = calculate_relevance(article)

    assert score == 9, f"Unexpected score: {score}"
    assert "AI & Machine Learning" in matched
    assert "India News" in matched
    assert "Business & Startups" in matched

def test_sports_news():
    article = {
        "title": "India wins the cricket championship",
        "summary": "",
    }

    score, matched = calculate_relevance(article)

    assert score == 6, f"Unexpected score: {score}"
    assert "India News" in matched
    assert "Sports" in matched

def test_summary_only_match():
    article = {
        "title": "A new platform launches",
        "summary": "Researchers discuss cybersecurity software.",
    }

    score, matched = calculate_relevance(article)

    assert score == 1, f"Unexpected score: {score}"
    assert "Technology" in matched

def test_unrelated_article():
    article = {
        "title": "A quiet afternoon in a small village",
        "summary": "Residents gathered for a local picnic.",
    }

    score, matched = calculate_relevance(article)

    assert score == 0, f"Unexpected score: {score}"
    assert matched == []

if __name__ == "__main__":
    tests = [
        test_ai_and_india_news,
        test_sports_news,
        test_summary_only_match,
        test_unrelated_article,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\nAll {len(tests)} tests passed!")