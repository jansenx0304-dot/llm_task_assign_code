from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sar_alloc.reporting import MarkdownTraceWriter


class SmokeRefactorTests(unittest.TestCase):
    def test_markdown_writer_flushes_events_before_close(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.md"
            writer = MarkdownTraceWriter(path, {"instance": "T50"})
            writer.append_event({
                "index": 1,
                "event_type": "supervisor_kickoff_prompt",
                "payload_type": "text",
                "payload": "prompt body",
                "step_index": None,
                "contract_id": None,
            })
            report = path.read_text(encoding="utf-8")
            self.assertIn("# LLM-ALNS Execution Report", report)
            self.assertIn("SUPERVISOR_KICKOFF_PROMPT", report)
            self.assertIn("prompt body", report)
            self.assertIn("<details>", report)
            writer.close()

    def test_markdown_writer_preserves_traceback_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.md"
            writer = MarkdownTraceWriter(path, {"instance": "T50"})
            writer.append_event({
                "index": 1,
                "event_type": "run_start",
                "payload_type": "json",
                "payload": {},
                "step_index": None,
                "contract_id": None,
            })
            try:
                raise RuntimeError("report failure test")
            except RuntimeError as exc:
                writer.append_error(exc)
            writer.close()
            report = path.read_text(encoding="utf-8")
            self.assertIn("RUN_START", report)
            self.assertIn("## Runtime Error", report)
            self.assertIn("RuntimeError: report failure test", report)
            self.assertIn("> Status: failed", report)

    def test_dummy_result_execution_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [
                    sys.executable, "-B", "-m", "sar_alloc.runner",
                    "--instance", "T50", "--time-limit", "0.03", "--iterations", "3",
                    "--max-step-calls", "6", "--max-solver-calls", "4",
                    "--seed", "0", "--dummy-llm", "--no-color", "--no-emoji", "--output-dir", tmp,
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=120,
                check=True,
            )
            self.assertIn("RUN_START", proc.stdout)
            self.assertIn("FINAL", proc.stdout)
            self.assertNotIn("\033[", proc.stdout)
            run_dirs = [path for path in Path(tmp).iterdir() if path.is_dir()]
            self.assertEqual(len(run_dirs), 1)
            self.assertEqual({path.name for path in run_dirs[0].iterdir()}, {"case.json", "result.md"})
            report = (run_dirs[0] / "result.md").read_text(encoding="utf-8")
            self.assertIn("# LLM-ALNS Execution Report", report)
            self.assertIn("## Run Config", report)
            self.assertIn("## Live Timeline", report)
            self.assertIn("## Final Summary", report)
            self.assertIn("<details>", report)
            self.assertIn("> Status: finished", report)

            forbidden = (
                "OBJECTIVE_OBSERVATION",
                "INITIAL_OBSERVATION",
                "OBJECTIVE_PROMPT",
                "INITIAL_PROMPT",
            )
            for value in forbidden:
                self.assertNotIn(value, report)

            ordered = [
                "SUPERVISOR_KICKOFF_OBSERVATION",
                "SUPERVISOR_KICKOFF_VALIDATED_PAYLOAD",
                "GLOBAL_OBJECTIVE_APPLIED",
                "COMPILED_CONTRACT",
                "SOLVER_OBSERVATION",
                "COMPILED_INITIAL_POLICY",
                "INITIAL_INSERTION_RESULT",
                "CONTRACT_COMPLETION_CHECK",
                "SUPERVISOR_REVIEW_OBSERVATION",
                "COMPILED_SOLVER_POLICY",
                "SOLVER_RESULT",
                "FINAL_RESULT",
            ]
            indices = [report.index(value) for value in ordered]
            self.assertEqual(indices, sorted(indices))

            alns_contract = None
            for chunk in report.split("COMPILED_CONTRACT"):
                if '"contract_type": "alns_search"' in chunk:
                    alns_contract = chunk
                    break
            self.assertIsNotNone(alns_contract)
            self.assertIn('"min_solver_actions": 3', report)
            self.assertIn('"max_solver_actions": 3', report)
            self.assertGreaterEqual(report.count('"action": "run_alns"'), 3)


if __name__ == "__main__":
    unittest.main()
