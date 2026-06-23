from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping


@dataclass(frozen=True, slots=True)
class ProtectedMetricBound:
    metric: str
    baseline: float
    max_worsen: float

    def as_dict(self) -> Dict[str, float | str]:
        return {
            "metric": self.metric,
            "baseline": self.baseline,
            "max_worsen": self.max_worsen,
        }


@dataclass(frozen=True, slots=True)
class ProtectedMetricCheck:
    passed: bool
    violations: list[Dict[str, float | str]]

    def as_dict(self) -> Dict[str, Any]:
        return {"passed": self.passed, "violations": list(self.violations)}


def compile_protected_metric_bounds(
    protected_metrics: Iterable[Mapping[str, Any]],
    baseline: Mapping[str, Any],
) -> list[ProtectedMetricBound]:
    return [
        ProtectedMetricBound(
            metric=str(item["metric"]),
            baseline=float(baseline[str(item["metric"])]),
            max_worsen=float(item.get("max_worsen", 0.0) or 0.0),
        )
        for item in protected_metrics
    ]


def check_protected_metrics(
    quality: Mapping[str, Any],
    bounds: Iterable[ProtectedMetricBound | Mapping[str, Any]],
) -> ProtectedMetricCheck:
    violations: list[Dict[str, float | str]] = []
    for raw_bound in bounds:
        bound = (
            raw_bound
            if isinstance(raw_bound, ProtectedMetricBound)
            else ProtectedMetricBound(
                metric=str(raw_bound["metric"]),
                baseline=float(raw_bound["baseline"]),
                max_worsen=float(raw_bound.get("max_worsen", 0.0) or 0.0),
            )
        )
        actual = float(quality[bound.metric])
        delta = actual - bound.baseline
        if delta > bound.max_worsen + 1e-9:
            violations.append(
                {
                    "metric": bound.metric,
                    "baseline": bound.baseline,
                    "actual": actual,
                    "delta": delta,
                    "max_worsen": bound.max_worsen,
                }
            )
    return ProtectedMetricCheck(passed=not violations, violations=violations)


def evaluation_quality(evaluation: Any) -> Dict[str, float]:
    metrics = getattr(evaluation, "quality_metrics", {}) or {}
    return {str(name): float(value) for name, value in metrics.items()}


__all__ = [
    "ProtectedMetricBound",
    "ProtectedMetricCheck",
    "check_protected_metrics",
    "compile_protected_metric_bounds",
    "evaluation_quality",
]
