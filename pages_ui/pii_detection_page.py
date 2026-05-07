"""PII Detection page."""

import streamlit as st

from app_components.customization_panels import (
    render_applyguardrails_display_options,
    render_regex_customization,
)
from app_components.inputs import render_runtime_text_area, render_sample_selector
from app_components.results import render_result
from mechanisms.pii_detection.applyguardrails import detect_pii_with_applyguardrails
from mechanisms.pii_detection.regex import (
    DEFAULT_RULES as PII_REGEX_RULES,
    MECHANISM_KEY as PII_REGEX_KEY,
    detect_pii_with_regex,
)
from shared.result import placeholder_result


MECHANISM = "PII Detection"
APPROACHES = [
    "Regex-based",
    "ApplyGuardrails API",
]


def render_pii_detection_page() -> None:
    st.title(MECHANISM)
    st.write("Detect personally identifiable information in text.")

    approach = st.selectbox("Approach", APPROACHES, key="pii_detection_approach")
    settings = _render_customization(approach)

    sample_text = render_sample_selector(MECHANISM, "pii_detection")
    runtime_text = render_runtime_text_area(MECHANISM, sample_text, "pii_detection")

    if st.button("Run Check", type="primary", key="pii_detection_run"):
        if approach == "Regex-based":
            result = detect_pii_with_regex(
                runtime_text,
                show_matches=settings.get("show_matches", True),
            )
        elif approach == "ApplyGuardrails API":
            result = detect_pii_with_applyguardrails(
                text=runtime_text,
            )
        else:
            result = placeholder_result(MECHANISM, approach)
            result.raw_output["input_preview"] = runtime_text[:120]
        render_result(result, show_raw_output=settings.get("show_raw_output", True))
    else:
        st.info("Choose an approach, review its customization options, then run a check.")


def _render_customization(approach: str) -> dict:
    if approach == "Regex-based":
        return render_regex_customization(
            "pii_detection_regex",
            PII_REGEX_KEY,
            PII_REGEX_RULES,
            entity_label="PII entity name",
        )
    return render_applyguardrails_display_options("pii_detection_applyguardrails")
