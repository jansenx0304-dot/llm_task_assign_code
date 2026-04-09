import unittest

from sar_alloc.config import Budget
from sar_alloc.llm_orchestrator import BudgetState


class BudgetAccountingTests(unittest.TestCase):
    def test_solver_usage_consumes_actual_usage_not_granted_budget(self) -> None:
        state = BudgetState.from_budget(Budget(time_limit_sec=5.0, max_iters=100), max_solver_calls=3)

        slice_budget, granted_budget = state.clamp_request(
            {"time_limit_sec": 5.0, "max_iters": 100},
            {"time_limit_sec": 1.0, "max_iters": 60},
        )

        self.assertEqual(slice_budget.max_iters, 100)
        self.assertEqual(slice_budget.time_limit_sec, 5.0)
        self.assertEqual(granted_budget["max_iters"], 100)
        self.assertEqual(granted_budget["time_limit_sec"], 5.0)

        state.consume_solver_usage(actual_iters_used=12, actual_time_used_sec=0.3, solver_calls=1)

        self.assertEqual(state.used["solver_calls"], 1.0)
        self.assertEqual(state.used["max_iters"], 12.0)
        self.assertAlmostEqual(state.used["time_limit_sec"], 0.3, places=6)
        self.assertEqual(state.remaining["solver_calls"], 2.0)
        self.assertEqual(state.remaining["max_iters"], 88.0)
        self.assertAlmostEqual(state.remaining["time_limit_sec"], 4.7, places=6)

    def test_remaining_budget_is_clamped_at_zero(self) -> None:
        state = BudgetState.from_budget(Budget(time_limit_sec=0.25, max_iters=10), max_solver_calls=1)

        state.consume_solver_usage(actual_iters_used=12, actual_time_used_sec=0.3, solver_calls=1)

        self.assertEqual(state.remaining["solver_calls"], 0.0)
        self.assertEqual(state.remaining["max_iters"], 0.0)
        self.assertEqual(state.remaining["time_limit_sec"], 0.0)


if __name__ == "__main__":
    unittest.main()
