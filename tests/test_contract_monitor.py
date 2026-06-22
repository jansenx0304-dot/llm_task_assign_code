from __future__ import annotations

import unittest

from sar_alloc.contract_monitor import check_contract_completion, update_contract_events
from sar_alloc.tools.llm_utils import ContractProgress, SearchContract


def _contract() -> SearchContract:
    return SearchContract(
        contract_id="C001",
        contract_type="alns_search",
        stage_goal={"summary": "x", "main_problem": "x", "search_intent": "x"},
        stage_objective_layers=[{"metric": "missed_priority", "direction": "min"}],
        guidance={
            "instruction": "x",
            "preferred_search_direction": "x",
            "protect": "x",
            "success_signal": "x",
            "failure_signal": "x",
        },
        feasibility_control={"mode": "strict", "relaxation_ratios": []},
        feasibility_policy={"mode": "strict"},
        completion_policy={
            "min_solver_actions": 3,
            "max_solver_actions": 6,
            "max_time_sec": 30.0,
            "max_iters": 240,
            "success_rules": [{"event": "quality_improved", "count": 2, "scope": "total"}],
            "failure_rules": [{"event": "quality_flat", "count": 2, "scope": "consecutive"}],
        },
    )


class ContractMonitorTests(unittest.TestCase):
    def test_event_rules_wait_for_min_solver_actions(self) -> None:
        progress = ContractProgress("C001", solver_actions=2)
        update_contract_events(progress, ["quality_flat"])
        update_contract_events(progress, ["quality_flat"])
        result = check_contract_completion(_contract(), progress)
        self.assertFalse(result["completed"])

    def test_failure_rule_after_min_solver_actions(self) -> None:
        progress = ContractProgress("C001", solver_actions=3)
        update_contract_events(progress, ["quality_flat"])
        update_contract_events(progress, ["quality_flat"])
        result = check_contract_completion(_contract(), progress)
        self.assertTrue(result["completed"])
        self.assertEqual(result["result"], "failure")

    def test_success_total_count(self) -> None:
        progress = ContractProgress("C001", solver_actions=3)
        update_contract_events(progress, ["quality_improved"])
        update_contract_events(progress, ["quality_flat"])
        update_contract_events(progress, ["quality_improved"])
        result = check_contract_completion(_contract(), progress)
        self.assertTrue(result["completed"])
        self.assertEqual(result["result"], "success")

    def test_max_solver_actions_always_completes(self) -> None:
        progress = ContractProgress("C001", solver_actions=6)
        result = check_contract_completion(_contract(), progress)
        self.assertTrue(result["completed"])
        self.assertEqual(result["reason"], "max_solver_actions_reached")

    def test_consecutive_scope_resets_and_total_scope_does_not(self) -> None:
        progress = ContractProgress("C001", solver_actions=3)
        update_contract_events(progress, ["quality_flat", "quality_improved"])
        update_contract_events(progress, ["quality_improved"])
        self.assertEqual(progress.consecutive_event_counts["quality_flat"], 0)
        self.assertEqual(progress.event_counts["quality_improved"], 2)
        result = check_contract_completion(_contract(), progress)
        self.assertTrue(result["completed"])
        self.assertEqual(result["result"], "success")


if __name__ == "__main__":
    unittest.main()
