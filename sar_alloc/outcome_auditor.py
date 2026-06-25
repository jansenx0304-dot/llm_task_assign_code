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
    applied_evaluation: Optional[EvalResult] = None,
    *,
    decision_id: str = "",
    verification_id: str = "",
) -> Dict[str, Any]:
    trace = dict(getattr(result, "trace", {}) or {})
    trace["trace_id"] = str(
        trace.get("trace_id") or f"X_{verification_id or 'initial'}"
    )
    evaluation = getattr(result, "evaluation", None)
    working_evaluation = applied_evaluation or evaluation
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
        intent_id=_manifest_intent(manifest),
    )
    verification.update(
        {
            "contract_objective_status": status,
            "metric_delta": {
                "working": (
                    _metric_values(working_evaluation, _contract_metrics(contract))
                    if working_evaluation is not None
                    else {}
                ),
                "best_feasible": (
                    _metric_values(working_evaluation, _contract_metrics(contract))
                    if working_evaluation is not None and working_evaluation.is_feasible
                    else {}
                ),
            },
            "debt_delta": {},
            "protected_metric_result": protected,
            "feasibility_result": {
                "mode": "strict",
                "passed": bool(evaluation is not None and evaluation.is_feasible),
                "is_feasible": bool(evaluation is not None and evaluation.is_feasible),
            },
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
                working_evaluation, _contract_metrics(contract)
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
    runtime_protection = dict(trace.get("protected_metrics", {}) or {})
    protected.update(
        {
            "rejected_trials": int(
                runtime_protection.get("rejected_trials", 0) or 0
            ),
            "rejection_reasons": dict(
                runtime_protection.get("rejection_reasons", {}) or {}
            ),
            "bounds": list(runtime_protection.get("bounds", []) or []),
        }
    )
    feasibility = _feasibility_result(
        before_working_eval, after_working_eval, trace, manifest
    )
    chosen_after = _better_eval(after_working_eval, after_action_best_eval, metrics)
    status = (
        "regressed"
        if not protected["passed"]
        else _contract_objective_status(
            before_working_eval, chosen_after, metrics, debt_delta
        )
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
        intent_id=_manifest_intent(manifest),
    )
    verification.update(
        {
            "contract_objective_status": status,
            "metric_delta": {"working": working_delta, "best_feasible": best_delta},
            "debt_delta": debt_delta,
            "protected_metric_result": protected,
            "feasibility_result": feasibility,
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
    review_reasons = _manifest_review_reasons(manifest)
    blocker = (
        "no_executable_action"
        if "no_executable_action" in review_reasons
        else "solver_requested_review"
    )
    trace = {
        "trace_id": trace_id,
        "kind": "review_request",
        "recent_verification_ids": [
            item.get("verification_id") for item in recent_verifications
        ],
        "review_reasons": review_reasons,
    }
    verification = _base_verification(
        verification_id=verification_id,
        contract=contract,
        decision_id=decision_id,
        manifest=manifest,
        trace=trace,
        action="request_supervisor_review",
        intent_id=(decision.get("solver_decision", decision)).get(
            "intent_id", "contract_review"
        ),
    )
    verification.update(
        {
            "contract_objective_status": "not_applicable",
            "metric_delta": {"working": {}, "best_feasible": {}},
            "debt_delta": {},
            "protected_metric_result": {"passed": True, "violations": []},
            "feasibility_result": {"mode": "not_applicable", "passed": True},
            "protected_metric_baseline": _protected_metric_baseline(contract),
            "dominant_blocker": blocker,
            "flow_diagnosis": _flow_diagnosis(blocker, "not_applicable"),
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


def _base_verification(
    *,
    verification_id: str,
    contract: Any,
    decision_id: str,
    manifest: Optional[Any],
    trace: Dict[str, Any],
    action: str,
    intent_id: str,
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
        "intent_id": intent_id,
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


def _feasibility_result(
    before_eval: EvalResult,
    after_eval: EvalResult,
    trace: Dict[str, Any],
    manifest: Any,
) -> Dict[str, Any]:
    manifest_raw = (
        manifest.as_dict() if hasattr(manifest, "as_dict") else dict(manifest or {})
    )
    compiled = dict(manifest_raw.get("compiled", {}) or {})
    policy = dict(compiled.get("feasibility", {}) or {})
    runtime = dict(trace.get("feasibility_control", {}) or {})
    runtime_check = dict(runtime.get("returned_check", {}) or {})
    runtime_policy = dict(runtime.get("policy", {}) or {})
    if runtime_policy:
        policy = runtime_policy
    mode = str(policy.get("mode", "strict"))
    before_report = before_eval.constraint_report
    after_report = after_eval.constraint_report
    ratios = dict(getattr(after_report, "violation_ratio_by_type", {}) or {})
    limits = dict(policy.get("per_type", {}) or {})
    violations: List[Dict[str, Any]] = []
    if mode == "strict":
        passed = bool(after_eval.is_feasible)
        if not passed:
            violations.append({"reason": "returned_working_is_infeasible"})
    elif mode == "recovery_only":
        before_total = float(getattr(before_report, "violation_total", 0.0) or 0.0)
        after_total = float(getattr(after_report, "violation_total", 0.0) or 0.0)
        passed = bool(after_eval.is_feasible or after_total < before_total - 1e-9)
        if not passed:
            violations.append(
                {
                    "reason": "recovery_non_reducing_returned_working",
                    "before": before_total,
                    "after": after_total,
                }
            )
    else:
        passed = bool(
            float(getattr(after_report, "unrecoverable_violation_total", 0.0) or 0.0)
            <= 1e-9
        )
        for name, values in limits.items():
            actual = float(ratios.get(name, 0.0) or 0.0)
            limit = float(values.get("limit_ratio", 0.0) or 0.0)
            if actual > limit + 1e-9:
                passed = False
                violations.append(
                    {"violation_type": str(name), "actual": actual, "limit": limit}
                )
        for name, actual in ratios.items():
            if float(actual) > 1e-9 and name not in limits:
                passed = False
                violations.append(
                    {"violation_type": str(name), "reason": "not_relaxable"}
                )
    return {
        "mode": mode,
        "passed": bool(passed),
        "is_feasible": bool(after_eval.is_feasible),
        "violation_ratio_by_type": {
            str(name): float(value) for name, value in ratios.items()
        },
        "violations": violations,
        "runtime_policy": policy,
        "runtime_check": runtime_check,
        "trace_consistent": bool(
            not runtime_check or bool(runtime_check.get("passed")) == bool(passed)
        ),
    }


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


def _contract_objective_status(
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


def _manifest_intent(manifest: Optional[Any]) -> str:
    raw = manifest.as_dict() if hasattr(manifest, "as_dict") else dict(manifest or {})
    return str(raw.get("intent_id", ""))


def _manifest_review_reasons(manifest: Optional[Any]) -> List[str]:
    raw = manifest.as_dict() if hasattr(manifest, "as_dict") else dict(manifest or {})
    review_request = dict((raw.get("compiled", {}) or {}).get("review_request", {}) or {})
    reasons = [str(value) for value in review_request.get("evidence_refs", []) or []]
    if review_request.get("reason"):
        reasons.insert(0, str(review_request["reason"]))
    return reasons


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
]
