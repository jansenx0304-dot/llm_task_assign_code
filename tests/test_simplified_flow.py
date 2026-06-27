from __future__ import annotations

import json
import unittest

from sar_alloc.config import Budget, Config
from sar_alloc.orchestrator import execute_runtime_control, run_orchestrator
from sar_alloc.runner import DEFAULT_GOAL, load_instance_from_json, resolve_instance_path
from sar_alloc.step_agent import RuntimeControl


FORBIDDEN = {
    "effect_audit",
    "dominant_blocker",
    "audit_note",
    "validation_report",
    "execution_semantics",
    "basis_ref_validation",
    "algorithm_manifest",
}


class FakeClient:
    def chat(self, messages, **kwargs):
        del kwargs
        prompt = messages[-1]["content"]
        observation = _observation_from_prompt(prompt)
        if "ROLE: SUPERVISOR" in prompt:
            return json.dumps(_supervisor_payload(observation))
        if "ROLE: STEP" in prompt:
            return json.dumps(_step_payload(observation))
        raise AssertionError("unknown prompt role")


class SimplifiedFlowTest(unittest.TestCase):
    def test_fake_flow_runs_and_records_basic_steps(self) -> None:
        instance = load_instance_from_json(resolve_instance_path("T50"))
        solution = run_orchestrator(
            client=FakeClient(),
            instance=instance,
            user_goal_text=DEFAULT_GOAL,
            config=Config(rng_seed=0),
            budget=Budget(time_limit_sec=3.0, max_iters=5),
            rng_seed=0,
            max_agent_steps=4,
            max_solver_calls=3,
            llm_mode="test",
            run_config={"instance": "T50"},
        )
        steps = solution.run_artifact["records"]["steps"]
        self.assertGreaterEqual(len(steps), 2)
        self.assertTrue(any(step["phase"] == "step" and step["result"] for step in steps))
        self.assertFalse(_contains_forbidden(solution.run_artifact))

    def test_review_request_is_not_executable_action(self) -> None:
        control = RuntimeControl(action="request_supervisor_review", intent_id="", runtime_target={})
        with self.assertRaisesRegex(ValueError, "control flow"):
            execute_runtime_control(
                control,
                instance=load_instance_from_json(resolve_instance_path("T50")),
                config=Config(),
                state=object(),
                rng_seed=0,
            )


def _observation_from_prompt(prompt: str):
    marker = "CONTEXT:\n"
    schema_marker = "\n\nOUTPUT JSON SCHEMA:"
    raw = prompt.split(marker, 1)[1].split(schema_marker, 1)[0]
    return json.loads(raw)["observation"]


def _supervisor_payload(observation):
    phase = observation["run_context"]["phase"]
    limits = observation["action_space"].get("next_stage_resource_limits", {})
    max_actions = max(1, min(1, int(limits.get("max_solver_actions_allowed", 1) or 1)))
    if phase == "supervisor_review" and int(limits.get("max_solver_actions_allowed", 0) or 0) <= 0:
        return {
            "supervisor_decision": {
                "action": "stop_run",
                "decision_evidence": _supervisor_evidence(stop=True),
                "stop_explanation": "No stage budget remains.",
            }
        }
    stage_type = "initial_construction" if phase == "supervisor_kickoff" else "alns_search"
    intent_id = "construct_coverage" if stage_type == "initial_construction" else "improve_coverage"
    intent_type = "construction" if stage_type == "initial_construction" else "improvement"
    return {
        "supervisor_decision": {
            "action": "issue_stage",
            "decision_evidence": _supervisor_evidence(stop=False),
            "global_objective": {"objective_layers": ["missed_priority", "unassigned_count"]},
            "next_stage": {
                "stage_type": stage_type,
                "objective_layers": ["missed_priority", "unassigned_count"],
                "feasibility_control": {"mode": "strict", "relaxation_ratios": []},
                "target_intents": [
                    {
                        "intent_id": intent_id,
                        "intent_type": intent_type,
                        "rationale": "bounded stage",
                    }
                ],
                "protected_metrics": [],
                "resource_policy": {
                    "min_actions": 1,
                    "max_actions": max_actions,
                    "max_iters": max(1, min(3, int(limits.get("max_iters_allowed", 3) or 3))),
                    "max_time_sec": max(0.1, min(1.0, float(limits.get("max_time_sec_allowed", 1.0) or 1.0))),
                    "require_feasible": False,
                    "metric_thresholds": {},
                },
            },
        }
    }


def _step_payload(observation):
    actions = observation["execution_state"]["hard_executable_actions"]
    if "construct_initial" in actions:
        action = "construct_initial"
    elif "run_alns" in actions:
        action = "run_alns"
    else:
        return {
            "step_decision": {
                "action": "request_supervisor_review",
                "decision_evidence": _decision_evidence("request_supervisor_review"),
                "review_request": {"reason": "No executable algorithm action remains."},
            }
        }

    active_stage = observation["active_stage"]
    intent_id = active_stage["target_intents"][0]["intent_id"]
    base = {
        "action": action,
        "intent_id": intent_id,
        "runtime_target": {
            "scope_kind": "global",
            "task_ids": [],
            "agent_ids": [],
            "focus_metrics": ["missed_priority"],
        },
        "insertion_control": {
            "operator_scores": [{"name": "greedy_insertion", "score": 6}],
            "task_signal_scores": [{"name": "priority_loss", "score": 6}],
            "position_signal_scores": [{"name": "insert_cost", "score": 6}],
        },
        "solver_budget": {"max_iters": 1, "max_time_sec": 0.2},
        "decision_evidence": _decision_evidence(action),
    }
    if action == "run_alns":
        base["destroy_control"] = {
            "operator_scores": [{"name": "random_removal", "score": 5}],
            "signal_scores": [{"name": "cost_pressure", "score": 5}],
            "intensity_score": 1,
        }
        base["acceptance_control"] = {"mode": "greedy", "intensity_score": 0}
    return {"step_decision": base}


def _supervisor_evidence(stop: bool):
    if stop:
        return {
            "basis": [
                {"source": "run_context", "name": "remaining_global_resources"},
                {"source": "solution_state", "name": "best_feasible_exists"},
            ],
            "argument": [{"claim": "The run should stop because no useful stage budget remains.", "uses": [0, 1]}],
            "control_intent": "Stop the run instead of issuing an infeasible or low-value stage.",
            "expected_effects": [],
        }
    return {
        "basis": [
            {"source": "run_context", "name": "remaining_global_resources"},
            {"source": "solution_state", "name": "missed_priority"},
        ],
        "argument": [
            {"claim": "A bounded stage is needed under the remaining budget to reduce priority loss.", "uses": [0, 1]}
        ],
        "control_intent": "Issue a bounded stage focused on missed priority.",
        "expected_effects": [{"metric": "missed_priority", "direction": "decrease"}],
    }


def _decision_evidence(action: str):
    if action == "request_supervisor_review":
        return {
            "basis": [{"source": "execution_state", "name": "hard_executable_actions"}],
            "argument": [{"claim": "Review is needed because no useful executable solver action remains.", "uses": [0]}],
            "control_intent": "Request supervisor review.",
            "expected_effects": [],
        }
    return {
        "basis": [
            {"source": "execution_state", "name": "hard_executable_actions"},
            {"source": "solution_evidence", "name": "missed_priority"},
        ],
        "argument": [
            {"claim": "The selected solver action is executable and should reduce priority loss.", "uses": [0, 1]}
        ],
        "control_intent": f"Execute {action} to reduce priority loss.",
        "expected_effects": [{"metric": "missed_priority", "direction": "decrease"}],
    }


def _contains_forbidden(value) -> bool:
    if isinstance(value, dict):
        if any(key in FORBIDDEN for key in value):
            return True
        return any(_contains_forbidden(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


if __name__ == "__main__":
    unittest.main()
