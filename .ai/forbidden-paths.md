# Ignored and Protected Paths

This file records paths that agents should not treat as source-code entrypoints and should not commit unless explicitly instructed.

## Dependency and build directories

- `node_modules/`
- `.venv/`
- `dist/`
- `build/`
- `.pytest_cache/`
- `__pycache__/`
- `.mypy_cache/`
- `.ruff_cache/`

## Generated video and review artifacts

- `outputs/`
- `test_outputs/`
- `review_frames/`
- `snapshots/`
- `rendered/`
- `rendered_smoke/`
- `frames/`
- `*.mp4`
- `*.mov`
- `*.webm`

## Temporary and local files

- `tmp/`
- `temp/`
- `.DS_Store`
- `*.log`
- `*.tmp`
- `*.bak`

## Manual archive

- `tests/manual_archive/`

This archive can be useful for history, but it should not be the first place an agent reads when trying to understand the active production path.

## Rule

Generated artifacts may be referenced in reports, but should not be added to source control unless the user explicitly asks for that artifact to be committed.
