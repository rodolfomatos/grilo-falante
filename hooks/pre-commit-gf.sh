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

BLOCK_PATTERNS=(
    "\\b(just|simply)\\b.*\\?"
    "\\b(can|could|would|should)\\s+we\\s+(just|simply)\\s"
    "\\bThis\\s+is\\s+(obviously|clearly|trivially)\\s"
    "\\bTrust\\s+me\\b"
    "\\bBelieve\\s+me\\b"
    "^(\\s*\\(?(?:Note|TODO|FIXME|HACK)\\b)"
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

for file in $STAGED; do
    if [ ! -f "$file" ]; then
        continue
    fi

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
