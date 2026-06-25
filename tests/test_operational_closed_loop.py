from __future__ import annotations

import unittest

from sar_alloc.config import Config
from sar_alloc.constraint_checker import ConstraintReport
from sar_alloc.contract_monitor import check_contract_completion, update_contract_progress
from sar_alloc.control_surface import (
    OBSERVATION_BLOCK_CONSUMERS,
    SOLVER_OUTPUT_FIELD_CONSUMERS,
    SUPERVISOR_KICKOFF_BLOCK_CONSUMERS,
    SUPERVISOR_OUTPUT_FIELD_CONSUMERS,
    SUPERVISOR_REVIEW_BLOCK_CONSUMERS,
)
from sar_alloc.demo_policy import demo_solver_decision
from sar_alloc.feasibility_policy import check_feasibility_admissibility
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.observation import (
    build_solver_observation,
    build_supervisor_kickoff_observation,
    build_supervisor_review_observation,
)
from sar_alloc.policy_validator import validate_solver_decision
from sar_alloc.schemas import solver_decision_schema_for_candidates
from sar_alloc.solution import AssignmentSolution
from sar_alloc.tools import (
    ContractProgress,
    compile_contract,
    compile_solver_control,
    feasibility_policy_from_manifest,
    solution_summary,
)

from tests.closed_loop_helpers import configured, contract, tiny_instance


def _report(
    *,
    feasible: bool,
    total: float,
    time_ratio: float = 0.0,
    energy_ratio: float = 0.0,
    unrecoverable: float = 0.0,
) -> ConstraintReport:
    return ConstraintReport(
        is_feasible=feasible,
        violation_total=total,
        violation_capability=unrecoverable,
        violation_time_window=time_ratio,
        violation_energy=energy_ratio,
        recoverable_violation_total=max(0.0, total - unrecoverable),
        unrecoverable_violation_total=unrecoverable,
        violation_ratio_by_type={
            "time_window": time_ratio,
            "energy": energy_ratio,
        },
    )


class OperationalClosedLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = tiny_instance()
        self.config = configured()
        self.candidates = build_public_candidates(self.instance, self.config)

    def _observation(
        self,
        *,
        contract_dict: dict,
        progress: ContractProgress,
        solution: AssignmentSolution,
        last_verification: dict | None = None,
        has_working: bool = True,
    ) -> dict:
        return build_solver_observation(
            active_contract=contract_dict,
            contract_progress=progress.as_dict(),
            remaining_contract_resources={
                "actions": max(
                    0,
                    int(contract_dict["resource_policy"]["max_actions"])
                    - progress.solver_actions,
                ),
                "min_actions_remaining": max(
                    0,
                    int(contract_dict["resource_policy"]["min_actions"])
                    - progress.solver_actions,
                ),
                "iters": 20,
                "time_sec": 5.0,
            },
            remaining_global_budget={
                "step_calls": 5,
                "solver_calls": 5,
                "iters": 20,
                "time_sec": 5.0,
            },
            working_summary=solution_summary(
                solution, self.instance, self.config
            ),
            best_summary=None,
            candidate_landscape={
                "target_buckets": {
                    "unassigned_priority": {
                        "task_count": len(solution.unassigned),
                        "priority_mass": sum(
                            self.instance.task_by_id(tid).priority
                            for tid in solution.unassigned
                        ),
                        "top_tasks": [
                            {
                                "task_id": tid,
                                "priority": self.instance.task_by_id(tid).priority,
                            }
                            for tid in sorted(solution.unassigned)
                        ],
                    }
                },
                "candidate_stats": {},
                "destroy_options": {},
            },
            recent_memory=[],
            candidates=self.candidates,
            last_verification=last_verification,
            has_working_solution=has_working,
        )

    def test_observation_blocks_have_declared_consumers(self) -> None:
        initial = contract().as_dict()
        initial["contract_type"] = "initial_construction"
        initial["target_policy"] = {
            "preferred_target_kinds": ["unassigned_priority"]
        }
        solution = AssignmentSolution.empty_from_instance(self.instance)
        observation = self._observation(
            contract_dict=initial,
            progress=ContractProgress("C1"),
            solution=solution,
            has_working=False,
        )
        self.assertEqual(set(observation), set(OBSERVATION_BLOCK_CONSUMERS))
        self.assertTrue(all(OBSERVATION_BLOCK_CONSUMERS.values()))
        self.assertEqual(
            observation["action_space"]["allowed_actions"], ["construct_initial"]
        )
        kickoff = build_supervisor_kickoff_observation(
            instance=self.instance,
            instance_summary={"time_window_risk": {}, "energy_risk": {}},
            candidates=self.candidates,
            user_goal_text="cover",
            remaining_global_budget={
                "step_calls": 2,
                "solver_calls": 2,
                "iters": 2,
                "time_sec": 2,
            },
            relaxation_scale_context={},
        )
        self.assertEqual(set(kickoff), set(SUPERVISOR_KICKOFF_BLOCK_CONSUMERS))
        review = build_supervisor_review_observation(
            remaining_global_budget={
                "step_calls": 1,
                "solver_calls": 1,
                "iters": 1,
                "time_sec": 1,
            },
            completed_contract=initial,
            completed_contract_progress=ContractProgress("C1").as_dict(),
            completed_contract_result={"completion_status": "success"},
            working_summary=solution_summary(solution, self.instance, self.config),
            best_summary=None,
            candidates=self.candidates,
        )
        self.assertEqual(set(review), set(SUPERVISOR_REVIEW_BLOCK_CONSUMERS))
        self.assertTrue(all(SUPERVISOR_OUTPUT_FIELD_CONSUMERS.values()))

    def test_action_and_target_enums_are_runtime_gated(self) -> None:
        search = contract(min_actions=2, max_actions=4).as_dict()
        solution = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2, 3})
        progress = ContractProgress("C1")
        observation = self._observation(
            contract_dict=search, progress=progress, solution=solution
        )
        self.assertEqual(observation["action_space"]["allowed_actions"], ["run_alns"])
        schema = solver_decision_schema_for_candidates(self.candidates, observation)
        branches = schema["properties"]["solver_decision"]["oneOf"]
        self.assertEqual(
            [branch["properties"]["action"]["const"] for branch in branches],
            ["run_alns"],
        )
        target_enum = branches[0]["properties"]["target_id"]["enum"]
        self.assertNotIn("contract_review", target_enum)

        progress.solver_actions = 2
        progress.recent_intent_statuses = ["not_achieved", "not_achieved"]
        progress.recent_blockers = ["no_quality_gain", "no_quality_gain"]
        progress.intent_status_counts = {"not_achieved": 2}
        progress.dominant_blocker_counts = {"no_quality_gain": 2}
        last = {
            "intent_status": "not_achieved",
            "dominant_blocker": "no_quality_gain",
        }
        observation = self._observation(
            contract_dict=search,
            progress=progress,
            solution=solution,
            last_verification=last,
        )
        self.assertEqual(
            observation["action_space"]["allowed_actions"],
            ["run_alns", "request_supervisor_review"],
        )
        schema = solver_decision_schema_for_candidates(self.candidates, observation)
        review = next(
            branch
            for branch in schema["properties"]["solver_decision"]["oneOf"]
            if branch["properties"]["action"]["const"]
            == "request_supervisor_review"
        )
        self.assertEqual(review["properties"]["target_id"]["enum"], ["contract_review"])

    def test_validator_compiler_manifest_runtime_field_closure(self) -> None:
        raw_contract = contract(min_actions=1, max_actions=2).as_dict()
        raw_contract["feasibility_control"] = {
            "mode": "relaxed_recoverable",
            "relaxation_ratios": [
                {"violation_type": "energy", "max_ratio": 0.10}
            ],
        }
        compiled_contract = compile_contract(
            raw_contract,
            "C1",
            Config(),
            protected_metric_baseline={
                "missed_priority": 8.0,
                "unassigned_count": 2.0,
                "energy_total": 3.0,
                "total_distance": 2.0,
                "makespan": 2.0,
                "route_balance": 0.0,
            },
        )
        solution = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2, 3})
        observation = self._observation(
            contract_dict=compiled_contract.as_dict(),
            progress=ContractProgress("C1"),
            solution=solution,
        )
        decision = demo_solver_decision(observation)
        validate_solver_decision(decision, observation, candidates=self.candidates)
        manifest = compile_solver_control(
            decision,
            compiled_contract,
            self.candidates,
            observation,
            decision_id="D1",
            manifest_id="R1",
            trace_id="X1",
        )
        self.assertTrue(manifest.validation_report["all_operational_fields_consumed"])
        self.assertTrue(manifest.validation_report["target_resolved"])
        self.assertEqual(manifest.compiled["target"]["target_id"], manifest.target_id)
        runtime_feasibility = feasibility_policy_from_manifest(manifest)
        self.assertEqual(runtime_feasibility, compiled_contract.feasibility_policy)
        self.assertGreater(
            runtime_feasibility["per_type"]["energy"]["delta_ratio"], 0.0
        )
        output_fields = set(decision["solver_decision"])
        self.assertLessEqual(output_fields, set(SOLVER_OUTPUT_FIELD_CONSUMERS))

    def test_feasibility_modes_are_hard_runtime_decisions(self) -> None:
        feasible = _report(feasible=True, total=0.0)
        infeasible = _report(feasible=False, total=0.2, energy_ratio=0.2)
        self.assertTrue(
            check_feasibility_admissibility(
                feasible, feasible, {"mode": "strict"}
            ).admissible
        )
        self.assertFalse(
            check_feasibility_admissibility(
                feasible, infeasible, {"mode": "strict"}
            ).admissible
        )

        relaxed = {
            "mode": "relaxed_recoverable",
            "per_type": {"energy": {"limit_ratio": 0.10, "delta_ratio": 0.05}},
        }
        within = _report(feasible=False, total=0.05, energy_ratio=0.05)
        over_delta = _report(feasible=False, total=0.06, energy_ratio=0.06)
        self.assertTrue(
            check_feasibility_admissibility(feasible, within, relaxed).admissible
        )
        self.assertFalse(
            check_feasibility_admissibility(feasible, over_delta, relaxed).admissible
        )

        current = _report(feasible=False, total=0.2, energy_ratio=0.2)
        reduced = _report(feasible=False, total=0.1, energy_ratio=0.1)
        self.assertTrue(
            check_feasibility_admissibility(
                current, reduced, {"mode": "recovery_only"}
            ).admissible
        )
        self.assertFalse(
            check_feasibility_admissibility(
                current, current, {"mode": "recovery_only"}
            ).admissible
        )

    def test_contract_monitor_runs_multiple_steps_before_builtin_failure(self) -> None:
        search = contract(min_actions=2, max_actions=4)
        progress = ContractProgress("C1")
        verifications = []
        for index in range(2):
            verification = {
                "verification_id": f"V{index}",
                "action": "run_alns",
                "intent_status": "not_achieved",
                "dominant_blocker": "no_quality_gain",
                "trace": {"iters": 1},
            }
            verifications.append(verification)
            update_contract_progress(progress, verification)
            result = check_contract_completion(search, progress, verifications)
            self.assertFalse(result["completed"])

        third = {
            "verification_id": "V3",
            "action": "run_alns",
            "intent_status": "not_achieved",
            "dominant_blocker": "no_quality_gain",
            "trace": {"iters": 1},
        }
        verifications.append(third)
        update_contract_progress(progress, third)
        result = check_contract_completion(search, progress, verifications)
        self.assertTrue(result["completed"])
        self.assertEqual(
            result["completion_reason"], "repeated_blocker:no_quality_gain"
        )


if __name__ == "__main__":
    unittest.main()
