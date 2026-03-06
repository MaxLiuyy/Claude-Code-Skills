#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_RELATIVE_DIRS = (
    Path(".agents/lessons"),
    Path(".claude/lessons"),
)
CONFIG_NAMES = ("AGENTS.md", "CLAUDE.md")
DECLARED_PATH_SPLIT_PATTERN = re.compile(r"\s+(?:or|\|)\s+", re.IGNORECASE)

DECLARATION_PATTERNS = (
    re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:LESSONS_DIR|LESSONS_PATH|LESSON_DIR|LESSON_PATH)\s*[:=]\s*([^\n#]+?)\s*$"
    ),
    re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:lessons?\s+(?:dir|path|folder|directory)|save\s+lessons\s+to)\s*[:=]\s*([^\n#]+?)\s*$"
    ),
)

HEADING_PATTERN = re.compile(r"(?m)^\s*#\s+(.+?)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve a lessons directory and write a lesson note."
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace used to search for AGENTS.md or CLAUDE.md and to resolve the fallback path.",
    )
    parser.add_argument(
        "--title",
        help="Optional note title. If omitted, use the first markdown H1 from the content.",
    )
    parser.add_argument(
        "--content-file",
        help="Read markdown content from this file instead of stdin.",
    )
    parser.add_argument(
        "--print-dir",
        action="store_true",
        help="Print the resolved lessons directory and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved output path without writing the file.",
    )
    return parser.parse_args()


def read_content(args: argparse.Namespace) -> str:
    if args.content_file:
        return Path(args.content_file).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise SystemExit(
            "No lesson content provided. Pass --content-file or pipe markdown via stdin."
        )
    return sys.stdin.read()


def candidate_config_files(workspace: Path) -> list[Path]:
    workspace = workspace.resolve()
    candidates: list[Path] = []
    for directory in (workspace, *workspace.parents):
        for name in CONFIG_NAMES:
            path = directory / name
            if path.is_file():
                candidates.append(path)
    return candidates


def clean_declared_path(raw_value: str) -> str:
    return raw_value.strip().strip("`").strip("'").strip('"').strip()


def declared_path_candidates(raw_value: str) -> list[str]:
    cleaned = clean_declared_path(raw_value)
    if not cleaned:
        return []
    parts = [part.strip() for part in DECLARED_PATH_SPLIT_PATTERN.split(cleaned)]
    return [part for part in parts if part]


def resolve_declared_dir(workspace: Path) -> tuple[Path, Path] | None:
    for config_path in candidate_config_files(workspace):
        content = config_path.read_text(encoding="utf-8")
        for pattern in DECLARATION_PATTERNS:
            match = pattern.search(content)
            if not match:
                continue
            declared_paths = declared_path_candidates(match.group(1))
            if not declared_paths:
                continue
            candidates: list[Path] = []
            for declared in declared_paths:
                candidate = Path(declared).expanduser()
                if not candidate.is_absolute():
                    candidate = (config_path.parent / candidate).resolve()
                candidates.append(candidate)
            for candidate in candidates:
                if candidate.exists():
                    return candidate, config_path
            return candidates[0], config_path
    return None


def resolve_default_lessons_dir(workspace: Path) -> Path:
    candidates = [(workspace.resolve() / relative_dir).resolve() for relative_dir in DEFAULT_RELATIVE_DIRS]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def resolve_lessons_dir(workspace: Path) -> tuple[Path, str]:
    resolved = resolve_declared_dir(workspace)
    if resolved is not None:
        directory, source = resolved
        return directory, f"declared in {source}"
    return resolve_default_lessons_dir(workspace), "default fallback"


def derive_title(content: str) -> str | None:
    match = HEADING_PATTERN.search(content)
    if match:
        return match.group(1).strip()
    return None


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "lesson"


def unique_note_path(directory: Path, title: str) -> Path:
    slug = slugify(title)
    base = directory / f"{slug}.md"
    if not base.exists():
        return base
    counter = 2
    while True:
        candidate = directory / f"{slug}-{counter}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    lessons_dir, source = resolve_lessons_dir(workspace)

    if args.print_dir:
        print(lessons_dir)
        return 0

    content = read_content(args)
    title = (args.title or derive_title(content) or "lesson").strip()
    output_path = unique_note_path(lessons_dir, title)

    if args.dry_run:
        print(output_path)
        return 0

    lessons_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(output_path)
    print(source, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
