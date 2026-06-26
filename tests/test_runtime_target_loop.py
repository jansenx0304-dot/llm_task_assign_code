from __future__ import annotations

import unittest

from sar_alloc.config import Budget, Config
from sar_alloc.llm_client import DummyLLMClient
from sar_alloc.llm_orchestrator import run_orchestrator
from sar_alloc.policy_validator import validate_solver_decision
from sar_alloc.runner import DEFAULT_GOAL, load_instance_from_json, resolve_instance_path


class RuntimeTargetLoopTest(unittest.TestCase):
    def test_dummy_run_threads_manifest_target_into_trace(self) -> None:
        instance = load_instance_from_json(resolve_instance_path("T50"))
        solution = run_orchestrator(
            client=DummyLLMClient(),
            instance=instance,
            user_goal_text=DEFAULT_GOAL,
            config=Config(rng_seed=0),
            budget=Budget(time_limit_sec=3.0, max_iters=5),
            rng_seed=0,
            max_agent_steps=3,
            max_solver_calls=3,
            llm_mode="dummy",
            run_config={"instance": "T50"},
        )
        events = solution.run_artifact["trace_events"]
        manifests = [
            event["payload"]
            for event in events
            if event["event_type"] == "runtime_control_manifest"
            and event["payload"]["action"] in {"construct_initial", "run_alns"}
        ]
        traces = [
            event["payload"]
            for event in events
            if event["event_type"] == "execution_trace"
            and event["payload"].get("kind") in {"initial_insertion", "alns"}
        ]
        self.assertEqual(len(manifests), len(traces))
        self.assertGreaterEqual(len(traces), 2)
        for manifest, trace in zip(manifests, traces):
            target = manifest["compiled"]["target"]
            self.assertEqual(target, trace["runtime_target"])
            self.assertNotEqual({}, trace["runtime_target"])
            if target["scope_kind"] != "global":
                engagement = trace.get("target_engagement", {})
                self.assertTrue(engagement)
                self.assertTrue(
                    engagement.get("target_tasks_inserted")
                    or engagement.get("target_destroy_moves_used", 0) > 0
                    or engagement.get("target_destroy_fallback_count", 0) > 0
                    or engagement.get("target_insertion_fallback_count", 0) > 0
                )

    def test_validator_rejects_non_visible_runtime_target_ids(self) -> None:
        observation = {
            "execution_state": {"hard_executable_actions": ["construct_initial"]},
            "active_contract": {
                "contract_type": "initial_construction",
                "target_intents": [{"intent_id": "construct_coverage"}],
            },
            "targetable_evidence": {
                "visible_task_ids": [1],
                "visible_agent_ids": [2],
            },
            "control_catalog": {
                "insertion_operators": ["greedy_insertion"],
                "insertion_task_signals": ["priority_loss"],
                "insertion_position_signals": ["insert_cost"],
            },
        }
        payload = {
            "solver_decision": {
                "action": "construct_initial",
                "decision_basis": [
                    {
                        "basis_id": "B1",
                        "claim": "construct",
                        "evidence_refs": ["targetable_evidence.visible_task_ids"],
                    }
                ],
                "situation_summary": {"summary": "construct", "basis_ids": ["B1"]},
                "intent_id": "construct_coverage",
                "runtime_target": {
                    "scope_kind": "task_scope",
                    "task_ids": [99],
                    "agent_ids": [],
                    "focus_metrics": ["missed_priority"],
                },
                "insertion_control": {
                    "operator_scores": [{"name": "greedy_insertion", "score": 5}],
                    "task_signal_scores": [{"name": "priority_loss", "score": 5}],
                    "position_signal_scores": [{"name": "insert_cost", "score": 5}],
                },
                "solver_budget": {"max_iters": 1, "max_time_sec": 1.0},
                "expected_effects": [
                    {
                        "effect_id": "E1",
                        "metric": "missed_priority",
                        "direction": "decrease",
                        "scope": "working",
                        "basis_ids": ["B1"],
                    }
                ],
            }
        }
        with self.assertRaisesRegex(ValueError, "non-visible task id"):
            validate_solver_decision(payload, observation)


if __name__ == "__main__":
    unittest.main()
