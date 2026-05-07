"""Prompt injection detection using simple regex rules."""

from customization.regex_rules import load_custom_rules
from shared.regex_utils import run_regex_rules
from shared.result import GuardrailResult


MECHANISM_KEY = "prompt_injection_detection"

DEFAULT_RULES = [
    {
        "name": "Ignore instructions",
        "pattern": r"\b(ignore|disregard)\b.{0,80}\b(previous|above|prior)\b.{0,40}\binstructions?\b",
        "explanation": "Flags attempts to ignore previous instructions.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "Reveal system prompt",
        "pattern": r"\b(reveal|show|print|display)\b.{0,80}\b(system prompt|hidden instructions|developer message)\b",
        "explanation": "Flags attempts to reveal hidden prompts or developer instructions.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "Bypass rules",
        "pattern": r"\b(bypass|override|disable)\b.{0,80}\b(rules|safety|guardrails|policy)\b",
        "explanation": "Flags attempts to bypass or disable safety rules.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "Secret extraction",
        "pattern": r"\b(show|reveal|print|exfiltrate)\b.{0,80}\b(secrets?|credentials?|api keys?|tokens?)\b",
        "explanation": "Flags attempts to extract secrets or credentials.",
        "case_sensitive": False,
        "source": "default",
    },
]


def detect_prompt_injection_with_regex(
    text: str,
    show_matches: bool = True,
) -> GuardrailResult:
    custom_rules = load_custom_rules(MECHANISM_KEY)
    return run_regex_rules(
        text=text,
        default_rules=DEFAULT_RULES,
        custom_rules=custom_rules,
        safe_explanation="No prompt injection regex rules matched the input.",
        unsafe_decision="blocked",
        safe_decision="allowed",
        show_matches=show_matches,
    )
