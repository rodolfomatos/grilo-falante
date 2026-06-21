#!/bin/bash
# AES pre-build hook: block if plan not done, check critical files
set -euo pipefail

AES_DIR="$(dirname "$0")/../.."

echo "[pre-build] Verifying plan phase complete..."

# Check if plan file exists for current ticket
TICKET_FILE=$(ls "$AES_DIR"/aes/tickets/*-plan.md 2>/dev/null || true)
if [ -z "$TICKET_FILE" ]; then
    echo "[FAIL] No plan file found in aes/tickets/. Run aes-plan first."
    exit 1
fi

# Check critical files exist
for f in "$AES_DIR"/docs/VISION.md "$AES_DIR"/docs/REQUIREMENTS.md "$AES_DIR"/docs/ROADMAP.md "$AES_DIR"/docs/HOSTILE_INSIGHTS.md; do
    if [ ! -f "$f" ]; then
        echo "[FAIL] Missing critical file: $f"
        exit 1
    fi
done

echo "[PASS] Pre-build checks passed."
