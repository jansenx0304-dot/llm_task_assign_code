from __future__ import annotations

import argparse
import json
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Tuple

from dotenv import load_dotenv

from sar_alloc.config import Budget, Config
from sar_alloc.llm_client import build_llm_client
from sar_alloc.llm_orchestrator import run_orchestrator
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.tools import solution_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOAL = (
    "Prioritize hard feasibility for assigned tasks, then rescue high-priority "
    "tasks, then reduce resource usage."
) # this goal only for test, in practice, the goal can be more complex, and goal can be different


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m sar_alloc.runner",
        description="Run the LLM-controlled SAR task allocation demo from the command line.",
    )
    parser.add_argument("--instance", default="T100", help="Instance name such as T100, or a JSON file path.")
    parser.add_argument("--time-limit", default=300.0, type=float, help="Total ALNS time budget in seconds.")
    parser.add_argument("--iterations", default=2000, type=int, help="Total ALNS iteration budget.")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducible solver behavior.")
    parser.add_argument("--dummy-llm", action="store_true", help="Use the local demo LLM policy.")
    parser.add_argument("--output-dir", default="runs", help="Directory for saved run artifacts.")
    parser.add_argument(
        "--allow-llm-fallback",
        action="store_true",
        help="Allow explicit demo-policy fallback when LLM output is invalid.",
    )
    parser.add_argument("--save-log", action="store_true", help="Accepted for CLI compatibility; no separate log file is written.")
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Command-line entry point for reproducible runner execution.

    Args:
        argv: Optional argument list for tests. When omitted, `sys.argv` is used.

    Raises:
        ValueError/FileNotFoundError: For invalid CLI values or missing instance
            files.
        LLMClientError/LLMOutputError/OrchestratorError: For LLM configuration,
            response, or action-sequence failures.
    """
    args = build_arg_parser().parse_args(argv)
    _validate_runner_args(args)
    load_dotenv(PROJECT_ROOT / ".env", override=False)

    instance_path = resolve_instance_path(args.instance)
    instance = load_instance_from_json(instance_path)

    run_dir = prepare_run_dir(args.output_dir, args.instance)
    run_config = {
        "instance": args.instance,
        "instance_path": str(instance_path),
        "time_limit_sec": float(args.time_limit),
        "max_iters": int(args.iterations),
        "seed": int(args.seed),
        "dummy_llm": bool(args.dummy_llm),
        "allow_llm_fallback": bool(args.allow_llm_fallback),
        "save_log": bool(args.save_log),
        "output_dir": str(args.output_dir),
    }

    case_file = "case.json"
    write_json(run_dir / case_file, build_case_payload(args.instance, instance))

    mode = "dummy" if args.dummy_llm else "real"
    print(
        f"[RUN] instance={args.instance} mode={mode} "
        f"time_limit={float(args.time_limit)} iters={int(args.iterations)} "
        f"seed={int(args.seed)}"
    )

    client = build_llm_client(dummy=bool(args.dummy_llm))
    cfg = Config(rng_seed=int(args.seed))
    budget = Budget(time_limit_sec=float(args.time_limit), max_iters=int(args.iterations))

    started_at = time.time()
    solution = run_orchestrator(
        client=client,
        instance=instance,
        user_goal_text=DEFAULT_GOAL,
        config=cfg,
        budget=budget,
        rng_seed=int(args.seed),
        max_agent_steps=3,
        max_solver_calls=2,
        max_stagnation_steps=3,
        allow_llm_fallback=bool(args.allow_llm_fallback),
        artifact_dir=run_dir,
    )
    elapsed = time.time() - started_at

    summary = build_summary(
        solution=solution,
        instance=instance,
        config=cfg,
        instance_name=args.instance,
        llm_mode=mode,
        allow_llm_fallback=bool(args.allow_llm_fallback),
        elapsed_sec=elapsed,
        time_limit_sec=float(args.time_limit),
        iteration_limit=int(args.iterations),
    )

    print_summary(summary)
    write_json(
        run_dir / "result.json",
        build_result_payload(
            case_file=case_file,
            run_config=run_config,
            solution=solution,
            summary=summary,
        ),
    )
    print(f"[ARTIFACTS] {_display_path(run_dir)}")


def _validate_runner_args(args: argparse.Namespace) -> None:
    if float(args.time_limit) <= 0:
        raise ValueError("--time-limit must be positive.")
    if int(args.iterations) <= 0:
        raise ValueError("--iterations must be positive.")


def resolve_instance_path(instance: str) -> Path:
    value = str(instance).strip()
    if not value:
        raise ValueError("--instance must be non-empty.")

    direct = Path(value)
    if direct.exists():
        return direct

    demo_map = {
        "T50": PROJECT_ROOT / "sar_alloc" / "data" / "instances" / "demo" / "seed42_T50_A6.json",
        "T100": PROJECT_ROOT / "sar_alloc" / "data" / "instances" / "demo" / "seed42_T100_A6.json",
        "T300": PROJECT_ROOT / "sar_alloc" / "data" / "instances" / "demo" / "seed42_T300_A6.json",
    }
    if value in demo_map and demo_map[value].exists():
        return demo_map[value]
    raise FileNotFoundError(f"Unknown instance '{instance}'. Use T50, T100, T300, or a JSON path.")


def _require_key(mapping: Mapping[str, Any], key: str, context: str) -> Any:
    if key not in mapping:
        prefix = f"{context}." if context else ""
        raise ValueError(f"missing required field: {prefix}{key}")
    return mapping[key]


def _require_mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"invalid field: {context} (expected object)")
    return value


def _require_list(value: Any, context: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(f"invalid field: {context} (expected list)")
    return value


def _as_loc(obj: Mapping[str, Any], context: str) -> Tuple[float, float]:
    if "loc" in obj:
        loc = obj["loc"]
        if isinstance(loc, (list, tuple)) and len(loc) >= 2:
            return (float(loc[0]), float(loc[1]))
        if isinstance(loc, dict) and "x" in loc and "y" in loc:
            return (float(loc["x"]), float(loc["y"]))
        raise ValueError(f"invalid field: {context}.loc (expected [x, y] or {{x, y}})")
    if "x" in obj and "y" in obj:
        return (float(obj["x"]), float(obj["y"]))
    raise ValueError(f"missing required field: {context}.loc (x, y)")


def load_instance_from_json(path: Path) -> Instance:
    """Load a task-allocation instance from the project JSON schema."""
    if not path.exists():
        raise FileNotFoundError(f"Instance JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("instance JSON must be an object")

    depot_d = _require_mapping(_require_key(data, "depot", ""), "depot")
    agents_raw = _require_list(_require_key(data, "agents", ""), "agents")
    tasks_raw = _require_list(_require_key(data, "tasks", ""), "tasks")
    default_speed = float(_require_key(data, "default_speed", ""))

    depot = Depot(id=int(_require_key(depot_d, "id", "depot")), loc=_as_loc(depot_d, "depot"))

    agents: List[Agent] = []
    for idx, item in enumerate(agents_raw):
        context = f"agents[{idx}]"
        item = _require_mapping(item, context)
        skills = _require_list(_require_key(item, "skills", context), f"{context}.skills")
        skill_energy_rate = _require_mapping(
            _require_key(item, "skill_energy_rate", context), f"{context}.skill_energy_rate"
        )
        agents.append(
            Agent(
                id=int(_require_key(item, "id", context)),
                init_energy=float(_require_key(item, "init_energy", context)),
                skills=set(skills),
                speed=float(_require_key(item, "speed", context)),
                travel_energy_rate=float(_require_key(item, "travel_energy_rate", context)),
                standby_power=float(_require_key(item, "standby_power", context)),
                skill_energy_rate=dict(skill_energy_rate),
            )
        )

    tasks: List[Task] = []
    for idx, item in enumerate(tasks_raw):
        context = f"tasks[{idx}]"
        item = _require_mapping(item, context)
        skill_req = _require_list(_require_key(item, "skill_req", context), f"{context}.skill_req")
        tasks.append(
            Task(
                id=int(_require_key(item, "id", context)),
                loc=_as_loc(item, context),
                tw_start=float(_require_key(item, "tw_start", context)),
                tw_end=float(_require_key(item, "tw_end", context)),
                service_time=float(_require_key(item, "service_time", context)),
                skill_req=set(skill_req),
                priority=float(_require_key(item, "priority", context)),
            )
        )

    return Instance(
        tasks=tuple(tasks),
        agents=tuple(agents),
        depot=depot,
        default_speed=default_speed,
    )


def build_summary(
    *,
    solution: Any,
    instance: Instance,
    config: Config,
    instance_name: str,
    llm_mode: str,
    allow_llm_fallback: bool,
    elapsed_sec: float,
    time_limit_sec: float,
    iteration_limit: int,
) -> Dict[str, Any]:
    sol_summary = solution_summary(solution=solution, instance=instance, config=config)
    metrics = dict(sol_summary.get("metrics", {}) or {})
    run_summary = dict(getattr(solution, "run_summary", {}) or {})
    return {
        "instance": instance_name,
        "llm_mode": llm_mode,
        "allow_llm_fallback": bool(allow_llm_fallback),
        "llm_fallback_used": bool(run_summary.get("llm_fallback_used", False)),
        "objective_tiers": list(run_summary.get("objective_tiers", [])),
        "alns_time_limit": float(time_limit_sec),
        "alns_iteration_limit": int(iteration_limit),
        "hard_feasible": bool(sol_summary.get("is_feasible", False)),
        "violation_total": float(metrics.get("violation_total", 0.0)),
        "missed_priority": float(metrics.get("missed_priority", 0.0)),
        "unassigned_count": int(round(float(metrics.get("unassigned_count", 0.0)))),
        "energy_total": float(metrics.get("energy_total", 0.0)),
        "distance_total": float(metrics.get("total_distance", 0.0)),
        "makespan": float(metrics.get("makespan", 0.0)),
        "elapsed_sec": round(float(elapsed_sec), 4),
        "run_summary": run_summary,
    }


def build_case_payload(case_name: str, instance: Instance) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "case_name": str(case_name),
        "instance": _instance_to_jsonable(instance),
    }


def build_result_payload(
    *,
    case_file: str,
    run_config: Dict[str, Any],
    solution: Any,
    summary: Dict[str, Any],
) -> Dict[str, Any]:
    artifact = dict(getattr(solution, "run_artifact", {}) or {})
    initial_evaluation = _initial_evaluation_from_steps(artifact.get("llm_steps", []))
    final_solution = _solution_to_jsonable(solution)
    return {
        "schema_version": 1,
        "case_file": str(case_file),
        "run_config": dict(run_config),
        "initial_solution": {"summary": initial_evaluation} if initial_evaluation else {},
        "initial_evaluation": initial_evaluation or {},
        "objective": dict(artifact.get("objective", {}) or {}),
        "llm_steps": list(artifact.get("llm_steps", []) or []),
        "iteration_trace": list(artifact.get("iteration_trace", []) or []),
        "final_solution": final_solution,
        "final_evaluation": dict(summary),
        "operator_statistics": dict(artifact.get("operator_statistics", {}) or {}),
        "diagnostics": dict(artifact.get("diagnostics", {}) or {}),
    }


def print_summary(summary: Dict[str, Any]) -> None:
    print(
        f"[DONE] feasible={_bool_text(summary.get('hard_feasible'))} "
        f"unassigned={summary.get('unassigned_count')} "
        f"missed_priority={summary.get('missed_priority')} "
        f"energy={summary.get('energy_total')} "
        f"elapsed={summary.get('elapsed_sec')}"
    )


def _bool_text(value: Any) -> str:
    return str(bool(value)).lower()


def _display_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _initial_evaluation_from_steps(steps: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(steps, list):
        return None
    for step in steps:
        if not isinstance(step, dict) or step.get("action_type") != "build_initial_solution":
            continue
        result = dict(step.get("solver_result_summary", {}) or {})
        summary = result.get("candidate_summary")
        return dict(summary) if isinstance(summary, dict) else None
    return None


def _instance_to_jsonable(instance: Instance) -> Dict[str, Any]:
    return {
        "depot": {
            "id": int(instance.depot.id),
            "x": float(instance.depot.loc[0]),
            "y": float(instance.depot.loc[1]),
        },
        "agents": [
            {
                "id": int(agent.id),
                "init_energy": float(agent.init_energy),
                "skills": sorted(str(skill) for skill in agent.skills),
                "speed": float(agent.speed),
                "travel_energy_rate": float(agent.travel_energy_rate),
                "standby_power": float(agent.standby_power),
                "skill_energy_rate": {str(key): float(value) for key, value in agent.skill_energy_rate.items()},
            }
            for agent in instance.agents
        ],
        "tasks": [
            {
                "id": int(task.id),
                "x": float(task.loc[0]),
                "y": float(task.loc[1]),
                "tw_start": float(task.tw_start),
                "tw_end": float(task.tw_end),
                "service_time": float(task.service_time),
                "skill_req": sorted(str(skill) for skill in task.skill_req),
                "priority": float(task.priority),
            }
            for task in instance.tasks
        ],
        "default_speed": float(instance.default_speed),
    }


def prepare_run_dir(output_dir: str, instance_name: str) -> Path:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_instance = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in instance_name)
    out = Path(output_dir) / f"{timestamp}_{safe_instance}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def _solution_to_jsonable(solution: Any) -> Any:
    if hasattr(solution, "to_dict"):
        return solution.to_dict()
    return _jsonable(solution)


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


class _TeeTextStream:
    def __init__(self, primary: Any, mirror: Any) -> None:
        self._primary = primary
        self._mirror = mirror

    @property
    def encoding(self) -> str:
        return getattr(self._primary, "encoding", None) or "utf-8"

    def write(self, data: str) -> int:
        written = self._primary.write(data)
        self._mirror.write(data)
        return written

    def flush(self) -> None:
        self._primary.flush()
        self._mirror.flush()

    def isatty(self) -> bool:
        return bool(getattr(self._primary, "isatty", lambda: False)())

    def __getattr__(self, name: str) -> Any:
        return getattr(self._primary, name)


@contextmanager
def tee_console_to_file(log_path: Path) -> Iterator[None]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    with log_path.open("w", encoding="utf-8") as handle:
        sys.stdout = _TeeTextStream(original_stdout, handle)
        sys.stderr = _TeeTextStream(original_stderr, handle)
        try:
            yield
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = original_stdout
            sys.stderr = original_stderr


@contextmanager
def nullcontext() -> Iterator[None]:
    yield


if __name__ == "__main__":
    main()
