"""OCI ApplyGuardrails client wrapper."""

from __future__ import annotations

from typing import Any

from config.settings import get_oci_settings


class ApplyGuardrailsConfigError(RuntimeError):
    """Raised when ApplyGuardrails cannot be configured."""


def apply_guardrails_to_text(
    text: str,
    guardrail_configs: Any,
    compartment_id: str = "",
    config_profile: str = "",
) -> dict[str, Any]:
    """Call OCI Generative AI Inference ApplyGuardrails for one text input."""

    try:
        import oci
        from oci.generative_ai_inference import GenerativeAiInferenceClient
        from oci.generative_ai_inference.models import ApplyGuardrailsDetails, GuardrailsTextInput
    except ImportError as exc:
        raise ApplyGuardrailsConfigError(
            "The OCI Python SDK is not installed. Install dependencies with "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    settings = get_oci_settings()
    selected_compartment_id = compartment_id.strip() or settings.compartment_id
    selected_profile = config_profile.strip() or settings.config_profile

    if not selected_compartment_id:
        raise ApplyGuardrailsConfigError("A compartment ID is required for ApplyGuardrails.")

    if settings.config_file:
        oci_config = oci.config.from_file(
            file_location=settings.config_file,
            profile_name=selected_profile,
        )
    else:
        oci_config = oci.config.from_file(profile_name=selected_profile)

    client_kwargs = {"config": oci_config}
    if settings.genai_endpoint:
        client_kwargs["service_endpoint"] = settings.genai_endpoint

    client = GenerativeAiInferenceClient(**client_kwargs)
    details = ApplyGuardrailsDetails(
        input=GuardrailsTextInput(
            content=text,
            language_code="en",
        ),
        guardrail_configs=guardrail_configs,
        compartment_id=selected_compartment_id,
    )

    response = client.apply_guardrails(details)
    return oci.util.to_dict(response.data)
