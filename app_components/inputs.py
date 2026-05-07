"""Shared input controls for mechanism pages."""

import streamlit as st

from samples.sample_inputs import get_sample_text, sample_names_for


def render_sample_selector(mechanism: str, key_prefix: str) -> str:
    sample_name = st.selectbox(
        "Sample input",
        sample_names_for(mechanism),
        key=f"{key_prefix}_sample",
    )
    return get_sample_text(mechanism, sample_name)


def render_runtime_text_area(mechanism: str, default_text: str, key_prefix: str) -> str:
    text_key = f"{key_prefix}_runtime_text"
    last_sample_key = f"{key_prefix}_last_sample_text"

    if st.session_state.get(last_sample_key) != default_text:
        st.session_state[text_key] = default_text
        st.session_state[last_sample_key] = default_text

    return st.text_area(
        "Runtime text to evaluate",
        height=180,
        key=text_key,
        help=f"Enter the {mechanism.lower()} input you want this approach to evaluate.",
    )
