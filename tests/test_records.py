from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sar_alloc.trace import RunTrace, StepRecord, TraceWriter


class RecordsTest(unittest.TestCase):
    def test_run_trace_recent_views_are_basic(self) -> None:
        run = RunTrace()
        run.add(
            StepRecord(
                step_id="S001",
                phase="step",
                observation_id="O1",
                stage_id="S001",
                decision={"action": "construct_initial"},
                control={"action": "construct_initial", "intent_id": "I1", "runtime_target": {}},
                result={
                    "quality_delta": {"unassigned_count": -1},
                    "before_feasible": False,
                    "after_feasible": True,
                    "protected_passed": True,
                    "after_quality": {"unassigned_count": 0},
                },
                completion={"completed": False, "status": "running", "reason": ""},
            )
        )
        self.assertEqual(run.recent_for_step()[0]["quality_delta"]["unassigned_count"], -1)
        self.assertEqual(run.recent_for_supervisor()[0]["completion"]["status"], "running")

    def test_trace_writer_writes_one_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            step = StepRecord(
                step_id="S001",
                phase="step",
                observation_id="O1",
                stage_id="S001",
            )
            writer = TraceWriter(jsonl_path=root / "trace.jsonl", markdown_path=root / "trace.md", use_console=False)
            writer.write_step(step)
            writer.close()
            lines = (root / "trace.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["step_id"], "S001")
            self.assertIn("Step S001", (root / "trace.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
