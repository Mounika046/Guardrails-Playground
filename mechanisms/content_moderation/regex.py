"""Content moderation using simple regex rules."""

from customization.regex_rules import load_custom_rules
from shared.regex_utils import run_regex_rules
from shared.result import GuardrailResult


MECHANISM_KEY = "content_moderation"

DEFAULT_RULES = [
    {
        "name": "Threat language",
        "pattern": r"\b(threaten|hurt|attack|kill)\b",
        "explanation": "Flags direct violent or threatening language.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "Harassment language",
        "pattern": r"\b(insults?|insulting|harass(?:es|ing)?|bully(?:ing)?|humiliat(?:e|es|ing)|cruel)\b",
        "explanation": "Flags language commonly associated with harassment.",
        "case_sensitive": False,
        "source": "default",
    },
    {
        "name": "Self-harm indicator",
        "pattern": r"\b(self[- ]?harm|suicide|end my life)\b",
        "explanation": "Flags self-harm related wording.",
        "case_sensitive": False,
        "source": "default",
    },
]


def moderate_content_with_regex(text: str, show_matches: bool = True) -> GuardrailResult:
    custom_rules = load_custom_rules(MECHANISM_KEY)
    return run_regex_rules(
        text=text,
        default_rules=DEFAULT_RULES,
        custom_rules=custom_rules,
        safe_explanation="No content moderation regex rules matched the input.",
        unsafe_decision="blocked",
        safe_decision="allowed",
        show_matches=show_matches,
    )
