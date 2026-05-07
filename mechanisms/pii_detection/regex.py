"""PII detection using simple regex rules."""

from customization.regex_rules import load_custom_rules
from shared.regex_utils import run_regex_rules
from shared.result import GuardrailResult


MECHANISM_KEY = "pii_detection"

DEFAULT_RULES = [
    {
        "name": "Email address",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "explanation": "Detects email-address-like text.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "US phone number",
        "pattern": r"\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b",
        "explanation": "Detects common US phone-number-like text.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "SSN-like value",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "explanation": "Detects US SSN-like values.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "Credit-card-like value",
        "pattern": r"\b(?:\d[ -]*?){13,16}\b",
        "explanation": "Detects credit-card-like digit sequences.",
        "case_sensitive": False,
        "source": "default",
    },
]


def detect_pii_with_regex(text: str, show_matches: bool = True) -> GuardrailResult:
    custom_rules = load_custom_rules(MECHANISM_KEY)
    return run_regex_rules(
        text=text,
        default_rules=DEFAULT_RULES,
        custom_rules=custom_rules,
        safe_explanation="No PII regex rules matched the input.",
        unsafe_decision="blocked",
        safe_decision="allowed",
        show_matches=show_matches,
    )
