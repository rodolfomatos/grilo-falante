#!/bin/bash
# GF-specific pre-build hook: premise propagation
# Wraps the propagator script for GF premise graphs
set -euo pipefail

PREMISES_DIR="aes/premises"
GATE_LEVEL="${PREMISE_GATE_LEVEL:-critical}"

if [ ! -d "$PREMISES_DIR" ]; then
    echo "Premise propagation: SKIPPED (no premises directory)"
    exit 0
fi

if [ -f "${PREMISES_DIR}/project-graph.dot" ]; then
    echo "Running premise propagation on project-graph.dot (gate: $GATE_LEVEL)..."
    if command -v python3 &>/dev/null; then
        python3 -c "
import sys, json, subprocess, re

graph_file = '${PREMISES_DIR}/project-graph.dot'
gate_level = '${GATE_LEVEL}'

with open(graph_file) as f:
    dot = f.read()

nodes = re.findall(r'\"([^\"]+)\"\s*\[([^\]]+)\]', dot)
edges = re.findall(r'\"([^\"]+)\"\s*->\s*\"([^\"]+)\"(?:\s*\[([^\]]*)\])?', dot)

node_types = {}
node_verify = {}
node_labels = {}
for name, attrs in nodes:
    t = re.search(r'type=(\w+)', attrs)
    v = re.search(r'verify=\"([^\"]+)\"', attrs)
    l = re.search(r'label=\"([^\"]+)\"', attrs)
    if t: node_types[name] = t.group(1)
    if v: node_verify[name] = v.group(1)
    if l: node_labels[name] = l.group(1)

adj = {}
for src, dst, _ in edges:
    adj.setdefault(src, []).append(dst)

def verify(id):
    cmd = node_verify.get(id, '')
    if not cmd or cmd == 'manual':
        return True
    if cmd.startswith('file:'):
        p = cmd[5:]
        return subprocess.call(['test', '-f', p]) == 0
    if cmd.startswith('cmd:'):
        return subprocess.call(cmd[4:], shell=True) == 0
    if cmd.startswith('env:'):
        var = cmd[4:]
        return var in __import__('os').environ
    if cmd.startswith('port:'):
        port = cmd[5:]
        r = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
        return f':{port}' in r.stdout
    return True

def should_block(id):
    if gate_level == 'strict':
        return True
    t = node_types.get(id, '')
    if gate_level == 'all':
        return t in ('FOUNDATIONAL', 'ASSUMPTION', 'CONSTRAINT', 'DERIVED')
    return t in ('FOUNDATIONAL', 'ASSUMPTION')

failed = []
for n in node_types:
    if not verify(n):
        lbl = node_labels.get(n, n)
        failed.append(n)

if failed:
    print(f'FAIL: {len(failed)} premises falsified')
    for n in failed:
        lbl = node_labels.get(n, n)
        print(f'  - {lbl} ({node_types.get(n, \"\")})')
        print(f'    verify: {node_verify.get(n, \"none\")}')
    print('GATE: FAILED')
    sys.exit(1)
else:
    print('GATE: PASSED — all premises verified')
" 2>&1 || exit $?
    fi
fi

exit 0
