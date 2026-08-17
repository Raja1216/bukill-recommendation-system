import math
from collections import defaultdict

from app.config import HYBRID_WEIGHTS


SCORE_FIELDS = list(HYBRID_WEIGHTS.keys())
SOURCE_NAMES = {
    "content_score": "content",
    "collaborative_score": "collaborative",
    "social_score": "social",
    "interest_score": "interest",
    "creator_affinity_score": "creator_affinity",
    "trending_score": "trending",
    "freshness_score": "fresh",
}


class HybridRanker:
    def rank(self, candidate_groups: list[list[dict]]) -> list[dict]:
        merged = defaultdict(lambda: {"buckil_id": None})

        for group in candidate_groups:
            for item in group:
                buckil_id = int(item["buckil_id"])
                merged[buckil_id]["buckil_id"] = buckil_id
                for field in SCORE_FIELDS:
                    if field in item:
                        merged[buckil_id][field] = max(
                            float(item[field]),
                            float(merged[buckil_id].get(field, 0.0)),
                        )

        candidates = list(merged.values())
        if not candidates:
            return []

        self._normalize(candidates)

        for item in candidates:
            final_score = 0.0
            sources = []
            for field, weight in HYBRID_WEIGHTS.items():
                score = self.safe_float(item.get(field, 0))
                final_score += score * weight
                if score > 0:
                    sources.append(SOURCE_NAMES[field])

            item["score"] = round(final_score, 6)
            item["sources"] = sources
            item["reason"] = self._reason(self, item)

        return sorted(candidates, key=lambda item: item["score"], reverse=True)

    def _normalize(self, candidates: list[dict]):
        for field in SCORE_FIELDS:
            values = [self.safe_float(item.get(field, 0)) for item in candidates]
            positive = [value for value in values if value > 0]
            if not positive:
                for item in candidates:
                    item[field] = 0.0
                continue

            min_value = min(positive)
            max_value = max(positive)

            for item in candidates:
                value = self.safe_float(item.get(field, 0))
                if value <= 0:
                    item[field] = 0.0
                elif max_value == min_value:
                    item[field] = 1.0
                else:
                    item[field] = (value - min_value) / (max_value - min_value)

    @staticmethod
    def _reason(self, item: dict) -> str:
        fields = {
            "content_score": "Matches your activity and content interests",
            "collaborative_score": "People with similar activity also engaged with this",
            "social_score": "Popular among your friends and people you follow",
            "interest_score": "Matches your selected interests",
            "creator_affinity_score": "From a creator you frequently engage with",
            "trending_score": "Trending now",
            "freshness_score": "New Buckil you may like",
        }
        best_field = max(fields.keys(), key=lambda field: (self.safe_float(item.get(field, 0))))
        if float(item.get(best_field, 0.0)) <= 0:
            return "Recommended for you"
        return fields[best_field]
    
    @staticmethod
    def safe_float(value):

        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0

        if math.isnan(value):
            return 0.0

        if math.isinf(value):
            return 0.0

        return value
