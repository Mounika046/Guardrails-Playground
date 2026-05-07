"""Home page for the playground."""

import streamlit as st


MECHANISMS = [
    {
        "name": "Content Moderation",
        "description": "Evaluate text for unsafe or policy-sensitive content.",
        "approaches": [
            "LLM / system-prompt based",
            "Embeddings-based",
            "Regex-based",
            "ApplyGuardrails API",
        ],
    },
    {
        "name": "PII Detection",
        "description": "Detect personally identifiable information in text.",
        "approaches": [
            "Regex-based",
            "ApplyGuardrails API",
        ],
    },
    {
        "name": "Prompt Injection Detection",
        "description": "Identify attempts to override instructions or bypass safeguards.",
        "approaches": [
            "LLM / system-prompt based",
            "Regex-based",
            "ApplyGuardrails API",
        ],
    },
]


def render_home_page() -> None:
    st.title("Guardrails Playground")
    st.write(
        "A simple reference app for comparing safety mechanisms and implementation "
        "approaches. Choose a mechanism below or from the sidebar to start."
    )

    cols = st.columns(3)
    for column, mechanism in zip(cols, MECHANISMS):
        with column:
            with st.container(border=True):
                st.markdown(f"**{mechanism['name']}**")
                st.write(mechanism["description"])
                st.write("**Supported approaches**")
                for approach in mechanism["approaches"]:
                    st.write(f"- {approach}")

                if st.button(
                    f"Open {mechanism['name']}",
                    key=f"open_{mechanism['name'].lower().replace(' ', '_')}",
                    use_container_width=True,
                ):
                    st.session_state["requested_page"] = mechanism["name"]
                    st.query_params["page"] = mechanism["name"]
                    st.rerun()
