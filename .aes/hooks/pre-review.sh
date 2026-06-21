#!/bin/bash
# AES pre-review hook: require verify with verdict
set -euo pipefail

AES_DIR="$(dirname "$0")/../.."

echo "[pre-review] Verifying verify phase complete..."

VERIFY_FILE=$(ls "$AES_DIR"/aes/tickets/*-verify.md 2>/dev/null || true)
if [ -z "$VERIFY_FILE" ]; then
    echo "[FAIL] No verify file found in aes/tickets/. Run aes-verify first."
    exit 1
fi

BUILD_FILE=$(ls "$AES_DIR"/aes/tickets/*-build.md 2>/dev/null || true)
if [ -z "$BUILD_FILE" ]; then
    echo "[FAIL] No build/diffstory file found. Run aes-build first."
    exit 1
fi

echo "[PASS] Pre-review checks passed."
