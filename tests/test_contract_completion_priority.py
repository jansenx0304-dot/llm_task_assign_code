from __future__ import annotations

import unittest

from sar_alloc.contract_monitor import check_contract_completion
from sar_alloc.tools import ContractProgress

from tests.closed_loop_helpers import contract


class CompletionPriorityTests(unittest.TestCase):
    def _state(self) -> dict:
        return {"working": {"quality_summary": {"missed_priority": 1.0}, "feasibility_summary": {"is_feasible": True}}}

    def test_review_beats_conditions_and_resource(self) -> None:
        c = contract(
            success=[{"condition_id": "S", "source": "working.missed_priority", "op": "<=", "value": 1, "window": 1}],
            failure=[{"condition_id": "F", "source": "aggregate.not_achieved", "op": ">=", "value": 1, "window": 1}],
            max_actions=1,
        )
        progress = ContractProgress("C1", solver_actions=1, intent_status_counts={"not_achieved": 1})
        result = check_contract_completion(c, progress, [{"action": "request_supervisor_review", "dominant_blocker": "solver_requested_review"}], self._state())
        self.assertEqual(result["completion_status"], "solver_requested_review")

    def test_success_and_failure_beat_resource(self) -> None:
        success = contract(success=[{"condition_id": "S", "source": "working.missed_priority", "op": "<=", "value": 1, "window": 1}], max_actions=1)
        progress = ContractProgress("C1", solver_actions=1)
        self.assertEqual(check_contract_completion(success, progress, [{"action": "run_alns"}], self._state())["completion_status"], "success")

        failure = contract(failure=[{"condition_id": "F", "source": "aggregate.not_achieved", "op": ">=", "value": 1, "window": 1}], max_actions=1)
        progress = ContractProgress("C1", solver_actions=1, intent_status_counts={"not_achieved": 1})
        self.assertEqual(check_contract_completion(failure, progress, [{"action": "run_alns"}], self._state())["completion_status"], "failure")

    def test_resource_when_no_review_or_condition(self) -> None:
        result = check_contract_completion(contract(max_actions=1), ContractProgress("C1", solver_actions=1), [{"action": "run_alns"}], self._state())
        self.assertEqual(result["completion_status"], "resource_exhausted")


if __name__ == "__main__":
    unittest.main()
