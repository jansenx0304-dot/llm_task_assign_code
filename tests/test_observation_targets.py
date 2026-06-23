from __future__ import annotations

import unittest

from sar_alloc.observation import build_solver_observation
from sar_alloc.llm_public_interface import build_public_candidates
from sar_alloc.operators.insertion import build_insertion_landscape
from sar_alloc.solution import AssignmentSolution
from sar_alloc.tools import solution_summary

from tests.closed_loop_helpers import configured, contract, tiny_instance


class ObservationTargetTests(unittest.TestCase):
    def _observation(self, solution: AssignmentSolution) -> dict:
        instance = tiny_instance()
        config = configured()
        landscape = build_insertion_landscape(solution, instance, config)
        return build_solver_observation(
            active_contract={**contract().as_dict(), "contract_type": "initial_construction"},
            contract_progress={},
            remaining_contract_resources={"actions": 1, "iters": 1, "time_sec": 1.0},
            working_summary=solution_summary(solution, instance, config),
            candidate_landscape=landscape,
            candidates=build_public_candidates(instance, config),
        )

    def test_empty_scarce_bucket_is_not_selectable(self) -> None:
        solution = AssignmentSolution(routes={0: [1], 1: [2]}, unassigned=set())
        observation = self._observation(solution)
        self.assertNotIn("T_scarce_unassigned", {item["target_id"] for item in observation["decision_targets"]})

    def test_scarce_mass_is_bucket_mass_and_initial_has_no_destroy_recommendation(self) -> None:
        solution = AssignmentSolution(routes={0: [], 1: []}, unassigned={1, 2, 3})
        observation = self._observation(solution)
        scarce = next(item for item in observation["task_buildability_view"]["target_buckets"] if item["target_id"] == "T_scarce_unassigned")
        instance = tiny_instance()
        expected = sum(instance.task_by_id(tid).priority for tid in scarce["task_ids"])
        self.assertEqual(scarce["priority_mass"], expected)
        self.assertNotIn("destroy_control.signal_scores", scarce["recommended_controls"])


if __name__ == "__main__":
    unittest.main()
