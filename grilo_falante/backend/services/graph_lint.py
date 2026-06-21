"""
graph_lint.py — Epistemic Graph Lint Service (L1-L8)

Ported from GePeTo's Notebook, adapted for Grilo Falante v3.0 models.

Epistemic integrity checks for collections of governed claims:
L1: Orphan claims (no relationship to claim pool)
L2: Self-referential claims
L3: Contradictory claims (same topic, opposing positions)
L4: Circular dependencies (claim_references cycles)
L5: Unsupported conclusions (CONCLUSION from CONFLICTED only)
L6: Missing prerequisites (CONCLUSION/SYNTHESIS without VERIFIED basis)
L7: Confidence mismatches (child > parent confidence)
L8: Temporal inconsistencies (source newer than claim)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from grilo_falante.models import GMIFLevel, GovernedClaim


@dataclass
class LintIssue:
    lint_code: str
    severity: str
    message: str
    claim_keys: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


@dataclass
class LintResult:
    passed: bool
    issues: list[LintIssue]
    summary: str
    issue_count: int = 0


class GraphLinter:
    """
    Epistemic integrity checks (L1-L8) on collections of governed claims.

    Operates on lists of GovernedClaim objects, using claim_references,
    GMIF levels, confidence scores, and timestamps.
    """

    def __init__(self):
        self.issue_history: list[LintIssue] = []

    def _get_references(self, claim: GovernedClaim) -> list[str]:
        """Get referenced claim keys — claim_references first, then provenance fallback."""
        if claim.claim_references:
            return claim.claim_references
        refs = claim.provenance.get("references", []) if claim.provenance else []
        return refs if isinstance(refs, list) else []

    def run_all_checks(self, claims: list[GovernedClaim]) -> LintResult:
        """Run all L1-L8 lint checks on a collection of claims."""
        all_issues = []
        all_issues.extend(self.check_orphans(claims))
        all_issues.extend(self.check_self_references(claims))
        all_issues.extend(self.check_contradictions(claims))
        all_issues.extend(self.check_cycles(claims))
        all_issues.extend(self.check_unsupported_conclusions(claims))
        all_issues.extend(self.check_missing_prerequisites(claims))
        all_issues.extend(self.check_confidence_mismatches(claims))
        all_issues.extend(self.check_temporal_consistency(claims))
        self.issue_history.extend(all_issues)
        return LintResult(
            passed=len(all_issues) == 0,
            issues=all_issues,
            summary=self._generate_summary(all_issues),
            issue_count=len(all_issues),
        )

    def check_orphans(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L1: Detect orphan claims with no relationships."""
        issues = []
        for claim in claims:
            has_refs = bool(self._get_references(claim))
            referenced = any(claim.claim_key in self._get_references(other) for other in claims)
            if not has_refs and not referenced:
                issues.append(LintIssue(
                    lint_code="L1", severity="warning",
                    claim_keys=[claim.claim_key],
                    message=f"Orphan claim '{claim.claim_key[:50]}' has no relationships",
                    details={
                        "gmif_level": claim.gmif_level.value if isinstance(claim.gmif_level, GMIFLevel) else str(claim.gmif_level),
                        "confidence": claim.gmif_confidence,
                    },
                ))
        return issues

    def check_self_references(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L2: Detect self-referential claims."""
        issues = []
        for claim in claims:
            if claim.claim_key in self._get_references(claim):
                issues.append(LintIssue(
                    lint_code="L2", severity="error",
                    claim_keys=[claim.claim_key],
                    message=f"Self-referential claim '{claim.claim_key[:50]}'",
                    details={"claim_key": claim.claim_key},
                ))
        return issues

    def check_contradictions(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L3: Detect contradictory claims about the same topic/source."""
        issues = []
        from collections import defaultdict
        by_source: dict = defaultdict(list)
        for claim in claims:
            key = str(claim.source_id or claim.session_id)
            by_source[key].append(claim)
        for source_key, group in by_source.items():
            verified = [c for c in group if c.gmif_level in (GMIFLevel.VERIFIED, GMIFLevel.M1_PRIMARY)]
            conflicted = [c for c in group if c.gmif_level in (GMIFLevel.CONFLICTED, GMIFLevel.M4_DOUBTFUL)]
            if verified and conflicted:
                issues.append(LintIssue(
                    lint_code="L3", severity="error",
                    claim_keys=[c.claim_key for c in verified + conflicted],
                    message=f"Contradictory claims in source '{source_key}'",
                    details={"verified_count": len(verified), "conflicted_count": len(conflicted)},
                ))
        return issues

    def check_cycles(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L4: Detect circular dependency chains in claim_references."""
        issues = []
        ref_map = {c.claim_key: self._get_references(c) for c in claims}

        def dfs(node: str, path: list[str], visited: set) -> Optional[list[str]]:
            if node in path:
                return path[path.index(node):] + [node]
            if node in visited:
                return None
            visited.add(node)
            for ref in ref_map.get(node, []):
                result = dfs(ref, path + [node], visited)
                if result:
                    return result
            return None

        for claim in claims:
            cycle = dfs(claim.claim_key, [], set())
            if cycle:
                issues.append(LintIssue(
                    lint_code="L4", severity="warning",
                    claim_keys=cycle,
                    message=f"Circular reference chain in '{claim.claim_key[:50]}'",
                    details={"cycle_length": len(cycle)},
                ))
                break
        return issues

    def check_unsupported_conclusions(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L5: Detect CONCLUSION claims only supported by CONFLICTED claims."""
        issues = []
        conclusions = [c for c in claims if c.gmif_level in (GMIFLevel.CONCLUSION, GMIFLevel.M8_CONCLUSION)]
        for conc in conclusions:
            refs = self._get_references(conc)
            if not refs:
                continue
            supporting = []
            for ref_key in refs:
                ref = next((c for c in claims if c.claim_key == ref_key), None)
                if ref:
                    supporting.append(ref.gmif_level)
            if supporting and all(
                lvl in (GMIFLevel.CONFLICTED, GMIFLevel.M4_DOUBTFUL) for lvl in supporting
            ):
                issues.append(LintIssue(
                    lint_code="L5", severity="error",
                    claim_keys=[conc.claim_key],
                    message=f"Conclusion '{conc.claim_key[:50]}' only has CONFLICTED support",
                    details={"supporting_levels": [
                        lvl.value if isinstance(lvl, GMIFLevel) else str(lvl) for lvl in supporting
                    ]},
                ))
        return issues

    def check_missing_prerequisites(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L6: Detect CONCLUSION/SYNTHESIS without VERIFIED prerequisites."""
        issues = []
        high = [c for c in claims if c.gmif_level in (
            GMIFLevel.CONCLUSION, GMIFLevel.M8_CONCLUSION,
            GMIFLevel.SYNTHESIS, GMIFLevel.M7_SYNTHESIS,
        )]
        for claim in high:
            refs = self._get_references(claim)
            if not refs:
                continue
            has_verified = any(
                next((c for c in claims if c.claim_key == r and
                      c.gmif_level in (GMIFLevel.VERIFIED, GMIFLevel.M1_PRIMARY)), None)
                for r in refs
            )
            if not has_verified:
                issues.append(LintIssue(
                    lint_code="L6", severity="warning",
                    claim_keys=[claim.claim_key],
                    message=f"Synthesis/Conclusion '{claim.claim_key[:50]}' lacks VERIFIED prerequisites",
                    details={
                        "gmif_level": claim.gmif_level.value if isinstance(claim.gmif_level, GMIFLevel) else str(claim.gmif_level),
                    },
                ))
        return issues

    def check_confidence_mismatches(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L7: Detect confidence mismatches (child > parent + 0.2)."""
        issues = []
        for claim in claims:
            for ref_key in self._get_references(claim):
                parent = next((c for c in claims if c.claim_key == ref_key), None)
                if not parent:
                    continue
                if claim.gmif_confidence > parent.gmif_confidence + 0.2:
                    issues.append(LintIssue(
                        lint_code="L7", severity="warning",
                        claim_keys=[parent.claim_key, claim.claim_key],
                        message=f"Confidence mismatch: '{claim.claim_key[:30]}' ({claim.gmif_confidence:.2f}) > parent ({parent.gmif_confidence:.2f})",
                        details={
                            "parent_confidence": parent.gmif_confidence,
                            "child_confidence": claim.gmif_confidence,
                        },
                    ))
        return issues

    def check_temporal_consistency(self, claims: list[GovernedClaim]) -> list[LintIssue]:
        """L8: Detect temporal inconsistencies (reference newer than claim)."""
        issues = []
        for claim in claims:
            claim_time = claim.created_at
            if not claim_time:
                continue
            for ref_key in self._get_references(claim):
                ref = next((c for c in claims if c.claim_key == ref_key), None)
                if not ref or not ref.created_at:
                    continue
                if ref.created_at > claim_time:
                    issues.append(LintIssue(
                        lint_code="L8", severity="warning",
                        claim_keys=[claim.claim_key, ref.claim_key],
                        message="Temporal inconsistency: reference is newer than claim",
                        details={
                            "claim_created": claim_time.isoformat() if isinstance(claim_time, datetime) else str(claim_time),
                            "ref_created": ref.created_at.isoformat() if isinstance(ref.created_at, datetime) else str(ref.created_at),
                        },
                    ))
        return issues

    def _generate_summary(self, issues: list[LintIssue]) -> str:
        if not issues:
            return "All lint checks passed."
        by_severity = {"error": 0, "warning": 0}
        by_code: dict[str, int] = {}
        for issue in issues:
            if issue.severity in by_severity:
                by_severity[issue.severity] += 1
            by_code[issue.lint_code] = by_code.get(issue.lint_code, 0) + 1
        parts = []
        if by_severity["error"] > 0:
            parts.append(f"{by_severity['error']} errors")
        if by_severity["warning"] > 0:
            parts.append(f"{by_severity['warning']} warnings")
        codes = ", ".join(f"{code}:{count}" for code, count in sorted(by_code.items()))
        return f"Found {len(issues)} issues ({', '.join(parts)}). Codes: [{codes}]"

    def to_dict(self, result: LintResult) -> dict:
        return {
            "passed": result.passed,
            "issue_count": result.issue_count,
            "summary": result.summary,
            "issues": [
                {
                    "lint_code": i.lint_code,
                    "severity": i.severity,
                    "claim_keys": i.claim_keys,
                    "message": i.message,
                    "details": i.details,
                }
                for i in result.issues
            ],
        }
