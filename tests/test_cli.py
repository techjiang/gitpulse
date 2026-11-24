import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gitpulse.cli import _parser, main
from gitpulse.collector import Commit


class ParserTests(unittest.TestCase):
    def test_defaults(self):
        args = _parser().parse_args([])
        self.assertEqual(args.path, ".")
        self.assertEqual(args.top, 5)
        self.assertIsNone(args.since_days)
        self.assertIsNone(args.output)

    def test_custom_values(self):
        args = _parser().parse_args(["/tmp/repo", "--top", "3", "--since-days", "7"])
        self.assertEqual(args.path, "/tmp/repo")
        self.assertEqual(args.top, 3)
        self.assertEqual(args.since_days, 7)

    def test_format_default_and_override(self):
        self.assertEqual(_parser().parse_args([]).format, "markdown")
        self.assertEqual(_parser().parse_args(["--format", "json"]).format, "json")

    def test_exclude_can_repeat(self):
        args = _parser().parse_args(["--exclude", "docs/", "--exclude", "tests/"])
        self.assertEqual(args.exclude, ["docs/", "tests/"])

    def test_since_date_parsing(self):
        self.assertIsNone(_parser().parse_args([]).since_date)
        self.assertEqual(
            _parser().parse_args(["--since-date", "2026-01-01"]).since_date,
            "2026-01-01"
        )


class MainTests(unittest.TestCase):
    def test_rejects_non_positive_top(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["--top", "0"])
        self.assertEqual(code, 2)
        self.assertIn("--top must be positive", stderr.getvalue())

    def test_rejects_non_positive_top_files(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["--top-files", "0"])
        self.assertEqual(code, 2)
        self.assertIn("--top-files must be positive", stderr.getvalue())

    def test_rejects_invalid_since_date(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["--since-date", "01-01-2026"])
        self.assertEqual(code, 2)
        self.assertIn("--since-date must be YYYY-MM-DD", stderr.getvalue())

    def test_writes_report_to_file(self):
        commit = Commit("a" * 40, "Alice", "a@b.c", 1700000000, "First commit")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.md"
            stdout = io.StringIO()
            with patch("gitpulse.cli.collect_commits", return_value=[commit]), \
                 patch("gitpulse.cli.collect_file_stats", return_value=[]), \
                 redirect_stdout(stdout):
                code = main([".", "--output", str(output)])
            self.assertEqual(code, 0)
            self.assertIn("Wrote report to", stdout.getvalue())
            self.assertIn("# Git activity report", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
