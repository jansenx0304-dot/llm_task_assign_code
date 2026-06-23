from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sar_alloc.reporting import MarkdownTraceWriter


class ReporterStatusTests(unittest.TestCase):
    def test_finished_rewrites_top_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.md"
            writer = MarkdownTraceWriter(path, {"instance": "T"})
            writer.append_final({"routes": {}}, {"ok": True})
            writer.close()
            text = path.read_text(encoding="utf-8")
            self.assertIn("> Status: finished", text.split("## Run Config", 1)[0])
            self.assertNotIn("> Status: running", text)

    def test_failed_rewrites_top_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.md"
            writer = MarkdownTraceWriter(path, {"instance": "T"})
            writer.append_error(RuntimeError("boom"))
            writer.close()
            text = path.read_text(encoding="utf-8")
            self.assertIn("> Status: failed", text.split("## Run Config", 1)[0])
            self.assertNotIn("> Status: running", text)


if __name__ == "__main__":
    unittest.main()
