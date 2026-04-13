from typing import List, Dict, Any, Optional
from models.epistemic_objects import (
    Proposition,
    FalsificationCondition,
    FalsificationStatus,
    PropositionRole,
    PropositionLegitimacy,
)
from reasoning.propositions import extract_falsification_conditions


class LintResult:
    def __init__(self):
        self.ok: List[str] = []
        self.conditional: List[str] = []
        self.failed: List[str] = []


def run_proposition_lint(propositions: List[Proposition]) -> LintResult:
    result = LintResult()
    
    fc_list = extract_falsification_conditions(propositions)
    fc_map = {fc.proposition_id: fc for fc in fc_list}
    
    for prop in propositions:
        if prop.role == PropositionRole.FOUNDATIONAL:
            fc = fc_map.get(prop.id)
            
            if fc is None:
                result.conditional.append(prop.id)
                continue
            
            if fc.status == FalsificationStatus.VALIDATED:
                result.ok.append(prop.id)
            elif fc.status == FalsificationStatus.FAILED:
                result.failed.append(prop.id)
            else:
                result.conditional.append(prop.id)
        
        elif prop.role == PropositionRole.DERIVED:
            if not prop.supporting_claim_ids:
                result.failed.append(prop.id)
            else:
                result.ok.append(prop.id)
        
        else:
            result.ok.append(prop.id)
    
    return result


def check_foundational_boundaries(propositions: List[Proposition]) -> List[str]:
    issues = []
    
    foundational = [p for p in propositions if p.role == PropositionRole.FOUNDATIONAL]
    
    for prop in foundational:
        if not prop.falsification_conditions:
            issues.append(f"{prop.id}: no falsification conditions defined")
        
        if not prop.boundary_conditions:
            issues.append(f"{prop.id}: no boundary conditions defined")
    
    return issues


def check_derived_support(propositions: List[Proposition]) -> List[str]:
    issues = []
    
    derived = [p for p in propositions if p.role == PropositionRole.DERIVED]
    
    for prop in derived:
        if not prop.supporting_claim_ids:
            issues.append(f"{prop.id}: derived proposition without supporting claims")
    
    return issues


def evaluate_lint_for_promotion(
    propositions: List[Proposition],
    lint_result: LintResult
) -> tuple[str, List[str]]:
    reasons = []
    
    if lint_result.failed:
        reasons.append(f"Failed propositions: {len(lint_result.failed)}")
    
    foundational = [p for p in propositions if p.role == PropositionRole.FOUNDATIONAL]
    for prop in foundational:
        if prop.legitimacy == PropositionLegitimacy.SUSPENDED:
            reasons.append(f"Foundational proposition {prop.id} has suspended legitimacy")
    
    boundary_issues = check_foundational_boundaries(propositions)
    if boundary_issues:
        reasons.extend(boundary_issues)
    
    derived_issues = check_derived_support(propositions)
    if derived_issues:
        reasons.extend(derived_issues)
    
    if reasons:
        return "BLOCK", reasons
    
    if lint_result.conditional:
        return "CONDITIONAL", [f"Conditional propositions: {len(lint_result.conditional)}"]
    
    return "PASS", []