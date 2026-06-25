from __future__ import annotations

import unittest
from dataclasses import dataclass
from typing import Any, Dict

from sar_alloc.config import Budget, Config, ObjectiveLayer
from sar_alloc.contract_monitor import (
    check_contract_completion,
    update_contract_progress,
)
from sar_alloc.demo_policy import (
    demo_solver_decision,
    demo_supervisor_kickoff,
    demo_supervisor_review,
)
from sar_alloc.llm_client import DummyLLMClient
from sar_alloc.llm_orchestrator import run_orchestrator
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.memory import RunMemory
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.observation import (
    build_solver_observation,
    build_supervisor_kickoff_observation,
    build_supervisor_review_observation,
)
from sar_alloc.outcome_auditor import verify_alns_action, verify_initial_construction
from sar_alloc.policy_validator import (
    validate_solver_decision,
    validate_supervisor_kickoff,
    validate_supervisor_review,
)
from sar_alloc.schemas import (
    SOLVER_DECISION_SCHEMA,
    SUPERVISOR_KICKOFF_SCHEMA,
    SUPERVISOR_REVIEW_SCHEMA,
    solver_decision_schema_for_candidates,
)
from sar_alloc.tools import (
    ContractProgress,
    SearchContract,
    alns_policy_from_manifest,
    compile_contract,
    compile_global_objective,
    compile_solver_control,
)


def tiny_instance() -> Instance:
    return Instance(
        tasks=(
            Task(
                id=1,
                loc=(1.0, 0.0),
                tw_start=0.0,
                tw_end=50.0,
                service_time=1.0,
                skill_req={"a"},
                priority=5.0,
            ),
            Task(
                id=2,
                loc=(2.0, 0.0),
                tw_start=0.0,
                tw_end=50.0,
                service_time=1.0,
                skill_req={"missing"},
                priority=2.0,
            ),
        ),
        agents=(
            Agent(
                id=0,
                init_energy=100.0,
                skills={"a"},
                speed=1.0,
                travel_energy_rate=1.0,
                standby_power=0.0,
                skill_energy_rate={"a": 1.0},
            ),
        ),
        depot=Depot(id=0, loc=(0.0, 0.0)),
        default_speed=1.0,
    )


@dataclass
class FakeReport:
    is_feasible: bool = True
    violation_total: float = 0.0
    recoverable_violation_total: float = 0.0
    violation_ratio_by_type: Dict[str, float] | None = None

    def __post_init__(self) -> None:
        if self.violation_ratio_by_type is None:
            self.violation_ratio_by_type = {"time_window": 0.0, "energy": 0.0}


@dataclass
class FakeEval:
    metrics: Dict[str, float]
    is_feasible: bool = True
    report: FakeReport | None = None

    @property
    def constraint_report(self) -> FakeReport:
        return self.report or FakeReport(self.is_feasible)

    def get_metric(self, name: str) -> float:
        return float(self.metrics.get(name, 0.0))

    def get_quality_metric(self, name: str) -> float:
        return self.get_metric(name)


class ClosedLoopRefactorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = tiny_instance()
        self.config = Config()
        self.config.eval.objective_policy.layers = [
            ObjectiveLayer(
                name="missed_priority", metric="missed_priority", direction="min"
            )
        ]
        self.candidates = build_public_candidates(self.instance, self.config)
        self.remaining = {
            "step_calls": 6.0,
            "solver_calls": 4.0,
            "time_sec": 5.0,
            "iters": 20.0,
        }
        kickoff_obs = build_supervisor_kickoff_observation(
            instance=self.instance,
            instance_summary={
                "time_window_risk": {},
                "energy_risk": {},
                "relaxation_scale_context": {},
            },
            candidates=self.candidates,
            user_goal_text="cover tasks",
            remaining_global_budget=self.remaining,
            relaxation_scale_context={
                "time_window_median_width": 10.0,
                "agent_energy_median": 100.0,
            },
        )
        raw = demo_supervisor_kickoff(kickoff_obs)["supervisor_decision"][
            "next_contract"
        ]
        self.contract = compile_contract(raw, "C001", self.config, kickoff_obs)

    def test_schema_pruned_operational_fields(self) -> None:
        forbidden = {
            "guidance",
            "completion_policy",
            "decision_basis",
            "reason",
            "success_signal",
            "failure_signal",
            "stage_goal",
            "stage_objective_layers",
            "completion_event_candidates",
        }

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                self.assertFalse(forbidden & set(node.keys()))
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        for schema in (
            SUPERVISOR_KICKOFF_SCHEMA,
            SUPERVISOR_REVIEW_SCHEMA,
            SOLVER_DECISION_SCHEMA,
        ):
            walk(schema)

    def test_solver_schema_separates_field_candidate_enums(self) -> None:
        observation = {
            "action_space": {
                "allowed_actions": ["run_alns"],
                "allowed_insertion_operators": list(
                    self.candidates.names("insertion_operator_candidates")
                ),
                "allowed_task_signals": list(
                    self.candidates.names("insertion_task_signal_candidates")
                ),
                "allowed_position_signals": list(
                    self.candidates.names("insertion_position_signal_candidates")
                ),
                "allowed_destroy_operators": list(
                    self.candidates.names("destroy_operator_candidates")
                ),
                "allowed_destroy_signals": list(
                    self.candidates.names("destroy_signal_candidates")
                ),
                "allowed_acceptance_modes": list(
                    self.candidates.names("acceptance_candidates")
                ),
            },
            "decision_targets": [{"target_id": "T1"}],
        }
        schema = solver_decision_schema_for_candidates(self.candidates, observation)
        branches = schema["properties"]["solver_decision"]["oneOf"]
        self.assertEqual(len(branches), 1)
        properties = branches[0]["properties"]
        task_names = properties["insertion_control"]["properties"][
            "task_signal_scores"
        ]["items"]["properties"]["name"]["enum"]
        destroy_names = properties["destroy_control"]["properties"]["signal_scores"][
            "items"
        ]["properties"]["name"]["enum"]
        self.assertIn("priority_loss", task_names)
        self.assertNotIn("priority_loss", destroy_names)
        self.assertEqual(properties["target_id"]["enum"], ["T1"])

    def test_validator_rejects_cross_field_signal_and_accepts_correct_field(
        self,
    ) -> None:
        action_space = {
            "allowed_actions": ["run_alns"],
            "allowed_insertion_operators": list(
                self.candidates.names("insertion_operator_candidates")
            ),
            "allowed_task_signals": list(
                self.candidates.names("insertion_task_signal_candidates")
            ),
            "allowed_position_signals": list(
                self.candidates.names("insertion_position_signal_candidates")
            ),
            "allowed_destroy_operators": list(
                self.candidates.names("destroy_operator_candidates")
            ),
            "allowed_destroy_signals": list(
                self.candidates.names("destroy_signal_candidates")
            ),
            "allowed_acceptance_modes": list(
                self.candidates.names("acceptance_candidates")
            ),
        }
        observation = {
            "action_space": action_space,
            "decision_targets": [{"target_id": "T1"}],
            "active_contract": {"contract_type": "alns_search"},
        }
        decision = {
            "solver_decision": {
                "action": "run_alns",
                "target_id": "T1",
                "destroy_control": {
                    "operator_scores": [],
                    "signal_scores": [{"name": "priority_loss", "score": 8}],
                    "intensity_score": 5,
                },
                "insertion_control": {
                    "operator_scores": [],
                    "task_signal_scores": [],
                    "position_signal_scores": [],
                },
                "acceptance_control": {"mode": "greedy", "intensity_score": 5},
            }
        }
        with self.assertRaisesRegex(ValueError, "priority_loss"):
            validate_solver_decision(decision, observation, candidates=self.candidates)
        decision["solver_decision"]["destroy_control"]["signal_scores"] = []
        decision["solver_decision"]["insertion_control"]["task_signal_scores"] = [
            {"name": "priority_loss", "score": 8}
        ]
        validate_solver_decision(decision, observation, candidates=self.candidates)

    def test_observation_minimality(self) -> None:
        kickoff = build_supervisor_kickoff_observation(
            instance=self.instance,
            instance_summary={
                "time_window_risk": {},
                "energy_risk": {},
                "relaxation_scale_context": {},
            },
            candidates=self.candidates,
            user_goal_text="cover tasks",
            remaining_global_budget=self.remaining,
            relaxation_scale_context={},
        )
        for key in (
            "instance_summary",
            "evidence_items",
            "memory_items",
            "objective_candidates",
            "completion_event_candidates",
        ):
            self.assertNotIn(key, kickoff)
        solver = build_solver_observation(
            active_contract=self.contract.as_dict(),
            contract_progress=ContractProgress("C001").as_dict(),
            remaining_contract_resources={"actions": 1, "iters": 1, "time_sec": 1.0},
            working_summary={
                "quality_summary": {"missed_priority": 2.0, "unassigned_count": 1.0},
                "feasibility_summary": {
                    "is_feasible": True,
                    "violation_ratio_by_type": {},
                },
            },
            best_summary=None,
            candidate_landscape={"candidate_stats": {}},
            recent_memory=[],
            candidates=self.candidates,
            observation_id="O1",
        )
        self.assertEqual(
            set(solver),
            {
                "run_context",
                "active_contract",
                "progress",
                "solution_state",
                "decision_targets",
                "action_space",
                "candidate_landscape",
                "recent_memory",
                "last_verification",
            },
        )
        review = build_supervisor_review_observation(
            remaining_global_budget=self.remaining,
            completed_contract=self.contract.as_dict(),
            completed_contract_progress={
                "condition_report": [{"condition_id": "S1", "passed": True}]
            },
            completed_contract_result={"completion_status": "success"},
            working_summary={},
            best_summary=None,
        )
        self.assertIn("completed_progress", review)
        self.assertIn("verification_summary", review)
        self.assertEqual(
            review["completed_progress"]["condition_report"][0]["condition_id"],
            "S1",
        )
        self.assertNotIn("candidate_landscape", review)

    def test_schema_outputs_validate_and_compile_to_manifest(self) -> None:
        kickoff_obs = build_supervisor_kickoff_observation(
            instance=self.instance,
            instance_summary={
                "time_window_risk": {},
                "energy_risk": {},
                "relaxation_scale_context": {},
            },
            candidates=self.candidates,
            user_goal_text="cover tasks",
            remaining_global_budget=self.remaining,
            relaxation_scale_context={},
        )
        kickoff = demo_supervisor_kickoff(kickoff_obs)
        validate_supervisor_kickoff(
            kickoff, kickoff_obs, self.candidates, self.config, self.remaining
        )
        compile_global_objective(
            self.config, kickoff["supervisor_decision"]["global_objective"]
        )

        obs = build_solver_observation(
            active_contract=self.contract.as_dict(),
            contract_progress=ContractProgress("C001").as_dict(),
            remaining_contract_resources={"actions": 1, "iters": 1, "time_sec": 1.0},
            working_summary={
                "quality_summary": {"missed_priority": 2.0, "unassigned_count": 1.0},
                "feasibility_summary": {
                    "is_feasible": True,
                    "violation_ratio_by_type": {},
                },
            },
            best_summary=None,
            candidate_landscape={"candidate_stats": {}},
            recent_memory=[],
            candidates=self.candidates,
        )
        decision = demo_solver_decision(obs)
        validate_solver_decision(decision, obs, candidates=self.candidates)
        manifest = compile_solver_control(
            decision,
            self.contract,
            self.candidates,
            obs,
            decision_id="D1",
            manifest_id="R1",
        )
        self.assertEqual(manifest.source_decision_id, "D1")
        self.assertTrue(manifest.validation_report["all_operational_fields_consumed"])
        self.assertTrue(manifest.validation_report["explanation_ignored_by_runtime"])
        self.assertIn("insertion", manifest.compiled)
        self.assertGreater(len(manifest.defaults_applied), 0)

    def test_runtime_manifest_alns_policy_alignment(self) -> None:
        review = demo_supervisor_review(
            {
                "budget_caps": {
                    "max_solver_actions": 3,
                    "max_time_sec": 3.0,
                    "max_iters": 9,
                }
            }
        )
        validate_supervisor_review(
            review,
            {
                "allowed_contract_types": ["alns_search"],
                "allowed_objective_metrics": [
                    "missed_priority",
                    "unassigned_count",
                    "energy_total",
                ],
            },
            self.candidates,
            self.config,
            self.remaining,
        )
        contract = compile_contract(
            review["supervisor_decision"]["next_contract"], "C002", self.config
        )
        obs = build_solver_observation(
            active_contract=contract.as_dict(),
            contract_progress=ContractProgress("C002").as_dict(),
            remaining_contract_resources={"actions": 3, "iters": 9, "time_sec": 3.0},
            working_summary={
                "quality_summary": {
                    "missed_priority": 2.0,
                    "unassigned_count": 1.0,
                    "energy_total": 4.0,
                },
                "feasibility_summary": {
                    "is_feasible": True,
                    "violation_ratio_by_type": {"energy": 0.0},
                },
            },
            best_summary=None,
            candidate_landscape={"candidate_stats": {}},
            recent_memory=[],
            candidates=self.candidates,
        )
        decision = demo_solver_decision(obs)
        validate_solver_decision(decision, obs, candidates=self.candidates)
        manifest = compile_solver_control(
            decision, contract, self.candidates, obs, decision_id="D2", manifest_id="R2"
        )
        policy = alns_policy_from_manifest(manifest)
        self.assertEqual(
            policy.destroy_policy.operator_weights["related_cluster_removal"], 8
        )
        self.assertEqual(policy.acceptance_policy.mode, "threshold")
        self.assertNotIn("explanation", manifest.compiled)

    def test_initial_audit_classification(self) -> None:
        class Result:
            evaluation = FakeEval(
                {"missed_priority": 1.0, "unassigned_count": 1.0}, is_feasible=False
            )
            trace = {
                "kind": "initial_insertion",
                "inserted_task_count": 1,
                "uninserted_task_count": 1,
            }

        partial = verify_initial_construction(Result(), self.contract)
        self.assertEqual(partial["event_tags"], ["initial_partial"])
        self.assertEqual(partial["intent_status"], "partial")

        class Empty:
            evaluation = FakeEval({"missed_priority": 2.0}, is_feasible=False)
            trace = {
                "kind": "initial_insertion",
                "inserted_task_count": 0,
                "uninserted_task_count": 2,
            }

        empty = verify_initial_construction(Empty(), self.contract)
        self.assertEqual(empty["event_tags"], ["initial_empty"])

    def test_outcome_verification_and_event_taxonomy(self) -> None:
        before = FakeEval(
            {"missed_priority": 5.0, "unassigned_count": 3.0, "energy_total": 10.0},
            True,
        )
        after = FakeEval(
            {"missed_priority": 5.0, "unassigned_count": 3.0, "energy_total": 8.0}, True
        )
        trace = {
            "kind": "alns",
            "iters": 4,
            "trial_flow": {
                "candidate_trials": 4,
                "hard_filter_failed": 0,
                "feasibility_rejected": 3,
                "admissible_trials": 1,
                "acceptance_rejected": 0,
                "accepted_trials": 1,
                "global_best_improved_trials": 0,
            },
            "rejection_reasons": {"energy_limit_exceeded": 3},
        }
        verification = verify_alns_action(
            before_working_eval=before,
            after_working_eval=after,
            before_best_feasible_eval=None,
            after_action_best_eval=None,
            trace=trace,
            contract=self.contract,
            manifest={
                "manifest_id": "R1",
                "source_decision_id": "D1",
                "target_id": "T_energy_debt",
                "contract_id": "C001",
            },
        )
        self.assertEqual(verification["dominant_blocker"], "protected_metric_violated")
        self.assertIn("protected_metric_violated", verification["event_tags"])
        self.assertNotIn("no_admissible_candidate", str(verification))
        self.assertEqual(verification["metric_delta"]["working"]["energy_total"], -2.0)

    def test_contract_monitor_conditions(self) -> None:
        contract = SearchContract(
            contract_id="C010",
            contract_type="alns_search",
            objective_layers=[{"metric": "missed_priority", "direction": "min"}],
            feasibility_control={"mode": "strict", "relaxation_ratios": []},
            feasibility_policy={"mode": "strict"},
            target_policy={"preferred_target_kinds": ["unassigned_priority"]},
            protected_metrics=[],
            resource_policy={
                "min_actions": 2,
                "max_actions": 4,
                "max_iters": 20,
                "max_time_sec": 5.0,
            },
            exit_conditions={
                "success": [
                    {
                        "condition_id": "S1",
                        "source": "aggregate.achieved",
                        "op": ">",
                        "value": 5,
                        "window": 2,
                    }
                ],
                "failure": [
                    {
                        "condition_id": "F1",
                        "source": "aggregate.not_achieved",
                        "op": ">=",
                        "value": 2,
                        "window": 2,
                    }
                ],
            },
        )
        progress = ContractProgress("C010")
        v1 = {
            "verification_id": "V1",
            "intent_status": "not_achieved",
            "dominant_blocker": "feasibility_rejected_trials",
            "metric_delta": {"working": {"missed_priority": 0.0}},
            "trace": {"trial_flow": {}, "iters": 1},
        }
        update_contract_progress(progress, v1)
        self.assertEqual(
            check_contract_completion(contract, progress, [v1])["completion_status"],
            "continue",
        )
        v2 = {
            "verification_id": "V2",
            "intent_status": "not_achieved",
            "dominant_blocker": "feasibility_rejected_trials",
            "metric_delta": {"working": {"missed_priority": 0.0}},
            "trace": {"trial_flow": {}, "iters": 1},
        }
        update_contract_progress(progress, v2)
        result = check_contract_completion(contract, progress, [v1, v2])
        self.assertEqual(result["completion_status"], "failure")
        self.assertTrue(result["condition_report"])

    def test_memory_traceability_chain(self) -> None:
        memory = RunMemory()
        obs = {
            "observation_id": "O1",
            "decision_targets": [{"target_id": "T1", "kind": "energy_debt"}],
        }
        decision = {"solver_decision": {"action": "run_alns", "target_id": "T1"}}
        memory.record_observation(obs)
        did = memory.record_decision(decision, obs)
        manifest = {
            "manifest_id": "R1",
            "source_decision_id": did,
            "contract_id": "C1",
            "target_id": "T1",
            "trace_id": "X1",
            "compiled": {"acceptance": {"mode": "threshold", "intensity_score": 4}},
        }
        trace = {
            "trace_id": "X1",
            "kind": "alns",
            "trial_flow": {"candidate_trials": 2, "accepted_trials": 1},
        }
        verification = {
            "trace_id": "X1",
            "intent_status": "partial",
            "dominant_blocker": "none",
            "metric_delta": {"working": {"energy_total": -1.0}},
            "trace": trace,
        }
        record = memory.record_verified_action(
            obs, decision, manifest, trace, verification
        )
        self.assertEqual(record["observation_id"], "O1")
        self.assertEqual(record["decision_id"], did)
        self.assertEqual(record["manifest_id"], "R1")
        self.assertTrue(record["trace_id"])
        self.assertTrue(record["verification_id"])
        self.assertEqual(
            memory.last_verification()["verification_id"], record["verification_id"]
        )
        self.assertEqual(memory.for_solver()[0]["record_id"], record["record_id"])

    def test_full_smoke_closed_loop(self) -> None:
        solution = run_orchestrator(
            DummyLLMClient(),
            self.instance,
            "cover tasks",
            self.config,
            Budget(time_limit_sec=0.2, max_iters=4),
            max_agent_steps=5,
            max_solver_calls=4,
            llm_mode="dummy",
        )
        events = [
            event["event_type"] for event in solution.run_artifact["trace_events"]
        ]
        for name in (
            "supervisor_kickoff_observation",
            "solver_observation",
            "runtime_control_manifest",
            "execution_trace",
            "outcome_verification",
            "memory_update",
            "contract_completion_check",
            "supervisor_review_observation",
            "final_result",
        ):
            self.assertIn(name, events)
        memory = solution.run_artifact["memory"]
        self.assertTrue(memory["verified_actions"])
        first = memory["verified_actions"][0]
        for key in (
            "observation_id",
            "decision_id",
            "manifest_id",
            "trace_id",
            "verification_id",
        ):
            self.assertTrue(first[key])
        self.assertNotIn("no_admissible_candidate", str(solution.run_artifact))


if __name__ == "__main__":
    unittest.main()
