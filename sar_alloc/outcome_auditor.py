from __future__ import annotations

from typing import Any, Dict, List, Optional

from .evaluator import build_objective_keys, compare_quality
from .protected_metrics import check_protected_metrics, compile_protected_metric_bounds
from .solution import EvalResult

EVENT_TAGS = (
    "initial_feasible",
    "initial_partial",
    "initial_empty",
    "initial_failed",
    "working_quality_improved",
    "best_feasible_improved",
    "protected_metric_violated",
    "trial_rejected_by_protection",
    "hard_filter_blocked",
    "feasibility_rejected_trials",
    "acceptance_rejected_trials",
    "no_accepted_trial",
    "no_quality_gain",
    "debt_reduced",
    "feasibility_recovered",
)


def verify_initial_construction(
    result: Any,
    contract: Any,
    manifest: Optional[Any] = None,
    *,
    decision_id: str = "",
    verification_id: str = "",
) -> Dict[str, Any]:
    trace = dict(getattr(result, "trace", {}) or {})
    trace["trace_id"] = str(
        trace.get("trace_id") or f"X_{verification_id or 'initial'}"
    )
    evaluation = getattr(result, "evaluation", None)
    inserted = int(trace.get("inserted_task_count", 0) or 0)
    if result is None or evaluation is None:
        tag = "initial_failed"
        status = "not_achieved"
        blocker = "initial_failed"
    elif inserted == 0:
        tag = "initial_empty"
        status = "not_achieved"
        blocker = (
            "no_candidate_position"
            if int(trace.get("zero_candidate_task_count", 0) or 0)
            else "initial_empty"
        )
    elif bool(evaluation.is_feasible):
        tag = "initial_feasible"
        status = "achieved"
        blocker = "none"
    else:
        tag = "initial_partial"
        status = "partial"
        blocker = _initial_blocker(trace)
    trace.setdefault("kind", "initial_insertion")
    protected = (
        {"passed": True, "violations": []}
        if evaluation is None
        else _protected_metric_result(evaluation, evaluation, contract)
    )
    if not protected["passed"]:
        status = "regressed"
        blocker = "protected_metric_violated"
        tag = "protected_metric_violated"
    verification = _base_verification(
        verification_id=verification_id,
        contract=contract,
        decision_id=decision_id,
        manifest=manifest,
        trace=trace,
        action="construct_initial",
        target_id=_manifest_target(manifest),
    )
    verification.update(
        {
            "intent_status": status,
            "metric_delta": {
                "working": (
                    _metric_values(evaluation, _contract_metrics(contract))
                    if evaluation is not None
                    else {}
                ),
                "best_feasible": (
                    _metric_values(evaluation, _contract_metrics(contract))
                    if evaluation is not None and evaluation.is_feasible
                    else {}
                ),
            },
            "debt_delta": {},
            "protected_metric_result": protected,
            "protected_metric_baseline": _protected_metric_baseline(contract),
            "dominant_blocker": blocker,
            "flow_diagnosis": _flow_diagnosis(blocker, status),
            "event_tags": [tag],
            "improvement_flags": {
                "working_contract_improved": False,
                "action_best_contract_improved": False,
                "run_global_best_improved": False,
                "protected_metrics_passed": bool(protected["passed"]),
            },
            "objective_keys": _verification_objective_keys(
                evaluation, _contract_metrics(contract)
            ),
            "trace": trace,
        }
    )
    return verification


def verify_alns_action(
    *,
    before_working_eval: EvalResult,
    after_working_eval: EvalResult,
    before_best_feasible_eval: Optional[EvalResult],
    after_action_best_eval: Optional[EvalResult],
    trace: Dict[str, Any],
    contract: Any,
    manifest: Any,
    before_global_best_eval: Optional[EvalResult] = None,
    after_global_best_eval: Optional[EvalResult] = None,
    decision_id: str = "",
    verification_id: str = "",
    global_objective_layers: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    metrics = _contract_metrics(contract)
    working_delta = _metric_delta(before_working_eval, after_working_eval, metrics)
    best_delta = _metric_delta(
        before_best_feasible_eval, after_action_best_eval, metrics
    )
    debt_delta = _debt_delta(before_working_eval, after_working_eval)
    protected = _protected_metric_result(
        before_working_eval, after_working_eval, contract
    )
    chosen_after = _better_eval(after_working_eval, after_action_best_eval, metrics)
    status = (
        "regressed"
        if not protected["passed"]
        else _intent_status(before_working_eval, chosen_after, metrics, debt_delta)
    )
    blocker = (
        "protected_metric_violated"
        if not protected["passed"]
        else _dominant_blocker_from_trace(trace, status)
    )
    working_contract_improved = bool(
        protected["passed"]
        and compare_quality(after_working_eval, before_working_eval, metrics) < 0
    )
    action_best_contract_improved = bool(
        protected["passed"]
        and after_action_best_eval is not None
        and (
            before_best_feasible_eval is None
            or compare_quality(
                after_action_best_eval, before_best_feasible_eval, metrics
            )
            < 0
        )
    )
    run_global_best_improved = bool(
        protected["passed"]
        and after_global_best_eval is not None
        and (
            before_global_best_eval is None
            or compare_quality(
                after_global_best_eval,
                before_global_best_eval,
                global_objective_layers or metrics,
            )
            < 0
        )
    )
    tags = _event_tags(
        before_working_eval,
        after_working_eval,
        before_global_best_eval,
        after_global_best_eval,
        working_delta,
        best_delta,
        debt_delta,
        protected,
        blocker,
        global_objective_layers or metrics,
    )
    trace = dict(trace)
    trace.setdefault("kind", "alns")
    verification = _base_verification(
        verification_id=verification_id,
        contract=contract,
        decision_id=decision_id,
        manifest=manifest,
        trace=trace,
        action="run_alns",
        target_id=_manifest_target(manifest),
    )
    verification.update(
        {
            "intent_status": status,
            "metric_delta": {"working": working_delta, "best_feasible": best_delta},
            "debt_delta": debt_delta,
            "protected_metric_result": protected,
            "protected_metric_baseline": _protected_metric_baseline(contract),
            "dominant_blocker": blocker,
            "flow_diagnosis": _flow_diagnosis(blocker, status),
            "event_tags": tags,
            "improvement_flags": {
                "working_contract_improved": working_contract_improved,
                "action_best_contract_improved": action_best_contract_improved,
                "run_global_best_improved": run_global_best_improved,
                "protected_metrics_passed": bool(protected["passed"]),
            },
            "objective_keys": build_objective_keys(
                chosen_after,
                metrics,
                global_objective_layers or metrics,
            ),
            "trace": trace,
        }
    )
    return verification


def verify_review_request(
    decision: Dict[str, Any],
    contract: Any,
    recent_verifications: List[Dict[str, Any]],
    *,
    manifest: Optional[Any] = None,
    decision_id: str = "",
    verification_id: str = "",
    trace_id: str = "X_review",
) -> Dict[str, Any]:
    trace = {
        "trace_id": trace_id,
        "kind": "review_request",
        "recent_verification_ids": [
            item.get("verification_id") for item in recent_verifications
        ],
    }
    verification = _base_verification(
        verification_id=verification_id,
        contract=contract,
        decision_id=decision_id,
        manifest=manifest,
        trace=trace,
        action="request_supervisor_review",
        target_id=(decision.get("solver_decision", decision)).get(
            "target_id", "contract_review"
        ),
    )
    verification.update(
        {
            "intent_status": "not_applicable",
            "metric_delta": {"working": {}, "best_feasible": {}},
            "debt_delta": {},
            "protected_metric_result": {"passed": True, "violations": []},
            "protected_metric_baseline": _protected_metric_baseline(contract),
            "dominant_blocker": "solver_requested_review",
            "flow_diagnosis": _flow_diagnosis(
                "solver_requested_review", "not_applicable"
            ),
            "event_tags": [],
            "improvement_flags": {
                "working_contract_improved": False,
                "action_best_contract_improved": False,
                "run_global_best_improved": False,
                "protected_metrics_passed": True,
            },
            "trace": trace,
        }
    )
    return verification


def audit_initial_result(*, initial_eval: Optional[EvalResult]) -> Dict[str, Any]:
    class _Result:
        evaluation = initial_eval
        trace = {
            "inserted_task_count": 1 if initial_eval is not None else 0,
            "kind": "initial_insertion",
        }

    return verify_initial_construction(
        _Result(), {"contract_id": "", "objective_layers": []}
    )


def audit_outcome(**kwargs: Any) -> Dict[str, Any]:
    return verify_alns_action(
        before_working_eval=kwargs["before_working_eval"],
        after_working_eval=kwargs["after_working_eval"],
        before_best_feasible_eval=kwargs.get("before_best_eval"),
        after_action_best_eval=kwargs.get("after_best_eval"),
        trace=kwargs.get("solver_diagnostics", {}).get("execution_trace", {}),
        contract={
            "contract_id": "",
            "objective_layers": kwargs.get("contract_objective_layers", []),
            "protected_metrics": [],
        },
        manifest=None,
        global_objective_layers=kwargs.get("global_objective_layers"),
    )


def _base_verification(
    *,
    verification_id: str,
    contract: Any,
    decision_id: str,
    manifest: Optional[Any],
    trace: Dict[str, Any],
    action: str,
    target_id: str,
) -> Dict[str, Any]:
    manifest_dict = (
        manifest.as_dict() if hasattr(manifest, "as_dict") else dict(manifest or {})
    )
    return {
        "verification_id": verification_id,
        "contract_id": _contract_id(contract),
        "decision_id": decision_id or manifest_dict.get("source_decision_id", ""),
        "manifest_id": manifest_dict.get("manifest_id", ""),
        "trace_id": trace.get("trace_id", ""),
        "action": action,
        "target_id": target_id,
        "protected_metric_baseline": _protected_metric_baseline(contract),
    }


def _metric_delta(
    before: Optional[EvalResult],
    after: Optional[EvalResult],
    metrics: List[Dict[str, Any]],
) -> Dict[str, float]:
    if before is None or after is None:
        return {}
    return {
        str(layer.get("metric", layer.get("name", ""))): float(
            after.get_metric(str(layer.get("metric", layer.get("name", ""))))
        )
        - float(before.get_metric(str(layer.get("metric", layer.get("name", "")))))
        for layer in metrics
        if str(layer.get("metric", layer.get("name", "")))
    }


def _metric_values(
    evaluation: Optional[EvalResult], metrics: List[Dict[str, Any]]
) -> Dict[str, float]:
    if evaluation is None:
        return {}
    return {
        str(layer.get("metric", layer.get("name", ""))): float(
            evaluation.get_metric(str(layer.get("metric", layer.get("name", ""))))
        )
        for layer in metrics
        if str(layer.get("metric", layer.get("name", "")))
    }


def _debt_delta(before: EvalResult, after: EvalResult) -> Dict[str, float]:
    out: Dict[str, float] = {}
    before_ratios = before.constraint_report.violation_ratio_by_type
    after_ratios = after.constraint_report.violation_ratio_by_type
    for name in sorted(
        set(before_ratios) | set(after_ratios) | {"time_window", "energy"}
    ):
        out[str(name)] = float(after_ratios.get(name, 0.0)) - float(
            before_ratios.get(name, 0.0)
        )
    return out


def _protected_metric_result(
    before_eval: EvalResult,
    after_eval: EvalResult,
    contract: Any,
) -> Dict[str, Any]:
    protected_metrics = _protected_metrics(contract)
    baseline = _protected_metric_baseline(contract)
    for item in protected_metrics:
        metric = str(item["metric"])
        baseline.setdefault(metric, float(before_eval.get_metric(metric)))
    bounds = compile_protected_metric_bounds(protected_metrics, baseline)
    quality = {
        str(item["metric"]): float(after_eval.get_metric(str(item["metric"])))
        for item in protected_metrics
    }
    return check_protected_metrics(quality, bounds).as_dict()


def _dominant_blocker_from_trace(trace: Dict[str, Any], status: str) -> str:
    flow = trace.get("trial_flow", {}) or {}
    candidate_trials = int(flow.get("candidate_trials", 0) or 0)
    hard_filter_failed = int(flow.get("hard_filter_failed", 0) or 0)
    feasibility_rejected = int(flow.get("feasibility_rejected", 0) or 0)
    protected_rejected = int(flow.get("protected_metric_rejected", 0) or 0)
    admissible = int(flow.get("admissible_trials", 0) or 0)
    accepted = int(flow.get("accepted_trials", 0) or 0)
    if candidate_trials == 0:
        return "no_candidate_position"
    if feasibility_rejected / max(1, candidate_trials) >= 0.7:
        return "feasibility_rejected_trials"
    if protected_rejected / max(1, candidate_trials) >= 0.7:
        return "protected_metric_violated"
    if hard_filter_failed / max(1, candidate_trials) >= 0.7:
        return "hard_filter_blocked"
    if admissible > 0 and accepted == 0:
        return "acceptance_rejected_trials"
    if status == "regressed":
        return "objective_regressed"
    if status == "not_achieved":
        return "no_quality_gain"
    return "none"


def _intent_status(
    before: EvalResult,
    after: EvalResult,
    layers: List[Dict[str, Any]],
    debt_delta: Dict[str, float],
) -> str:
    primary = layers[0]
    metric = str(primary.get("metric", ""))
    direction = str(primary.get("direction", "min"))
    before_primary = float(before.get_quality_metric(metric))
    after_primary = float(after.get_quality_metric(metric))
    oriented_delta = after_primary - before_primary
    if direction == "max":
        oriented_delta = -oriented_delta
    if oriented_delta > 1e-9:
        return "regressed"
    if oriented_delta < -1e-9:
        return "achieved"
    secondary_improved = any(
        compare_quality(after, before, [layer]) < 0 for layer in layers[1:]
    )
    non_objective_improved = any(value < -1e-9 for value in debt_delta.values())
    if secondary_improved or non_objective_improved:
        return "partial"
    return "not_achieved"


def _event_tags(
    before_working_eval: EvalResult,
    after_working_eval: EvalResult,
    before_best_eval: Optional[EvalResult],
    after_best_eval: Optional[EvalResult],
    working_delta: Dict[str, float],
    best_delta: Dict[str, float],
    debt_delta: Dict[str, float],
    protected: Dict[str, Any],
    blocker: str,
    global_layers: List[Dict[str, Any]],
) -> List[str]:
    tags: List[str] = []
    if any(value < -1e-9 for value in working_delta.values()):
        tags.append("working_quality_improved")
    global_improved = bool(
        after_best_eval is not None
        and (
            before_best_eval is None
            or compare_quality(after_best_eval, before_best_eval, global_layers) < 0
        )
    )
    if global_improved or any(value < -1e-9 for value in best_delta.values()):
        tags.append("best_feasible_improved")
    if not protected.get("passed", False):
        tags = [
            tag
            for tag in tags
            if tag not in {"working_quality_improved", "best_feasible_improved"}
        ]
        tags.append("protected_metric_violated")
        tags.append("trial_rejected_by_protection")
    elif blocker == "protected_metric_violated":
        tags.append("protected_metric_violated")
        tags.append("trial_rejected_by_protection")
    if blocker in {
        "hard_filter_blocked",
        "feasibility_rejected_trials",
        "acceptance_rejected_trials",
        "no_quality_gain",
    }:
        tags.append(blocker)
    if blocker in {"feasibility_rejected_trials", "acceptance_rejected_trials"}:
        tags.append("no_accepted_trial")
    if any(value < -1e-9 for value in debt_delta.values()):
        tags.append("debt_reduced")
    if not before_working_eval.is_feasible and after_working_eval.is_feasible:
        tags.append("feasibility_recovered")
    return [tag for tag in EVENT_TAGS if tag in tags]


def _flow_diagnosis(blocker: str, status: str = "") -> Dict[str, bool]:
    return {
        "candidate_problem": blocker == "no_candidate_position",
        "hard_filter_problem": blocker == "hard_filter_blocked",
        "feasibility_problem": blocker == "feasibility_rejected_trials",
        "acceptance_problem": blocker == "acceptance_rejected_trials",
        "quality_problem": (
            status in {"not_achieved", "regressed"}
            and blocker
            in {
                "no_quality_gain",
                "objective_regressed",
                "protected_metric_violated",
            }
        ),
        "protected_metric_problem": blocker == "protected_metric_violated",
    }


def _better_eval(
    first: EvalResult, second: Optional[EvalResult], layers: List[Dict[str, Any]]
) -> EvalResult:
    if second is None:
        return first
    return second if compare_quality(second, first, layers) < 0 else first


def _initial_blocker(trace: Dict[str, Any]) -> str:
    dominant = str(trace.get("dominant_failure_reason", "") or "")
    if dominant in {"no_candidate", "no_candidate_position"}:
        return "no_candidate_position"
    if dominant in {"no_feasible", "no_feasible_position"}:
        return "hard_filter_blocked"
    return dominant or "initial_partial"


def _contract_metrics(contract: Any) -> List[Dict[str, Any]]:
    raw = contract.as_dict() if hasattr(contract, "as_dict") else dict(contract or {})
    return [dict(item) for item in raw.get("objective_layers", [])]


def _protected_metrics(contract: Any) -> List[Dict[str, Any]]:
    raw = contract.as_dict() if hasattr(contract, "as_dict") else dict(contract or {})
    return [dict(item) for item in raw.get("protected_metrics", [])]


def _protected_metric_baseline(contract: Any) -> Dict[str, float]:
    raw = contract.as_dict() if hasattr(contract, "as_dict") else dict(contract or {})
    return {
        str(metric): float(value)
        for metric, value in dict(
            raw.get("protected_metric_baseline", {}) or {}
        ).items()
    }


def _contract_id(contract: Any) -> str:
    raw = contract.as_dict() if hasattr(contract, "as_dict") else dict(contract or {})
    return str(raw.get("contract_id", ""))


def _manifest_target(manifest: Optional[Any]) -> str:
    raw = manifest.as_dict() if hasattr(manifest, "as_dict") else dict(manifest or {})
    return str(raw.get("target_id", ""))


def _verification_objective_keys(
    evaluation: Optional[EvalResult], layers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    if evaluation is None or not layers:
        return {}
    return build_objective_keys(evaluation, layers, layers)


__all__ = [
    "EVENT_TAGS",
    "verify_initial_construction",
    "verify_alns_action",
    "verify_review_request",
    "audit_initial_result",
    "audit_outcome",
]
