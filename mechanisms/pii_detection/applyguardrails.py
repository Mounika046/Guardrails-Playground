"""PII detection using OCI ApplyGuardrails."""

from integrations.applyguardrails.wrapper import check_pii_detection
from shared.result import GuardrailResult


def detect_pii_with_applyguardrails(
    text: str,
    compartment_id: str = "",
    config_profile: str = "",
) -> GuardrailResult:
    return check_pii_detection(
        text=text,
        compartment_id=compartment_id,
        config_profile=config_profile,
    )
