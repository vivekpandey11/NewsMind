
import json
from pathlib import Path
import math

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "ranking_evaluation.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "ranking_evaluation.json"

with INPUT_FILE.open("r", encoding="utf-8") as file:
    report = json.load(file)

labels = report["manual_evaluation"]

# Graded relevance: relevant = 2, partially relevant = 1, irrelevant = 0
grades = {
    "relevant": 2,
    "partially-relevant": 1,
    "partially_relevant": 1,
    "irrelevant": 0,
}

scores = [
    grades.get(item["relevance_label"], 0)
    for item in labels
]

# Precision@5 counts only fully relevant articles.
precision_at_5 = sum(score == 2 for score in scores) / len(scores) if scores else 0

# NDCG@5: relevance-weighted ranking quality.
dcg = sum(
    (2 ** score - 1) / math.log2(index + 2)
    for index, score in enumerate(scores)
)

ideal_scores = sorted(scores, reverse=True)
idcg = sum(
    (2 ** score - 1) / math.log2(index + 2)
    for index, score in enumerate(ideal_scores)
)

ndcg_at_5 = dcg / idcg if idcg else 0

report["manual_metrics"] = {
    "evaluated_articles": len(scores),
    "relevant_count": sum(score == 2 for score in scores),
    "partially_relevant_count": sum(score == 1 for score in scores),
    "irrelevant_count": sum(score == 0 for score in scores),
    "precision_at_5": round(precision_at_5, 4),
    "ndcg_at_5": round(ndcg_at_5, 4),
    "note": "Metrics evaluate the manually labelled semantic top 5 only."
}

OUTPUT_FILE.write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("MANUAL RANKING EVALUATION")
print(f"Articles evaluated: {len(scores)}")
print(f"Relevant: {sum(score == 2 for score in scores)}")
print(f"Partially relevant: {sum(score == 1 for score in scores)}")
print(f"Irrelevant: {sum(score == 0 for score in scores)}")
print(f"Precision@5: {precision_at_5:.2f}")
print(f"NDCG@5: {ndcg_at_5:.4f}")
print(f"Updated report: {OUTPUT_FILE}")
