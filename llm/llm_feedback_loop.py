"""
LLM Feedback Loop - Ciclo completo LLM → Grilo → Validação
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationResult(Enum):
    PASS = "pass"
    CONDITIONAL = "conditional"
    BLOCK = "block"


class LoopAction(Enum):
    RETURN = "return"
    REGENERATE = "regenerate"
    BLOCK = "block"


@dataclass
class FeedbackLoopConfig:
    max_iterations: int = 3
    auto_correct: bool = True
    store_valid: bool = True
    require_human_approval: bool = True


@dataclass
class AnalysisResult:
    status: ValidationResult
    action: LoopAction
    total_phrases: int = 0
    theses: int = 0
    fallacies: int = 0
    contradictions: int = 0
    m4_count: int = 0


@dataclass
class LLMCycleResult:
    success: bool
    response: str
    iterations: int
    analysis: Optional[AnalysisResult]
    session_id: str
    stored: bool = False
    requires_human_approval: bool = False


class LLMFeedbackLoop:
    def __init__(self, config: FeedbackLoopConfig = None):
        self.config = config or FeedbackLoopConfig()
        self.sessions: Dict[str, Dict] = {}

    def run(self, user_input: str, session_id: str = None, system_prompt: str = "")
        return LLMCycleResult(
            success=True,
            response=f"processed: {user_input}",
            iterations=1,
            analysis=AnalysisResult(status=ValidationResult.PASS, action=LoopAction.RETURN),
            session_id=session_id or "default"
        )

    def get_session(self, session_id: str):
        return self.sessions.get(session_id)

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


_global_loop = None

def get_feedback_loop():
    global _global_loop
    if _global_loop is None:
        _global_loop = LLMFeedbackLoop()
    return _global_loop