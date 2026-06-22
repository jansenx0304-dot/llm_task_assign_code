from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

from dotenv import load_dotenv

from .config import Budget, Config
from .llm_client import build_llm_client
from .llm_orchestrator import run_orchestrator
from .models import Agent, Depot, Instance, Task
from .reporting import RunReporter
from .tools import solution_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOAL = "Prioritize valuable task coverage, then reduce resource use."


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m sar_alloc.runner")
    parser.add_argument("--instance", default="T100")
    parser.add_argument("--time-limit", default=300.0, type=float)
    parser.add_argument("--iterations", default=2000, type=int)
    parser.add_argument("--max-step-calls", default=10, type=int)
    parser.add_argument("--max-solver-calls", default=20, type=int)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--dummy-llm", action="store_true")
    parser.add_argument("--allow-llm-fallback", action="store_true")
    parser.add_argument("--output-dir", default="runs")
    parser.add_argument("--save-log", action="store_true", help="Accepted for CLI compatibility.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in terminal trace.")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji in terminal trace.")
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    args = build_arg_parser().parse_args(argv)
    _validate_args(args)
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    instance_path = resolve_instance_path(args.instance)
    instance = load_instance_from_json(instance_path)
    run_dir = prepare_run_dir(args.output_dir, args.instance)
    case_file = "case.json"
    write_json(run_dir / case_file, build_case_payload(args.instance, instance))
    run_config = {
        "instance": args.instance,
        "instance_path": str(instance_path),
        "time_limit_sec": args.time_limit,
        "max_iters": args.iterations,
        "max_step_calls": args.max_step_calls,
        "max_solver_calls": args.max_solver_calls,
        "seed": args.seed,
        "dummy_llm": args.dummy_llm,
        "allow_llm_fallback": args.allow_llm_fallback,
    }
    mode = "dummy" if args.dummy_llm else "api"
    reporter = RunReporter(
        markdown_path=run_dir / "result.md",
        run_config=run_config,
        use_color=not args.no_color,
        use_emoji=not args.no_emoji,
    )
    started_at = time.time()
    try:
        client = build_llm_client(dummy=args.dummy_llm)
        config = Config(rng_seed=args.seed)
        solution = run_orchestrator(
            client=client,
            instance=instance,
            user_goal_text=DEFAULT_GOAL,
            config=config,
            budget=Budget(time_limit_sec=args.time_limit, max_iters=args.iterations),
            rng_seed=args.seed,
            max_agent_steps=args.max_step_calls,
            max_solver_calls=args.max_solver_calls,
            allow_llm_fallback=args.allow_llm_fallback,
            llm_mode=mode,
            run_config=run_config,
            case_file=case_file,
            trace_callback=reporter.on_trace_event,
        )
        elapsed = time.time() - started_at
        summary = build_summary(solution, instance, config, args.instance, mode, elapsed)
        reporter.finish(solution, summary)
    except Exception as exc:
        try:
            reporter.fail(exc)
        except Exception:
            pass
        raise
    print(f"[ARTIFACTS] {str(run_dir).replace(chr(92), '/')}")


def build_result_text(solution: Any, summary: Dict[str, Any]) -> str:
    artifact = dict(getattr(solution, "run_artifact", {}) or {})
    events = list(artifact.get("trace_events", []) or [])
    lines = ["# LLM-ALNS Execution Trace", ""]
    for event in events:
        event_type = str(event.get("event_type", ""))
        label = event_type.replace("_", " ").upper()
        context = []
        if event.get("contract_id") is not None:
            context.append(str(event["contract_id"]))
        if event.get("step_index") is not None:
            context.append(f"STEP {int(event['step_index']):03d}")
        suffix = " / ".join(context)
        lines.append(f"## [{label}]" + (f" {suffix}" if suffix else ""))
        payload = event.get("payload")
        if event.get("payload_type") == "text":
            lines.extend(["```text", str(payload), "```", ""])
        else:
            lines.extend(["```json", json.dumps(payload, ensure_ascii=False, indent=2), "```", ""])
    lines.extend([
        "## [FINAL SOLUTION]",
        "```json",
        json.dumps(_solution_json(solution), ensure_ascii=False, indent=2),
        "```",
        "",
        "## [FINAL SUMMARY]",
        "```json",
        json.dumps(summary, ensure_ascii=False, indent=2),
        "```",
        "",
    ])
    return "\n".join(lines)


def build_summary(
    solution: Any,
    instance: Instance,
    config: Config,
    instance_name: str,
    mode: str,
    elapsed: float,
) -> Dict[str, Any]:
    raw = solution_summary(solution, instance, config)
    quality = raw["quality_summary"]
    feasibility = raw["feasibility_summary"]
    return {
        "instance": instance_name,
        "llm_mode": mode,
        "hard_feasible": bool(feasibility["is_feasible"]),
        "violation_total": float(feasibility["violation_total"]),
        "missed_priority": float(quality["missed_priority"]),
        "unassigned_count": int(quality["unassigned_count"]),
        "energy_total": float(quality["energy_total"]),
        "total_distance": float(quality["total_distance"]),
        "makespan": float(quality["makespan"]),
        "quality_summary": quality,
        "feasibility_summary": feasibility,
        "run_summary": dict(getattr(solution, "run_summary", {}) or {}),
        "elapsed_sec": round(elapsed, 4),
    }


def resolve_instance_path(instance: str) -> Path:
    direct = Path(instance)
    if direct.exists():
        return direct
    demo = PROJECT_ROOT / "sar_alloc" / "data" / "instances" / "demo" / f"seed42_{instance}_A6.json"
    if instance in {"T50", "T100", "T300"} and demo.exists():
        return demo
    raise FileNotFoundError(f"Unknown instance: {instance}")


def load_instance_from_json(path: Path) -> Instance:
    data = json.loads(path.read_text(encoding="utf-8"))
    depot_raw = _mapping(_required(data, "depot"), "depot")
    depot = Depot(id=int(_required(depot_raw, "id")), loc=_location(depot_raw, "depot"))
    agents = []
    for index, value in enumerate(_list(_required(data, "agents"), "agents")):
        raw = _mapping(value, f"agents[{index}]")
        agents.append(Agent(
            id=int(_required(raw, "id")),
            init_energy=float(_required(raw, "init_energy")),
            skills=set(_list(_required(raw, "skills"), "skills")),
            speed=float(_required(raw, "speed")),
            travel_energy_rate=float(_required(raw, "travel_energy_rate")),
            standby_power=float(_required(raw, "standby_power")),
            skill_energy_rate=dict(_mapping(_required(raw, "skill_energy_rate"), "skill_energy_rate")),
        ))
    tasks = []
    for index, value in enumerate(_list(_required(data, "tasks"), "tasks")):
        raw = _mapping(value, f"tasks[{index}]")
        tasks.append(Task(
            id=int(_required(raw, "id")),
            loc=_location(raw, f"tasks[{index}]"),
            tw_start=float(_required(raw, "tw_start")),
            tw_end=float(_required(raw, "tw_end")),
            service_time=float(_required(raw, "service_time")),
            skill_req=set(_list(_required(raw, "skill_req"), "skill_req")),
            priority=float(_required(raw, "priority")),
        ))
    return Instance(
        tasks=tuple(tasks),
        agents=tuple(agents),
        depot=depot,
        default_speed=float(_required(data, "default_speed")),
    )


def build_case_payload(name: str, instance: Instance) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "case_name": name,
        "instance": {
            "depot": {"id": instance.depot.id, "loc": list(instance.depot.loc)},
            "agents": [
                {
                    "id": agent.id,
                    "init_energy": agent.init_energy,
                    "skills": sorted(agent.skills),
                    "speed": agent.speed,
                    "travel_energy_rate": agent.travel_energy_rate,
                    "standby_power": agent.standby_power,
                    "skill_energy_rate": agent.skill_energy_rate,
                }
                for agent in instance.agents
            ],
            "tasks": [
                {
                    "id": task.id,
                    "loc": list(task.loc),
                    "tw_start": task.tw_start,
                    "tw_end": task.tw_end,
                    "service_time": task.service_time,
                    "skill_req": sorted(task.skill_req),
                    "priority": task.priority,
                }
                for task in instance.tasks
            ],
            "default_speed": instance.default_speed,
        },
    }


def prepare_run_dir(output_dir: str, instance_name: str) -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{Path(instance_name).stem}"
    try:
        run_dir.mkdir(parents=False, exist_ok=False)
    except PermissionError:
        if output_dir != "runs":
            raise
        root = Path("runs_generated")
        root.mkdir(parents=True, exist_ok=True)
        run_dir = root / f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{Path(instance_name).stem}"
        run_dir.mkdir(parents=False, exist_ok=False)
    return run_dir


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.write_text(payload, encoding="utf-8")


def _solution_json(solution: Any) -> Any:
    return solution.to_dict() if hasattr(solution, "to_dict") else solution


def _validate_args(args: argparse.Namespace) -> None:
    for name in ("time_limit", "iterations", "max_step_calls", "max_solver_calls"):
        if float(getattr(args, name)) <= 0:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")


def _required(mapping: Mapping[str, Any], key: str) -> Any:
    if key not in mapping:
        raise ValueError(f"missing required field: {key}")
    return mapping[key]


def _mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{context} must be an object")
    return value


def _list(value: Any, context: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{context} must be a list")
    return value


def _location(raw: Mapping[str, Any], context: str) -> Tuple[float, float]:
    if "loc" in raw and isinstance(raw["loc"], (list, tuple)) and len(raw["loc"]) >= 2:
        return float(raw["loc"][0]), float(raw["loc"][1])
    if "x" in raw and "y" in raw:
        return float(raw["x"]), float(raw["y"])
    raise ValueError(f"{context} has no valid location")


if __name__ == "__main__":
    main()
