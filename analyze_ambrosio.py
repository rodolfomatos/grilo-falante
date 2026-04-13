#!/usr/bin/env python3
"""
Analisador de文档tos Ambrosio v2.5.0

Este script analisa hostilmente todos os documentos no diretório ambrosio_v2.5.0
e produz um relatório de auditoria como Feynman faria:
- Simples para crianças
- Rigoroso para especialistas

Usage:
    python3 analyze_ambrosio.py <path> [--output OUTPUT]
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

GF_ID_PATTERN = re.compile(r'^GF-\d{6}-[A-Z]\d-[a-f0-9]+$')
GMIF_TYPES = re.compile(r'\b(M1|M2|M3|M4|M5|M6|M7)\b')


def find_markdown_files(path):
    """Find all markdown files."""
    path = Path(path)
    return list(path.glob("**/*.md"))


def extract_headers(content):
    """Extract markdown headers."""
    headers = []
    for line in content.split('\n'):
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.strip('# ').strip()
            headers.append((level, text))
    return headers


def find_gf_ids(content):
    """Find all GF-ID references."""
    return GF_ID_PATTERN.findall(content)


def find_gmif_references(content):
    """Find all GMIF type references."""
    return GMIF_TYPES.findall(content)


def find_claims(content):
    """Find claims - lines ending with : or containing 'é'/'são'."""
    claims = []
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line and len(line) < 200:
            claims.append(line)
    return claims[:50]  # Limit


def analyze_file(filepath):
    """Analyze a single markdown file."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {"error": str(e), "file": str(filepath)}

    gf_ids = find_gf_ids(content)
    gmif_refs = find_gmif_references(content)
    headers = extract_headers(content)

    word_count = len(content.split())
    char_count = len(content)

    return {
        "file": str(filepath.relative_to(filepath.parents[1])),
        "size_bytes": char_count,
        "word_count": word_count,
        "gf_ids": gf_ids,
        "gf_id_count": len(gf_ids),
        "gmif_refs": gmif_refs,
        "gmif_counts": defaultdict(int),
        "headers": [{"level": h[0], "text": h[1][:80]} for h in headers[:20]],
        "has_gf_id": len(gf_ids) > 0,
        "has_gmif": len(gmif_refs) > 0,
    }


def categorize_file(filepath):
    """Categorize file by its path."""
    path_str = str(filepath)
    parts = Path(path_str).parts

    if 'system' in parts:
        if 'core' in parts:
            return "system-core"
        elif 'epistemic' in parts:
            return "system-epistemic"
        elif 'experiments' in parts:
            return "system-experiments"
        elif 'governance' in parts:
            return "system-governance"
        elif 'modes' in parts:
            return "system-modes"
        elif 'pipeline' in parts:
            return "system-pipeline"
        return "system"
    elif 'capsules' in parts:
        return "capsules"
    elif 'extras' in parts:
        return "extras"
    elif 'graphs' in parts:
        return "graphs"
    elif 'shadow' in parts:
        return "shadow"
    elif 'protocols' in parts:
        return "protocols"
    elif 'rules' in parts:
        return "rules"
    elif 'loader' in parts:
        return "loader"
    elif 'ledger' in parts:
        return "ledger"
    elif 'installer' in parts:
        return "installer"
    else:
        return "root"


def run_audit(path):
    """Run complete audit."""
    path = Path(path)

    if not path.exists():
        return {"error": f"Path not found: {path}"}

    files = find_markdown_files(path)
    print(f"Found {len(files)} markdown files")

    results = []
    total_words = 0
    total_gf_ids = 0
    gmif_totals = defaultdict(int)
    categories = defaultdict(list)

    for f in files:
        result = analyze_file(f)
        if "error" in result:
            continue

        category = categorize_file(f)
        result["category"] = category
        categories[category].append(result)

        total_words += result["word_count"]
        total_gf_ids += result["gf_id_count"]

        for gmif_type in result.get("gmif_refs", []):
            gmif_totals[gmif_type] += 1

        results.append(result)

    # Sort by size
    results.sort(key=lambda x: x["size_bytes"], reverse=True)

    return {
        "total_files": len(results),
        "total_words": total_words,
        "total_gf_ids": total_gf_ids,
        "gmif_totals": dict(gmif_totals),
        "categories": {k: len(v) for k, v in categories.items()},
        "largest_files": results[:10],
        "files_with_gf_id": sum(1 for r in results if r["has_gf_id"]),
        "files_with_gmif": sum(1 for r in results if r["has_gmif"]),
    }


def find_inconsistencies(path):
    """Find specific inconsistencies."""
    path = Path(path)

    issues = []

    # Check system.md vs system.kernel.md
    system = path / "system.md"
    kernel = path / "system.kernel.md"

    if system.exists() and kernel.exists():
        s_size = system.stat().st_size
        k_size = kernel.stat().st_size

        if abs(s_size - k_size) < 1000:
            issues.append({
                "type": "possible_duplicate",
                "files": ["system.md", "system.kernel.md"],
                "message": "Files have very similar sizes - possible duplication"
            })

    # Check for orphaned capsules
    capsules_dir = path / "capsules"
    if capsules_dir.exists():
        capsules = list(capsules_dir.glob("*.md"))
        orphaned = [c for c in capsules if "capsula" not in c.name.lower()]
        if orphaned:
            issues.append({
                "type": "naming_mismatch",
                "files": [c.name for c in orphaned[:5]],
                "message": "Files in capsules/ without 'capsula' in name"
            })

    # Check for version inconsistencies
    version_pattern = re.compile(r'v\d+\.\d+.\d+')
    versions_found = {}

    for f in path.glob("**/*.md"):
        if f.is_file():
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                versions = version_pattern.findall(content)
                for v in set(versions):
                    versions_found[v] = versions_found.get(v, 0) + 1
            except:
                pass

    if len(versions_found) > 5:
        issues.append({
            "type": "version_inconsistency",
            "message": f"Found {len(versions_found)} different versions: {list(versions_found.keys())[:10]}",
            "details": versions_found
        })

    return issues


def find_missing_files(path):
    """Check for files referenced but missing."""
    path = Path(path)

    # Files that should exist according to KERNEL.md
    expected_files = [
        "system.md",
        "system.kernel.md",
        "loader/LOADER.md",
        "rules/epistemic.md",
        "rules/validation.md",
        "protocols/analysis.md",
        "protocols/cognitive_cycle.md",
    ]

    missing = []
    for expected in expected_files:
        f = path / expected
        if not f.exists():
            missing.append(expected)

    return missing


def generate_feynman_report(audit_result, inconsistencies, missing):
    """Generate report as Feynman would."""

    report = """
═══════════════════════════════════════════════════════════════════════════════
                    ANÁLISE HOSTIL - GRILO FALANTE v2.5.0
                         Como uma criança explicaria
═══════════════════════════════════════════════════════════════════════════════

O QUE É ESTE PROJETO?
───────────────────
O Grilo Falante é como um professor muito rigoroso que nunca descansa.
Ele ajuda a pensar sobre ideias semogar实事求是 (com verdade).
Não diz "isso é verdade" ou "isso é errado".
Apenas diz: "Pensa bem antes de decidir."

NÚMEROS IMPORTANTES
────────────────
"""

    report += f"""
• Ficheiros analisados: {audit_result['total_files']}
• Palavras no total:   {audit_result['total_words']:,}
• IDs de identificação (GF-IDs): {audit_result['total_gf_ids']}
• Com GF-ID: {audit_result['files_with_gf_id']} ficheiros
• Com GMIF: {audit_result['files_with_gmif']} ficheiros
"""

    if audit_result['gmif_totals']:
        report += "\nTipos de ideia (GMIF):\n"
        for gmif_type, count in sorted(audit_result['gmif_totals'].items()):
            report += f"  • {gmif_type}: {count} referências\n"

    if audit_result['categories']:
        report += "\nPor onde está guardado:\n"
        for cat, count in sorted(audit_result['categories'].items(), key=lambda x: -x[1]):
            report += f"  • {cat}: {count} ficheiros\n"

    report += """
═══════════════════════════════════════════════════════════════════════════════
                         O que está mal (como Feynman veria)
═══════════════════════════════════════════════════════════════════════════════
"""

    if inconsistencies:
        for issue in inconsistencies:
            report += f"""
[{issue['type'].upper()}]
{issue['message']}
"""
    else:
        report += "\nNenhuma inconsistência grave encontrada.\n"

    if missing:
        report += "\nFicheiros em falta:\n"
        for m in missing:
            report += f"  ✗ {m}\n"

    # Technical details
    report += """
═══════════════════════════════════════════════════════════════════════════════
                         Detalhes para especialistas
═══════════════════════════════════════════════════════════════════════════════
"""

    report += "\nMaiores ficheiros:\n"
    for f in audit_result.get("largest_files", [])[:5]:
        report += f"  • {f['file']}: {f['size_bytes']:,} bytes\n"

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analisa documentos Ambrosio")
    parser.add_argument("path", help="Caminho para ambrosio_v2.5.0")
    parser.add_argument("--output", "-o", help="Ficheiro de saída")

    args = parser.parse_args()

    print("A analisar...")
    audit = run_audit(args.path)

    print("A procurar inconsistências...")
    inconsistencies = find_inconsistencies(args.path)

    print("A verificar ficheiros em falta...")
    missing = find_missing_files(args.path)

    report = generate_feynman_report(audit, inconsistencies, missing)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

    # Also output JSON for machine processing
    output_data = {
        "audit": audit,
        "inconsistencies": inconsistencies,
        "missing": missing,
        "timestamp": datetime.now().isoformat()
    }

    if args.output:
        json_output = Path(args.output).with_suffix('.json')
        json_output.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        print(f"JSON written to: {json_output}")