"""
Cognitive Lint — Validate outputs for blocking patterns

Detects patterns that should block or warn in epistemic outputs.
"""

import re
from dataclasses import dataclass
from enum import Enum


class LintState(str, Enum):
    """Lint result state."""

    ACCEPT = "accept"
    WARN = "warn"
    REJECT = "reject"


@dataclass
class LintResult:
    """Result of cognitive lint."""

    state: LintState
    message: str
    issues: list[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class CognitiveLint:
    """
    Cognitive lint for epistemic validation.

    Blocks:
    - Leading questions (bypass patterns)
    - Authority claims without evidence
    - Unresolved TODO/FIXME markers

    Warns:
    - Hedging language
    - Subjective qualifiers
    - Weak assertions
    """

    BLOCK_PATTERNS = [
        (r"\b(just|simply)\b.*\?", "Leading question pattern - don't assume answer"),
        (
            r"\b(can|could|would|should)\s+we\s+(just|simply)\s",
            "Bypass pattern - don't skip validation",
        ),
        (
            r"\bThis\s+is\s+(obviously|clearly|trivially)\s",
            "Fluency assumption - evidence required",
        ),
        (r"\bTrust\s+me\b", "Authority claim without evidence"),
        (r"\bBelieve\s+me\b", "Authority claim without evidence"),
        (r"^\s*\(?(?:Note|TODO|FIXME|HACK)\b", "Unresolved marker"),
    ]

    WARN_PATTERNS = [
        (r"\b(maybe|perhaps|possibly|probably)\b", "Hedging detected"),
        (r"\bI\s+think\b", "Subjective qualifier"),
        (r"\bIt\s+seems\b", "Weak assertion"),
        (r"\bmight\s+be\b", "Hedging detected"),
        (r"\bcould\s+be\b", "Hedging detected"),
    ]

    def lint(self, text: str) -> LintResult:
        """
        Lint text for blocking patterns.

        Args:
            text: Text to lint

        Returns:
            LintResult with state and issues
        """
        issues = []

        # Check blocking patterns
        for pattern, message in self.BLOCK_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                issues.append(message)
                return LintResult(
                    state=LintState.REJECT,
                    message="Blocking pattern detected",
                    issues=issues,
                )

        # Check warning patterns
        for pattern, message in self.WARN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                issues.append(message)

        if issues:
            return LintResult(
                state=LintState.WARN,
                message="Warning patterns detected",
                issues=issues,
            )

        return LintResult(
            state=LintState.ACCEPT,
            message="No blocking patterns detected",
        )

    def is_blocking(self, text: str) -> bool:
        """Check if text has blocking patterns."""
        return self.lint(text).state == LintState.REJECT

    def is_warn(self, text: str) -> bool:
        """Check if text has warning patterns."""
        return self.lint(text).state == LintState.WARN
