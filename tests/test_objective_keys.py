from __future__ import annotations

import json
import random
import unittest

from sar_alloc.evaluator import build_objective_keys, compare_quality
from sar_alloc.tools.assign_solvers import _alns_accept

from tests.closed_loop_helpers import Evaluation


class ObjectiveKeyTests(unittest.TestCase):
    def test_contract_and_global_key_lengths_are_explicit(self) -> None:
        ev = Evaluation(
            {"missed_priority": 5.0, "unassigned_count": 2.0, "energy_total": 9.0}
        )
        keys = build_objective_keys(
            ev,
            [
                {"metric": "missed_priority", "direction": "min"},
                {"metric": "unassigned_count", "direction": "min"},
                {"metric": "energy_total", "direction": "min"},
            ],
            [
                {"metric": "missed_priority", "direction": "min"},
                {"metric": "energy_total", "direction": "min"},
            ],
        )
        self.assertEqual(len(keys["contract"]["key"]), 3)
        self.assertEqual(len(keys["global"]["key"]), 2)
        self.assertNotIn('"lex_key"', json.dumps(keys))

    def test_acceptance_uses_contract_and_global_comparison_uses_global(self) -> None:
        current = Evaluation(
            {"missed_priority": 5.0, "energy_total": 10.0, "route_balance": 1.0}
        )
        trial = Evaluation(
            {"missed_priority": 5.0, "energy_total": 8.0, "route_balance": 2.0}
        )
        contract_layers = [{"metric": "route_balance", "direction": "min"}]
        global_layers = [{"metric": "energy_total", "direction": "min"}]
        decision = _alns_accept(
            current,
            trial,
            contract_layers,
            "greedy",
            random.Random(0),
            1.0,
            0.0,
            True,
            "working",
            "ok",
        )
        self.assertFalse(decision.accepted)
        self.assertLess(compare_quality(trial, current, global_layers), 0)


if __name__ == "__main__":
    unittest.main()
