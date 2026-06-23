from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class RunMemory:
    observations: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    verified_actions: List[Dict[str, Any]] = field(default_factory=list)
    contract_summaries: List[Dict[str, Any]] = field(default_factory=list)

    def record_observation(self, observation: Dict[str, Any]) -> str:
        observation_id = str(observation.get("observation_id") or f"O{len(self.observations)}")
        observation["observation_id"] = observation_id
        self.observations.append(dict(observation))
        return observation_id

    def record_decision(self, decision: Dict[str, Any], observation: Dict[str, Any]) -> str:
        decision_id = f"D{len(self.decisions) + 1}"
        item = {
            "decision_id": decision_id,
            "observation_id": observation.get("observation_id", ""),
            "payload": dict(decision),
        }
        self.decisions.append(item)
        return decision_id

    def record_verified_action(
        self,
        observation: Dict[str, Any],
        decision: Dict[str, Any],
        manifest: Any,
        trace: Dict[str, Any],
        verification: Dict[str, Any],
    ) -> Dict[str, Any]:
        manifest_dict = manifest.as_dict() if hasattr(manifest, "as_dict") else dict(manifest or {})
        record_id = f"M{len(self.verified_actions) + 1}"
        trace_id = str(trace.get("trace_id", ""))
        manifest_trace_id = str(manifest_dict.get("trace_id", ""))
        verification_trace_id = str(verification.get("trace_id", ""))
        if not trace_id or not manifest_trace_id or not verification_trace_id:
            raise ValueError("manifest, execution trace, and verification must have a non-empty trace_id")
        if len({trace_id, manifest_trace_id, verification_trace_id}) != 1:
            raise ValueError("manifest, execution trace, and verification trace_id must match")
        verification_id = str(verification.get("verification_id") or f"V{len(self.verified_actions) + 1}")
        verification["verification_id"] = verification_id
        verification["manifest_id"] = manifest_dict.get("manifest_id", verification.get("manifest_id", ""))
        verification["decision_id"] = manifest_dict.get("source_decision_id", verification.get("decision_id", ""))
        verification["contract_id"] = manifest_dict.get("contract_id", verification.get("contract_id", ""))
        verification["target_id"] = manifest_dict.get("target_id", verification.get("target_id", ""))
        verification["trace"] = dict(trace)
        target_kind = _target_kind(observation, str(verification.get("target_id", "")))
        item = {
            "record_id": record_id,
            "kind": "verified_action",
            "contract_id": verification.get("contract_id", ""),
            "observation_id": observation.get("observation_id", ""),
            "decision_id": verification.get("decision_id", ""),
            "manifest_id": verification.get("manifest_id", ""),
            "trace_id": trace_id,
            "verification_id": verification_id,
            "target_id": verification.get("target_id", ""),
            "target_kind": target_kind,
            "control_fingerprint": _control_fingerprint(manifest_dict),
            "outcome_fingerprint": _outcome_fingerprint(verification),
            "manifest": manifest_dict,
            "trace": dict(trace),
            "verification": dict(verification),
        }
        self.verified_actions.append(item)
        return item

    def record_contract_summary(self, contract: Any, progress: Any, completion: Dict[str, Any]) -> Dict[str, Any]:
        contract_dict = contract.as_dict() if hasattr(contract, "as_dict") else dict(contract)
        progress_dict = progress.as_dict() if hasattr(progress, "as_dict") else dict(progress)
        item = {
            "summary_id": f"CS{len(self.contract_summaries) + 1}",
            "kind": "contract_summary",
            "contract_id": contract_dict.get("contract_id", ""),
            "contract_type": contract_dict.get("contract_type", ""),
            "objective_layers": contract_dict.get("objective_layers", []),
            "progress": progress_dict,
            "completion": dict(completion),
        }
        self.contract_summaries.append(item)
        return item

    def last_verification(self) -> Optional[Dict[str, Any]]:
        if not self.verified_actions:
            return None
        return dict(self.verified_actions[-1]["verification"])

    def recent_verifications(self, contract_id: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        values = [item["verification"] for item in self.verified_actions]
        if contract_id is not None:
            values = [item for item in values if str(item.get("contract_id", "")) == str(contract_id)]
        return [dict(item) for item in values[-limit:]]

    def for_solver(self, contract: Optional[Any] = None, decision_targets: Optional[List[Dict[str, Any]]] = None, limit: int = 3) -> List[Dict[str, Any]]:
        del decision_targets
        contract_id = None
        if contract is not None:
            raw = contract.as_dict() if hasattr(contract, "as_dict") else dict(contract)
            contract_id = raw.get("contract_id")
        values = self.verified_actions
        if contract_id is not None:
            values = [item for item in values if str(item.get("contract_id", "")) == str(contract_id)]
        return [_solver_memory_item(item) for item in values[-limit:]]

    def for_supervisor(self, limit: int = 5) -> List[Dict[str, Any]]:
        values: List[Dict[str, Any]] = []
        values.extend(self.contract_summaries)
        values.extend(self.verified_actions)
        values.sort(key=lambda item: str(item.get("summary_id", item.get("record_id", ""))))
        return [_supervisor_memory_item(item) for item in values[-limit:]]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "observations": self.observations,
            "decisions": self.decisions,
            "verified_actions": self.verified_actions,
            "contract_summaries": self.contract_summaries,
        }


def _target_kind(observation: Dict[str, Any], target_id: str) -> str:
    for item in observation.get("decision_targets", []) or []:
        if isinstance(item, dict) and str(item.get("target_id", "")) == target_id:
            return str(item.get("kind", ""))
    return ""


def _control_fingerprint(manifest: Dict[str, Any]) -> Dict[str, Any]:
    compiled = manifest.get("compiled", {}) or {}
    if manifest.get("action") == "request_supervisor_review":
        return {"action": "review_request"}
    destroy_manifest = compiled.get("destroy", {}) or {}
    destroy = destroy_manifest.get("operator_weights", {}) or {}
    destroy_signals = destroy_manifest.get("signal_weights", {}) or {}
    insertion = compiled.get("insertion", {}) or {}
    insertion_operators = insertion.get("operator_weights", {}) or {}
    task = insertion.get("task_signal_weights", {}) or {}
    pos = insertion.get("position_signal_weights", {}) or {}
    acceptance = compiled.get("acceptance", {}) or {}
    return {
        "destroy_operator_top": _top_nonzero(destroy),
        "destroy_signal_top": _top_nonzero(destroy_signals),
        "insertion_operator_top": _top_nonzero(insertion_operators),
        "insertion_task_signal_top": _top_nonzero(task),
        "insertion_position_signal_top": _top_nonzero(pos),
        "acceptance": "" if not acceptance else f"{acceptance.get('mode')}:{acceptance.get('intensity_score', '')}",
    }


def _outcome_fingerprint(verification: Dict[str, Any]) -> Dict[str, Any]:
    flow = ((verification.get("trace", {}) or {}).get("trial_flow", {}) or {})
    working = (verification.get("metric_delta", {}) or {}).get("working", {}) or {}
    return {
        "intent_status": verification.get("intent_status"),
        "dominant_blocker": verification.get("dominant_blocker"),
        "best_improved": int(flow.get("best_improved_trials", 0) or 0) > 0,
        "metric_delta": dict(working),
    }


def _top_nonzero(values: Dict[str, Any], limit: int = 2) -> List[str]:
    if not isinstance(values, dict) or not values:
        return []
    ordered = sorted(values.items(), key=lambda item: (-float(item[1]), str(item[0])))
    return [str(name) for name, value in ordered if float(value) > 0.0][:limit]


def _solver_memory_item(item: Dict[str, Any]) -> Dict[str, Any]:
    outcome = item.get("outcome_fingerprint", {}) or {}
    control = item.get("control_fingerprint", {}) or {}
    trace = item.get("trace", {}) or {}
    flow = trace.get("trial_flow", {}) or {}
    metric_delta = outcome.get("metric_delta", {}) or {}
    delta_text = ", ".join(f"{k} {v:+.3g}" for k, v in metric_delta.items()) or "no metric delta"
    return {
        "record_id": item.get("record_id"),
        "target_kind": item.get("target_kind"),
        "control_summary": _control_summary(control),
        "outcome": f"{delta_text}, accepted {flow.get('accepted_trials', 0)}/{flow.get('candidate_trials', 0)}, blocker {outcome.get('dominant_blocker')}",
    }


def _supervisor_memory_item(item: Dict[str, Any]) -> Dict[str, Any]:
    if item.get("kind") == "contract_summary":
        return {
            "summary_id": item.get("summary_id"),
            "contract_id": item.get("contract_id"),
            "contract_type": item.get("contract_type"),
            "completion_status": (item.get("completion", {}) or {}).get("completion_status"),
            "condition_report": (item.get("completion", {}) or {}).get("condition_report", []),
        }
    return {
        "record_id": item.get("record_id"),
        "contract_id": item.get("contract_id"),
        "intent_status": (item.get("outcome_fingerprint", {}) or {}).get("intent_status"),
        "dominant_blocker": (item.get("outcome_fingerprint", {}) or {}).get("dominant_blocker"),
    }


def _control_summary(control: Dict[str, Any]) -> str:
    if control.get("action") == "review_request":
        return "review_request"
    pieces = []
    pieces.extend(control.get("destroy_operator_top", [])[:1])
    pieces.extend(control.get("destroy_signal_top", [])[:1])
    pieces.extend(control.get("insertion_operator_top", [])[:1])
    pieces.extend(control.get("insertion_task_signal_top", [])[:1])
    pieces.extend(control.get("insertion_position_signal_top", [])[:1])
    if control.get("acceptance"):
        pieces.append(str(control["acceptance"]))
    return " + ".join(str(piece) for piece in pieces if piece)


__all__ = ["RunMemory"]
