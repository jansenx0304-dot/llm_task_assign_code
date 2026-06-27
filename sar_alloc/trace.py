"""Basic run trace records and outputs."""

from __future__ import annotations

import json
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping


@dataclass(slots=True)
class StepRecord:
    step_id: str
    phase: str
    observation_id: str | None
    observation: Dict[str, Any] | None = None
    stage_id: str | None = None
    raw_output: str | None = None
    parsed: Dict[str, Any] | None = None
    decision: Dict[str, Any] | None = None
    control: Dict[str, Any] | None = None
    result: Dict[str, Any] | None = None
    completion: Dict[str, Any] | None = None
    error: str | None = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "phase": self.phase,
            "observation_id": self.observation_id,
            "observation": dict(self.observation or {}),
            "stage_id": self.stage_id,
            "raw_output": self.raw_output,
            "parsed": dict(self.parsed or {}),
            "decision": dict(self.decision or {}),
            "control": dict(self.control or {}),
            "result": dict(self.result or {}),
            "completion": dict(self.completion or {}),
            "error": self.error,
        }


@dataclass(slots=True)
class RunTrace:
    steps: List[StepRecord] = field(default_factory=list)

    def add(self, record: StepRecord) -> None:
        self.steps.append(record)

    def recent_for_step(self, n: int = 3) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for record in self.steps[-n:]:
            result = dict(record.result or {})
            control = dict(record.control or {})
            if not result and not control:
                continue
            out.append(
                {
                    "step_id": record.step_id,
                    "action": (record.decision or {}).get("action") or control.get("action"),
                    "intent_id": control.get("intent_id"),
                    "quality_delta": dict(result.get("quality_delta", {}) or {}),
                    "before_feasible": result.get("before_feasible"),
                    "after_feasible": result.get("after_feasible"),
                    "accepted": result.get("accepted"),
                }
            )
        return out

    def recent_for_supervisor(self, n: int = 5) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for record in self.steps[-n:]:
            if not record.stage_id:
                continue
            result = dict(record.result or {})
            completion = dict(record.completion or {})
            out.append(
                {
                    "step_id": record.step_id,
                    "stage_id": record.stage_id,
                    "action": (record.decision or {}).get("action"),
                    "quality": dict(result.get("after_quality", {}) or {}),
                    "feasible": result.get("after_feasible"),
                    "completion": {
                        "completed": completion.get("completed"),
                        "status": completion.get("status"),
                        "reason": completion.get("reason"),
                    },
                }
            )
        return out

    def as_artifact(self) -> Dict[str, Any]:
        return {"steps": [step.as_dict() for step in self.steps]}


class TraceWriter:
    def __init__(
        self,
        *,
        jsonl_path: Path,
        markdown_path: Path | None = None,
        summary_path: Path | None = None,
        run_config: Dict[str, Any] | None = None,
        use_console: bool = True,
    ) -> None:
        self.jsonl_path = jsonl_path
        self.markdown_path = markdown_path or jsonl_path.with_suffix(".md")
        self.summary_path = summary_path or (jsonl_path.parent / "summary.md")
        self.use_console = use_console
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self._jsonl = self.jsonl_path.open("w", encoding="utf-8", newline="\n")
        self._md = self.markdown_path.open("w", encoding="utf-8", newline="\n")
        self._md.write("# Run Trace\n\n")
        if run_config is not None:
            self._write_jsonl({"record_type": "run_config", "payload": run_config})
            self._md.write("## Run Config\n\n```json\n")
            self._md.write(json.dumps(run_config, ensure_ascii=False, indent=2, default=str))
            self._md.write("\n```\n")
        self._md.flush()

    def write_step(self, record: StepRecord) -> None:
        data = record.as_dict()
        self._write_jsonl({"record_type": "step", **data})
        self._md.write(f"\n---\n\n## {record.phase.title()} {record.step_id}\n\n")
        self._md.write(f"- stage: `{record.stage_id or ''}`\n")
        if record.decision:
            self._md.write(f"- action: `{record.decision.get('action', '')}`\n")
        if record.result:
            self._md.write(f"- accepted: `{record.result.get('accepted')}` feasible: `{record.result.get('after_feasible')}`\n")
            self._md.write(f"- quality_delta: `{record.result.get('quality_delta', {})}`\n")
        if record.completion:
            self._md.write(f"- completion: `{record.completion.get('status')}` `{record.completion.get('reason')}`\n")
        if record.error:
            self._md.write(f"- error: `{record.error}`\n")
        self._write_decision_evidence(record)
        self._md.write("\n```json\n")
        self._md.write(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        self._md.write("\n```\n")
        self._md.flush()
        if self.use_console:
            _print_console(record)

    def write_final(self, artifact: Dict[str, Any]) -> None:
        self._write_jsonl({"record_type": "run_final", "payload": artifact})
        self._md.write("\n---\n\n## Final\n\n```json\n")
        self._md.write(json.dumps(artifact, ensure_ascii=False, indent=2, default=str))
        self._md.write("\n```\n")
        self._md.flush()
        self.summary_path.write_text(_summary_markdown(artifact), encoding="utf-8")

    def write_error(self, error: str) -> None:
        self._write_jsonl({"record_type": "run_error", "error": error})
        self._md.write(f"\n---\n\n## Error\n\n`{error}`\n")
        self._md.flush()
        self.summary_path.write_text(f"# Run Summary\n\nstatus: failed\n\nerror: {error}\n", encoding="utf-8")

    def fail(self, exc: BaseException) -> None:
        self.write_error(f"{type(exc).__name__}: {exc}\n{''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")
        self.close()

    def close(self) -> None:
        self._jsonl.close()
        self._md.close()

    def _write_jsonl(self, record: Dict[str, Any]) -> None:
        self._jsonl.write(json.dumps(record, ensure_ascii=False, default=str, separators=(",", ":")) + "\n")
        self._jsonl.flush()

    def _write_decision_evidence(self, record: StepRecord) -> None:
        evidence = _decision_evidence_from_record(record)
        if not evidence:
            return
        self._md.write("\n### Decision Evidence\n\n")
        basis = [dict(item) for item in evidence.get("basis", []) or [] if isinstance(item, dict)]
        if basis:
            self._md.write("Basis:\n")
            for index, item in enumerate(basis):
                value = _resolve_basis_value(record.observation or {}, str(item.get("source", "")), str(item.get("name", "")))
                suffix = "" if value is None else f" = `{_compact_json(value)}`"
                self._md.write(f"- [{index}] {item.get('source', '')}.{item.get('name', '')}{suffix}\n")
            self._md.write("\n")
        argument = [dict(item) for item in evidence.get("argument", []) or [] if isinstance(item, dict)]
        if argument:
            self._md.write("Argument:\n")
            for item in argument:
                self._md.write(f"- uses {item.get('uses', [])}: {item.get('claim', '')}\n")
            self._md.write("\n")
        intent = str(evidence.get("control_intent", "") or "")
        if intent:
            self._md.write("Control intent:\n")
            self._md.write(f"> {intent}\n\n")
        effects = [dict(item) for item in evidence.get("expected_effects", []) or [] if isinstance(item, dict)]
        self._md.write("Expected effects:\n")
        if effects:
            for item in effects:
                self._md.write(f"- {item.get('metric', '')}: {item.get('direction', '')}\n")
        else:
            self._md.write("- none\n")
        if record.result:
            self._md.write(f"\nActual quality_delta:\n- `{record.result.get('quality_delta', {})}`\n")
        self._md.write("\n")


def _decision_evidence_from_record(record: StepRecord) -> Dict[str, Any]:
    decision = dict(record.decision or {})
    if "decision_evidence" in decision:
        return dict(decision.get("decision_evidence") or {})
    parsed = dict(record.parsed or {})
    if "decision_evidence" in parsed:
        return dict(parsed.get("decision_evidence") or {})
    return {}


def _resolve_basis_value(observation: Mapping[str, Any], source: str, name: str) -> Any:
    block = observation.get(source)
    if isinstance(block, Mapping) and name in block:
        return block.get(name)
    if source in {"solution_evidence", "solution_state"} and isinstance(block, Mapping):
        working = dict(block.get("working", {}) or {})
        best = dict(block.get("best_feasible", {}) or {})
        quality = dict(working.get("quality", {}) or {})
        if name in quality:
            return quality.get(name)
        if name == "working_is_feasible":
            return working.get("is_feasible")
        if name == "best_feasible_exists":
            return best.get("exists")
        if name == "feasibility_summary":
            return working.get("feasibility")
    if source == "runtime_feedback" and isinstance(block, Mapping):
        last = dict(block.get("last_result", {}) or {})
        aliases = {
            "last_action": "last_action",
            "last_quality_delta": "quality_delta",
            "last_accepted": "accepted",
            "last_protected_passed": "protected_passed",
            "last_trace_counts": "trace_counts",
        }
        return last.get(aliases.get(name, name))
    if source == "recent_records" and isinstance(block, list):
        if name == "recent_actions":
            return [dict(item).get("action") for item in block if isinstance(item, Mapping)]
        if name in {"recent_quality", "recent_quality_delta"}:
            return [dict(item).get("quality_delta", dict(item).get("quality")) for item in block if isinstance(item, Mapping)]
        if name in {"recent_acceptance", "recent_completion"}:
            key = "accepted" if name == "recent_acceptance" else "completion"
            return [dict(item).get(key) for item in block if isinstance(item, Mapping)]
    return None


def _compact_json(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))
    return text if len(text) <= 180 else text[:177] + "..."


def _print_console(record: StepRecord) -> None:
    result = record.result or {}
    text = (
        f"[{record.phase.upper()}] {record.step_id} stage={record.stage_id or ''} "
        f"action={(record.decision or {}).get('action', '')} "
        f"accepted={result.get('accepted')} feasible={result.get('after_feasible')}"
    )
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"), flush=True)


def _summary_markdown(summary: Dict[str, Any]) -> str:
    return (
        "# Run Summary\n\n"
        f"- hard_feasible: {summary.get('hard_feasible')}\n"
        f"- missed_priority: {summary.get('missed_priority')}\n"
        f"- unassigned_count: {summary.get('unassigned_count')}\n"
        f"- energy_total: {summary.get('energy_total')}\n"
        f"- total_distance: {summary.get('total_distance')}\n"
        f"- elapsed_sec: {summary.get('elapsed_sec')}\n"
    )


__all__ = ["RunTrace", "StepRecord", "TraceWriter"]
