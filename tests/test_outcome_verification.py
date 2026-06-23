from __future__ import annotations

import unittest

from sar_alloc.outcome_auditor import verify_alns_action, verify_review_request

from tests.closed_loop_helpers import Evaluation, contract


class OutcomeVerificationTests(unittest.TestCase):
    def _verify(self, before: dict, after: dict) -> dict:
        return verify_alns_action(
            before_working_eval=Evaluation(before),
            after_working_eval=Evaluation(after),
            before_best_feasible_eval=None,
            after_action_best_eval=None,
            trace={"trace_id": "X1", "kind": "alns", "trial_flow": {"candidate_trials": 1, "admissible_trials": 1, "accepted_trials": 1}},
            contract=contract(objective=["missed_priority", "energy_total"]),
            manifest={"manifest_id": "R1", "source_decision_id": "D1", "contract_id": "C1", "target_id": "T1"},
        )

    def test_four_contract_outcomes(self) -> None:
        cases = (
            ({"missed_priority": 5, "energy_total": 10}, {"missed_priority": 4, "energy_total": 12}, "achieved"),
            ({"missed_priority": 5, "energy_total": 10}, {"missed_priority": 5, "energy_total": 8}, "partial"),
            ({"missed_priority": 5, "energy_total": 10}, {"missed_priority": 6, "energy_total": 8}, "regressed"),
            ({"missed_priority": 5, "energy_total": 10}, {"missed_priority": 5, "energy_total": 10}, "not_achieved"),
        )
        for before, after, expected in cases:
            with self.subTest(expected=expected):
                result = self._verify(before, after)
                self.assertEqual(result["intent_status"], expected)
                if expected == "regressed":
                    self.assertEqual(result["dominant_blocker"], "objective_regressed")
                if expected == "not_achieved":
                    self.assertEqual(result["dominant_blocker"], "no_quality_gain")

    def test_review_request_is_not_applicable(self) -> None:
        result = verify_review_request(
            {"solver_decision": {"action": "request_supervisor_review", "target_id": "contract_review"}},
            contract(), [], trace_id="X2",
        )
        self.assertEqual(result["intent_status"], "not_applicable")
        self.assertEqual(result["dominant_blocker"], "solver_requested_review")


if __name__ == "__main__":
    unittest.main()
