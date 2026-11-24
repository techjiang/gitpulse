import json
import unittest

from gitpulse.collector import Commit, FileStat
from gitpulse.report import build_json, build_markdown


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.commits = [
            Commit("a" * 40, "Alice", "a@b.c", 1700000000, "First commit"),
            Commit("b" * 40, "Alice", "a@b.c", 1700003600, "Second commit"),
            Commit("c" * 40, "Bob", "bob@b.c", 1700007200, "Third commit"),
        ]

    def test_empty_report(self):
        text = build_markdown([], "empty-repo")
        self.assertIn("# Git activity report: empty-repo", text)
        self.assertIn("No commits matched", text)

    def test_summary_and_contributors(self):
        text = build_markdown(self.commits, "demo")
        self.assertIn("- Commits: 3", text)
        self.assertIn("- Contributors: 2", text)
        self.assertIn("| Alice | 2 | 66.7% |", text)
        self.assertIn("| Bob | 1 | 33.3% |", text)

    def test_recent_commit_limit(self):
        text = build_markdown(self.commits, "demo", top=1)
        self.assertIn("`ccccccc` Third commit", text)
        self.assertNotIn("`aaaaaaa`", text)

    def test_file_stats_section(self):
        stats = [FileStat("gitpulse/cli.py", 4), FileStat("README.md", 2)]
        text = build_markdown(self.commits, "demo", file_stats=stats, top_files=1)
        self.assertIn("## Most touched files", text)
        self.assertIn("| `gitpulse/cli.py` | 4 |", text)
        self.assertNotIn("| `README.md` | 2 |", text)

    def test_json_report(self):
        stats = [FileStat("README.md", 1)]
        data = json.loads(build_json(self.commits, "demo", file_stats=stats))
        self.assertEqual(data["repository"], "demo")
        self.assertEqual(data["total_commits"], 3)
        self.assertEqual(data["contributors"][0]["author"], "Alice")
        self.assertEqual(data["files"][0]["path"], "README.md")
        self.assertEqual(len(data["commits"]), 3)

    def test_since_date_window(self):
        text = build_markdown(self.commits, "demo", since_date="2026-01-01")
        self.assertIn("- Window: since 2026-01-01", text)

    def test_sort_contributors_by_author(self):
        commits = [
            Commit("a" * 40, "Zoe", "z@b.c", 1700000000, "Z"),
            Commit("b" * 40, "Zoe", "z@b.c", 1700003600, "Z2"),
            Commit("c" * 40, "Adam", "a@b.c", 1700007200, "A"),
        ]
        text = build_markdown(commits, "demo", sort="author")
        self.assertLess(text.index("| Adam |"), text.index("| Zoe |"))


if __name__ == "__main__":
    unittest.main()
