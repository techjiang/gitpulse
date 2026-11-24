"""Collect commit data from a local Git repository."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

FIELD_SEP = "\x1f"
DATE_FORMAT = "%Y-%m-%d"


@dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    email: str
    timestamp: int
    subject: str

    @property
    def date(self) -> str:
        return datetime.fromtimestamp(self.timestamp, tz=timezone.utc).strftime(DATE_FORMAT)

    @property
    def short_sha(self) -> str:
        return self.sha[:7]


def parse_log(text: str) -> list[Commit]:
    """Parse the output produced by git log --pretty=format:..."""
    commits: list[Commit] = []
    for line in text.splitlines():
        parts = line.split(FIELD_SEP)
        if len(parts) != 5:
            continue
        sha, author, email, raw_ts, subject = parts
        try:
            commits.append(Commit(sha, author, email, int(raw_ts), subject))
        except ValueError:
            continue
    return commits


def repo_name(path: Path) -> str:
    """Return a human-friendly repository name."""
    resolved = path.resolve()
    if resolved.name:
        return resolved.name
    return str(resolved)


def collect_commits(
    path: Path,
    *,
    since_days: int | None = None,
    author: str | None = None,
    limit: int | None = None,
) -> list[Commit]:
    """Run git log and return parsed commits, newest first."""
    cmd = [
        "git",
        "-C",
        str(path),
        "log",
        "--no-merges",
        f"--pretty=format:%H{FIELD_SEP}%aN{FIELD_SEP}%ae{FIELD_SEP}%at{FIELD_SEP}%s",
    ]
    if since_days is not None:
        if since_days <= 0:
            raise ValueError("since_days must be positive")
        cmd.append(f"--since={since_days} days ago")
    if author:
        cmd.append(f"--author={author}")
    if limit is not None:
        if limit <= 0:
            raise ValueError("limit must be positive")
        cmd.append(f"-n{limit}")

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return parse_log(result.stdout)
