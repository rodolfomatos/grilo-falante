"""
Grilo Falante Capsule Stamper — GF-ID and GMIF Headers

Adds epistemic metadata headers to capsules:
- GF-ID: Content hash-based identifier
- GMIF: Epistemic level classification
- Timestamp and source tracking
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional


CAPSULE_GMIF_DEFAULTS = {
    "capitulo": "M7",
    "metodologico": "M7",
    "mae": "M7",
    "integracao": "M7",
    "representacao": "M6",
    "estado_da_arte": "M5",
    "auditoria": "M7",
    "validacao": "M2",
    "revalidacao": "M6",
    "experimental": "M6",
    "exemplo": "M5",
    "conceptual": "M7",
    "documento": "M7",
    "pipeline": "M7",
    "promocao": "M7",
    "subcapsula": "M6",
    "jogo": "M6",
    "rdeo": "M5",
    "rivh": "M1",
    "ecc": "M5",
    "leitura": "M5",
    "feynman": "M6",
    "def": "M5",
}

GMIF_DESCRIPTIONS = {
    "M1": "Primary evidence - multiple sources",
    "M2": "Contextual condition - with assumptions",
    "M3": "Partial - no edges",
    "M4": "Doubtful - contradictions detected",
    "M5": "Interpretation - one clear source",
    "M6": "Derived - from inference",
    "M7": "Synthesis - final aggregate",
    "M8": "Conclusion",
}


def extract_gmif_from_filename(filename: str) -> str:
    """Determine GMIF level from capsule filename"""
    filename_lower = filename.lower()

    for key, level in CAPSULE_GMIF_DEFAULTS.items():
        if key in filename_lower:
            return level

    return "M7"


def generate_gfid(content: str, gmif_level: str, suffix: str = "") -> str:
    """Generate a GF-ID from content hash"""
    content_hash = hashlib.md5(content[:500].encode()).hexdigest()[:8]
    suffix_part = f"-{suffix}" if suffix else ""
    return f"GF-{gmif_level}-{content_hash}{suffix_part}"


def generate_capsule_header(
    capsule_path: Path, gmif_level: Optional[str] = None, force: bool = False
) -> str:
    """Generate GF-ID and GMIF header for a capsule"""
    if gmif_level is None:
        gmif_level = extract_gmif_from_filename(capsule_path.name)

    content = capsule_path.read_text(encoding="utf-8", errors="ignore")

    content_hash = content[:200] if len(content) > 200 else content
    gfid = generate_gfid(content_hash, gmif_level, capsule_path.stem)

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    gmif_desc = GMIF_DESCRIPTIONS.get(gmif_level, "Unknown")

    header = f"""## Metadados Epistemicos

- **GF-ID:** {gfid}
- **GMIF:** {gmif_level} — {gmif_desc}
- **Gerado:** {timestamp}
- **Fonte:** {capsule_path.name}

---

"""

    if "## Metadados Epistemicos" in content and not force:
        return ""

    if content.startswith("#"):
        parts = content.split("\n", 1)
        if len(parts) > 1:
            return parts[0] + "\n" + header + parts[1]

    return header + content


def stamp_capsule(
    capsule_path: Path, gmif_level: Optional[str] = None, force: bool = False
) -> bool:
    """Add GF-ID and GMIF header to a capsule file"""
    try:
        original = capsule_path.read_text(encoding="utf-8", errors="ignore")

        if "## Metadados Epistemicos" in original and not force:
            return False

        stamped = generate_capsule_header(capsule_path, gmif_level, force)

        if stamped == original:
            return False

        capsule_path.write_text(stamped, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error stamping {capsule_path}: {e}")
        return False


def stamp_all_capsules(
    capsules_dir: Path, gmif_level: Optional[str] = None, force: bool = False
) -> dict:
    """Stamp all capsules in a directory"""
    results = {"stamped": [], "skipped": [], "errors": []}

    if not capsules_dir.exists():
        results["errors"].append(f"Directory not found: {capsules_dir}")
        return results

    for capsule_file in capsules_dir.glob("*.md"):
        if "## Metadados Epistemicos" in capsule_file.read_text(encoding="utf-8", errors="ignore"):
            results["skipped"].append(capsule_file.name)
            continue

        if stamp_capsule(capsule_file, gmif_level, force):
            results["stamped"].append(capsule_file.name)
        else:
            results["skipped"].append(capsule_file.name)

    return results
