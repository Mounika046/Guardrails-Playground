"""Small helpers shared by regex-based approaches."""

from __future__ import annotations

import re
from typing import Any

from shared.result import GuardrailResult


def run_regex_rules(
    text: str,
    default_rules: list[dict[str, Any]],
    custom_rules: list[dict[str, Any]] | None = None,
    safe_explanation: str = "No regex rules matched the input.",
    unsafe_decision: str = "match_found",
    safe_decision: str = "no_match",
    show_matches: bool = True,
) -> GuardrailResult:
    rules = default_rules + [rule for rule in custom_rules or [] if rule.get("enabled", True)]
    matches = []
    errors = []

    for rule in rules:
        flags = 0 if rule.get("case_sensitive", False) else re.IGNORECASE
        pattern = rule.get("pattern", "")

        try:
            found = list(re.finditer(pattern, text, flags))
        except re.error as exc:
            errors.append(
                {
                    "rule_name": rule.get("name", "Unnamed rule"),
                    "pattern": pattern,
                    "error": str(exc),
                }
            )
            continue

        for match in found:
            match_value = match.group(0) if show_matches else "[hidden]"
            matches.append(
                {
                    "rule_name": rule.get("name", "Unnamed rule"),
                    "pattern": pattern,
                    "matched_text": match_value,
                    "start": match.start(),
                    "end": match.end(),
                    "explanation": rule.get("explanation", ""),
                    "source": rule.get("source", "default"),
                }
            )

    if matches:
        explanation = f"{len(matches)} regex match(es) found."
        decision = unsafe_decision
    elif errors:
        explanation = "No matches found, but one or more regex rules had errors."
        decision = "rule_error"
    else:
        explanation = safe_explanation
        decision = safe_decision

    return GuardrailResult(
        decision=decision,
        explanation=explanation,
        raw_output={
            "rules_checked": len(rules),
            "matches_found": len(matches),
            "rule_errors": errors,
        },
        matches=matches,
    )
