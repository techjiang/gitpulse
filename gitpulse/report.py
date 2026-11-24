"""Render commit data as Markdown."""

from __future__ import annotations

from collections import Counter
import json

from .collector import Commit, FileStat


def _percentage(count: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{count / total * 100:.1f}%"


def build_markdown(
    commits: list[Commit],
    repository: str,
    *,
    since_days: int | None = None,
    since_date: str | None = None,
    top: int = 5,
    file_stats: list[FileStat] | None = None,
    top_files: int = 5,
) -> str:
    """Build a Markdown activity report."""
    lines = [f"# Git activity report: {repository}", ""]

    if not commits:
        lines.append("No commits matched the requested filters.")
        return "\n".join(lines) + "\n"

    total = len(commits)
    counts = Counter(commit.author for commit in commits)
    first_date = min(commit.date for commit in commits)
    last_date = max(commit.date for commit in commits)

    lines.append(f"- Commits: {total}")
    lines.append(f"- Contributors: {len(counts)}")
    if since_date:
        lines.append(f"- Window: since {since_date}")
    elif since_days is not None:
        lines.append(f"- Window: last {since_days} days")
    else:
        lines.append(f"- Window: {first_date} to {last_date}")
    lines.append("")

    lines.append("## Contributors")
    lines.append("")
    lines.append("| Author | Commits | Share |")
    lines.append("| --- | ---: | ---: |")
    for author, count in counts.most_common():
        lines.append(f"| {author} | {count} | {_percentage(count, total)} |")
    lines.append("")

    if file_stats:
        lines.append("## Most touched files")
        lines.append("")
        lines.append("| File | Commits |")
        lines.append("| --- | ---: |")
        for stat in file_stats[:top_files]:
            lines.append(f"| `{stat.path}` | {stat.commits} |")
        lines.append("")

    lines.append("## Recent commits")
    lines.append("")
    recent = sorted(commits, key=lambda commit: commit.timestamp, reverse=True)
    for commit in recent[:top]:
        lines.append(f"- `{commit.short_sha}` {commit.subject} — {commit.author} ({commit.date})")
    lines.append("")

    return "\n".join(lines)


def build_json(
    commits: list[Commit],
    repository: str,
    *,
    file_stats: list[FileStat] | None = None,
    top_files: int = 5,
) -> str:
    """Build a machine-readable JSON report."""
    counts = Counter(commit.author for commit in commits)
    data = {
        "repository": repository,
        "total_commits": len(commits),
        "contributors": [
            {"author": author, "commits": count}
            for author, count in counts.most_common()
        ],
        "files": [
            {"path": stat.path, "commits": stat.commits}
            for stat in (file_stats or [])[:top_files]
        ],
        "commits": [
            {
                "sha": commit.sha,
                "short_sha": commit.short_sha,
                "author": commit.author,
                "email": commit.email,
                "timestamp": commit.timestamp,
                "date": commit.date,
                "subject": commit.subject,
            }
            for commit in commits
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
