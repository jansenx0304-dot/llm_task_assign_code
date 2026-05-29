from __future__ import annotations

"""Shared score conversions for LLM-guided ALNS metrics and operators."""

from typing import Mapping

from .types import OPERATOR_PRIOR_BOUNDS, MetricPreference


def direction_sign(direction: str) -> float:
    if direction == "prefer_high":
        return 1.0
    if direction == "prefer_low":
        return -1.0
    if direction == "avoid_high":
        return -1.0
    if direction == "neutral":
        return 0.0
    raise ValueError(f"illegal metric direction: {direction}")


def score_metric_preferences(
    features: Mapping[str, float],
    preferences: Mapping[str, MetricPreference],
) -> float:
    denom = sum(
        abs(int(pref.score))
        for pref in preferences.values()
        if str(pref.direction) != "neutral"
    )
    if denom <= 0:
        return 0.0
    total = 0.0
    for name, pref in preferences.items():
        sign = direction_sign(str(pref.direction))
        total += sign * float(pref.score) / float(denom) * float(features[name])
    return float(total)


def operator_score_to_prior(score: int) -> float:
    lower, upper = OPERATOR_PRIOR_BOUNDS
    return lower + (float(score) / 10.0) * (upper - lower)


def score_to_range(score: int, lower: float, upper: float) -> float:
    return float(lower) + (float(score) / 10.0) * (float(upper) - float(lower))
