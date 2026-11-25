"""Transparent, analyst-supplied investment scoring. Never a predicted return/probability."""
from dataclasses import dataclass
from math import isfinite
from typing import Any

# Fixed rubric for cross-report consistency. The analyst must justify every input.
RUBRIC = (
    ('valuation', 'Valuation & margin of safety', 30),
    ('return', 'Conditional shareholder return', 20),
    ('quality', 'Business quality & durability', 20),
    ('resilience', 'Balance sheet & downside resilience', 20),
    ('evidence', 'Evidence quality & uncertainty', 10),
)


@dataclass(frozen=True)
class RatingDimension:
    key: str
    label: str
    weight: int
    score: float
    rationale: str


@dataclass(frozen=True)
class InvestmentRating:
    score: int
    category: str
    dimensions: tuple[RatingDimension, ...]
    thesis: str
    catalysts: tuple[str, ...]
    invalidators: tuple[str, ...]


def category_for_score(score: int) -> str:
    if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 100:
        raise ValueError('Investment rating score must be an integer 1–100')
    return ('Strong Sell' if score <= 20 else 'Sell' if score <= 40 else
            'Hold' if score <= 60 else 'Buy' if score <= 80 else 'Strong Buy')


def calculate_rating(data: dict[str, Any]) -> InvestmentRating | None:
    assessment = data.get('investment_assessment')
    if assessment is None:
        return None  # Deliberately unscored: never make up analytical ratings.
    if not isinstance(assessment, dict):
        raise ValueError('investment_assessment must be an object')
    comps = assessment.get('components')
    if not isinstance(comps, dict) or set(comps) != {x[0] for x in RUBRIC}:
        raise ValueError('Score requires exactly all five investment_assessment.components keys')
    dimensions = []
    for key, label, weight in RUBRIC:
        entry = comps[key]
        if not isinstance(entry, dict) or set(entry) != {'score', 'rationale'}:
            raise ValueError(f'{key}: requires score and rationale only')
        score = entry['score']
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not isfinite(score) or not 0 <= score <= 100:
            raise ValueError(f'{key}: score must be finite, 0–100')
        rationale = entry['rationale']
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f'{key}: rationale is mandatory')
        dimensions.append(RatingDimension(key, label, weight, float(score), rationale.strip()))
    total = sum(d.score * d.weight for d in dimensions) / 100
    composite = max(1, min(100, int(total + 0.5)))
    thesis = assessment.get('thesis')
    if not isinstance(thesis, str) or not thesis.strip():
        raise ValueError('investment_assessment.thesis must explain conditional stance')
    def items(key):
        val = assessment.get(key, [])
        if not isinstance(val, list) or any(not isinstance(s, str) or not s.strip() for s in val):
            raise ValueError(f'investment_assessment.{key} must be a list of nonempty strings')
        return tuple(x.strip() for x in val)
    return InvestmentRating(composite, category_for_score(composite), tuple(dimensions),
                            thesis.strip(), items('catalysts'), items('invalidation_triggers'))
