from __future__ import annotations

import unittest

from sar_alloc.observation import (
    _insertion_position_landscape,
    _state_digest_from_summary,
)


class ObservationStatisticsTests(unittest.TestCase):
    def test_p50_uses_supplied_median_not_average(self) -> None:
        view = _insertion_position_landscape(
            {
                "candidate_stats": {
                    "avg_candidate_positions": 34.0,
                    "candidate_position_percentiles": {
                        "p25": 1.5,
                        "p50": 2.0,
                        "p75": 51.0,
                    },
                    "feasible_position_percentiles": {
                        "p25": 1.0,
                        "p50": 1.5,
                        "p75": 2.0,
                    },
                }
            }
        )
        self.assertEqual(view["candidate_position_count"]["p50"], 2.0)
        self.assertNotEqual(view["candidate_position_count"]["p50"], 34.0)

    def test_zero_debt_has_none_dominant_type(self) -> None:
        digest = _state_digest_from_summary(
            {
                "quality_summary": {},
                "feasibility_summary": {
                    "is_feasible": True,
                    "violation_total": 0.0,
                    "violation_ratio_by_type": {"time_window": 0.0, "energy": 0.0},
                },
            }
        )
        self.assertEqual(digest["debt"]["dominant_type"], "none")
        self.assertEqual(digest["debt"]["dominant_ratio"], 0.0)


if __name__ == "__main__":
    unittest.main()
