#!/bin/bash
# GitHub Upload Safety Scanner for video-director-v3
# Exits 0 if safe to upload, non-zero if issues found

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ISSUES=0

echo "=========================================="
echo "GitHub Upload Safety Scanner"
echo "=========================================="
echo ""

# ── Check 1: Secret keywords in code ────────────────────────────────────────
echo "─── Check 1: Secret keywords ─────────────"
SECRETS=$(rg -n --hidden \
  --glob '!outputs/**' \
  --glob '!test_outputs/**' \
  --glob '!.venv/**' \
  --glob '!.git/**' \
  --glob '!__pycache__/**' \
  --glob '!.pytest_cache/**' \
  --glob '!node_modules/**' \
  'sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|xox[bpas]-[a-zA-Z0-9-]{20,}' \
  . 2>/dev/null | grep -v '.pyc' || true)

if [ -n "$SECRETS" ]; then
  echo -e "${RED}FAIL: Hardcoded secrets found:${NC}"
  echo "$SECRETS" | while read -r line; do
    # Redact secret, show only path:line
    REDACTED=$(echo "$line" | sed -E 's/(sk-|ghp_|xox[bpas]-)[a-zA-Z0-9_-]{10,}[a-zA-Z0-9_-]*/\1****/g')
    echo "  $REDACTED"
  done
  ISSUES=$((ISSUES + 1))
else
  echo -e "${GREEN}PASS: No hardcoded secrets found${NC}"
fi
echo ""

# ── Check 2: Media files in git ───────────────────────────────────────────────
echo "─── Check 2: Media files tracked by git ───"
MEDIA_TRACKED=$(git ls-files 2>/dev/null | grep -E '\.(mp4|mp3|wav|aiff|m4a|aac|mov|avi|mkv|webm|png|jpg|jpeg|webp|gif)$' || true)
if [ -n "$MEDIA_TRACKED" ]; then
  echo -e "${RED}FAIL: Media files tracked by git:${NC}"
  echo "$MEDIA_TRACKED" | head -20
  ISSUES=$((ISSUES + 1))
else
  echo -e "${GREEN}PASS: No media files tracked by git${NC}"
fi
echo ""

# ── Check 3: outputs/test_outputs in git ─────────────────────────────────────
echo "─── Check 3: outputs/test_outputs in git ──"
OUTPUTS_TRACKED=$(git ls-files 2>/dev/null | grep -E '^outputs/|^test_outputs/' || true)
if [ -n "$OUTPUTS_TRACKED" ]; then
  echo -e "${RED}FAIL: outputs/ or test_outputs/ tracked by git:${NC}"
  echo "$OUTPUTS_TRACKED" | head -20
  ISSUES=$((ISSUES + 1))
else
  echo -e "${GREEN}PASS: No outputs/test_outputs tracked by git${NC}"
fi
echo ""

# ── Check 4: .env in git ──────────────────────────────────────────────────────
echo "─── Check 4: .env files in git ─────────────"
ENV_TRACKED=$(git ls-files 2>/dev/null | grep -E '^\.env$' || true)
if [ -n "$ENV_TRACKED" ]; then
  echo -e "${RED}FAIL: .env file tracked by git:${NC}"
  echo "$ENV_TRACKED"
  ISSUES=$((ISSUES + 1))
else
  echo -e "${GREEN}PASS: No .env file tracked by git${NC}"
fi
echo ""

# ── Check 5: Private paths in public files ────────────────────────────────
echo "─── Check 5: Private paths in public files ─"
PRIVATE_PATHS=$(rg -n --hidden \
  --glob '!outputs/**' \
  --glob '!test_outputs/**' \
  --glob '!.venv/**' \
  --glob '!.git/**' \
  --glob '!__pycache__/**' \
  --glob '!.pytest_cache/**' \
  --glob '!node_modules/**' \
  --glob '!scripts/security_scan.sh' \
  --glob '!docs/status/GITHUB_UPLOAD_SAFETY_REPORT.md' \
  '/Users/muzi|tudou0168|dou.tu' \
  . 2>/dev/null | grep -v '.pyc' || true)

if [ -n "$PRIVATE_PATHS" ]; then
  echo -e "${RED}FAIL: Private/local paths found in public files:${NC}"
  echo "$PRIVATE_PATHS" | head -20
  ISSUES=$((ISSUES + 1))
else
  echo -e "${GREEN}PASS: No private paths in public files${NC}"
fi
echo ""

# ── Check 6: Key/credential files present ─────────────────────────────────────
echo "─── Check 6: Key/credential files present ──"
KEY_FILES=$(find . -type f \( -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.p8" -o -name "id_rsa" -o -name "id_ed25519" \) ! -path './.git/*' ! -path './.venv/*' ! -path './outputs/*' ! -path './test_outputs/*' 2>/dev/null | sort)
if [ -n "$KEY_FILES" ]; then
  echo -e "${RED}FAIL: Key/credential files present:${NC}"
  echo "$KEY_FILES" | head -20
  ISSUES=$((ISSUES + 1))
else
  echo -e "${GREEN}PASS: No key/credential files present${NC}"
fi
echo ""

# ── Check 7: gitleaks / trufflehog ───────────────────────────────────────────
echo "─── Check 7: Secret scanners ───────────────"
if command -v gitleaks &>/dev/null; then
  echo "Running gitleaks..."
  GITLEAKS_RESULT=$(gitleaks detect --source . --no-git --redact 2>&1 || true)
  if [ -n "$GITLEAKS_RESULT" ]; then
    echo -e "${YELLOW}WARN: gitleaks findings:${NC}"
    echo "$GITLEAKS_RESULT" | head -20
  else
    echo -e "${GREEN}PASS: gitleaks clean${NC}"
  fi
else
  echo -e "${YELLOW}SKIP: gitleaks not installed${NC}"
fi

if command -v trufflehog &>/dev/null; then
  echo "Running trufflehog..."
  TRUFFLEHOG_RESULT=$(trufflehog filesystem . --no-update 2>&1 | head -20 || true)
  if [ -n "$TRUFFLEHOG_RESULT" ]; then
    echo -e "${YELLOW}WARN: trufflehog findings:${NC}"
    echo "$TRUFFLEHOG_RESULT" | head -20
  else
    echo -e "${GREEN}PASS: trufflehog clean${NC}"
  fi
else
  echo -e "${YELLOW}SKIP: trufflehog not installed${NC}"
fi
echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
echo "=========================================="
if [ $ISSUES -gt 0 ]; then
  echo -e "${RED}RESULT: FAIL — $ISSUES blocking issue(s)${NC}"
  echo "Must fix before uploading to GitHub"
  exit 1
else
  echo -e "${GREEN}RESULT: PASS — No blocking issues${NC}"
  echo "Ready for git add + commit"
  exit 0
fi