from __future__ import annotations

import unittest

from sar_alloc.outcome_auditor import verify_alns_action

from tests.closed_loop_helpers import Evaluation, contract


class ProtectedMetricVerificationTests(unittest.TestCase):
    def test_violation_overrides_improvement_status_and_tags(self) -> None:
        search_contract = contract(objective=["energy_total"])
        search_contract.protected_metrics = [
            {"metric": "missed_priority", "max_worsen": 0.0}
        ]
        search_contract.protected_metric_baseline = {"missed_priority": 5.0}
        result = verify_alns_action(
            before_working_eval=Evaluation(
                {"missed_priority": 5.0, "energy_total": 10.0}
            ),
            after_working_eval=Evaluation(
                {"missed_priority": 6.0, "energy_total": 8.0}
            ),
            before_best_feasible_eval=None,
            after_action_best_eval=None,
            trace={
                "trace_id": "X1",
                "trial_flow": {
                    "candidate_trials": 1,
                    "admissible_trials": 0,
                    "protected_metric_rejected": 1,
                    "accepted_trials": 0,
                },
            },
            contract=search_contract,
            manifest={"trace_id": "X1"},
        )

        self.assertEqual(result["intent_status"], "regressed")
        self.assertEqual(result["dominant_blocker"], "protected_metric_violated")
        self.assertFalse(result["protected_metric_result"]["passed"])
        self.assertIn("protected_metric_violated", result["event_tags"])
        self.assertNotIn("working_quality_improved", result["event_tags"])
        self.assertFalse(result["improvement_flags"]["working_contract_improved"])
        self.assertFalse(result["improvement_flags"]["run_global_best_improved"])


if __name__ == "__main__":
    unittest.main()
