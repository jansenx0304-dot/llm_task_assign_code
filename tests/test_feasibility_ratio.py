from __future__ import annotations

import json
import unittest

from sar_alloc.config import Budget, Config, ObjectiveLayer
from sar_alloc.constraint_checker import ConstraintReport, check_constraints
from sar_alloc.demo_policy import (
    demo_solver_decision,
    demo_supervisor_kickoff,
    demo_supervisor_review,
)
from sar_alloc.feasibility_policy import check_feasibility_admissibility
from sar_alloc.feasibility_policy_compiler import compile_feasibility_control
from sar_alloc.llm_orchestrator import run_orchestrator
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.policy_validator import validate_feasibility_control
from sar_alloc.runner import build_result_text
from sar_alloc.solution import AssignmentSolution


def _instance(task: Task, agent: Agent) -> Instance:
    return Instance(tasks=(task,), agents=(agent,), depot=Depot(id=0, loc=(0.0, 0.0)), default_speed=1.0)


def _report(
    *,
    capability: float = 0.0,
    time_window: float = 0.0,
    energy: float = 0.0,
    time_ratio: float = 0.0,
    energy_ratio: float = 0.0,
    time_individual: float = 0.0,
    energy_individual: float = 0.0,
) -> ConstraintReport:
    by_type = {}
    if capability:
        by_type["capability"] = capability
    if time_window:
        by_type["time_window"] = time_window
    if energy:
        by_type["energy"] = energy
    total = capability + time_window + energy
    return ConstraintReport(
        is_feasible=total == 0.0,
        violation_total=total,
        violation_capability=capability,
        violation_time_window=time_window,
        violation_energy=energy,
        recoverable_violation_total=time_window + energy,
        unrecoverable_violation_total=capability,
        violation_by_type=by_type,
        violation_ratio_by_type={"time_window": time_ratio, "energy": energy_ratio},
        violation_details_by_type={
            "time_window": [{"ratio": time_individual}],
            "energy": [{"ratio": energy_individual}],
        },
    )


class FeasibilityControlValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        task = Task(1, (1.0, 0.0), 0.0, 10.0, 1.0, {"a"}, 1.0)
        agent = Agent(0, 100.0, {"a"}, 1.0, 1.0, 0.0, {"a": 1.0})
        self.candidates = build_public_candidates(_instance(task, agent), Config())

    def test_modes_and_valid_relaxations(self) -> None:
        for mode in ("strict", "recovery_only"):
            validate_feasibility_control(
                {"mode": mode, "relaxation_ratios": []}, self.candidates
            )
        validate_feasibility_control(
            {
                "mode": "relaxed_recoverable",
                "relaxation_ratios": [
                    {"type": "time_window", "limit_ratio": 0.30, "reason": "Tight windows."},
                    {"type": "energy", "limit_ratio": 0.20, "reason": "Energy pressure."},
                ],
            },
            self.candidates,
        )

    def test_invalid_relaxations(self) -> None:
        invalid = [
            {"mode": "strict", "relaxation_ratios": [{"type": "energy", "limit_ratio": 0.1, "reason": "x"}]},
            {"mode": "relaxed_recoverable", "relaxation_ratios": []},
            {"mode": "relaxed_recoverable", "relaxation_ratios": [{"type": "capability", "limit_ratio": 0.1, "reason": "x"}]},
            {"mode": "relaxed_recoverable", "relaxation_ratios": [
                {"type": "energy", "limit_ratio": 0.1, "reason": "x"},
                {"type": "energy", "limit_ratio": 0.1, "reason": "x"},
            ]},
            {"mode": "relaxed_recoverable", "relaxation_ratios": [{"type": "time_window", "limit_ratio": 0.31, "reason": "x"}]},
            {"mode": "relaxed_recoverable", "relaxation_ratios": [{"type": "energy", "limit_ratio": 0.21, "reason": "x"}]},
            {"mode": "relaxed_recoverable", "relaxation_ratios": [{"type": "energy", "limit_ratio": float("nan"), "reason": "x"}]},
        ]
        for control in invalid:
            with self.subTest(control=control), self.assertRaises(ValueError):
                validate_feasibility_control(control, self.candidates)


class FeasibilityCompilerTests(unittest.TestCase):
    def test_compiles_default_ratios_and_modes(self) -> None:
        control = {
            "mode": "relaxed_recoverable",
            "relaxation_ratios": [
                {"type": "time_window", "limit_ratio": 0.10, "reason": "x"},
                {"type": "energy", "limit_ratio": 0.05, "reason": "x"},
            ],
        }
        compiled = compile_feasibility_control(control)
        self.assertAlmostEqual(compiled["per_type"]["time_window"]["delta_ratio"], 0.05)
        self.assertAlmostEqual(compiled["per_type"]["energy"]["delta_ratio"], 0.025)
        self.assertEqual(compile_feasibility_control({"mode": "strict", "relaxation_ratios": []}), {"mode": "strict"})
        self.assertEqual(compile_feasibility_control({"mode": "recovery_only", "relaxation_ratios": []}), {"mode": "recovery_only"})

    def test_config_override(self) -> None:
        config = Config(extras={"relaxation_delta_rules": {"energy": {"delta_fraction": 0.25, "delta_cap": 0.01}}})
        compiled = compile_feasibility_control(
            {"mode": "relaxed_recoverable", "relaxation_ratios": [{"type": "energy", "limit_ratio": 0.20, "reason": "x"}]},
            config,
        )
        self.assertAlmostEqual(compiled["per_type"]["energy"]["delta_ratio"], 0.01)


class ConstraintRatioTests(unittest.TestCase):
    def test_documented_time_window_ratio(self) -> None:
        task = Task(1, (53.0, 0.0), 20.0, 50.0, 1.0, {"a"}, 1.0)
        agent = Agent(0, 1000.0, {"a"}, 1.0, 0.0, 0.0, {"a": 0.0})
        instance = _instance(task, agent)
        solution = AssignmentSolution(routes={0: [1]})
        report, _ = check_constraints(solution, instance, Config())
        detail = report.violation_details_by_type["time_window"][0]
        self.assertAlmostEqual(detail["lateness"], 3.0)
        self.assertAlmostEqual(detail["time_ref"], 30.0)
        self.assertAlmostEqual(detail["ratio"], 0.10)
        self.assertAlmostEqual(report.violation_ratio_by_type["time_window"], 0.10)

    def test_documented_energy_ratio_and_reference_floors(self) -> None:
        task = Task(1, (5.0, 0.0), 0.0, 1000.0, 100.0, {"a"}, 1.0)
        agent = Agent(0, 100.0, {"a"}, 1.0, 1.0, 0.0, {"a": 1.0})
        instance = _instance(task, agent)
        solution = AssignmentSolution(routes={0: [1]})
        config = Config()
        config.eval.include_depot_legs = False
        report, _ = check_constraints(solution, instance, config)
        detail = report.violation_details_by_type["energy"][0]
        self.assertAlmostEqual(detail["energy_over"], 5.0)
        self.assertAlmostEqual(detail["energy_ref"], 100.0)
        self.assertAlmostEqual(detail["ratio"], 0.05)
        self.assertAlmostEqual(report.violation_ratio_by_type["energy"], 0.05)

        floor_task = Task(1, (1.0, 0.0), 0.0, 0.0, 1.0, {"a"}, 1.0)
        floor_agent = Agent(0, 0.0, {"a"}, 1.0, 1.0, 0.0, {"a": 0.0})
        floor_config = Config(extras={"min_time_window_ref": 2.0, "min_energy_ref": 4.0})
        floor_config.eval.include_depot_legs = False
        floor_report, _ = check_constraints(
            AssignmentSolution(routes={0: [1]}), _instance(floor_task, floor_agent), floor_config
        )
        self.assertAlmostEqual(floor_report.violation_details_by_type["time_window"][0]["time_ref"], 2.0)
        self.assertAlmostEqual(floor_report.violation_details_by_type["energy"][0]["energy_ref"], 4.0)


class FeasibilityPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = {
            "mode": "relaxed_recoverable",
            "per_type": {
                "time_window": {"limit_ratio": 0.10, "delta_ratio": 0.05},
                "energy": {"limit_ratio": 0.05, "delta_ratio": 0.025},
            },
        }

    def test_rejects_capability_total_individual_and_delta(self) -> None:
        cases = [
            (_report(), _report(capability=1.0), "not relaxable"),
            (_report(time_window=1.0, time_ratio=0.08), _report(time_window=2.0, time_ratio=0.11, time_individual=0.09), "total"),
            (_report(time_window=1.0, time_ratio=0.08), _report(time_window=2.0, time_ratio=0.09, time_individual=0.11), "individual"),
            (_report(energy=1.0, energy_ratio=0.01), _report(energy=2.0, energy_ratio=0.04, energy_individual=0.04), "delta"),
        ]
        for current, trial, reason in cases:
            decision = check_feasibility_admissibility(current, trial, self.policy)
            with self.subTest(reason=reason):
                self.assertFalse(decision.admissible)
                self.assertIn(reason, decision.reason)

    def test_accepts_per_type_ratios_and_reports_recovery(self) -> None:
        current = _report(time_window=1.0, energy=1.0, time_ratio=0.04, energy_ratio=0.01)
        trial = _report(time_window=2.0, energy=2.0, time_ratio=0.08, energy_ratio=0.03, time_individual=0.09, energy_individual=0.04)
        decision = check_feasibility_admissibility(current, trial, self.policy)
        self.assertTrue(decision.admissible)
        self.assertEqual(decision.accept_scope, "working_only")
        recovered = check_feasibility_admissibility(current, _report(), self.policy)
        self.assertTrue(recovered.admissible)
        self.assertIn("feasibility_recovered", recovered.events)


class _RelaxedClient:
    def chat(self, messages, **kwargs):
        del kwargs
        prompt = messages[-1]["content"]
        observation = _observation_from_prompt(prompt)
        if "ROLE: SUPERVISOR_KICKOFF" in prompt:
            payload = demo_supervisor_kickoff(observation)
        elif "ROLE: SUPERVISOR_REVIEW" in prompt:
            payload = demo_supervisor_review(observation)
            if payload["supervisor_decision"]["action"] == "issue_contract":
                payload["supervisor_decision"]["next_contract"]["feasibility_control"] = {
                    "mode": "relaxed_recoverable",
                    "relaxation_ratios": [
                        {"type": "time_window", "limit_ratio": 0.10, "reason": "Allow bounded lateness."},
                        {"type": "energy", "limit_ratio": 0.05, "reason": "Allow bounded energy pressure."},
                    ],
                }
        elif "ROLE: SOLVER" in prompt:
            payload = demo_solver_decision(observation)
        else:
            raise AssertionError("unknown role")
        return json.dumps(payload)


def _observation_from_prompt(prompt: str):
    raw = prompt.split("CONTEXT:\n", 1)[1].split("\n\nOUTPUT JSON SCHEMA:", 1)[0]
    return json.loads(raw)["observation"]


class OrchestratorFeasibilityTests(unittest.TestCase):
    def test_compiled_policy_reaches_solver_and_result(self) -> None:
        task = Task(1, (1.0, 0.0), 0.0, 50.0, 1.0, {"a"}, 1.0)
        agent = Agent(0, 100.0, {"a"}, 1.0, 1.0, 0.0, {"a": 1.0})
        config = Config()
        config.eval.objective_policy.layers = [ObjectiveLayer("missed_priority", "missed_priority")]
        solution = run_orchestrator(
            _RelaxedClient(), _instance(task, agent), "cover tasks", config,
            Budget(time_limit_sec=0.2, max_iters=4), max_agent_steps=5,
            max_solver_calls=4,
        )
        events = solution.run_artifact["trace_events"]
        by_type = {event["event_type"]: event["payload"] for event in events}
        self.assertEqual(by_type["validated_feasibility_control"]["mode"], "relaxed_recoverable")
        self.assertAlmostEqual(by_type["compiled_feasibility_policy"]["per_type"]["energy"]["delta_ratio"], 0.025)
        solver_contract = by_type["solver_observation"]["active_contract"]
        self.assertIn("compiled_policy_summary", solver_contract["feasibility_control"])
        self.assertNotIn("feasibility_policy", solver_contract)
        solver_diagnostics = by_type["solver_result"]["diagnostics"]
        self.assertEqual(solver_diagnostics["feasibility_policy"]["mode"], "relaxed_recoverable")
        self.assertIn("violation_ratios", solver_diagnostics)
        report = build_result_text(solution, {"ok": True})
        self.assertIn("VALIDATED FEASIBILITY CONTROL", report)
        self.assertIn("COMPILED FEASIBILITY POLICY", report)


if __name__ == "__main__":
    unittest.main()
