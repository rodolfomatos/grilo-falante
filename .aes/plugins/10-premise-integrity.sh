#!/bin/bash
# Plugin: premise integrity check for GF
set -u

plugin_name="10-premise-integrity"
PASS=0
FAIL=0

pass() { PASS=$((PASS+1)); echo "  PASS  $1"; }
fail() { FAIL=$((FAIL+1)); echo "  FAIL  $1"; }

PREMS="aes/premises"
[ ! -d "$PREMS" ] && { echo "  SKIP  no premises directory"; exit 0; }

echo "  ── Premise file validation ──"
for f in "$PREMS"/*.dot; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    if command -v dot &>/dev/null; then
        if dot -Tsvg "$f" -o /dev/null 2>/dev/null; then
            pass "$name: valid DOT syntax"
        else
            fail "$name: invalid DOT syntax"
        fi
    else
        if grep -q '^digraph ' "$f" 2>/dev/null; then
            pass "$name: basic DOT structure valid"
        else
            fail "$name: missing 'digraph' declaration"
        fi
    fi
done

echo "  ── JSON premise validation ──"
for f in "$PREMS"/*.json; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    if python3 -c "
import json, sys
with open('$f') as fh:
    data = json.load(fh)
premises = data.get('premises', data.get('graph', {}).get('premises', []))
edges = data.get('edges', data.get('graph', {}).get('edges', []))
valid_types = {'FOUNDATIONAL', 'ASSUMPTION', 'DERIVED', 'CONSTRAINT'}
errs = []
prem_ids = {p['id'] for p in premises}
for p in premises:
    if p.get('type') not in valid_types:
        errs.append(f\"premise '{p['id']}': invalid type '{p.get('type')}'\")
for e in edges:
    if e.get('from') not in prem_ids:
        errs.append(f\"edge references nonexistent premise '{e.get('from')}'\")
    if e.get('to') not in prem_ids:
        errs.append(f\"edge references nonexistent premise '{e.get('to')}'\")
if errs:
    for e in errs: print(f'  FAIL  $name: {e}')
    sys.exit(1)
" 2>&1; then
        pass "$name: valid JSON structure"
    else
        fail "$name: JSON validation failed"
    fi
done

total=$((PASS + FAIL))
echo ""
echo "  $plugin_name: $PASS passed, $FAIL failed ($total total)"
[ "$FAIL" -gt 0 ] && exit 1
exit 0
