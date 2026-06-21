"""
grilo CLI — AES–GF bridge for premise validation, cognitive linting,
GMIF classification, and system health.

Entry point declared in pyproject.toml as:
    grilo = "grilo_falante.cli:main"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

VALID_NODE_TYPES = {"FOUNDATIONAL", "ASSUMPTION", "DERIVED", "CONSTRAINT"}
VALID_EDGE_RELATIONS = {"DEPENDS_ON", "SUPPORTS", "CONTRADICTS", "CONSTRAINS"}


class ImportProxy:
    """Lazy module import with graceful degradation."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._modules = {}

    def _import(self, import_path: str):
        if import_path in self._modules:
            return self._modules[import_path]
        try:
            parts = import_path.split(".")
            module_path = ".".join(parts[:-1])
            attr_name = parts[-1]
            if module_path:
                mod = __import__(module_path, fromlist=[attr_name])
                obj = getattr(mod, attr_name)
            else:
                obj = __import__(attr_name)
            self._modules[import_path] = obj
            return obj
        except ImportError as e:
            if self.verbose:
                print(f"DEBUG: Failed to import {import_path}: {e}", file=sys.stderr)
            return None

    @property
    def TransitionValidator(self):
        return self._import("grilo_falante.regime.validate.TransitionValidator")

    @property
    def StateMachine(self):
        return self._import("grilo_falante.regime.state.StateMachine")

    @property
    def CognitiveLint(self):
        return self._import("grilo_falante.backend.services.lint.CognitiveLint")

    @property
    def LintResult(self):
        return self._import("grilo_falante.backend.services.lint.LintResult")

    @property
    def LintState(self):
        return self._import("grilo_falante.backend.services.lint.LintState")

    @property
    def GMIFClassifier(self):
        return self._import("grilo_falante.backend.services.gmif.GMIFClassifier")

    @property
    def GMIFLevel(self):
        return self._import("grilo_falante.models.GMIFLevel")


# ── Module health registry ────────────────────────────────────────────────────

MODULES = {
    "TransitionValidator": "grilo_falante.regime.validate.TransitionValidator",
    "StateMachine": "grilo_falante.regime.state.StateMachine",
    "CognitiveLint": "grilo_falante.backend.services.lint.CognitiveLint",
    "LintResult": "grilo_falante.backend.services.lint.LintResult",
    "LintState": "grilo_falante.backend.services.lint.LintState",
    "GMIFClassifier": "grilo_falante.backend.services.gmif.GMIFClassifier",
    "GMIFLevel": "grilo_falante.models.GMIFLevel",
}

# ── DOT parser ────────────────────────────────────────────────────────────────


def parse_dot(filepath: str) -> dict:
    """Parse a DOT premise graph file.

    Returns:
        dict with keys: graph_id, name, nodes (list of str), edges (list of (str,str)),
        node_types (dict[str,str]), edge_labels (dict[(str,str),str])
    """
    text = Path(filepath).read_text(encoding="utf-8")

    # Strip comments (// to end of line)
    text = re.sub(r"//.*$", "", text, flags=re.MULTILINE)

    graph_name_match = re.search(r"digraph\s+(\w+)", text)
    if not graph_name_match:
        raise ValueError("No 'digraph' declaration found")
    graph_id = graph_name_match.group(1)

    # Extract node declarations: "id" [ ... type=TYPE ... ]
    node_ids = []
    node_types = {}
    node_pattern = re.compile(r'^\s*"([^"]+)"\s*\[', re.MULTILINE)
    for m in node_pattern.finditer(text):
        nid = m.group(1)
        node_ids.append(nid)
        # Find type= in the node's [...] block
        block_start = m.end()
        # Find matching close bracket (naively: find next unmatched ])
        bracket_depth = 1
        block_end = block_start
        for i in range(block_start, len(text)):
            if text[i] == "[":
                bracket_depth += 1
            elif text[i] == "]":
                bracket_depth -= 1
                if bracket_depth == 0:
                    block_end = i
                    break
        block_text = text[block_start:block_end]
        type_match = re.search(r"\btype=(\w+)", block_text)
        if type_match:
            node_types[nid] = type_match.group(1)

    # Extract edge definitions: "src" -> "dst" [label=RELATION]
    edges = []
    edge_labels = {}
    edge_pattern = re.compile(r'"([^"]+)"\s*->\s*"([^"]+)"')
    for m in edge_pattern.finditer(text):
        src, dst = m.group(1), m.group(2)
        edges.append((src, dst))
        # Find label= after this match on the same line
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        if line_end == -1:
            line_end = len(text)
        line_text = text[line_start:line_end]
        label_match = re.search(r"label=(\w+)", line_text)
        if label_match:
            edge_labels[(src, dst)] = label_match.group(1)

    return {
        "graph_id": graph_id,
        "name": graph_id,
        "nodes": node_ids,
        "edges": edges,
        "node_types": node_types,
        "edge_labels": edge_labels,
    }


# ── Subcommand: validate-dot ──────────────────────────────────────────────────


def cmd_validate_dot(args: argparse.Namespace) -> int:
    """Validate a DOT premise graph file."""
    imp = ImportProxy(verbose=args.verbose)
    filepath = args.graph

    if not os.path.isfile(filepath):
        result = {"valid": False, "error": f"File not found: {filepath}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"  FAIL  File not found: {filepath}")
        return 2

    try:
        graph = parse_dot(filepath)
    except ValueError as e:
        result = {"valid": False, "error": str(e)}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"  FAIL  {e}")
        return 2
    except Exception as e:
        result = {"valid": False, "error": f"Parse error: {e}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"  FAIL  Parse error: {e}")
        return 2

    errors = []
    warnings = []

    # Validate node types
    for nid, ntype in graph["node_types"].items():
        if ntype not in VALID_NODE_TYPES:
            errors.append(f"Node '{nid}': invalid type '{ntype}' (must be one of {sorted(VALID_NODE_TYPES)})")

    # Validate edge labels
    for (src, dst), label in graph["edge_labels"].items():
        if label not in VALID_EDGE_RELATIONS:
            errors.append(f"Edge '{src}' -> '{dst}': invalid relation '{label}' (must be one of {sorted(VALID_EDGE_RELATIONS)})")

    # Check orphan references (edge targets that are not declared nodes)
    declared = set(graph["nodes"])
    for src, dst in graph["edges"]:
        if src not in declared:
            warnings.append(f"Edge references undeclared node '{src}'")
        if dst not in declared:
            warnings.append(f"Edge references undeclared node '{dst}'")

    # Register with TransitionValidator if available
    registered = False
    tv_cls = imp.TransitionValidator
    sm_cls = imp.StateMachine
    if tv_cls and sm_cls:
        try:
            sm = sm_cls()
            tv = tv_cls(sm)
            tv.register_graph(
                graph["graph_id"],
                graph["name"],
                graph["nodes"],
                graph["edges"],
            )
            registered = True
        except Exception as e:
            warnings.append(f"Failed to register graph with TransitionValidator: {e}")

    valid = len(errors) == 0
    name = os.path.basename(filepath)

    if args.json:
        output = {
            "file": filepath,
            "graph_id": graph["graph_id"],
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "registered": registered,
        }
        print(json.dumps(output, indent=2))
    else:
        status = "valid" if valid else "INVALID"
        print(f"  {name}: {status} ({len(graph['nodes'])} nodes, {len(graph['edges'])} edges)")
        if registered:
            print(f"         Registered with TransitionValidator")
        for e in errors:
            print(f"  ERROR  {e}")
        for w in warnings:
            print(f"  WARN   {w}")

    return 0 if valid else 1


# ── Subcommand: lint-text ────────────────────────────────────────────────────


def cmd_lint_text(args: argparse.Namespace) -> int:
    """Run CognitiveLint on text from file or stdin."""
    imp = ImportProxy(verbose=args.verbose)

    lint_cls = imp.CognitiveLint
    if lint_cls is None:
        msg = "CognitiveLint module not available"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"  FAIL  {msg}")
        return 2

    try:
        if args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()
    except Exception as e:
        result = {"error": f"Failed to read input: {e}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"  FAIL  {e}")
        return 2

    try:
        lint = lint_cls()
        result = lint.lint(text)
    except Exception as e:
        result = {"error": f"Lint failed: {e}"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"  FAIL  {e}")
        return 2

    if args.json:
        print(json.dumps({
            "state": result.state.value,
            "message": result.message,
            "issues": result.issues,
        }, indent=2))
    else:
        prefix = {"accept": "ACCEPT", "warn": "WARN", "reject": "REJECT"}
        print(f"  {prefix.get(result.state.value, result.state.value)}  {result.message}")
        for issue in result.issues:
            print(f"         Issue: {issue}")

    return {"accept": 0, "warn": 1, "reject": 1}.get(result.state.value, 1)


# ── Subcommand: classify ─────────────────────────────────────────────────────


def cmd_classify(args: argparse.Namespace) -> int:
    """Run GMIF classification on text."""
    imp = ImportProxy(verbose=args.verbose)

    cls_cls = imp.GMIFClassifier
    if cls_cls is None:
        msg = "GMIFClassifier module not available"
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(f"  FAIL  {msg}")
        return 1

    try:
        if args.text:
            text = args.text
        elif args.file:
            text = Path(args.file).read_text(encoding="utf-8")
        else:
            if args.json:
                print(json.dumps({"error": "No input provided; use --text or --file"}))
            else:
                print("  FAIL  No input provided; use --text or --file")
            return 1
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"  FAIL  {e}")
        return 1

    try:
        level, confidence = cls_cls.classify(text, source_count=args.sources or 1)
    except Exception as e:
        if args.json:
            print(json.dumps({"error": f"Classification failed: {e}"}))
        else:
            print(f"  FAIL  Classification failed: {e}")
        return 1

    if args.json:
        print(json.dumps({
            "level": level.value,
            "confidence": confidence,
        }, indent=2))
    else:
        print(f"  Level:      {level.value}")
        print(f"  Confidence: {confidence:.2f}")

    return 0


# ── Subcommand: status ────────────────────────────────────────────────────────


def cmd_status(args: argparse.Namespace) -> int:
    """Check that all required modules can be imported."""
    imp = ImportProxy(verbose=args.verbose)

    results = {}
    all_ok = True

    for name, import_path in MODULES.items():
        obj = imp._import(import_path)
        ok = obj is not None
        results[name] = {"importable": ok, "module": import_path}
        if not ok:
            all_ok = False

    if args.json:
        print(json.dumps({"status": "ok" if all_ok else "issues_found", "modules": results}, indent=2))
    else:
        for name, info in results.items():
            icon = "OK" if info["importable"] else "FAIL"
            print(f"  {icon}  {name}")
        print("")
        if all_ok:
            print("  All modules importable")
        else:
            print("  Some modules failed to import")

    return 0 if all_ok else 1


# ── Subcommand: check-epistemic ──────────────────────────────────────────────


def _extract_premise_text(graph: dict, dot_text: str) -> list[dict]:
    """Extract premise descriptions from node labels for linting/classification."""
    premises = []
    for nid in graph["nodes"]:
        desc = None
        ntype = graph.get("node_types", {}).get(nid, "UNKNOWN")
        label_match = re.search(
            rf'"{re.escape(nid)}"\s*\[[^\]]*?label="([^"]*)"',
            dot_text,
        )
        if label_match:
            desc = label_match.group(1)
        premises.append({
            "id": nid,
            "type": ntype,
            "description": desc or "(no description)",
        })
    return premises


def _check_graph_consistency(graph: dict) -> list[str]:
    """Check epistemic consistency of a premise graph.

    Rules:
    - DERIVED nodes must have at least one incoming edge
    - FOUNDATIONAL nodes must have at least one outgoing edge
    - No self-referencing edges
    """
    issues = []
    incoming = {n: 0 for n in graph["nodes"]}
    outgoing = {n: 0 for n in graph["nodes"]}
    for src, dst in graph["edges"]:
        if src == dst:
            issues.append(f"Self-referencing edge: '{src}' -> '{dst}'")
        if src in incoming:
            incoming[dst] = incoming.get(dst, 0) + 1
            outgoing[src] = outgoing.get(src, 0) + 1

    for nid, ntype in graph.get("node_types", {}).items():
        if ntype == "DERIVED" and incoming.get(nid, 0) == 0:
            issues.append(f"DERIVED node '{nid}' has no incoming edges (nothing supports it)")
        if ntype == "FOUNDATIONAL" and outgoing.get(nid, 0) == 0:
            issues.append(f"FOUNDATIONAL node '{nid}' has no outgoing edges (no dependency depends on it)")

    return issues


def _run_epistemic_on_graph(
    filepath: str,
    imp: ImportProxy,
    verbose: bool = False,
) -> dict:
    """Run full epistemic validation on a single DOT graph file.

    Returns a dict with all checks aggregated.
    """
    name = os.path.basename(filepath)
    result = {
        "file": filepath,
        "name": name,
        "valid": True,
        "dot_valid": True,
        "dot_errors": [],
        "dot_warnings": [],
        "consistency_issues": [],
        "lint_results": [],
        "classify_results": [],
        "nodes": 0,
        "edges": 0,
        "graph_id": None,
    }

    if not os.path.isfile(filepath):
        result["valid"] = False
        result["dot_errors"].append("File not found")
        return result

    dot_text = Path(filepath).read_text(encoding="utf-8")

    try:
        graph = parse_dot(filepath)
    except ValueError as e:
        result["valid"] = False
        result["dot_valid"] = False
        result["dot_errors"].append(str(e))
        return result
    except Exception as e:
        result["valid"] = False
        result["dot_valid"] = False
        result["dot_errors"].append(f"Parse error: {e}")
        return result

    result["graph_id"] = graph["graph_id"]
    result["nodes"] = len(graph["nodes"])
    result["edges"] = len(graph["edges"])

    # DOT validation
    for nid, ntype in graph["node_types"].items():
        if ntype not in VALID_NODE_TYPES:
            result["dot_errors"].append(
                f"Node '{nid}': invalid type '{ntype}'"
            )
    for (src, dst), label in graph["edge_labels"].items():
        if label not in VALID_EDGE_RELATIONS:
            result["dot_errors"].append(
                f"Edge '{src}' -> '{dst}': invalid relation '{label}'"
            )
    declared = set(graph["nodes"])
    for src, dst in graph["edges"]:
        if src not in declared:
            result["dot_warnings"].append(f"Edge references undeclared node '{src}'")
        if dst not in declared:
            result["dot_warnings"].append(f"Edge references undeclared node '{dst}'")

    if result["dot_errors"]:
        result["valid"] = False

    # Register with TransitionValidator
    tv_cls = imp.TransitionValidator
    sm_cls = imp.StateMachine
    if tv_cls and sm_cls:
        try:
            sm = sm_cls()
            tv = tv_cls(sm)
            tv.register_graph(graph["graph_id"], graph["name"], graph["nodes"], graph["edges"])
        except Exception as e:
            result["dot_warnings"].append(f"TransitionValidator register failed: {e}")

    # Graph consistency checks
    result["consistency_issues"] = _check_graph_consistency(graph)
    if result["consistency_issues"]:
        result["valid"] = False

    # Extract premise descriptions for lint + classify
    premises = _extract_premise_text(graph, dot_text)

    # CognitiveLint on each premise description
    lint_cls = imp.CognitiveLint
    if lint_cls:
        try:
            lint = lint_cls()
            for prem in premises:
                lr = lint.lint(prem["description"])
                entry = {
                    "node_id": prem["id"],
                    "node_type": prem["type"],
                    "description": prem["description"],
                    "state": lr.state.value,
                    "message": lr.message,
                    "issues": lr.issues,
                }
                result["lint_results"].append(entry)
                if lr.state.value in ("reject", "warn"):
                    result["valid"] = False
        except Exception as e:
            result["dot_warnings"].append(f"CognitiveLint failed: {e}")

    # GMIF classification on each premise description
    cls_cls = imp.GMIFClassifier
    if cls_cls:
        try:
            for prem in premises:
                level, confidence = cls_cls.classify(prem["description"])
                entry = {
                    "node_id": prem["id"],
                    "node_type": prem["type"],
                    "description": prem["description"],
                    "level": level.value if hasattr(level, "value") else str(level),
                    "confidence": round(confidence, 2),
                }
                result["classify_results"].append(entry)
        except Exception as e:
            result["dot_warnings"].append(f"GMIF classification failed: {e}")

    return result


def cmd_check_epistemic(args: argparse.Namespace) -> int:
    """Run full epistemic validation on all premise graphs."""
    imp = ImportProxy(verbose=args.verbose)

    files = []
    if args.graph:
        files.append(args.graph)
    if args.dir:
        d = Path(args.dir)
        if d.is_dir():
            files.extend(str(f) for f in sorted(d.glob("*.dot")))
        else:
            print(f"  FAIL  Directory not found: {args.dir}")
            return 2

    if not files:
        print("  FAIL  No graph files to check (use --graph or --dir)")
        return 2

    all_results = []
    overall_valid = True
    total_errors = 0
    total_warnings = 0

    for fp in files:
        res = _run_epistemic_on_graph(fp, imp, verbose=args.verbose)
        all_results.append(res)
        if not res["valid"]:
            overall_valid = False
        total_errors += len(res["dot_errors"]) + len(res["consistency_issues"])
        rej = [l for l in res["lint_results"] if l["state"] == "reject"]
        total_errors += len(rej)
        war = len(res["dot_warnings"])
        warn_lint = [l for l in res["lint_results"] if l["state"] == "warn"]
        total_warnings += war + len(warn_lint)

    summary = {
        "overall_valid": overall_valid,
        "files_checked": len(files),
        "files_valid": sum(1 for r in all_results if r["valid"]),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "results": all_results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"\n  ═══ Epistemic Quality Report ═══\n")
        for res in all_results:
            status = "VALID" if res["valid"] else "INVALID"
            print(f"  [{status}] {res['name']} ({res['nodes']} nodes, {res['edges']} edges)")
            for e in res["dot_errors"]:
                print(f"    ERROR  {e}")
            for w in res["dot_warnings"]:
                print(f"    WARN   {w}")
            for c in res["consistency_issues"]:
                print(f"    ERROR  {c}")
            for lr in res["lint_results"]:
                if lr["state"] != "accept":
                    tag = lr["state"].upper()
                    print(f"    {tag}   [{lr['node_id']}] {lr['message']}")
                    for iss in lr["issues"]:
                        print(f"           {iss}")
            if res["classify_results"]:
                weak = [c for c in res["classify_results"] if c["level"] in ("M3", "M4", "M5", "M6", "M7", "M8")]
                if weak:
                    print(f"    NOTE   GMIF quality levels (M3+ may indicate weak premises):")
                    for c in weak:
                        print(f"           [{c['node_id']}] {c['level']} ({c['confidence']:.2f}) — {c['description'][:60]}")
            print("")
        print(f"  Files: {summary['files_valid']}/{summary['files_checked']} valid")
        print(f"  Errors: {total_errors}, Warnings: {total_warnings}")
        print("")

    return 0 if overall_valid else 1


# ── Argument parser ───────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grilo",
        description="AES–GF CLI bridge: premise validation, cognitive lint, GMIF classification, health.",
    )
    parser.add_argument("--verbose", action="store_true", help="Show debug information")
    sub = parser.add_subparsers(dest="command", required=True)

    # validate-dot
    p_dot = sub.add_parser("validate-dot", help="Validate a DOT premise graph file")
    p_dot.add_argument("--graph", required=True, help="Path to .dot file")
    p_dot.add_argument("--json", action="store_true", help="JSON output")
    p_dot.set_defaults(func=cmd_validate_dot)

    # lint-text
    p_lint = sub.add_parser("lint-text", help="Run CognitiveLint on text")
    p_lint.add_argument("--file", type=str, default=None, help="Path to file (reads stdin if omitted)")
    p_lint.add_argument("--json", action="store_true", help="JSON output")
    p_lint.set_defaults(func=cmd_lint_text)

    # classify
    p_cls = sub.add_parser("classify", help="Run GMIF classification on text")
    p_cls.add_argument("--text", type=str, default=None, help="Text to classify")
    p_cls.add_argument("--file", type=str, default=None, help="Path to file with text")
    p_cls.add_argument("--sources", type=int, default=1, help="Number of sources (default: 1)")
    p_cls.add_argument("--json", action="store_true", help="JSON output")
    p_cls.set_defaults(func=cmd_classify)

    # check-epistemic
    p_epi = sub.add_parser("check-epistemic", help="Run full epistemic validation on premise graphs")
    p_epi.add_argument("--graph", type=str, default=None, help="Path to .dot file")
    p_epi.add_argument("--dir", type=str, default=None, help="Directory with .dot files")
    p_epi.add_argument("--json", action="store_true", help="JSON output")
    p_epi.set_defaults(func=cmd_check_epistemic)

    # status
    p_st = sub.add_parser("status", help="Check module health")
    p_st.add_argument("--json", action="store_true", help="JSON output")
    p_st.set_defaults(func=cmd_status)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        exit_code = args.func(args)
        sys.exit(exit_code)
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"  FAIL  {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
