"""Command-line interface for gitpulse."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .collector import collect_commits, collect_file_stats, repo_name
from .report import build_json, build_markdown


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitpulse",
        description="Generate a Markdown activity report from a local Git repository.",
    )
    parser.add_argument("path", nargs="?", default=".", help="repository path (default: .)")
    parser.add_argument("--since-days", type=int, help="only include commits from the last N days")
    parser.add_argument("--author", help="only include commits by this author (git --author pattern)")
    parser.add_argument("--top", type=int, default=5, help="number of recent commits to list")
    parser.add_argument("--top-files", type=int, default=5, help="number of most touched files to list")
    parser.add_argument("--include-merges", action="store_true", help="include merge commits in the report")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="output format")
    parser.add_argument("--output", type=Path, help="write the report to this file instead of stdout")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    path = Path(args.path)

    if args.top <= 0:
        print("gitpulse: --top must be positive", file=sys.stderr)
        return 2
    if args.top_files <= 0:
        print("gitpulse: --top-files must be positive", file=sys.stderr)
        return 2
    if args.since_days is not None and args.since_days <= 0:
        print("gitpulse: --since-days must be positive", file=sys.stderr)
        return 2

    try:
        commits = collect_commits(
            path,
            since_days=args.since_days,
            author=args.author,
            include_merges=args.include_merges,
        )
        file_stats = collect_file_stats(
            path,
            since_days=args.since_days,
            author=args.author,
            include_merges=args.include_merges,
        )
    except (OSError, ValueError) as exc:
        print(f"gitpulse: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # subprocess.CalledProcessError
        print(f"gitpulse: failed to read git history: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        report = build_json(
            commits,
            repo_name(path),
            file_stats=file_stats,
            top_files=args.top_files,
        )
    else:
        report = build_markdown(
            commits,
            repo_name(path),
            since_days=args.since_days,
            top=args.top,
            file_stats=file_stats,
            top_files=args.top_files,
        )

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote report to {args.output}")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
