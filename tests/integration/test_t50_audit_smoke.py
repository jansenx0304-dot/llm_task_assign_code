from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from sar_alloc.runner import main


class T50AuditSmokeTests(unittest.TestCase):
    def test_dummy_t50_writes_only_case_and_chronological_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            main(
                [
                    "--instance",
                    "T50",
                    "--dummy-llm",
                    "--time-limit",
                    "10",
                    "--iterations",
                    "4",
                    "--max-step-calls",
                    "4",
                    "--max-solver-calls",
                    "4",
                    "--output-dir",
                    directory,
                    "--no-color",
                    "--no-emoji",
                ]
            )
            run_dirs = [path for path in Path(directory).iterdir() if path.is_dir()]
            self.assertEqual(len(run_dirs), 1)
            files = {path.name for path in run_dirs[0].iterdir() if path.is_file()}
            self.assertEqual(files, {"case.json", "result.txt"})
            text = (run_dirs[0] / "result.txt").read_text(encoding="utf-8")
            ordered = [
                "SOLVER_OBSERVATION",
                "SOLVER_PROMPT",
                "SOLVER_RAW_OUTPUT",
                "SOLVER_VALIDATION_RESULT",
                "RUNTIME_CONTROL_MANIFEST",
                "EXECUTION_TRACE",
                "OUTCOME_VERIFICATION",
                "MEMORY_UPDATE",
                "CONTRACT_PROGRESS",
                "CONTRACT_COMPLETION_CHECK",
                "FINAL_RESULT",
            ]
            offsets = [text.index(name) for name in ordered]
            self.assertEqual(offsets, sorted(offsets))
            self.assertNotIn("## Final Solution", text)
            self.assertIn("> Status: finished", text.split("## Run Config", 1)[0])

    @unittest.skipUnless(
        os.environ.get("RUN_REAL_API_SMOKE") == "1",
        "set RUN_REAL_API_SMOKE=1 to execute the configured real API smoke",
    )
    def test_real_api_t50_without_dummy_fallback(self) -> None:
        required = ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL")
        if not all(os.environ.get(name) for name in required):
            self.skipTest("real API environment is not configured")
        with tempfile.TemporaryDirectory() as directory:
            main(
                [
                    "--instance",
                    "T50",
                    "--time-limit",
                    "30",
                    "--iterations",
                    "3",
                    "--max-step-calls",
                    "3",
                    "--max-solver-calls",
                    "3",
                    "--output-dir",
                    directory,
                    "--no-color",
                    "--no-emoji",
                ]
            )
            result = next(Path(directory).glob("*/result.txt"))
            text = result.read_text(encoding="utf-8")
            self.assertIn('"llm_mode": "api"', text)
            self.assertNotIn("_FALLBACK", text)
            self.assertIn("> Status: finished", text.split("## Run Config", 1)[0])


if __name__ == "__main__":
    unittest.main()
