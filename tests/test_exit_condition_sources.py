from __future__ import annotations

import unittest

from sar_alloc.contract_monitor import (
    check_contract_completion,
    resolve_condition_source,
)
from sar_alloc.policy_validator import _exit_conditions
from sar_alloc.schemas import SUPPORTED_CONDITION_SOURCES
from sar_alloc.tools import ContractProgress

from tests.closed_loop_helpers import contract


class ExitConditionSourceTests(unittest.TestCase):
    def test_legacy_sources_are_rejected(self) -> None:
        for source in ("missed_priority", "total_actions"):
            with self.subTest(source=source), self.assertRaisesRegex(
                ValueError, "source is not allowed"
            ):
                _exit_conditions(
                    {
                        "success": [
                            {
                                "condition_id": "S",
                                "source": source,
                                "op": ">",
                                "value": 0,
                                "window": 1,
                            }
                        ],
                        "failure": [],
                    }
                )

    def test_supported_sources_resolve_real_values(self) -> None:
        progress = ContractProgress(
            "C1",
            solver_actions=3,
            iters_used=7,
            time_used_sec=1.5,
            intent_status_counts={
                "achieved": 1,
                "partial": 2,
                "not_achieved": 3,
                "regressed": 4,
            },
            dominant_blocker_counts={"solver_requested_review": 1},
        )
        state = {
            "working": {
                "quality_summary": {
                    name: float(index)
                    for index, name in enumerate(
                        (
                            "missed_priority",
                            "unassigned_count",
                            "energy_total",
                            "total_distance",
                            "makespan",
                            "route_balance",
                        ),
                        1,
                    )
                },
                "feasibility_summary": {"is_feasible": True},
            },
            "best_feasible": {
                "quality_summary": {
                    name: float(index)
                    for index, name in enumerate(
                        (
                            "missed_priority",
                            "unassigned_count",
                            "energy_total",
                            "total_distance",
                            "makespan",
                            "route_balance",
                        ),
                        11,
                    )
                },
                "feasibility_summary": {"is_feasible": True},
            },
        }
        last = {
            "intent_status": "partial",
            "dominant_blocker": "none",
            "improvement_flags": {"run_global_best_improved": True},
        }
        self.assertEqual(
            resolve_condition_source("progress.solver_actions", progress, state), 3
        )
        self.assertEqual(
            resolve_condition_source("best_feasible.missed_priority", progress, state),
            11.0,
        )
        for source in SUPPORTED_CONDITION_SOURCES:
            with self.subTest(source=source):
                self.assertIsNotNone(
                    resolve_condition_source(source, progress, state, last)
                )

    def test_condition_report_actual_is_not_null(self) -> None:
        condition = {
            "condition_id": "S",
            "source": "working.missed_priority",
            "op": "<=",
            "value": 5,
            "window": 1,
        }
        progress = ContractProgress("C1", solver_actions=1)
        result = check_contract_completion(
            contract(success=[condition]),
            progress,
            [
                {
                    "action": "run_alns",
                    "intent_status": "achieved",
                    "dominant_blocker": "none",
                }
            ],
            {
                "working": {
                    "quality_summary": {"missed_priority": 4.0},
                    "feasibility_summary": {"is_feasible": True},
                }
            },
        )
        self.assertEqual(result["condition_report"][0]["actual"], 4.0)


if __name__ == "__main__":
    unittest.main()
