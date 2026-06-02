#!/usr/bin/env python3
"""Build a lightweight AI-readable repository index.

This script intentionally avoids AST parsing and vector databases. It records
file paths, sizes, coarse file types, and likely roles so agents can orient
quickly before editing the repository.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / ".ai" / "code-index.json"

IGNORED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "test_outputs",
    "review_frames",
    "snapshots",
    "tmp",
    "temp",
    "tests/manual_archive",
}

IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".mp4",
    ".mov",
    ".webm",
    ".log",
    ".tmp",
    ".bak",
    ".DS_Store",
}

LANG_BY_SUFFIX = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".json": "json",
    ".md": "markdown",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".sh": "shell",
    ".html": "html",
    ".css": "css",
}


def is_ignored(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    parts = rel.split("/")

    for ignored in IGNORED_DIRS:
        if rel == ignored or rel.startswith(ignored + "/"):
            return True
        ignored_parts = ignored.split("/")
        if parts[: len(ignored_parts)] == ignored_parts:
            return True

    if path.name in IGNORED_SUFFIXES:
        return True
    return path.suffix in IGNORED_SUFFIXES


def classify_role(rel: str) -> str:
    if rel == "README.md":
        return "human_entrypoint"
    if rel == "AGENTS.md":
        return "agent_rules"
    if rel == "CLAUDE.md":
        return "claude_handoff"
    if rel.startswith(".ai/"):
        return "ai_index"
    if rel.startswith("docs/status/"):
        return "project_state"
    if rel.startswith("docs/runbooks/"):
        return "runbook"
    if rel.startswith("docs/"):
        return "documentation"
    if rel.startswith("src/video_director_v3/pipeline/"):
        return "pipeline"
    if rel.startswith("src/video_director_v3/director/"):
        return "director"
    if rel.startswith("src/video_director_v3/motion/"):
        return "motion"
    if rel.startswith("src/video_director_v3/renderers/"):
        return "renderer"
    if rel.startswith("src/video_director_v3/tts/"):
        return "tts"
    if rel.startswith("src/video_director_v3/design/"):
        return "design"
    if rel.startswith("src/video_director_v3/quality/"):
        return "quality"
    if rel.startswith("src/"):
        return "source"
    if rel.startswith("tests/"):
        return "test"
    if rel.startswith("samples/"):
        return "sample"
    if rel.startswith("scripts/"):
        return "script"
    if rel in {"pyproject.toml", "package.json", "requirements.txt"}:
        return "project_config"
    return "other"


def file_record(path: Path) -> dict[str, Any]:
    rel = path.relative_to(ROOT).as_posix()
    stat = path.stat()
    return {
        "path": rel,
        "size_bytes": stat.st_size,
        "language": LANG_BY_SUFFIX.get(path.suffix, "unknown"),
        "role": classify_role(rel),
    }


def main() -> None:
    records: list[dict[str, Any]] = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        current = Path(dirpath)
        dirnames[:] = [
            name for name in dirnames if not is_ignored(current / name)
        ]

        for filename in filenames:
            path = current / filename
            if is_ignored(path) or not path.is_file():
                continue
            records.append(file_record(path))

    records.sort(key=lambda item: item["path"])

    by_role: dict[str, int] = {}
    by_language: dict[str, int] = {}
    for record in records:
        by_role[record["role"]] = by_role.get(record["role"], 0) + 1
        by_language[record["language"]] = by_language.get(record["language"], 0) + 1

    payload = {
        "project": "video-director-v3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": ".",
        "ignored_dirs": sorted(IGNORED_DIRS),
        "file_count": len(records),
        "summary": {
            "by_role": dict(sorted(by_role.items())),
            "by_language": dict(sorted(by_language.items())),
        },
        "files": records,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(records)} files")


if __name__ == "__main__":
    main()
