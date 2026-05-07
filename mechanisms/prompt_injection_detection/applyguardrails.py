"""Prompt injection detection using OCI ApplyGuardrails."""

from integrations.applyguardrails.wrapper import check_prompt_injection
from shared.result import GuardrailResult


def detect_prompt_injection_with_applyguardrails(
    text: str,
    compartment_id: str = "",
    config_profile: str = "",
) -> GuardrailResult:
    return check_prompt_injection(
        text=text,
        compartment_id=compartment_id,
        config_profile=config_profile,
    )
