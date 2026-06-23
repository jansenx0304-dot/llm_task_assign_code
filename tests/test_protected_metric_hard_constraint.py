from __future__ import annotations

import unittest
from unittest.mock import patch

from sar_alloc.config import Budget
from sar_alloc.operators import (
    DESTROY_OPERATOR_NAMES,
    DESTROY_SIGNAL_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    INSERTION_TASK_SIGNAL_NAMES,
    AcceptancePolicy,
    CompiledALNSPolicy,
    DestroyPolicy,
    InsertionPolicy,
)
from sar_alloc.protected_metrics import ProtectedMetricBound, check_protected_metrics
from sar_alloc.solution import AssignmentSolution
from sar_alloc.tools.assign_solvers import solve_assignment

from tests.closed_loop_helpers import configured, tiny_instance


def _policy() -> CompiledALNSPolicy:
    return CompiledALNSPolicy(
        DestroyPolicy(
            {name: 2 for name in DESTROY_OPERATOR_NAMES},
            {name: 0 for name in DESTROY_SIGNAL_NAMES},
            1,
            0.05,
        ),
        InsertionPolicy(
            {name: 2 for name in INSERTION_OPERATOR_NAMES},
            {name: 0 for name in INSERTION_TASK_SIGNAL_NAMES},
            {name: 0 for name in INSERTION_POSITION_SIGNAL_NAMES},
        ),
        AcceptancePolicy("greedy", 0, 0.0, 0.0),
    )


class ProtectedMetricHardConstraintTests(unittest.TestCase):
    def test_objective_improving_protected_violation_is_rejected(self) -> None:
        instance = tiny_instance()
        initial = AssignmentSolution(routes={0: [1, 2, 3], 1: []}, unassigned=set())
        violating_trial = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2, 3})
        bounds = [ProtectedMetricBound("missed_priority", 0.0, 0.0)]

        with patch(
            "sar_alloc.tools.assign_solvers.run_insertion_kernel",
            return_value=violating_trial,
        ):
            result = solve_assignment(
                instance,
                initial,
                configured(),
                Budget(time_limit_sec=1.0, max_iters=1),
                _policy(),
                contract_objective_layers=[
                    {"metric": "energy_total", "direction": "min"}
                ],
                global_objective_layers=[
                    {"metric": "energy_total", "direction": "min"}
                ],
                feasibility_policy={"mode": "strict"},
                protected_metric_bounds=bounds,
            )

        self.assertEqual(result.accepted_trial_count, 0)
        self.assertEqual(result.rejected_trial_count, 1)
        self.assertEqual(result.final_current.routes, initial.routes)
        self.assertEqual(result.final_current.unassigned, initial.unassigned)
        self.assertEqual(result.working_solution.routes, initial.routes)
        self.assertEqual(result.working_solution.unassigned, initial.unassigned)
        self.assertEqual(result.diagnostics["protected_metric_rejections"], 1)
        self.assertEqual(
            result.diagnostics["protected_metric_rejection_reasons"],
            {"missed_priority": 1},
        )
        iteration = result.diagnostics["iteration_trace"][0]
        self.assertFalse(iteration["protected_metric_passed"])
        self.assertEqual(iteration["rejection_reason"], "protected_metric_violated")
        self.assertEqual(result.trace["trial_flow"]["global_best_improved_trials"], 0)

    def test_protected_passing_improvement_can_be_accepted(self) -> None:
        instance = tiny_instance()
        initial = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2, 3})
        improving_trial = AssignmentSolution(
            routes={0: [1, 2, 3], 1: []}, unassigned=set()
        )
        bounds = [ProtectedMetricBound("energy_total", 3.0, 10.0)]

        with patch(
            "sar_alloc.tools.assign_solvers.run_insertion_kernel",
            return_value=improving_trial,
        ):
            result = solve_assignment(
                instance,
                initial,
                configured(),
                Budget(time_limit_sec=1.0, max_iters=1),
                _policy(),
                contract_objective_layers=[
                    {"metric": "missed_priority", "direction": "min"}
                ],
                feasibility_policy={"mode": "strict"},
                protected_metric_bounds=bounds,
            )

        self.assertEqual(result.accepted_trial_count, 1)
        self.assertEqual(result.diagnostics["protected_metric_rejections"], 0)

    def test_empty_bounds_add_no_automatic_protection(self) -> None:
        self.assertTrue(check_protected_metrics({"missed_priority": 99.0}, []).passed)


if __name__ == "__main__":
    unittest.main()
