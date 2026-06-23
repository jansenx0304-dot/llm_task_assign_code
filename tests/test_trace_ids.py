from __future__ import annotations

import unittest

from sar_alloc.config import Budget
from sar_alloc.llm_client import DummyLLMClient
from sar_alloc.llm_orchestrator import run_orchestrator

from tests.closed_loop_helpers import configured, tiny_instance


class TraceIdTests(unittest.TestCase):
    def test_manifest_trace_verification_memory_share_nonempty_id(self) -> None:
        solution = run_orchestrator(
            DummyLLMClient(),
            tiny_instance(),
            "cover",
            configured(),
            Budget(time_limit_sec=0.2, max_iters=5),
            max_agent_steps=4,
            max_solver_calls=4,
            llm_mode="dummy",
        )
        records = solution.run_artifact["memory"]["verified_actions"]
        self.assertTrue(records)
        for record in records:
            ids = {
                record["trace_id"],
                record["manifest"]["trace_id"],
                record["trace"]["trace_id"],
                record["verification"]["trace_id"],
            }
            self.assertEqual(len(ids), 1)
            self.assertTrue(next(iter(ids)))


if __name__ == "__main__":
    unittest.main()
