"""
Auditoria Hostil — Hostile Audit Service

Implements the 5 axes of hostile audit cycle from Grilo Falante v1.9.2:

Eixo 1 — Modo Automático
  - Limits: não infere, não decide, não promove

Eixo 2 — Validação Automática
  - Severity levels: CRÍTICA / MAJOR / MINOR

Eixo 3 — Grafos Epistémicos
  - Conceptual vs Operative graph distinction

Eixo 4 — Ledger de Preservação Funcional
  - Event typology, human authority qualification

Eixo 5 — Pipeline Normativo
  - Explicit transitions, transverse states (BLOCKED, SUSPENSO, RETOMÁVEL)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class AuditSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class AuditAxis(str, Enum):
    AUTOMATIC_MODE = "automatic_mode"
    AUTOMATIC_VALIDATION = "automatic_validation"
    EPISTEMIC_GRAPHS = "epistemic_graphs"
    PRESERVATION_LEDGER = "preservation_ledger"
    NORMATIVE_PIPELINE = "normative_pipeline"


class IssueStatus(str, Enum):
    OPEN = "open"
    BLOCKED = "blocked"
    RESOLVED = "resolved"
    SUSPENDED = "suspended"


@dataclass
class AuditIssue:
    """An issue found during hostile audit."""

    id: Optional[int] = None
    issue_key: str = ""
    axis: AuditAxis = AuditAxis.AUTOMATIC_MODE
    severity: AuditSeverity = AuditSeverity.MINOR
    title: str = ""
    description: str = ""
    finding: str = ""
    recommendation: str = ""
    status: IssueStatus = IssueStatus.OPEN
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


@dataclass
class AuditReport:
    """Complete hostile audit report."""

    report_key: str = ""
    audit_date: datetime = field(default_factory=datetime.utcnow)
    axes_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    issues: List[AuditIssue] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    blocked_count: int = 0
    resolved_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_key": self.report_key,
            "audit_date": self.audit_date.isoformat(),
            "axes_results": self.axes_results,
            "issues": [
                {
                    "id": i.id,
                    "issue_key": i.issue_key,
                    "axis": i.axis.value,
                    "severity": i.severity.value,
                    "title": i.title,
                    "finding": i.finding,
                    "recommendation": i.recommendation,
                    "status": i.status.value,
                }
                for i in self.issues
            ],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "blocked_count": self.blocked_count,
            "resolved_count": self.resolved_count,
        }


class AuditoriaHostil:
    """
    Hostile Audit Service — 5-axis epistemic audit.

    Implements the hostile audit cycle from Grilo Falante v1.9.2.
    """

    AXIS_DESCRIPTIONS = {
        AuditAxis.AUTOMATIC_MODE: {
            "name": "Modo Automático",
            "limits": ["não infere", "não decide", "não promove"],
        },
        AuditAxis.AUTOMATIC_VALIDATION: {
            "name": "Validação Automática",
            "severity_levels": ["CRÍTICA", "MAJOR", "MINOR"],
        },
        AuditAxis.EPISTEMIC_GRAPHS: {
            "name": "Grafos Epistémicos",
            "distinction": "Grafo Conceptual vs Operativo",
        },
        AuditAxis.PRESERVATION_LEDGER: {
            "name": "Ledger de Preservação Funcional",
            "event_types": ["rejection", "decision", "creation", "modification"],
        },
        AuditAxis.NORMATIVE_PIPELINE: {
            "name": "Pipeline Normativo",
            "states": ["BLOCKED", "SUSPENDED", "RETOMÁVEL"],
        },
    }

    def __init__(self):
        self._counter: int = 0
        self._reports: Dict[str, AuditReport] = {}

    async def run_full_audit(
        self,
        claims: List[dict],
        governance_records: List[dict],
        graph_data: Optional[dict] = None,
    ) -> AuditReport:
        """
        Run a full 5-axis hostile audit.

        Returns an AuditReport with findings for each axis.
        """
        self._counter += 1
        report_key = f"audit_{self._counter:04d}"

        report = AuditReport(report_key=report_key)

        axis1_result = await self._audit_automatic_mode(claims)
        report.axes_results[AuditAxis.AUTOMATIC_MODE.value] = axis1_result

        axis2_result = await self._audit_validation(claims)
        report.axes_results[AuditAxis.AUTOMATIC_VALIDATION.value] = axis2_result

        axis3_result = await self._audit_epistemic_graphs(graph_data or {})
        report.axes_results[AuditAxis.EPISTEMIC_GRAPHS.value] = axis3_result

        axis4_result = await self._audit_ledger(governance_records)
        report.axes_results[AuditAxis.PRESERVATION_LEDGER.value] = axis4_result

        axis5_result = await self._audit_pipeline(claims, governance_records)
        report.axes_results[AuditAxis.NORMATIVE_PIPELINE.value] = axis5_result

        report.issues = self._collect_issues(report.axes_results)
        report.blocked_count = sum(1 for i in report.issues if i.status == IssueStatus.BLOCKED)
        report.resolved_count = sum(1 for i in report.issues if i.status == IssueStatus.RESOLVED)

        report.summary = self._generate_summary(report)
        report.recommendations = self._generate_recommendations(report.issues)

        self._reports[report_key] = report
        return report

    async def _audit_automatic_mode(self, claims: List[dict]) -> Dict[str, Any]:
        """Eixo 1: Modo Automático limits."""
        issues = []
        compliant = True

        for claim in claims:
            text = claim.get("claim_text", "").lower()

            inference_markers = ["therefore", "thus", "hence", "consequently", " logo", "portanto"]
            if any(marker in text for marker in inference_markers):
                if claim.get("gmif_level") in ("M4", "M3"):
                    issues.append(
                        {
                            "type": "implicit_inference",
                            "claim_id": claim.get("id"),
                            "finding": "M4/M3 claim contains inference markers",
                        }
                    )
                    compliant = False

            promotion_markers = ["prove", "demonstrate", "demonstrates"]
            if any(marker in text for marker in promotion_markers):
                if claim.get("gmif_level") not in ("M1", "M2"):
                    issues.append(
                        {
                            "type": "unjustified_promotion",
                            "claim_id": claim.get("id"),
                            "finding": "Non-M1/M2 claim attempts promotion",
                        }
                    )
                    compliant = False

        return {
            "compliant": compliant,
            "issues": issues,
            "limits_checked": self.AXIS_DESCRIPTIONS[AuditAxis.AUTOMATIC_MODE]["limits"],
        }

    async def _audit_validation(self, claims: List[dict]) -> Dict[str, Any]:
        """Eixo 2: Validação Automática severity levels."""
        issues = []
        severity_counts = {s.value: 0 for s in AuditSeverity}

        for claim in claims:
            validation_status = claim.get("validation_status", "pending")

            if validation_status == "pending":
                severity_counts[AuditSeverity.MINOR.value] += 1
            elif validation_status == "rejected":
                severity_counts[AuditSeverity.MAJOR.value] += 1
            elif validation_status == "contradicted":
                severity_counts[AuditSeverity.CRITICAL.value] += 1
                issues.append(
                    {
                        "type": "contradicted_claim",
                        "claim_id": claim.get("id"),
                        "severity": AuditSeverity.CRITICAL.value,
                    }
                )

        return {
            "severity_counts": severity_counts,
            "issues": issues,
            "total_claims": len(claims),
        }

    async def _audit_epistemic_graphs(self, graph_data: dict) -> Dict[str, Any]:
        """Eixo 3: Grafos Epistémicos distinction."""
        issues = []
        conceptual_count = 0
        operative_count = 0

        if not graph_data:
            return {
                "compliant": True,
                "note": "No graph data provided",
                "conceptual_count": 0,
                "operative_count": 0,
            }

        for node_id, node_data in graph_data.items():
            node_type = node_data.get("type", "")
            if node_type == "conceptual":
                conceptual_count += 1
            elif node_type == "operative":
                operative_count += 1

            if node_data.get("is_operative") and node_data.get("is_conceptual"):
                issues.append(
                    {
                        "type": "graph_type_confusion",
                        "node_id": node_id,
                        "finding": "Node marked as both conceptual and operative",
                    }
                )

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "conceptual_count": conceptual_count,
            "operative_count": operative_count,
        }

    async def _audit_ledger(self, records: List[dict]) -> Dict[str, Any]:
        """Eixo 4: Ledger de Preservação Funcional."""
        issues = []
        event_types = {}

        for record in records:
            action = record.get("action", "unknown")
            event_types[action] = event_types.get(action, 0) + 1

            if action == "reject" and not record.get("reason"):
                issues.append(
                    {
                        "type": "rejection_without_reason",
                        "record_id": record.get("id"),
                        "finding": "Rejection event missing reason",
                    }
                )

            if not record.get("curator_key") and action not in ("system", "auto"):
                issues.append(
                    {
                        "type": "action_without_authority",
                        "record_id": record.get("id"),
                        "finding": "Action taken without curator authority",
                    }
                )

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "event_types": event_types,
            "total_events": len(records),
        }

    async def _audit_pipeline(self, claims: List[dict], records: List[dict]) -> Dict[str, Any]:
        """Eixo 5: Pipeline Normativo transitions."""
        issues = []
        states = {}

        for claim in claims:
            status = claim.get("status", "derived")
            states[status] = states.get(status, 0) + 1

            if status == "derived":
                has_audit = any(
                    r.get("entity_id") == claim.get("id") and r.get("action") == "audit"
                    for r in records
                )
                if has_audit:
                    issues.append(
                        {
                            "type": "premature_audit",
                            "claim_id": claim.get("id"),
                            "finding": "Claim in 'derived' state already audited",
                        }
                    )

        blocked_count = states.get("blocked", 0) + states.get("suspended", 0)
        retormavel_count = states.get("retomavel", 0)

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "states": states,
            "blocked_count": blocked_count,
            "retomavel_count": retormavel_count,
        }

    def _collect_issues(self, axes_results: Dict[str, Dict[str, Any]]) -> List[AuditIssue]:
        """Collect all issues from axes results."""
        issues = []
        issue_id = 0

        for axis_key, result in axes_results.items():
            for issue_data in result.get("issues", []):
                issue_id += 1
                severity_str = issue_data.get("severity", "minor")
                try:
                    severity = AuditSeverity(severity_str)
                except ValueError:
                    severity = AuditSeverity.MINOR

                issues.append(
                    AuditIssue(
                        id=issue_id,
                        issue_key=f"issue_{issue_id:04d}",
                        axis=AuditAxis(axis_key),
                        severity=severity,
                        title=issue_data.get("type", "unknown"),
                        finding=issue_data.get("finding", ""),
                        status=IssueStatus.OPEN,
                    )
                )

        return issues

    def _generate_summary(self, report: AuditReport) -> str:
        """Generate audit summary."""
        total_issues = len(report.issues)
        critical = sum(1 for i in report.issues if i.severity == AuditSeverity.CRITICAL)
        compliant_axes = sum(1 for r in report.axes_results.values() if r.get("compliant", False))

        return (
            f"Audit {report.report_key}: {compliant_axes}/5 axes compliant. "
            f"{total_issues} issues found ({critical} critical)."
        )

    def _generate_recommendations(self, issues: List[AuditIssue]) -> List[str]:
        """Generate recommendations from issues."""
        recommendations = []

        if any(i.axis == AuditAxis.AUTOMATIC_MODE for i in issues):
            recommendations.append(
                "Review automatic mode limits — ensure no implicit inference in M4/M3 claims."
            )

        if any(i.severity == AuditSeverity.CRITICAL for i in issues):
            recommendations.append("CRITICAL: Address contradicted claims immediately.")

        if any(i.axis == AuditAxis.EPISTEMIC_GRAPHS for i in issues):
            recommendations.append("Clarify conceptual vs operative graph distinction.")

        if not recommendations:
            recommendations.append("No immediate actions required.")

        return recommendations

    def get_report(self, report_key: str) -> Optional[AuditReport]:
        """Get a specific audit report."""
        return self._reports.get(report_key)

    def list_reports(self) -> List[AuditReport]:
        """List all audit reports."""
        return list(self._reports.values())
