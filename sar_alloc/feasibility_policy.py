from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .constraint_checker import ConstraintReport


_EPS = 1e-9


@dataclass(frozen=True)
class FeasibilityDecision:
    admissible: bool
    accept_scope: str
    reason: str
    events: List[str]


def check_feasibility_admissibility(
    current_report: ConstraintReport,
    trial_report: ConstraintReport,
    policy: Dict[str, Any],
) -> FeasibilityDecision:
    mode = str(policy.get("mode", ""))
    if mode == "strict":
        return _strict_decision(trial_report)
    if mode == "relaxed_recoverable":
        return _relaxed_recoverable_decision(current_report, trial_report, policy)
    if mode == "recovery_only":
        return _recovery_only_decision(current_report, trial_report)
    raise ValueError(f"unknown feasibility policy mode: {mode}")


def _strict_decision(trial: ConstraintReport) -> FeasibilityDecision:
    if trial.is_feasible:
        return FeasibilityDecision(True, "working_and_best_candidate", "Trial is feasible under strict policy.", [])
    return FeasibilityDecision(False, "reject", "Strict policy rejects infeasible trials.", ["no_admissible_candidate"])


def _relaxed_recoverable_decision(
    current: ConstraintReport,
    trial: ConstraintReport,
    policy: Dict[str, Any],
) -> FeasibilityDecision:
    events: List[str] = []
    per_type = dict(policy.get("per_type", {}) or {})
    for violation_type, value in trial.violation_by_type.items():
        if value > _EPS and violation_type not in per_type:
            return FeasibilityDecision(
                False,
                "reject",
                f"{violation_type} is not relaxable under current policy.",
                ["feasibility_debt_exceeded"],
            )

    for violation_type, limits in per_type.items():
        limit_ratio = float(limits["limit_ratio"])
        delta_ratio = float(limits["delta_ratio"])
        trial_ratio = float(trial.violation_ratio_by_type.get(violation_type, 0.0))
        current_ratio = float(current.violation_ratio_by_type.get(violation_type, 0.0))
        if trial_ratio - limit_ratio > _EPS:
            return FeasibilityDecision(
                False,
                "reject",
                f"{violation_type} total violation ratio exceeds limit_ratio.",
                ["feasibility_debt_exceeded"],
            )
        if (trial_ratio - current_ratio) - delta_ratio > _EPS:
            return FeasibilityDecision(
                False,
                "reject",
                f"{violation_type} violation ratio delta exceeds delta_ratio.",
                ["feasibility_debt_exceeded"],
            )
        for item in trial.violation_details_by_type.get(violation_type, []):
            if float(item.get("ratio", 0.0)) - limit_ratio > _EPS:
                return FeasibilityDecision(
                    False,
                    "reject",
                    f"{violation_type} individual violation ratio exceeds limit_ratio.",
                    ["feasibility_debt_exceeded"],
                )

    if trial.is_feasible:
        if current.violation_total > _EPS:
            events.append("feasibility_recovered")
        return FeasibilityDecision(True, "working_and_best_candidate", "Trial is feasible.", events)

    if trial.recoverable_violation_total > current.recoverable_violation_total + _EPS:
        events.append("feasibility_debt_created")
    elif trial.recoverable_violation_total < current.recoverable_violation_total - _EPS:
        events.append("feasibility_debt_reduced")
    return FeasibilityDecision(
        True,
        "working_only",
        "Trial is relaxed-admissible under per-type ratio policy.",
        events,
    )


def _recovery_only_decision(
    current: ConstraintReport,
    trial: ConstraintReport,
) -> FeasibilityDecision:
    if trial.is_feasible:
        return FeasibilityDecision(True, "working_and_best_candidate", "Trial restored feasibility.", ["feasibility_recovered"])
    if trial.violation_total < current.violation_total - _EPS:
        return FeasibilityDecision(True, "working_only", "Trial reduced violation debt.", ["feasibility_debt_reduced"])
    return FeasibilityDecision(False, "reject", "Recovery-only policy rejects non-reducing trial.", ["recovery_failed"])
