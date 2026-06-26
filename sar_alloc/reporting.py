from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional


def event_category(event_type: str) -> str:
    normalized = event_type.lower()
    if normalized.endswith("_observation"):
        return "observation"
    if normalized.endswith("_prompt"):
        return "prompt"
    if normalized.endswith("_raw_output"):
        return "raw"
    if normalized.endswith("_validation_result") or normalized.startswith("validated_"):
        return "validated"
    if normalized.startswith("compiled_") or normalized == "runtime_control_manifest":
        return "compiled"
    if normalized.startswith("solver_") or normalized in {
        "solver_request",
        "solver_result",
    }:
        return "solver"
    if normalized in {"outcome_audit", "outcome_verification"}:
        return "audit"
    if normalized == "execution_trace":
        return "solver"
    if normalized in {"contract_completion_check", "contract_end", "contract_progress"}:
        return "review"
    if normalized == "final_result":
        return "final"
    if normalized == "run_start":
        return "run"
    if normalized == "public_candidates":
        return "public"
    if normalized == "memory_update":
        return "memory"
    if "initial" in normalized:
        return "initial"
    return "default"


EMOJI = {
    "run": "[RUN]",
    "public": "[PUB]",
    "observation": "[OBS]",
    "prompt": "[PROMPT]",
    "raw": "[RAW]",
    "validated": "[OK]",
    "compiled": "[COMP]",
    "solver": "[SOLVER]",
    "audit": "[AUDIT]",
    "review": "[CONTRACT]",
    "memory": "[MEM]",
    "initial": "[INIT]",
    "final": "[FINAL]",
    "default": "[TRACE]",
}

COLOR = {
    "run": "\033[96m",
    "public": "\033[36m",
    "observation": "\033[90m",
    "prompt": "\033[95m",
    "raw": "\033[94m",
    "validated": "\033[92m",
    "compiled": "\033[34m",
    "solver": "\033[36m",
    "audit": "\033[93m",
    "review": "\033[33m",
    "memory": "\033[90m",
    "initial": "\033[92m",
    "final": "\033[92m",
    "error": "\033[91m",
    "default": "\033[0m",
}

RESET = "\033[0m"


class JsonlTraceWriter:
    def __init__(self, path: Path, run_config: Dict[str, Any]) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8", newline="\n")
        self._closed = False
        self._write_record(
            {
                "record_type": "run_config",
                "status": "running",
                "payload": run_config,
            }
        )

    def append_event(self, event: Dict[str, Any]) -> None:
        self._write_record({"record_type": "trace_event", **event})

    def append_final(self, solution: Any, summary: Dict[str, Any]) -> None:
        del solution
        self._write_record(
            {
                "record_type": "run_final",
                "status": "finished",
                "payload": summary,
            }
        )

    def append_error(self, exc: BaseException) -> None:
        self._write_record(
            {
                "record_type": "run_error",
                "status": "failed",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "traceback": "".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__)
                ),
            }
        )

    def close(self) -> None:
        if self._closed:
            return
        self.flush()
        self._file.close()
        self._closed = True

    def flush(self) -> None:
        if not self._closed:
            self._file.flush()

    def _write_record(self, record: Dict[str, Any]) -> None:
        self._file.write(
            json.dumps(record, ensure_ascii=False, default=str, separators=(",", ":"))
            + "\n"
        )
        self.flush()


class MarkdownTraceWriter:
    def __init__(self, path: Path, run_config: Dict[str, Any]) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8", newline="\n")
        self._closed = False
        self._write("# Run Trace\n\n")
        self._write("## Run Config\n\n")
        self._write("```json\n")
        self._write(json.dumps(run_config, ensure_ascii=False, indent=2, default=str))
        self._write("\n```\n")

    def append_event(self, event: Dict[str, Any]) -> None:
        event_type = str(event.get("event_type", ""))
        payload = event.get("payload")
        if event_type == "runtime_control_manifest":
            self._append_manifest(event, payload)
        elif event_type == "execution_trace":
            self._append_execution_trace(event, payload)
        elif event_type in {"outcome_verification", "outcome_audit"}:
            self._append_audit(event, payload)
        elif event_type == "contract_end":
            self._write("\n---\n\n## ⚠️ Contract End\n\n")
            self._write(_compact_json(payload))
        elif event_type == "final_result":
            self._write("\n---\n\n## ✅ Final Summary\n\n")
            self._write(_compact_json(payload))

    def append_final(self, solution: Any, summary: Dict[str, Any]) -> None:
        del solution
        self._write("\n---\n\n## ✅ Run Finished\n\n")
        self._write(_compact_json(summary))

    def append_error(self, exc: BaseException) -> None:
        self._write("\n---\n\n## ❌ Run Failed\n\n")
        self._write(f"- error: `{type(exc).__name__}: {exc}`\n")

    def close(self) -> None:
        if self._closed:
            return
        self.flush()
        self._file.close()
        self._closed = True

    def flush(self) -> None:
        if not self._closed:
            self._file.flush()

    def _append_manifest(self, event: Dict[str, Any], payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        action = str(payload.get("action", ""))
        heading = "🧭 Supervisor Kickoff" if action == "start_run" else "🔧 Solver Step"
        self._write(f"\n---\n\n## {heading} {event.get('step_index', '')}\n\n")
        compiled = dict(payload.get("compiled", {}) or {})
        self._write("### Action\n\n")
        self._write(f"- action: `{action}`\n")
        self._write(f"- intent: `{payload.get('intent_id', '')}`\n")
        self._write(f"- target: `{compiled.get('target', {})}`\n")
        self._append_basis(compiled.get("decision_basis", []) or [])
        self._append_effects(compiled.get("expected_effects", []) or [])

    def _append_execution_trace(self, event: Dict[str, Any], payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        self._write("\n### Operator Priors\n\n")
        prior = dict(payload.get("operator_prior_trace", {}) or {})
        if prior:
            self._write(_compact_json(prior))
        engagement = dict(payload.get("target_agent_engagement", {}) or {})
        if engagement:
            self._write("\n### 📊 Target Engagement\n\n")
            self._write(_compact_json(engagement))

    def _append_audit(self, event: Dict[str, Any], payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        self._write("\n### 📈 Expected Effects vs Actual Effects\n\n")
        effects = payload.get("effect_audit", []) or []
        if effects:
            self._write("| Effect | Metric | Expected | Actual Delta | Matched |\n")
            self._write("|---|---|---|---:|---|\n")
            for item in effects:
                if not isinstance(item, dict):
                    continue
                self._write(
                    f"| {item.get('effect_id', '')} | {item.get('metric', '')} | "
                    f"{item.get('expected_direction', '')} | {item.get('actual_delta', '')} | "
                    f"{item.get('matched', '')} |\n"
                )
        else:
            self._write("- no expected effects recorded\n")

    def _append_basis(self, basis: Any) -> None:
        if not basis:
            return
        self._write("\n### Decision Basis\n\n")
        self._write("| Basis | Claim | Evidence |\n")
        self._write("|---|---|---|\n")
        for item in basis:
            if not isinstance(item, dict):
                continue
            self._write(
                f"| {item.get('basis_id', '')} | {item.get('claim', '')} | "
                f"{', '.join(str(ref) for ref in item.get('evidence_refs', []) or [])} |\n"
            )

    def _append_effects(self, effects: Any) -> None:
        if not effects:
            return
        self._write("\n### Expected Effects\n\n")
        self._write("| Effect | Metric | Direction | Scope | Basis |\n")
        self._write("|---|---|---|---|---|\n")
        for item in effects:
            if not isinstance(item, dict):
                continue
            self._write(
                f"| {item.get('effect_id', '')} | {item.get('metric', '')} | "
                f"{item.get('direction', '')} | {item.get('scope', '')} | "
                f"{', '.join(str(ref) for ref in item.get('basis_ids', []) or [])} |\n"
            )

    def _write(self, text: str) -> None:
        self._file.write(text)
        self.flush()


def _compact_json(payload: Any) -> str:
    return "```json\n" + json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n```\n"


class ConsoleTracePrinter:
    def __init__(self, use_color: bool = True, use_emoji: bool = True) -> None:
        self.use_color = use_color
        self.use_emoji = use_emoji
        self._last_group = ""

    def print_event(self, event: Dict[str, Any]) -> None:
        event_type = str(event.get("event_type", ""))
        category = event_category(event_type)
        self._print_separator(event, category)
        marker = EMOJI.get(category, "[TRACE]") if self.use_emoji else ""
        color = COLOR.get(category, "") if self.use_color else ""
        reset = RESET if self.use_color else ""
        label = self._label(event)
        text = (
            f"{marker + ' ' if marker else ''}{label:<28} {self._event_summary(event)}"
        )
        print(self._sanitize(color + text + reset), flush=True)

    def print_final(self, summary: Dict[str, Any]) -> None:
        feasible = bool(summary.get("hard_feasible", False))
        category = "final" if feasible else "error"
        self._print_separator({"event_type": "final"}, category, force=True)
        color = COLOR.get(category, "") if self.use_color else ""
        reset = RESET if self.use_color else ""
        marker = "[FINAL] " if self.use_emoji else ""
        text = (
            f"{marker}{'FINAL':<28} feasible={str(feasible).lower()} "
            f"unassigned={summary.get('unassigned_count')} "
            f"missed_priority={summary.get('missed_priority')} "
            f"energy={summary.get('energy_total')} elapsed={summary.get('elapsed_sec')}"
        )
        print(self._sanitize(color + text + reset), flush=True)

    def print_error(self, exc: BaseException) -> None:
        self._print_separator({"event_type": "error"}, "error", force=True)
        color = COLOR["error"] if self.use_color else ""
        reset = RESET if self.use_color else ""
        marker = "[ERROR] " if self.use_emoji else ""
        text = f"{marker}{'ERROR':<28} {type(exc).__name__}: {exc}"
        print(self._sanitize(color + text + reset), flush=True)

    def _label(self, event: Dict[str, Any]) -> str:
        event_type = str(event.get("event_type", ""))
        if event.get("step_index") is not None:
            step = int(event["step_index"])
            if event_type.startswith("solver_"):
                return f"SOLVER {step:03d}"
            if event_type in {
                "solver_request",
                "solver_result",
                "outcome_audit",
                "contract_completion_check",
            }:
                return f"{event_type.upper()} {step:03d}"
        if event.get("contract_id") is not None:
            return f"{event_type.upper()} {event['contract_id']}"
        return event_type.upper()

    def _print_separator(
        self, event: Dict[str, Any], category: str, force: bool = False
    ) -> None:
        group = self._event_group(event, category)
        if not force and group == self._last_group:
            return
        self._last_group = group
        color = COLOR.get(category, "") if self.use_color else ""
        reset = RESET if self.use_color else ""
        line = f"\n{'-' * 88}\n{group}"
        print(self._sanitize(color + line + reset), flush=True)

    def _event_group(self, event: Dict[str, Any], category: str) -> str:
        event_type = str(event.get("event_type", "")).upper()
        index = int(event.get("index", 0) or 0)
        context = []
        if event.get("contract_id") is not None:
            context.append(str(event["contract_id"]))
        if event.get("step_index") is not None:
            context.append(f"SOLVER {int(event['step_index']):03d}")
        suffix = f" | {' / '.join(context)}" if context else ""
        prefix = f"#{index:03d} " if index else ""
        return f"{prefix}{category.upper()} :: {event_type}{suffix}"

    def _event_summary(self, event: Dict[str, Any]) -> str:
        event_type = str(event.get("event_type", ""))
        payload = event.get("payload")
        if event_type.endswith("_observation"):
            return "observation recorded"
        if event_type.endswith("_prompt"):
            return "prompt recorded"
        if event_type.endswith("_raw_output"):
            return "raw output received"
        if event_type.endswith("_validation_result"):
            return self._validated_summary(event_type, payload)
        if event_type == "run_start":
            return self._run_start_summary(payload)
        if event_type == "public_candidates":
            return "public candidates recorded"
        if event_type == "compiled_contract":
            return self._compiled_contract_summary(payload)
        if event_type == "runtime_control_manifest":
            return self._manifest_summary(payload)
        if event_type == "compiled_solver_policy":
            return self._compiled_solver_summary(payload)
        if event_type == "compiled_initial_policy":
            return "initial insertion policy compiled"
        if event_type == "solver_request":
            return self._solver_request_summary(payload)
        if event_type == "solver_result":
            return self._solver_result_summary(payload)
        if event_type == "execution_trace":
            return self._execution_trace_summary(payload)
        if event_type in {"outcome_audit", "outcome_verification"}:
            if isinstance(payload, dict) and "contract_objective_status" in payload:
                return f"status={payload.get('contract_objective_status')} blocker={payload.get('dominant_blocker')}"
            return (
                f"events={payload.get('events', [])}"
                if isinstance(payload, dict)
                else "audit recorded"
            )
        if event_type == "contract_completion_check":
            if isinstance(payload, dict):
                return f"completed={payload.get('completed')} reason={payload.get('completion_reason')}"
            return "completion check recorded"
        if event_type == "initial_insertion_result":
            return self._initial_result_summary(payload)
        if event_type == "memory_update":
            return "memory updated"
        if event_type == "final_result":
            return "final result recorded"
        return "recorded"

    def _run_start_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "run started"
        return (
            f"instance={payload.get('instance')} mode={payload.get('llm_mode')} "
            f"budget={payload.get('global_budget')}"
        )

    def _validated_summary(self, event_type: str, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "validated"
        validated = payload.get("validated_payload", {}) or {}
        if event_type == "solver_validation_result":
            return f"action={(validated.get('solver_decision') or {}).get('action', 'unknown')} source={payload.get('source')}"
        if event_type in {
            "supervisor_kickoff_validation_result",
            "supervisor_review_validation_result",
        }:
            return f"action={(validated.get('supervisor_decision') or {}).get('action', 'unknown')} source={payload.get('source')}"
        return "validated"

    def _compiled_contract_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "contract compiled"
        policy = payload.get("resource_policy", {}) or {}
        objective = [
            item.get("metric")
            for item in payload.get("objective_layers", [])
            if isinstance(item, dict)
        ]
        return (
            f"type={payload.get('contract_type')} objective={objective} "
            f"actions={policy.get('min_actions')}..{policy.get('max_actions')}"
        )

    def _manifest_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "manifest compiled"
        compiled = payload.get("compiled", {}) or {}
        action = payload.get("action")
        intent = payload.get("intent_id")
        target = compiled.get("target", {}) or {}
        target_text = self._format_runtime_target(target)
        if action == "run_alns":
            destroy = (compiled.get("destroy", {}) or {}).get("operator_weights", {})
            insertion = (compiled.get("insertion", {}) or {}).get(
                "operator_weights", {}
            )
            return f"action={action} intent={intent} {target_text} destroy={self._format_operator_weights(destroy)} insertion={self._format_operator_weights(insertion)}"
        return f"action={action} intent={intent} {target_text}"

    def _execution_trace_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "execution trace recorded"
        flow = payload.get("trial_flow", {}) or {}
        target = payload.get("runtime_target", {}) or {}
        engagement = payload.get("target_engagement", {}) or {}
        target_text = self._format_runtime_target(target)
        if flow:
            return (
                f"trials={flow.get('candidate_trials')} accepted={flow.get('accepted_trials')} "
                f"global_best_updates={flow.get('global_best_improved_trials')} {target_text} "
                f"target_destroy_used={engagement.get('target_destroy_moves_used', 0)} "
                f"target_inserted={engagement.get('target_tasks_inserted', [])}"
            )
        return (
            f"kind={payload.get('kind')} inserted={payload.get('inserted_task_count')} {target_text}"
        )

    def _compiled_solver_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "solver policy compiled"
        llm_scores = payload.get("llm_operator_scores", {}) or {}
        if llm_scores:
            return (
                f"llm_destroy_scores={self._format_operator_scores(llm_scores.get('destroy'))} "
                f"llm_insertion_scores={self._format_operator_scores(llm_scores.get('insertion'))}"
            )
        destroy = payload.get("destroy_policy", {}) or {}
        insertion = payload.get("insertion_policy", {}) or {}
        return (
            f"destroy={self._format_operator_weights(destroy.get('operator_weights'))} "
            f"insertion={self._format_operator_weights(insertion.get('operator_weights'))}"
        )

    def _solver_request_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "solver request recorded"
        return f"time={payload.get('time_limit_sec')}s iters={payload.get('max_iters')}"

    def _solver_result_summary(self, payload: Any) -> str:
        diagnostics = (
            payload.get("diagnostics", {}) if isinstance(payload, dict) else {}
        )
        return (
            f"accepted={diagnostics.get('accepted_trial_count')} "
            f"rejected={diagnostics.get('rejected_trial_count')} "
            f"iters={diagnostics.get('actual_iters_used')} time={diagnostics.get('actual_time_used_sec')}"
        )

    def _initial_result_summary(self, payload: Any) -> str:
        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        quality = result.get("quality_summary", {}) or {}
        feasibility = result.get("feasibility_summary", {}) or {}
        return (
            f"feasible={feasibility.get('is_feasible')} "
            f"unassigned={quality.get('unassigned_count')} missed={quality.get('missed_priority')}"
        )

    def _format_operator_weights(self, weights: Any) -> str:
        if not isinstance(weights, dict) or not weights:
            return "unknown"
        ordered = sorted(
            weights.items(), key=lambda item: (-float(item[1]), str(item[0]))
        )
        return "[" + ", ".join(f"{name}:{weight}" for name, weight in ordered) + "]"

    def _format_operator_scores(self, scores: Any) -> str:
        if not isinstance(scores, list) or not scores:
            return "[]"
        return (
            "["
            + ", ".join(
                f"{item.get('name')}:{item.get('score')}"
                for item in scores
                if isinstance(item, dict)
            )
            + "]"
        )

    def _format_runtime_target(self, target: Any) -> str:
        if not isinstance(target, dict) or not target:
            return "runtime_target=none"
        return (
            f"runtime_target={target.get('scope_kind', 'global')} "
            f"task_ids={target.get('task_ids', [])} "
            f"agent_ids={target.get('agent_ids', [])}"
        )

    def _sanitize(self, text: str) -> str:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        return text.encode(encoding, errors="replace").decode(
            encoding, errors="replace"
        )


class RunReporter:
    def __init__(
        self,
        jsonl_path: Optional[Path] = None,
        run_config: Optional[Dict[str, Any]] = None,
        use_color: bool = True,
        use_emoji: bool = True,
        *,
        markdown_path: Optional[Path] = None,
        summary_path: Optional[Path] = None,
    ) -> None:
        if jsonl_path is None:
            if markdown_path is None:
                raise TypeError("RunReporter requires jsonl_path")
            jsonl_path = markdown_path
        self.jsonl = JsonlTraceWriter(jsonl_path, run_config or {})
        self.markdown = MarkdownTraceWriter(
            markdown_path or (jsonl_path.parent / "trace.md"), run_config or {}
        )
        self.summary_path = summary_path or (jsonl_path.parent / "summary.md")
        self.console = ConsoleTracePrinter(use_color=use_color, use_emoji=use_emoji)

    def on_trace_event(self, event: Dict[str, Any]) -> None:
        self.console.print_event(event)
        self.jsonl.append_event(event)
        self.markdown.append_event(event)

    def finish(self, solution: Any, summary: Dict[str, Any]) -> None:
        self.console.print_final(summary)
        self.jsonl.append_final(solution, summary)
        self.markdown.append_final(solution, summary)
        self.summary_path.write_text(_summary_markdown(summary), encoding="utf-8")
        self.jsonl.close()
        self.markdown.close()

    def fail(self, exc: BaseException) -> None:
        self.console.print_error(exc)
        self.jsonl.append_error(exc)
        self.markdown.append_error(exc)
        self.summary_path.write_text(
            f"# Run Summary\n\nstatus: failed\n\nerror: {type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        self.jsonl.close()
        self.markdown.close()


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


__all__ = [
    "ConsoleTracePrinter",
    "JsonlTraceWriter",
    "MarkdownTraceWriter",
    "RunReporter",
    "event_category",
]
