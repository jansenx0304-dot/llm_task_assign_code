"""Small candidate-name registry used by validators and compilers."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Dict, Iterable, List, Optional

from .config import Config
from .control_surface import (
    ACCEPTANCE_MODES,
    DESTROY_OPERATOR_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    QUALITY_METRICS,
)
from .models import Instance


@dataclass(frozen=True, slots=True)
class PublicCandidate:
    name: str
    description: str = ""

    def as_dict(self) -> Dict[str, str]:
        return {"name": self.name, "description": self.description}


@dataclass(frozen=True, slots=True)
class PublicCandidates:
    objective_candidates: tuple[PublicCandidate, ...]
    insertion_operator_candidates: tuple[PublicCandidate, ...]
    insertion_task_signal_candidates: tuple[PublicCandidate, ...]
    insertion_position_signal_candidates: tuple[PublicCandidate, ...]
    destroy_operator_candidates: tuple[PublicCandidate, ...]
    destroy_signal_candidates: tuple[PublicCandidate, ...]
    acceptance_candidates: tuple[PublicCandidate, ...]
    feasibility_mode_candidates: tuple[PublicCandidate, ...]
    relaxable_violation_candidates: tuple[PublicCandidate, ...]

    def as_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            field.name: [candidate.as_dict() for candidate in getattr(self, field.name)]
            for field in fields(self)
        }

    def names(self, field_name: str) -> tuple[str, ...]:
        return tuple(candidate.name for candidate in getattr(self, field_name))


def _items(values: Iterable[tuple[str, str]]) -> tuple[PublicCandidate, ...]:
    return tuple(PublicCandidate(name, description) for name, description in values)


def build_public_candidates(
    instance: Instance,
    config: Config,
    state: Optional[Any] = None,
) -> PublicCandidates:
    del instance, config
    feasibility = [
        ("strict", ""),
        ("relaxed_recoverable", ""),
        ("recovery_only", ""),
    ]
    del state

    return PublicCandidates(
        objective_candidates=_items(
            (name, "Global solution quality metric.") for name in QUALITY_METRICS
        ),
        insertion_operator_candidates=_items(
            (name, "Public insertion operator.") for name in INSERTION_OPERATOR_NAMES
        ),
        insertion_task_signal_candidates=_items(
            [
                (
                    "priority_loss",
                    "Task-level signal equal to missed priority contribution.",
                ),
                (
                    "scarcity_pressure",
                    "Task-level signal measuring limited feasible insertion options.",
                ),
                (
                    "regret_pressure",
                    "Task-level signal measuring the gap between best and alternative insertion options.",
                ),
                (
                    "bottleneck_pressure",
                    "Task-level signal measuring limited feasible agents or positions.",
                ),
                (
                    "mobility_opportunity",
                    "Task-level signal measuring reassignment or insertion opportunity.",
                ),
            ]
        ),
        insertion_position_signal_candidates=_items(
            (name, "Public insertion-position signal.")
            for name in INSERTION_POSITION_SIGNAL_NAMES
        ),
        destroy_operator_candidates=_items(
            (name, "Public destroy operator.") for name in DESTROY_OPERATOR_NAMES
        ),
        destroy_signal_candidates=_items(
            [
                (
                    "cost_pressure",
                    "Destroy signal measuring cost released by removing an assigned component.",
                ),
                (
                    "coupling_pressure",
                    "Destroy signal measuring relatedness of local assigned structures.",
                ),
                (
                    "route_balance_pressure",
                    "Destroy signal measuring route load or cost imbalance pressure.",
                ),
                (
                    "mobility_opportunity",
                    "Destroy signal measuring reassignment opportunity after removal.",
                ),
                (
                    "scarcity_protection",
                    "Destroy signal that decreases removal score for scarce reassignment options.",
                ),
            ]
        ),
        acceptance_candidates=_items(
            (name, "Public ALNS acceptance mode.") for name in ACCEPTANCE_MODES
        ),
        feasibility_mode_candidates=_items(feasibility),
        relaxable_violation_candidates=_items(
            [
                ("time_window", ""),
                ("energy", ""),
            ]
        ),
    )


__all__ = ["PublicCandidate", "PublicCandidates", "build_public_candidates"]
