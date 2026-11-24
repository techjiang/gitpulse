import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from gitpulse.cli import main

REPO_ROOT = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    def test_cli_runs_on_repository(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main([str(REPO_ROOT), "--top", "1", "--sort", "author"])
        self.assertEqual(code, 0)
        report = stdout.getvalue()
        self.assertIn("# Git activity report:", report)
        self.assertIn("## Contributors", report)
        self.assertIn("## Recent commits", report)
