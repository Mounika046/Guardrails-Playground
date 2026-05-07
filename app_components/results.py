"""Shared result display components."""

import streamlit as st

from shared.result import GuardrailResult


def render_result(result: GuardrailResult, show_raw_output: bool = True) -> None:
    st.subheader("Result")

    st.write("**Decision**")
    st.code(result.decision)

    st.write("**Explanation**")
    st.write(result.explanation)

    if result.matches:
        st.write("**Matches / Entities**")
        st.dataframe(result.matches, use_container_width=True)

    if show_raw_output and result.raw_output is not None:
        with st.expander("Raw output"):
            st.json(result.raw_output)
