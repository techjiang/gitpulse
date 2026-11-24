import unittest

from gitpulse.collector import FIELD_SEP, Commit, parse_log


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


if __name__ == "__main__":
    unittest.main()
