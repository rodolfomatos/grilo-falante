from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
from models.epistemic_objects import (
    Proposition,
    PropositionRole,
    PropositionDependency,
    RelationType,
    TensionRecord,
    TensionType,
    TensionResolution,
    FalsificationCondition,
    FalsificationStatus,
    PropositionLegitimacy,
)


def generate_proposition_id() -> str:
    return f"PROP-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"


def extract_foundational_propositions(
    input_text: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]]
) -> List[Proposition]:
    propositions = []
    
    for node in nodes:
        gmif_type = node.get("gmif_type", "")
        
        role = PropositionRole.DERIVED
        if gmif_type == "M1":
            role = PropositionRole.FOUNDATIONAL
        elif gmif_type == "M3":
            role = PropositionRole.ASSUMPTION
        elif gmif_type == "M4":
            role = PropositionRole.CONSTRAINT
        
        prop = Proposition(
            id=generate_proposition_id(),
            statement=node.get("text", node.get("content", "")),
            role=role,
            gmif_type=gmif_type,
            legitimacy=PropositionLegitimacy.SUSPENDED,
            supporting_claim_ids=[],
            boundary_conditions="",
            confidence=node.get("confidence", 0.5)
        )
        propositions.append(prop)
    
    return propositions


def classify_proposition_role(proposition: Proposition, context: Dict[str, Any]) -> PropositionRole:
    text_lower = proposition.statement.lower()
    
    if context.get("is_root_claim", False):
        return PropositionRole.FOUNDATIONAL
    
    if any(word in text_lower for word in ["assume", "presuposto", "assume that", "given that"]):
        return PropositionRole.ASSUMPTION
    
    if any(word in text_lower for word in ["therefore", "thus", "hence", "consequently", "logo"]):
        return PropositionRole.DERIVED
    
    if any(word in text_lower for word in ["must", "cannot", "should not", "constraint", "limite"]):
        return PropositionRole.CONSTRAINT
    
    return proposition.role


def build_dependency_map(
    propositions: List[Proposition],
    edges: List[Dict[str, Any]]
) -> List[PropositionDependency]:
    dependencies = []
    
    for edge in edges:
        from_id = edge.get("from", "")
        to_id = edge.get("to", "")
        
        if not from_id or not to_id:
            continue
        
        source_prop = next((p for p in propositions if from_id in p.id), None)
        target_prop = next((p for p in propositions if to_id in p.id), None)
        
        if source_prop and target_prop:
            relation = RelationType.SUPPORTS
            if edge.get("type") == "contradicts":
                relation = RelationType.CONTRADICTS
            elif edge.get("type") == "depends_on":
                relation = RelationType.DEPENDS_ON
            elif edge.get("type") == "narrows":
                relation = RelationType.NARROWS
            
            dependencies.append(PropositionDependency(
                from_proposition=source_prop.id,
                to_proposition=target_prop.id,
                relation_type=relation
            ))
    
    return dependencies


def detect_proposition_tensions(
    propositions: List[Proposition],
    dependencies: List[PropositionDependency]
) -> List[TensionRecord]:
    tensions = []
    
    for dep in dependencies:
        if dep.relation_type == RelationType.CONTRADICTS:
            tension = TensionRecord(
                id=f"TENSION-{uuid.uuid4().hex[:6]}",
                left_proposition_id=dep.from_proposition,
                right_proposition_id=dep.to_proposition,
                tension_type=TensionType.CONTRADICTION,
                severity=3,
                resolution_status=TensionResolution.UNRESOLVED
            )
            tensions.append(tension)
    
    foundational = [p for p in propositions if p.role == PropositionRole.FOUNDATIONAL]
    derived = [p for p in propositions if p.role == PropositionRole.DERIVED]
    
    if not foundational and derived:
        tension = TensionRecord(
            id=f"TENSION-{uuid.uuid4().hex[:6]}",
            left_proposition_id="",
            right_proposition_id="",
            tension_type=TensionType.INCOMPLETENESS,
            severity=2,
            resolution_status=TensionResolution.UNRESOLVED
        )
        tensions.append(tension)
    
    return tensions


def extract_falsification_conditions(
    propositions: List[Proposition]
) -> List[FalsificationCondition]:
    conditions = []
    
    for prop in propositions:
        if prop.role == PropositionRole.FOUNDATIONAL:
            condition = FalsificationCondition(
                id=f"FC-{uuid.uuid4().hex[:6]}",
                proposition_id=prop.id,
                condition_text=f"Condition that would falsify: {prop.statement}",
                evidence_needed="Evidence contradicting the foundational claim",
                status=FalsificationStatus.PENDING
            )
            conditions.append(condition)
        
        elif prop.role == PropositionRole.DERIVED:
            supporting = prop.supporting_claim_ids
            if not supporting:
                condition = FalsificationCondition(
                    id=f"FC-{uuid.uuid4().hex[:6]}",
                    proposition_id=prop.id,
                    condition_text="Derived proposition without supporting claims",
                    evidence_needed="Chain of evidence from foundational to derived",
                    status=FalsificationStatus.PENDING
                )
                conditions.append(condition)
    
    return conditions


def validate_propositions(
    propositions: List[Proposition],
    falsification_conditions: List[FalsificationCondition]
) -> Dict[str, Any]:
    results = {
        "valid": [],
        "conditional": [],
        "failed": []
    }
    
    for prop in propositions:
        if prop.role == PropositionRole.FOUNDATIONAL:
            fc = next((f for f in falsification_conditions if f.proposition_id == prop.id), None)
            if fc and fc.status == FalsificationStatus.VALIDATED:
                results["valid"].append(prop.id)
            elif fc and fc.status == FalsificationStatus.FAILED:
                results["failed"].append(prop.id)
            else:
                results["conditional"].append(prop.id)
        else:
            results["valid"].append(prop.id)
    
    return results


def get_proposition_summary(propositions: List[Proposition]) -> Dict[str, Any]:
    return {
        "total": len(propositions),
        "foundational": len([p for p in propositions if p.role == PropositionRole.FOUNDATIONAL]),
        "assumption": len([p for p in propositions if p.role == PropositionRole.ASSUMPTION]),
        "derived": len([p for p in propositions if p.role == PropositionRole.DERIVED]),
        "constraint": len([p for p in propositions if p.role == PropositionRole.CONSTRAINT]),
        "legitimacy_asserted": len([p for p in propositions if p.legitimacy == PropositionLegitimacy.ASSERTED]),
        "legitimacy_suspended": len([p for p in propositions if p.legitimacy == PropositionLegitimacy.SUSPENDED])
    }