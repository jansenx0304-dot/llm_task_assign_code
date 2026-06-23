"""Single registry for the public, executable LLM control surface."""

from __future__ import annotations

from typing import Dict, Tuple

from .operators.types import (
    ACCEPTANCE_MODES,
    DESTROY_OPERATOR_NAMES,
    DESTROY_SIGNAL_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    INSERTION_TASK_SIGNAL_NAMES,
)

QUALITY_METRICS: Tuple[str, ...] = (
    "missed_priority",
    "unassigned_count",
    "energy_total",
    "total_distance",
    "makespan",
    "route_balance",
)

FIELD_CANDIDATES: Dict[str, Tuple[str, ...]] = {
    "destroy_control.operator_scores": DESTROY_OPERATOR_NAMES,
    "destroy_control.signal_scores": DESTROY_SIGNAL_NAMES,
    "insertion_control.operator_scores": INSERTION_OPERATOR_NAMES,
    "insertion_control.task_signal_scores": INSERTION_TASK_SIGNAL_NAMES,
    "insertion_control.position_signal_scores": INSERTION_POSITION_SIGNAL_NAMES,
    "acceptance_control.mode": ACCEPTANCE_MODES,
}

INITIAL_CONTROL_FIELDS: Tuple[str, ...] = (
    "insertion_control.operator_scores",
    "insertion_control.task_signal_scores",
    "insertion_control.position_signal_scores",
)

ALNS_CONTROL_FIELDS: Tuple[str, ...] = tuple(FIELD_CANDIDATES)

DESTROY_INTERNAL_TO_PUBLIC_SIGNAL: Dict[str, str] = {
    "cost_pressure": "cost_pressure",
    "coupling_pressure": "coupling_pressure",
    "route_balance_pressure": "route_balance_pressure",
    "mobility_opportunity": "mobility_opportunity",
    "scarcity_pressure": "scarcity_protection",
}


__all__ = [
    "ACCEPTANCE_MODES",
    "ALNS_CONTROL_FIELDS",
    "DESTROY_INTERNAL_TO_PUBLIC_SIGNAL",
    "DESTROY_OPERATOR_NAMES",
    "DESTROY_SIGNAL_NAMES",
    "FIELD_CANDIDATES",
    "INITIAL_CONTROL_FIELDS",
    "INSERTION_OPERATOR_NAMES",
    "INSERTION_POSITION_SIGNAL_NAMES",
    "INSERTION_TASK_SIGNAL_NAMES",
    "QUALITY_METRICS",
]
