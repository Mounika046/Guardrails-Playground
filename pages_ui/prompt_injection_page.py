"""Prompt Injection Detection page."""

import streamlit as st

from app_components.customization_panels import (
    render_applyguardrails_display_options,
    render_llm_customization,
    render_regex_customization,
)
from app_components.inputs import render_runtime_text_area, render_sample_selector
from app_components.results import render_result
from config.settings import get_oci_settings
from mechanisms.prompt_injection_detection.applyguardrails import (
    detect_prompt_injection_with_applyguardrails,
)
from mechanisms.prompt_injection_detection.llm_prompt import (
    DEFAULT_FEW_SHOT_EXAMPLES as PROMPT_INJECTION_LLM_EXAMPLES,
    DEFAULT_POLICY_TEXT as PROMPT_INJECTION_LLM_POLICY,
    DEFAULT_SYSTEM_PROMPT as PROMPT_INJECTION_LLM_SYSTEM_PROMPT,
    detect_prompt_injection_with_llm,
)
from mechanisms.prompt_injection_detection.regex import (
    DEFAULT_RULES as PROMPT_INJECTION_REGEX_RULES,
    MECHANISM_KEY as PROMPT_INJECTION_REGEX_KEY,
    detect_prompt_injection_with_regex,
)
from shared.result import placeholder_result


MECHANISM = "Prompt Injection Detection"
APPROACHES = [
    "LLM / system-prompt based",
    "Regex-based",
    "ApplyGuardrails API",
]


def render_prompt_injection_page() -> None:
    st.title(MECHANISM)
    st.write("Identify attempts to override instructions or bypass safeguards.")

    approach = st.selectbox("Approach", APPROACHES, key="prompt_injection_approach")
    settings = _render_customization(approach)

    sample_text = render_sample_selector(MECHANISM, "prompt_injection")
    runtime_text = render_runtime_text_area(
        MECHANISM,
        sample_text,
        "prompt_injection",
    )

    if st.button("Run Check", type="primary", key="prompt_injection_run"):
        if approach == "LLM / system-prompt based":
            result = detect_prompt_injection_with_llm(
                text=runtime_text,
                system_prompt=settings["system_prompt"],
                policy_text=settings["policy_text"],
                few_shot_examples=settings["few_shot_examples"],
                model_id=settings["model_id"],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
            )
        elif approach == "Regex-based":
            result = detect_prompt_injection_with_regex(
                runtime_text,
                show_matches=settings.get("show_matches", True),
            )
        elif approach == "ApplyGuardrails API":
            result = detect_prompt_injection_with_applyguardrails(
                text=runtime_text,
            )
        else:
            result = placeholder_result(MECHANISM, approach)
            result.raw_output["input_preview"] = runtime_text[:120]
        render_result(result, show_raw_output=settings.get("show_raw_output", True))
    else:
        st.info("Choose an approach, review its customization options, then run a check.")


def _render_customization(approach: str) -> dict:
    if approach == "LLM / system-prompt based":
        return render_llm_customization(
            "prompt_injection_llm",
            PROMPT_INJECTION_LLM_SYSTEM_PROMPT,
            PROMPT_INJECTION_LLM_POLICY,
            PROMPT_INJECTION_LLM_EXAMPLES,
            default_model_id=get_oci_settings().default_llm_model_id,
        )
    if approach == "Regex-based":
        return render_regex_customization(
            "prompt_injection_regex",
            PROMPT_INJECTION_REGEX_KEY,
            PROMPT_INJECTION_REGEX_RULES,
        )
    return render_applyguardrails_display_options("prompt_injection_applyguardrails")
