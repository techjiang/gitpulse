import unittest
from pathlib import Path
from unittest.mock import patch

from gitpulse.collector import FIELD_SEP, Commit, collect_commits, collect_file_stats, parse_file_stats, parse_log


class ParseLogTests(unittest.TestCase):
    def test_parses_valid_lines(self):
        text = (
            f"abc1234{FIELD_SEP}Alice{FIELD_SEP}alice@example.com{FIELD_SEP}1700000000{FIELD_SEP}First commit\n"
            f"def5678{FIELD_SEP}Bob{FIELD_SEP}bob@example.com{FIELD_SEP}1700003600{FIELD_SEP}Second commit\n"
        )
        commits = parse_log(text)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].short_sha, "abc1234")
        self.assertEqual(commits[0].author, "Alice")
        self.assertEqual(commits[1].subject, "Second commit")

    def test_ignores_malformed_lines(self):
        text = f"bad-line\nvalid{FIELD_SEP}Alice{FIELD_SEP}a@b.c{FIELD_SEP}oops{FIELD_SEP}Subject\n"
        self.assertEqual(parse_log(text), [])

    def test_date_is_utc(self):
        commit = Commit("a" * 40, "Alice", "a@b.c", 0, "Epoch")
        self.assertEqual(commit.date, "1970-01-01")


class ParseFileStatsTests(unittest.TestCase):
    def test_counts_and_sorts_paths(self):
        text = "a.py\nb.py\n\na.py\nc.py\na.py\n"
        stats = parse_file_stats(text)
        self.assertEqual(stats[0].path, "a.py")
        self.assertEqual(stats[0].commits, 3)
        self.assertEqual(stats[1].path, "b.py")
        self.assertEqual(stats[2].path, "c.py")
        self.assertEqual(stats[2].commits, 1)


class CollectCommandTests(unittest.TestCase):
    @patch("gitpulse.collector.subprocess.run")
    def test_excludes_merges_by_default(self, run):
        run.return_value.stdout = ""
        collect_commits(Path("."))
        self.assertIn("--no-merges", run.call_args.args[0])

    @patch("gitpulse.collector.subprocess.run")
    def test_can_include_merges(self, run):
        run.return_value.stdout = ""
        collect_commits(Path("."), include_merges=True)
        self.assertNotIn("--no-merges", run.call_args.args[0])

    @patch("gitpulse.collector.subprocess.run")
    def test_file_stats_exclude(self, run):
        run.return_value.stdout = "src/main.py\ndocs/readme.md\n"
        stats = collect_file_stats(Path("."), exclude=("docs/",))
        self.assertEqual([stat.path for stat in stats], ["src/main.py"])

    @patch("gitpulse.collector.subprocess.run")
    def test_since_date_is_forwarded(self, run):
        run.return_value.stdout = ""
        collect_commits(Path("."), since="2026-01-01")
        self.assertIn("--since=2026-01-01", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
