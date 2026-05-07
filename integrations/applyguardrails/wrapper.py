"""Mechanism-friendly wrappers around OCI ApplyGuardrails."""

from __future__ import annotations

from typing import Any

from integrations.applyguardrails.oci_client import (
    ApplyGuardrailsConfigError,
    apply_guardrails_to_text,
)
from shared.result import GuardrailResult


def check_content_moderation(
    text: str,
    compartment_id: str = "",
    config_profile: str = "",
) -> GuardrailResult:
    try:
        from oci.generative_ai_inference.models import (
            ContentModerationConfiguration,
            GuardrailConfigs,
        )
    except ImportError as exc:
        return _sdk_missing_result(exc)

    configs = GuardrailConfigs(
        content_moderation_config=ContentModerationConfiguration(
            categories=["OVERALL", "BLOCKLIST"],
        )
    )
    return _run_and_convert(
        text=text,
        configs=configs,
        compartment_id=compartment_id,
        config_profile=config_profile,
        converter=_convert_content_moderation,
    )


def check_pii_detection(
    text: str,
    compartment_id: str = "",
    config_profile: str = "",
) -> GuardrailResult:
    try:
        from oci.generative_ai_inference.models import (
            GuardrailConfigs,
            PersonallyIdentifiableInformationConfiguration,
        )
    except ImportError as exc:
        return _sdk_missing_result(exc)

    configs = GuardrailConfigs(
        personally_identifiable_information_config=PersonallyIdentifiableInformationConfiguration(
            types=["PERSON", "EMAIL", "TELEPHONE_NUMBER"],
        )
    )
    return _run_and_convert(
        text=text,
        configs=configs,
        compartment_id=compartment_id,
        config_profile=config_profile,
        converter=_convert_pii,
    )


def check_prompt_injection(
    text: str,
    compartment_id: str = "",
    config_profile: str = "",
) -> GuardrailResult:
    try:
        from oci.generative_ai_inference.models import GuardrailConfigs, PromptInjectionConfiguration
    except ImportError as exc:
        return _sdk_missing_result(exc)

    configs = GuardrailConfigs(
        prompt_injection_config=PromptInjectionConfiguration()
    )
    return _run_and_convert(
        text=text,
        configs=configs,
        compartment_id=compartment_id,
        config_profile=config_profile,
        converter=_convert_prompt_injection,
    )


def _run_and_convert(
    text: str,
    configs: Any,
    compartment_id: str,
    config_profile: str,
    converter,
) -> GuardrailResult:
    try:
        raw_output = apply_guardrails_to_text(
            text=text,
            guardrail_configs=configs,
            compartment_id=compartment_id,
            config_profile=config_profile,
        )
    except ApplyGuardrailsConfigError as exc:
        return GuardrailResult(
            decision="configuration_error",
            explanation=str(exc),
            raw_output={"error": str(exc)},
        )
    except Exception as exc:
        return GuardrailResult(
            decision="oci_error",
            explanation=f"OCI ApplyGuardrails call failed: {exc}",
            raw_output={
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )

    return converter(raw_output)


def _convert_content_moderation(raw_output: dict[str, Any]) -> GuardrailResult:
    categories = _get(raw_output, "results", "content_moderation", "categories") or []
    matches = [
        {
            "category": item.get("name"),
            "score": item.get("score"),
        }
        for item in categories
        if item.get("score", 0) > 0
    ]

    decision = "blocked" if matches else "allowed"
    explanation = (
        f"{len(matches)} content moderation category/categories flagged."
        if matches
        else "ApplyGuardrails did not flag content moderation categories."
    )
    return GuardrailResult(
        decision=decision,
        explanation=explanation,
        raw_output=raw_output,
        matches=matches,
    )


def _convert_pii(raw_output: dict[str, Any]) -> GuardrailResult:
    entities = _get(raw_output, "results", "personally_identifiable_information") or []
    matches = [
        {
            "label": item.get("label"),
            "text": item.get("text"),
            "score": item.get("score"),
            "offset": item.get("offset"),
            "length": item.get("length"),
        }
        for item in entities
    ]

    decision = "blocked" if matches else "allowed"
    explanation = (
        f"{len(matches)} PII entity/entities detected."
        if matches
        else "ApplyGuardrails did not detect PII entities."
    )
    return GuardrailResult(
        decision=decision,
        explanation=explanation,
        raw_output=raw_output,
        matches=matches,
    )


def _convert_prompt_injection(raw_output: dict[str, Any]) -> GuardrailResult:
    result = _get(raw_output, "results", "prompt_injection") or {}
    score = result.get("score", 0)
    decision = "blocked" if score > 0 else "allowed"
    explanation = f"ApplyGuardrails prompt injection score: {score}."
    matches = [{"score": score}] if score > 0 else []

    return GuardrailResult(
        decision=decision,
        explanation=explanation,
        raw_output=raw_output,
        matches=matches,
    )


def _get(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _sdk_missing_result(exc: ImportError) -> GuardrailResult:
    message = (
        "The OCI Python SDK is not installed. Install dependencies with "
        "`python -m pip install -r requirements.txt`."
    )
    return GuardrailResult(
        decision="configuration_error",
        explanation=message,
        raw_output={"error": str(exc)},
    )
