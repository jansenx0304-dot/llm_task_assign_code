from __future__ import annotations

import json
import os
import random
import tempfile
from dataclasses import replace
from pathlib import Path

from . import runner as runner_module
from .config import Budget, Config
from .demo_policy import demo_objective_plan, demo_run_alns_action
from .llm_client import DummyLLMClient, build_llm_client
from .llm_orchestrator import LLMOutputError, parse_action_plan
from .operators import (
    DESTROY_CANDIDATE_GENERATORS,
    LANDSCAPE_METRIC_FIELDS,
    REPAIR_POSITION_METRIC_FIELDS,
    REPAIR_TASK_SELECTORS,
    SEARCH_DIAGNOSIS_FIELDS,
    InsertPosition,
    MetricPreference,
    PositionMetricPreferences,
)
from .operators.destroy import DESTROY_OPERATORS, compute_destroy_strength
from .operators import repair as repair_module
from .schemas import SCHEMA_CONSTRAINTS
from .solution import AssignmentSolution
from .tools import apply_objective
from .tools.assign_solvers import select_destroy_move, solve_assignment
from .tools.init_solutions import build_initial_solution


def main() -> None:
    parser = runner_module.build_arg_parser()
    args = parser.parse_args(
        [
            "--instance",
            "T100",
            "--time-limit",
            "0.05",
            "--iterations",
            "2",
            "--dummy-llm",
        ]
    )
    assert args.instance == "T100"
    assert args.dummy_llm is True

    client = build_llm_client(dummy=True)
    assert isinstance(client, DummyLLMClient)

    saved_env = {name: os.environ.pop(name, None) for name in ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")}
    try:
        try:
            build_llm_client(dummy=False)
        except ValueError as exc:
            assert "LLM_" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("real LLM config missing should raise ValueError")
    finally:
        for name, value in saved_env.items():
            if value is not None:
                os.environ[name] = value

    try:
        parse_action_plan('{"rationale": "missing fields"}', ["build_initial_solution"])
    except LLMOutputError:
        pass
    else:  # pragma: no cover
        raise AssertionError("missing action fields should raise LLMOutputError")

    _test_policy_schema_and_validation()
    _test_destroy_move_shapes()
    _test_repair_position_scoring_before_strict()
    _test_solver_diagnostics()

    _test_runner_two_file_artifacts()
    print("smoke_test_ok")


def _test_policy_schema_and_validation() -> None:
    expected_destroy = (
        "random_removal",
        "worst_task_removal",
        "related_cluster_removal",
        "critical_block_removal",
        "route_rebalance_removal",
    )
    assert DESTROY_CANDIDATE_GENERATORS == expected_destroy
    assert tuple(DESTROY_OPERATORS.keys()) == expected_destroy
    assert SCHEMA_CONSTRAINTS["next_action"]["search_diagnosis_scores"] == list(SEARCH_DIAGNOSIS_FIELDS)
    assert SCHEMA_CONSTRAINTS["next_action"]["destroy_operator_scores"] == list(expected_destroy)
    assert SCHEMA_CONSTRAINTS["next_action"]["repair_operator_scores"] == list(REPAIR_TASK_SELECTORS)
    assert SCHEMA_CONSTRAINTS["next_action"]["landscape_metric_fields"] == list(LANDSCAPE_METRIC_FIELDS)
    assert SCHEMA_CONSTRAINTS["next_action"]["repair_position_metric_fields"] == list(REPAIR_POSITION_METRIC_FIELDS)

    compiled = parse_action_plan(_json(demo_run_alns_action(time_limit_sec=0.01, max_iters=1)), ["run_alns"])
    assert compiled["_compiled_policy"].candidate_budget_score == 7

    for old_field in (
        "remove_" + "metric_weights",
        "repair_" + "profile",
        "destroy_" + "generator_priors",
        "repair_task_" + "selector_priors",
        "strength_" + "ratio",
    ):
        action = demo_run_alns_action(time_limit_sec=0.01, max_iters=1)
        action["action_payload"][old_field] = {}
        _assert_invalid_action(action, f"old field should be rejected: {old_field}")

    action = demo_run_alns_action(time_limit_sec=0.01, max_iters=1)
    action["action_payload"]["destroy_metric_preferences"]["cost_pressure"]["direction"] = "high"
    _assert_invalid_action(action, "illegal direction should be rejected")

    action = demo_run_alns_action(time_limit_sec=0.01, max_iters=1)
    action["action_payload"]["destroy_operator_scores"]["random_removal"] = 2.5
    _assert_invalid_action(action, "float operator score should be rejected")

    action = demo_run_alns_action(time_limit_sec=0.01, max_iters=1)
    del action["action_payload"]["repair_task_metric_preferences"]["cost_pressure"]
    _assert_invalid_action(action, "missing metric should be rejected")

    action = demo_run_alns_action(time_limit_sec=0.01, max_iters=1)
    action["action_payload"]["repair_position_metric_preferences"]["extra_metric"] = {"score": 1, "direction": "neutral"}
    _assert_invalid_action(action, "extra metric should be rejected")


def _test_destroy_move_shapes() -> None:
    instance = runner_module.load_instance_from_json(runner_module.resolve_instance_path("T50"))
    cfg = _configured(rng_seed=0)
    sol = build_initial_solution(instance, cfg, rng_seed=0)
    policy = parse_action_plan(_json(demo_run_alns_action(time_limit_sec=0.01, max_iters=1)), ["run_alns"])["_compiled_policy"]
    assigned_count = len(sol.all_assigned_tasks())
    assert assigned_count > 0

    for name in ("random_removal", "worst_task_removal", "related_cluster_removal"):
        move = select_destroy_move(sol, instance, cfg, policy, DESTROY_OPERATORS[name], random.Random(1))
        strength = compute_destroy_strength(sol, policy.strength_ratio)
        assert len(move.task_ids) == min(assigned_count, strength.target_k)
        assert move.operator_name == name

    block_move = select_destroy_move(sol, instance, cfg, policy, DESTROY_OPERATORS["critical_block_removal"], random.Random(2))
    assert block_move.shape == "block"
    meta = block_move.metadata
    route = list(sol.routes[int(meta["route_id"])])
    assert block_move.task_ids == tuple(route[int(meta["start"]): int(meta["end_exclusive"])])
    assert int(meta["length"]) == int(meta["end_exclusive"]) - int(meta["start"])

    route_move = select_destroy_move(sol, instance, cfg, policy, DESTROY_OPERATORS["route_rebalance_removal"], random.Random(3))
    assert route_move.shape in {"route", "random"}


def _test_solver_diagnostics() -> None:
    instance = runner_module.load_instance_from_json(runner_module.resolve_instance_path("T50"))
    cfg = _configured(rng_seed=1)
    sol = build_initial_solution(instance, cfg, rng_seed=1)
    policy = parse_action_plan(_json(demo_run_alns_action(time_limit_sec=0.01, max_iters=1)), ["run_alns"])["_compiled_policy"]
    solved = solve_assignment(
        instance=instance,
        init_solution=sol,
        config=cfg,
        budget=Budget(time_limit_sec=0.01, max_iters=1),
        policy=policy,
        rng_seed=1,
    )
    diagnostics = dict(solved.solver_diagnostics or {})
    assert diagnostics.get("last_destroy_move")
    assert diagnostics.get("last_repair")
    assert "destroy_operator_summary" in diagnostics
    assert "repair_operator_summary" in diagnostics
    assert "destroy_operators" in diagnostics.get("operator_weights", {})
    assert "repair_operators" in diagnostics.get("operator_weights", {})


def _test_repair_position_scoring_before_strict() -> None:
    instance = runner_module.load_instance_from_json(runner_module.resolve_instance_path("T50"))
    cfg = _configured(rng_seed=2)
    tid = int(instance.all_task_ids()[0])
    sol = AssignmentSolution.empty_from_instance(instance)
    sol.unassigned = {tid}
    policy = parse_action_plan(_json(demo_run_alns_action(time_limit_sec=0.01, max_iters=1)), ["run_alns"])["_compiled_policy"]
    policy = replace(
        policy,
        repair_position_metric_preferences=PositionMetricPreferences(
            insert_cost=MetricPreference(0, "neutral"),
            future_slack=MetricPreference(10, "prefer_high"),
            route_balance_gain=MetricPreference(0, "neutral"),
            local_coupling_penalty=MetricPreference(0, "neutral"),
            diversity_gain=MetricPreference(0, "neutral"),
        ),
    )
    positions = [InsertPosition(agent_id=0, position=0), InsertPosition(agent_id=1, position=0)]
    checked = []

    original_enum = repair_module.enumerate_hard_filtered_positions
    original_build = repair_module._build_lightweight_repair_candidate
    original_strict = repair_module._strict_evaluate_repair_candidate

    def fake_enum(sol_arg, tid_arg, instance_arg, config_arg):
        del sol_arg, tid_arg, instance_arg, config_arg
        return list(positions)

    def fake_build(sol, tid, position, instance, config, route_pressure_before):
        del sol, instance, config, route_pressure_before
        slack = 1.0 if int(position.agent_id) == 0 else 100.0
        return repair_module.RepairCandidate(
            tid=int(tid),
            agent_id=int(position.agent_id),
            position=int(position.position),
            delta_distance=1.0,
            delta_energy=1.0,
            route_duration_after=1.0,
            suffix_min_slack=slack,
            suffix_tardiness_total=0.0,
            suffix_ratio=0.0,
            energy_remaining_ratio=0.0,
            depot_return_pressure=0.0,
            route_pressure_after=0.0,
            balance_improvement=0.0,
            candidate_cost=1.0,
            dominated=False,
            strict_feasible=False,
        )

    def fake_strict(candidate, sol, instance, config):
        del sol, instance, config
        checked.append((int(candidate.agent_id), int(candidate.position), float(candidate.position_score)))
        return replace(candidate, strict_feasible=True)

    try:
        repair_module.enumerate_hard_filtered_positions = fake_enum
        repair_module._build_lightweight_repair_candidate = fake_build
        repair_module._strict_evaluate_repair_candidate = fake_strict
        stats, _, diag = repair_module.collect_task_repair_stats(
            sol=sol,
            tid=tid,
            instance=instance,
            config=cfg,
            policy=policy,
            budget=repair_module.RepairBudget(max_tasks_considered=1, max_positions_per_task=1, strict_check_limit=10),
            strict_checks_left=10,
            route_pressure_before={int(aid): 0.0 for aid in instance.all_agent_ids()},
            recent_task_failures=None,
        )
    finally:
        repair_module.enumerate_hard_filtered_positions = original_enum
        repair_module._build_lightweight_repair_candidate = original_build
        repair_module._strict_evaluate_repair_candidate = original_strict

    assert checked and checked[0][0] == 1
    assert checked[0][2] > 0.0
    assert stats.feasible_count == 1
    assert diag["positions_generated"] == 2
    assert diag["positions_strict_checked"] == 1


def _test_runner_two_file_artifacts() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runner_module.main(
            [
                "--instance",
                "T100",
                "--time-limit",
                "0.05",
                "--iterations",
                "2",
                "--seed",
                "0",
                "--dummy-llm",
                "--output-dir",
                tmp,
            ]
        )
        run_dirs = [path for path in Path(tmp).iterdir() if path.is_dir()]
        assert len(run_dirs) == 1
        files = {path.name for path in run_dirs[0].iterdir() if path.is_file()}
        assert files == {"case.json", "result.json"}
        result = json.loads((run_dirs[0] / "result.json").read_text(encoding="utf-8"))
        assert result["case_file"] == "case.json"
        for step in result.get("llm_steps", []):
            strict_action_plan = step["strict_action_plan"]
            parse_action_plan(json.dumps(strict_action_plan), ["build_initial_solution", "run_alns", "stop"])
            compiled_policy = dict(step.get("compiled_policy", {}) or {})
            if compiled_policy:
                _assert_invalid_action(compiled_policy, "compiled policy should not parse as strict action plan")


def _assert_invalid_action(action: object, message: str) -> None:
    try:
        parse_action_plan(_json(action), ["run_alns"])
    except LLMOutputError:
        return
    raise AssertionError(message)


def _json(value: object) -> str:
    import json

    return json.dumps(value)


def _configured(rng_seed: int) -> Config:
    cfg = Config(rng_seed=int(rng_seed))
    result = apply_objective(cfg, demo_objective_plan())
    assert result.get("ok") is True
    return cfg


if __name__ == "__main__":
    main()
