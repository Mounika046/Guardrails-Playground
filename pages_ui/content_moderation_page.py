"""Content Moderation page."""

import streamlit as st

from app_components.customization_panels import (
    render_applyguardrails_display_options,
    render_embeddings_customization,
    render_llm_customization,
    render_regex_customization,
)
from app_components.inputs import render_runtime_text_area, render_sample_selector
from app_components.results import render_result
from config.settings import get_oci_settings
from mechanisms.content_moderation.applyguardrails import moderate_content_with_applyguardrails
from mechanisms.content_moderation.embeddings import moderate_content_with_embeddings
from mechanisms.content_moderation.llm_prompt import (
    DEFAULT_FEW_SHOT_EXAMPLES as CONTENT_MODERATION_LLM_EXAMPLES,
    DEFAULT_POLICY_TEXT as CONTENT_MODERATION_LLM_POLICY,
    DEFAULT_SYSTEM_PROMPT as CONTENT_MODERATION_LLM_SYSTEM_PROMPT,
    moderate_content_with_llm,
)
from mechanisms.content_moderation.regex import (
    DEFAULT_RULES as CONTENT_MODERATION_REGEX_RULES,
    MECHANISM_KEY as CONTENT_MODERATION_REGEX_KEY,
    moderate_content_with_regex,
)
from shared.result import placeholder_result


MECHANISM = "Content Moderation"
APPROACHES = [
    "LLM / system-prompt based",
    "Embeddings-based",
    "Regex-based",
    "ApplyGuardrails API",
]


def render_content_moderation_page() -> None:
    st.title(MECHANISM)
    st.write("Evaluate text for unsafe or policy-sensitive content.")

    approach = st.selectbox("Approach", APPROACHES, key="content_moderation_approach")
    settings = _render_customization(approach)

    if approach == "Embeddings-based":
        sample_text = ""
    else:
        sample_text = render_sample_selector(MECHANISM, "content_moderation")
    runtime_text = render_runtime_text_area(
        MECHANISM,
        sample_text,
        "content_moderation",
    )

    if st.button("Run Check", type="primary", key="content_moderation_run"):
        if approach == "LLM / system-prompt based":
            result = moderate_content_with_llm(
                text=runtime_text,
                system_prompt=settings["system_prompt"],
                policy_text=settings["policy_text"],
                few_shot_examples=settings["few_shot_examples"],
                model_id=settings["model_id"],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
            )
        elif approach == "Embeddings-based":
            result = moderate_content_with_embeddings(
                text=runtime_text,
                vector_store_id=settings["vector_store_id"],
                top_k=settings["top_k"],
                min_match_score=settings["min_match_score"],
            )
        elif approach == "Regex-based":
            result = moderate_content_with_regex(
                runtime_text,
                show_matches=settings.get("show_matches", True),
            )
        elif approach == "ApplyGuardrails API":
            result = moderate_content_with_applyguardrails(
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
            "content_moderation_llm",
            CONTENT_MODERATION_LLM_SYSTEM_PROMPT,
            CONTENT_MODERATION_LLM_POLICY,
            CONTENT_MODERATION_LLM_EXAMPLES,
            default_model_id=get_oci_settings().default_llm_model_id,
        )
    if approach == "Embeddings-based":
        return render_embeddings_customization("content_moderation_embeddings")
    if approach == "Regex-based":
        return render_regex_customization(
            "content_moderation_regex",
            CONTENT_MODERATION_REGEX_KEY,
            CONTENT_MODERATION_REGEX_RULES,
        )
    return render_applyguardrails_display_options("content_moderation_applyguardrails")
