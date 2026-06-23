from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sar_alloc.config import Budget, Config
from sar_alloc.llm_client import DummyLLMClient
from sar_alloc.llm_orchestrator import run_orchestrator
from sar_alloc.reporting import RunReporter
from sar_alloc.runner import load_instance_from_json, resolve_instance_path
from sar_alloc.schemas import SUPPORTED_CONDITION_SOURCES
from sar_alloc.tools import compile_global_objective, solution_summary


class T100ClosedLoopIntegrationTests(unittest.TestCase):
    def test_scripted_t100_full_loop_and_report(self) -> None:
        instance = load_instance_from_json(resolve_instance_path("T100"))
        config = Config()
        compile_global_objective(
            config,
            {
                "objective_layers": [
                    "missed_priority",
                    "unassigned_count",
                    "energy_total",
                ]
            },
        )
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "result.md"
            reporter = RunReporter(
                result_path,
                {"instance": "T100", "dummy_llm": True},
                use_color=False,
                use_emoji=False,
            )
            solution = run_orchestrator(
                DummyLLMClient(),
                instance,
                "cover",
                config,
                Budget(time_limit_sec=1.0, max_iters=8),
                max_agent_steps=5,
                max_solver_calls=5,
                llm_mode="dummy",
                trace_callback=reporter.on_trace_event,
            )
            reporter.finish(solution, solution_summary(solution, instance, config))
            text = result_path.read_text(encoding="utf-8")
            artifact = solution.run_artifact
            records = artifact["memory"]["verified_actions"]
            self.assertRegex(
                text.split("## Run Config", 1)[0], r"Status: (finished|failed)"
            )
            self.assertNotIn('"lex_key"', text)
            self.assertTrue(records)
            for record in records:
                self.assertTrue(record["trace_id"])
                self.assertEqual(record["trace_id"], record["manifest"]["trace_id"])
                verification = record["verification"]
                keys = verification.get("objective_keys", {})
                if keys:
                    self.assertEqual(
                        len(keys["contract"]["key"]), len(keys["contract"]["layers"])
                    )
                    self.assertEqual(
                        len(keys["global"]["key"]), len(keys["global"]["layers"])
                    )
            events = artifact["trace_events"]
            for event in events:
                if event["event_type"] == "compiled_contract":
                    for group in ("success", "failure"):
                        for condition in event["payload"]["exit_conditions"][group]:
                            self.assertIn(
                                condition["source"], SUPPORTED_CONDITION_SOURCES
                            )
                if event["event_type"] == "contract_completion_check":
                    for condition in event["payload"].get("condition_report", []):
                        self.assertIsNotNone(condition["actual"])
                if event["event_type"] == "solver_result":
                    self.assertEqual(
                        event["payload"]["diagnostics"]["returned_solution_source"],
                        "action_best_feasible",
                    )
            self.assertIn(
                "solver_requested_review", json.dumps(artifact, ensure_ascii=False)
            )


if __name__ == "__main__":
    unittest.main()
