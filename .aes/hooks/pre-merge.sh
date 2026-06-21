#!/bin/bash
# AES pre-merge hook: check diff size, forbidden files, all phases complete
set -euo pipefail

AES_DIR="$(dirname "$0")/../.."

echo "[pre-merge] Running final quality gates..."

# Check all phase files exist
for phase in plan build verify review learn; do
    PHASE_FILE=$(ls "$AES_DIR"/aes/tickets/*-$phase.md 2>/dev/null || true)
    if [ -z "$PHASE_FILE" ]; then
        echo "[FAIL] Missing $phase output in aes/tickets/"
        exit 1
    fi
done

# Check diff size (warn if > 500 lines)
CHANGED=$(cd "$AES_DIR" && git diff --stat HEAD 2>/dev/null | tail -1 | grep -oE '[0-9]+' | tail -1 || echo "0")
if [ "$CHANGED" -gt 500 ]; then
    echo "[WARN] Large diff: $CHANGED lines. Consider splitting into smaller PRs."
fi

# Forbidden patterns
if grep -rn "console\.log\|debugger\|TODO\|FIXME" "$AES_DIR/grilo_falante/" "$AES_DIR/app/" --include="*.py" 2>/dev/null | grep -v ".pyc"; then
    echo "[FAIL] Found debug statements or TODOs in source code."
    exit 1
fi

echo "[PASS] Pre-merge checks passed."
