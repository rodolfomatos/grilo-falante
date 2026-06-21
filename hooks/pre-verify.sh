#!/bin/bash
# Pre-verify hook for GF
# Confirms build phase is complete before verification starts
set -euo pipefail

echo "Running pre-verify checks..."

if [ ! -f "aes/kanban.md" ]; then
    echo "Error: Not in an AES project (missing aes/kanban.md)"
    exit 1
fi

CURRENT_TICKET=$(grep "current_ticket:" aes/kanban.md | awk '{print $2}' | head -1)
if [ -z "$CURRENT_TICKET" ]; then
    echo "Error: No current_ticket found in aes/kanban.md"
    exit 1
fi

BUILD_FILE="aes/tickets/${CURRENT_TICKET}-build.md"
if [ ! -f "$BUILD_FILE" ]; then
    echo "Error: Build file not found: $BUILD_FILE"
    echo "Please run '/aes-build' before verifying."
    exit 1
fi

if ! grep -q "status: done" "$BUILD_FILE"; then
    echo "Error: Build phase not complete (status != done) in $BUILD_FILE"
    exit 1
fi

echo "Pre-verify checks passed."
exit 0
