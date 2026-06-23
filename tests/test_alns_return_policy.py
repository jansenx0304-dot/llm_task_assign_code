from __future__ import annotations

import unittest

from sar_alloc.config import Budget
from sar_alloc.evaluator import compare_quality, evaluate
from sar_alloc.operators import (
    AcceptancePolicy,
    CompiledALNSPolicy,
    DestroyPolicy,
    InsertionPolicy,
    DESTROY_OPERATOR_NAMES,
    DESTROY_SIGNAL_NAMES,
    INSERTION_OPERATOR_NAMES,
    INSERTION_POSITION_SIGNAL_NAMES,
    INSERTION_TASK_SIGNAL_NAMES,
)
from sar_alloc.solution import AssignmentSolution
from sar_alloc.tools.assign_solvers import solve_assignment

from tests.closed_loop_helpers import configured, tiny_instance


class AlnsReturnPolicyTests(unittest.TestCase):
    def test_returns_action_best_and_tracks_global_candidate(self) -> None:
        instance = tiny_instance()
        config = configured()
        initial = AssignmentSolution(routes={0: [1, 2, 3], 1: []}, unassigned=set())
        policy = CompiledALNSPolicy(
            DestroyPolicy(
                {name: 2 for name in DESTROY_OPERATOR_NAMES},
                {name: 0 for name in DESTROY_SIGNAL_NAMES},
                3,
                0.14,
            ),
            InsertionPolicy(
                {name: 2 for name in INSERTION_OPERATOR_NAMES},
                {name: 0 for name in INSERTION_TASK_SIGNAL_NAMES},
                {name: 0 for name in INSERTION_POSITION_SIGNAL_NAMES},
            ),
            AcceptancePolicy("sa", 8, 0.4, 8.0),
        )
        contract_layers = [
            {"metric": "missed_priority", "direction": "min"},
            {"metric": "energy_total", "direction": "min"},
        ]
        global_layers = [{"metric": "energy_total", "direction": "min"}]
        result = solve_assignment(
            instance,
            initial,
            config,
            Budget(time_limit_sec=0.1, max_iters=8),
            policy,
            contract_objective_layers=contract_layers,
            global_objective_layers=global_layers,
            feasibility_policy={"mode": "strict"},
            trace_id="X1",
        )
        self.assertEqual(
            result.diagnostics["returned_solution_source"], "action_best_feasible"
        )
        self.assertIsNotNone(result.action_best_feasible)
        self.assertIsNotNone(result.global_best_feasible)
        working_eval = evaluate(result.working_solution, instance, config)
        best_eval = evaluate(result.action_best_feasible, instance, config)  # type: ignore[arg-type]
        final_eval = evaluate(result.final_current, instance, config)
        self.assertEqual(compare_quality(working_eval, best_eval, contract_layers), 0)
        self.assertLessEqual(compare_quality(best_eval, final_eval, contract_layers), 0)
        self.assertEqual(
            result.diagnostics["solution_flow"]["returned_solution_source"],
            "action_best_feasible",
        )


if __name__ == "__main__":
    unittest.main()
