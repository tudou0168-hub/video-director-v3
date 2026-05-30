#!/bin/bash
# Agent session startup — read project memory before proceeding
# Usage: source this script or run: bash scripts/memory/start_agent_session.sh

echo "=========================================="
echo "Video Director V3 — Agent Start Here"
echo "=========================================="
echo ""

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Step 1: Read PROJECT_STATE.md"
echo "---"
cat "$PROJECT_ROOT/docs/status/PROJECT_STATE.md"
echo ""
echo ""

echo "Step 2: Read NEXT_TASK.md"
echo "---"
cat "$PROJECT_ROOT/docs/status/NEXT_TASK.md"
echo ""
echo ""

echo "Step 3: Read CURRENT_BUGS.md"
echo "---"
cat "$PROJECT_ROOT/docs/status/CURRENT_BUGS.md"
echo ""
echo ""

echo "Step 4: Read COMMANDS.md"
echo "---"
cat "$PROJECT_ROOT/docs/runbooks/COMMANDS.md"
echo ""
echo ""

echo "=========================================="
echo "Do not proceed before reading these files."
echo "=========================================="
echo ""
echo "Quick check commands:"
echo "  cd $PROJECT_ROOT"
echo "  source .venv/bin/activate"
echo "  PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -v --tb=short"
echo ""