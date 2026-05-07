"""Streamlit entrypoint for the Guardrails Playground."""

import streamlit as st

from pages_ui.content_moderation_page import render_content_moderation_page
from pages_ui.home import render_home_page
from pages_ui.pii_detection_page import render_pii_detection_page
from pages_ui.prompt_injection_page import render_prompt_injection_page


PAGES = {
    "Home": render_home_page,
    "Content Moderation": render_content_moderation_page,
    "PII Detection": render_pii_detection_page,
    "Prompt Injection Detection": render_prompt_injection_page,
}

PAGE_STATE_KEY = "selected_page"
PAGE_REQUEST_KEY = "requested_page"
PAGE_QUERY_PARAM = "page"


def main() -> None:
    st.set_page_config(
        page_title="Guardrails Playground",
        page_icon="GP",
        layout="wide",
    )

    if PAGE_STATE_KEY not in st.session_state:
        st.session_state[PAGE_STATE_KEY] = _page_from_query_params()

    if PAGE_REQUEST_KEY in st.session_state:
        st.session_state[PAGE_STATE_KEY] = st.session_state.pop(PAGE_REQUEST_KEY)

    st.sidebar.title("Guardrails Playground")
    st.sidebar.radio(
        "Navigation",
        list(PAGES.keys()),
        key=PAGE_STATE_KEY,
    )

    _set_page_query_param(st.session_state[PAGE_STATE_KEY])

    st.sidebar.divider()
    st.sidebar.caption(
        "Security mechanisms first, with supported approaches inside each page."
    )

    PAGES[st.session_state[PAGE_STATE_KEY]]()


def _page_from_query_params() -> str:
    page = st.query_params.get(PAGE_QUERY_PARAM, "Home")
    return page if page in PAGES else "Home"


def _set_page_query_param(page: str) -> None:
    st.query_params[PAGE_QUERY_PARAM] = page


if __name__ == "__main__":
    main()
