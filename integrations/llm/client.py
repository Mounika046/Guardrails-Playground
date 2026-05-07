"""OCI Generative AI chat client wrapper."""

from __future__ import annotations

from typing import Any

from config.settings import get_oci_settings


class OciLlmConfigError(RuntimeError):
    """Raised when the OCI LLM call cannot be configured."""


def chat_with_oci(
    prompt: str,
    system_prompt: str,
    model_id: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Call OCI Generative AI Chat using a Cohere chat request.

    OCI details stay here so mechanism modules only need prompt text and
    model parameters.
    """

    try:
        import oci
        from oci.generative_ai_inference import GenerativeAiInferenceClient
        from oci.generative_ai_inference.models import (
            ChatDetails,
            CohereChatRequest,
            OnDemandServingMode,
        )
    except ImportError as exc:
        raise OciLlmConfigError(
            "The OCI Python SDK is not installed. Install dependencies with "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    settings = get_oci_settings()
    selected_model_id = model_id.strip() or settings.default_llm_model_id
    temperature = _normalize_temperature(temperature)
    max_tokens = _normalize_max_tokens(max_tokens)

    if not settings.compartment_id:
        raise OciLlmConfigError("OCI_COMPARTMENT_ID is required for LLM checks.")
    if not selected_model_id:
        raise OciLlmConfigError("A Model ID is required for LLM checks.")

    if settings.config_file:
        oci_config = oci.config.from_file(
            file_location=settings.config_file,
            profile_name=settings.config_profile,
        )
    else:
        oci_config = oci.config.from_file(profile_name=settings.config_profile)
    client_kwargs = {"config": oci_config}
    if settings.genai_endpoint:
        client_kwargs["service_endpoint"] = settings.genai_endpoint

    client = GenerativeAiInferenceClient(**client_kwargs)

    chat_request = CohereChatRequest(
        message=prompt,
        preamble_override=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    chat_details = ChatDetails(
        compartment_id=settings.compartment_id,
        serving_mode=OnDemandServingMode(model_id=selected_model_id),
        chat_request=chat_request,
    )

    response = client.chat(chat_details)
    response_dict = oci.util.to_dict(response.data)

    return {
        "text": _extract_text(response.data),
        "model_id": selected_model_id,
        "oci_response": response_dict,
    }


def _extract_text(response_data: Any) -> str:
    chat_response = getattr(response_data, "chat_response", None)
    if chat_response is None:
        return ""

    text = getattr(chat_response, "text", None)
    if text:
        return text

    message = getattr(chat_response, "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, list):
        parts = []
        for item in content:
            item_text = getattr(item, "text", None)
            if item_text:
                parts.append(item_text)
        return "\n".join(parts)

    return str(chat_response)


def _normalize_temperature(temperature: float) -> float:
    if temperature < 0.0 or temperature > 1.0:
        raise OciLlmConfigError("Temperature must be between 0.0 and 1.0.")
    return temperature


def _normalize_max_tokens(max_tokens: int) -> int:
    if max_tokens < 50 or max_tokens > 1000:
        raise OciLlmConfigError("Maximum output tokens must be between 50 and 1000.")
    return max_tokens
