from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict


def event_category(event_type: str) -> str:
    normalized = event_type.lower()
    if normalized.endswith("_observation"):
        return "observation"
    if normalized.endswith("_prompt"):
        return "prompt"
    if normalized.endswith("_raw_output"):
        return "raw"
    if normalized.endswith("_validated_payload") or normalized.startswith("validated_"):
        return "validated"
    if normalized.startswith("compiled_") or normalized == "runtime_control_manifest":
        return "compiled"
    if normalized.startswith("solver_") or normalized in {"solver_request", "solver_result"}:
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


class MarkdownTraceWriter:
    def __init__(self, path: Path, run_config: Dict[str, Any]) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8", newline="\n")
        self._closed = False
        self._write_header(run_config)

    def _write_header(self, run_config: Dict[str, Any]) -> None:
        self._file.write("# LLM-ALNS Execution Report\n\n")
        self._file.write("> Status: running\n\n")
        self._file.write("## Run Config\n\n")
        self._write_json_block(run_config)
        self._file.write("\n---\n\n## Live Timeline\n\n")
        self.flush()

    def append_event(self, event: Dict[str, Any]) -> None:
        event_type = str(event.get("event_type", ""))
        marker = EMOJI.get(event_category(event_type), "[TRACE]")
        index = int(event.get("index", 0) or 0)
        context = []
        if event.get("contract_id") is not None:
            context.append(str(event["contract_id"]))
        if event.get("step_index") is not None:
            context.append(f"SOLVER {int(event['step_index']):03d}")
        title = f"### #{index:03d} {marker} {event_type.upper()}"
        if context:
            title += f" | {' / '.join(context)}"
        self._file.write(title + "\n\n")

        payload = event.get("payload")
        payload_type = str(event.get("payload_type", "json"))
        if self._default_open(event_type):
            self._write_payload(payload, payload_type)
        else:
            self._file.write("<details>\n")
            self._file.write(f"<summary>{self._summary_text(event_type)}</summary>\n\n")
            self._write_payload(payload, payload_type)
            self._file.write("</details>\n\n")
        self.flush()

    def append_final(self, solution: Any, summary: Dict[str, Any]) -> None:
        self._file.write("\n---\n\n## Final Solution\n\n")
        payload = solution.to_dict() if hasattr(solution, "to_dict") else solution
        self._write_json_block(payload)
        self._file.write("\n## Final Summary\n\n")
        self._write_json_block(summary)
        self._file.write("\n> Status: finished\n")
        self.flush()

    def append_error(self, exc: BaseException) -> None:
        self._file.write("\n---\n\n## Runtime Error\n\n```text\n")
        self._file.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        self._file.write("```\n\n> Status: failed\n")
        self.flush()

    def close(self) -> None:
        if self._closed:
            return
        self.flush()
        self._file.close()
        self._closed = True

    def flush(self) -> None:
        if not self._closed:
            self._file.flush()

    def _write_payload(self, payload: Any, payload_type: str) -> None:
        if payload_type == "text":
            text = str(payload)
            self._file.write("```text\n")
            self._file.write(text)
            if not text.endswith("\n"):
                self._file.write("\n")
            self._file.write("```\n\n")
            return
        self._write_json_block(payload)

    def _write_json_block(self, payload: Any) -> None:
        self._file.write("```json\n")
        self._file.write(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        self._file.write("\n```\n\n")

    def _default_open(self, event_type: str) -> bool:
        normalized = event_type.lower()
        return (
            normalized.endswith("_validated_payload")
            or normalized.startswith("validated_")
            or normalized.startswith("compiled_")
            or normalized in {
                "initial_insertion_result",
                "runtime_control_manifest",
                "execution_trace",
                "solver_request",
                "solver_result",
                "outcome_audit",
                "outcome_verification",
                "contract_completion_check",
                "contract_end",
                "contract_progress",
                "final_result",
            }
        )

    def _summary_text(self, event_type: str) -> str:
        if event_type.endswith("_observation"):
            return "Open LLM observation input"
        if event_type.endswith("_prompt"):
            return "Open generated prompt"
        if event_type.endswith("_raw_output"):
            return "Open raw LLM output"
        if event_type == "public_candidates":
            return "Open public candidates"
        if event_type == "memory_update":
            return "Open memory update"
        return "Open payload"


class ConsoleTracePrinter:
    def __init__(self, use_color: bool = True, use_emoji: bool = True) -> None:
        self.use_color = use_color
        self.use_emoji = use_emoji

    def print_event(self, event: Dict[str, Any]) -> None:
        event_type = str(event.get("event_type", ""))
        category = event_category(event_type)
        marker = EMOJI.get(category, "[TRACE]") if self.use_emoji else ""
        color = COLOR.get(category, "") if self.use_color else ""
        reset = RESET if self.use_color else ""
        label = self._label(event)
        text = f"{marker + ' ' if marker else ''}{label:<28} {self._event_summary(event)}"
        print(self._sanitize(color + text + reset), flush=True)

    def print_final(self, summary: Dict[str, Any]) -> None:
        feasible = bool(summary.get("hard_feasible", False))
        category = "final" if feasible else "error"
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
            if event_type in {"solver_request", "solver_result", "outcome_audit", "contract_completion_check"}:
                return f"{event_type.upper()} {step:03d}"
        if event.get("contract_id") is not None:
            return f"{event_type.upper()} {event['contract_id']}"
        return event_type.upper()

    def _event_summary(self, event: Dict[str, Any]) -> str:
        event_type = str(event.get("event_type", ""))
        payload = event.get("payload")
        if event_type.endswith("_observation"):
            return "observation recorded"
        if event_type.endswith("_prompt"):
            return "prompt recorded"
        if event_type.endswith("_raw_output"):
            return "raw output received"
        if event_type.endswith("_validated_payload"):
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
            if isinstance(payload, dict) and "intent_status" in payload:
                return f"status={payload.get('intent_status')} blocker={payload.get('dominant_blocker')}"
            return f"events={payload.get('events', [])}" if isinstance(payload, dict) else "audit recorded"
        if event_type == "contract_completion_check":
            if isinstance(payload, dict):
                return f"completed={payload.get('completed')} reason={payload.get('reason')}"
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
        cfg = payload.get("run_config", {}) or {}
        return (
            f"instance={cfg.get('instance')} mode={payload.get('llm_mode')} "
            f"step_budget={cfg.get('max_step_calls')} solver_budget={cfg.get('max_solver_calls')}"
        )

    def _validated_summary(self, event_type: str, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "validated"
        if event_type == "solver_validated_payload":
            return f"action={(payload.get('solver_decision') or {}).get('action', 'unknown')}"
        if event_type in {"supervisor_kickoff_validated_payload", "supervisor_review_validated_payload"}:
            return f"action={(payload.get('supervisor_decision') or {}).get('action', 'unknown')}"
        return "validated"

    def _compiled_contract_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "contract compiled"
        policy = payload.get("resource_policy", {}) or {}
        objective = [item.get("metric") for item in payload.get("objective_layers", []) if isinstance(item, dict)]
        return (
            f"type={payload.get('contract_type')} objective={objective} "
            f"actions={policy.get('min_actions')}..{policy.get('max_actions')}"
        )

    def _manifest_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "manifest compiled"
        compiled = payload.get("compiled", {}) or {}
        action = payload.get("action")
        target = payload.get("target_id")
        if action == "run_alns":
            destroy = (compiled.get("destroy", {}) or {}).get("operator_weights", {})
            insertion = (compiled.get("insertion", {}) or {}).get("operator_weights", {})
            return f"action={action} target={target} destroy={self._format_operator_weights(destroy)} insertion={self._format_operator_weights(insertion)}"
        return f"action={action} target={target}"

    def _execution_trace_summary(self, payload: Any) -> str:
        if not isinstance(payload, dict):
            return "execution trace recorded"
        flow = payload.get("trial_flow", {}) or {}
        if flow:
            return f"trials={flow.get('candidate_trials')} accepted={flow.get('accepted_trials')} best={flow.get('best_improved_trials')}"
        return f"kind={payload.get('kind')} inserted={payload.get('inserted_task_count')}"

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
        diagnostics = payload.get("diagnostics", {}) if isinstance(payload, dict) else {}
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
        ordered = sorted(weights.items(), key=lambda item: (-float(item[1]), str(item[0])))
        return "[" + ", ".join(f"{name}:{weight}" for name, weight in ordered) + "]"

    def _format_operator_scores(self, scores: Any) -> str:
        if not isinstance(scores, list) or not scores:
            return "[]"
        return "[" + ", ".join(
            f"{item.get('name')}:{item.get('score')}"
            for item in scores
            if isinstance(item, dict)
        ) + "]"

    def _sanitize(self, text: str) -> str:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


class RunReporter:
    def __init__(
        self,
        markdown_path: Path,
        run_config: Dict[str, Any],
        use_color: bool = True,
        use_emoji: bool = True,
    ) -> None:
        self.markdown = MarkdownTraceWriter(markdown_path, run_config)
        self.console = ConsoleTracePrinter(use_color=use_color, use_emoji=use_emoji)

    def on_trace_event(self, event: Dict[str, Any]) -> None:
        self.console.print_event(event)
        self.markdown.append_event(event)

    def finish(self, solution: Any, summary: Dict[str, Any]) -> None:
        self.console.print_final(summary)
        self.markdown.append_final(solution, summary)
        self.markdown.close()

    def fail(self, exc: BaseException) -> None:
        self.console.print_error(exc)
        self.markdown.append_error(exc)
        self.markdown.close()


__all__ = ["ConsoleTracePrinter", "MarkdownTraceWriter", "RunReporter", "event_category"]
