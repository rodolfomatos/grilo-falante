#!/bin/bash
# Cognitive Lint pre-commit hook for GF
# Scans staged .md files for epistemic block patterns
# Fails on BLOCK patterns, warns on WARN patterns
set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== GF Cognitive Lint (pre-commit) ==="

STAGED=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.md$' || true)
if [ -z "$STAGED" ]; then
    echo "No staged .md files to lint."
    exit 0
fi

DECISION_PATHS=(
    "^aes/adr/"
    "^aes/sprints/"
    "^aes/tickets/"
    "^aes/premises/"
    "^aes/handoffs/"
    "^docs/TASKS/"
    "^docs/HOSTILE_"
    "^docs/QUALITY_GATES"
)
GOVERNANCE_FILES=()
OTHER_FILES=()
for file in $STAGED; do
    matched=0
    for path in "${DECISION_PATHS[@]}"; do
        if echo "$file" | grep -q -E "$path"; then
            GOVERNANCE_FILES+=("$file")
            matched=1
            break
        fi
    done
    if [ "$matched" -eq 0 ]; then
        OTHER_FILES+=("$file")
    fi
done

BLOCK_PATTERNS=(
    "This is (obviously|clearly|trivially)"
    "\\bTrust\\s+me\\b"
    "\\bBelieve\\s+me\\b"
)

WARN_PATTERNS=(
    "\\b(maybe|perhaps|possibly|probably)\\b"
    "\\bI\\s+think\\b"
    "\\bIt\\s+seems\\b"
    "\\bmight\\s+be\\b"
    "\\bcould\\s+be\\b"
)

HAD_BLOCK=0
HAD_WARN=0

for file in "${GOVERNANCE_FILES[@]}"; do
    if [ ! -f "$file" ]; then continue; fi
    for pattern in "${BLOCK_PATTERNS[@]}"; do
        if grep -q -E "$pattern" "$file" 2>/dev/null; then
            echo -e "${RED}[BLOCK]${NC} $file matches: $pattern"
            HAD_BLOCK=1
        fi
    done
    for pattern in "${WARN_PATTERNS[@]}"; do
        if grep -q -E "$pattern" "$file" 2>/dev/null; then
            echo -e "${YELLOW}[WARN]${NC}  $file matches: $pattern"
            HAD_WARN=1
        fi
    done
done

for file in "${OTHER_FILES[@]}"; do
    if [ ! -f "$file" ]; then continue; fi
    for pattern in "${WARN_PATTERNS[@]}"; do
        if grep -q -E "$pattern" "$file" 2>/dev/null; then
            echo -e "${YELLOW}[WARN]${NC}  $file matches: $pattern"
            HAD_WARN=1
        fi
    done
done

echo "---"
if [ "$HAD_BLOCK" -eq 1 ]; then
    echo -e "${RED}Cognitive lint FAILED: blocking patterns found.${NC}"
    echo "Fix them before committing, or use --no-verify to bypass."
    exit 1
fi

if [ "$HAD_WARN" -eq 1 ]; then
    echo -e "${YELLOW}Cognitive lint passed with warnings.${NC}"
else
    echo "Cognitive lint passed clean."
fi
exit 0
