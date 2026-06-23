from __future__ import annotations

import unittest

from sar_alloc.memory import RunMemory


class MemoryFingerprintTests(unittest.TestCase):
    def _record(self, action: str = "run_alns") -> dict:
        memory = RunMemory()
        observation = {"observation_id": "O1", "decision_targets": [{"target_id": "T1", "kind": "unassigned_priority"}]}
        decision = {"solver_decision": {"action": action, "target_id": "T1"}}
        manifest = {
            "manifest_id": "R1", "source_decision_id": "D1", "contract_id": "C1", "target_id": "T1", "action": action, "trace_id": "X1",
            "compiled": {
                "destroy": {"operator_weights": {"random": 2, "worst": 8}, "signal_weights": {"scarcity_protection": 0, "mobility_opportunity": 7}},
                "insertion": {"operator_weights": {"greedy": 2, "regret": 6}, "task_signal_weights": {"priority_loss": 9, "scarcity_pressure": 8, "zero": 0}, "position_signal_weights": {"future_slack": 7, "insert_cost": 5}},
                "acceptance": {"mode": "sa", "intensity_score": 4},
            } if action == "run_alns" else {"review_request": {"requested": True}},
        }
        trace = {"trace_id": "X1", "trial_flow": {}}
        verification = {"trace_id": "X1", "intent_status": "not_achieved", "dominant_blocker": "no_quality_gain", "metric_delta": {}, "trace": trace}
        return memory.record_verified_action(observation, decision, manifest, trace, verification)

    def test_fingerprint_uses_sorted_nonzero_compiled_weights(self) -> None:
        fingerprint = self._record()["control_fingerprint"]
        self.assertEqual(fingerprint["destroy_signal_top"], ["mobility_opportunity"])
        self.assertEqual(fingerprint["insertion_task_signal_top"], ["priority_loss", "scarcity_pressure"])
        self.assertEqual(fingerprint["insertion_position_signal_top"], ["future_slack", "insert_cost"])
        self.assertNotIn("zero", str(fingerprint))

    def test_review_does_not_fabricate_controls(self) -> None:
        self.assertEqual(self._record("request_supervisor_review")["control_fingerprint"], {"action": "review_request"})


if __name__ == "__main__":
    unittest.main()
