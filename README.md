# gitpulse

`gitpulse` turns any local Git repository into a compact Markdown activity report. It has no third-party dependencies, works offline, and is useful for weekly digests, contributor summaries, and release notes.

## Features

- Counts commits in a date range and groups them by author.
- Shows the most active contributors and their share of total commits.
- Lists the latest commits with short messages.
- Ranks the most frequently touched files.
- Writes to stdout or a Markdown file.
- Requires only Python 3.9+ and Git.

## Install

```bash
python -m pip install -e .
```

Or run directly from a checkout:

```bash
python -m gitpulse /path/to/repo
```

## Usage

```bash
# Print a report for the current repository
gitpulse .

# Last 30 days, written to a file
gitpulse . --since-days 30 --output report.md

# Only one contributor, top 10 recent commits
gitpulse . --author alice --top 10

# Include merge commits (excluded by default)
gitpulse . --include-merges

# Show the top 10 most touched files
gitpulse . --top-files 10
```

Example output:

```markdown
# Git activity report: my-project

- Commits: 42
- Contributors: 3
- Range: last 30 days

| Author | Commits | Share |
| --- | ---: | ---: |
| Alice | 20 | 47.6% |
| Bob | 15 | 35.7% |

## Recent commits

- `a1b2c3d` Fix parser edge case — Alice
```

## Development

```bash
python -m unittest discover -s tests -v
```

CI runs the same tests on Python 3.9, 3.10, 3.11, and 3.12.

## License

MIT — see [LICENSE](LICENSE).
