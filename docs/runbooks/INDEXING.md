# Repository Indexing Runbook

This runbook explains how to refresh the lightweight AI-readable repository index.

## Purpose

The repository index helps Claude Code, Codex, ChatGPT, and other agents understand the project before editing files.

It is intentionally lightweight:

- Markdown handoff docs
- YAML repository map
- JSON file inventory
- No vector database
- No new service
- No new runtime dependency

## Core index files

| File | Purpose |
|---|---|
| `AGENTS.md` | Global agent rules |
| `CLAUDE.md` | Claude Code startup and reporting rules |
| `docs/START_HERE.md` | Human and agent orientation entrypoint |
| `.ai/repo-index.yml` | Machine-readable project map |
| `.ai/code-index.json` | Generated file inventory |
| `.ai/agent-rules.md` | Expanded agent behavior guide |
| `.ai/forbidden-paths.md` | Generated and low-priority paths |
| `docs/pipeline/MAINLINE.md` | Canonical production flow |
| `docs/architecture/SYSTEM_MAP.md` | Compact module map |

## Refresh code index

From the repository root:

```bash
python3 scripts/index/build_repo_index.py
```

Expected output:

```text
Wrote .ai/code-index.json with <N> files
```

Then inspect the diff:

```bash
git diff -- .ai/code-index.json
```

## When to refresh

Refresh `.ai/code-index.json` after:

- Adding or removing source directories
- Adding major docs
- Moving pipeline modules
- Cleaning historical files
- Updating agent entrypoints

## Validation

```bash
python3 scripts/index/build_repo_index.py
python3 -m json.tool .ai/code-index.json >/tmp/code-index-check.json
```

## Agent startup prompt

Use this when starting a new coding session:

```text
先读取 AGENTS.md、CLAUDE.md、docs/START_HERE.md、.ai/repo-index.yml、.ai/code-index.json、docs/status/PROJECT_STATE.md、docs/pipeline/MAINLINE.md、docs/runbooks/COMMANDS.md。
然后说明当前主线、当前阶段、本次任务影响文件、不能触碰的机制、验证方式，再执行。
```
