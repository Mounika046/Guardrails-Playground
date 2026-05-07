"""Content moderation using OCI ApplyGuardrails."""

from integrations.applyguardrails.wrapper import check_content_moderation
from shared.result import GuardrailResult


def moderate_content_with_applyguardrails(
    text: str,
    compartment_id: str = "",
    config_profile: str = "",
) -> GuardrailResult:
    return check_content_moderation(
        text=text,
        compartment_id=compartment_id,
        config_profile=config_profile,
    )
