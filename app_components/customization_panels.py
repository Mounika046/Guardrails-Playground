"""Placeholder customization panels for each approach."""

import streamlit as st

from config.settings import get_oci_settings
from customization.regex_rules import add_custom_rule, load_custom_rules, reset_custom_rules, save_custom_rules
from integrations.vector_store.files import (
    reset_tracked_vector_files,
    tracked_files_for_store,
    upload_manual_reference_text,
    upload_reference_file,
)


def render_llm_customization(
    key_prefix: str,
    default_system_prompt: str,
    default_policy_text: str,
    default_few_shot_examples: str,
    default_model_id: str = "",
) -> dict:
    with st.expander("LLM customization", expanded=True):
        st.caption(
            "Uses OCI Generative AI Chat. OCI profile, compartment, and endpoint "
            "come from environment variables."
        )
        system_prompt = st.text_area(
            "System prompt",
            value=default_system_prompt,
            height=220,
            key=f"{key_prefix}_system_prompt",
        )
        policy_text = st.text_area(
            "Policy text",
            value=default_policy_text,
            height=260,
            key=f"{key_prefix}_policy_text",
        )
        few_shot_examples = st.text_area(
            "Few-shot examples",
            value=default_few_shot_examples,
            height=280,
            key=f"{key_prefix}_few_shot_examples",
        )
        model_id = st.text_input(
            "OCI Cohere model ID",
            value=default_model_id,
            placeholder="Example: cohere.command-r-plus-08-2024",
            key=f"{key_prefix}_model_id",
        )
        temperature = st.number_input(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key=f"{key_prefix}_temperature",
            help="Lower values are more stable. This playground limits temperature to 0.0-1.0 for guardrail checks.",
        )
        max_tokens = st.number_input(
            "Maximum output tokens",
            min_value=50,
            max_value=1000,
            value=300,
            step=50,
            key=f"{key_prefix}_max_tokens",
            help="Allowed range is 50-1000. Very low values can cut off JSON responses.",
        )
        show_raw = st.checkbox(
            "Show raw LLM response",
            value=True,
            key=f"{key_prefix}_show_raw_llm",
        )

    return {
        "system_prompt": system_prompt,
        "policy_text": policy_text,
        "few_shot_examples": few_shot_examples,
        "model_id": model_id,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "show_raw_output": show_raw,
    }


def render_embeddings_customization(key_prefix: str) -> dict:
    settings = get_oci_settings()
    with st.expander("Embeddings customization", expanded=True):
        st.caption(
            "Reference files/text are added to the existing OCI Vector Store. "
            "The runtime textarea below is still the text being evaluated."
        )
        vector_store_id = st.text_input(
            "OCI Vector Store ID",
            value=settings.vector_store_id,
            key=f"{key_prefix}_vector_store_id",
        )

        _render_tracked_vector_files(vector_store_id)

        uploaded_files = st.file_uploader(
            "Upload reference files",
            accept_multiple_files=True,
            key=f"{key_prefix}_reference_files",
        )
        if st.button("Add Uploaded Files", key=f"{key_prefix}_add_uploaded_files"):
            if not uploaded_files:
                st.warning("Choose one or more files before adding them.")
            else:
                with st.spinner("Uploading and indexing reference files..."):
                    for uploaded_file in uploaded_files:
                        upload_reference_file(
                            file_obj=uploaded_file,
                            filename=uploaded_file.name,
                            vector_store_id=vector_store_id,
                            source="upload",
                        )
                st.success("Uploaded files were added to the vector store.")
                st.rerun()

        manual_reference_text = st.text_area(
            "Manual reference text",
            value="",
            height=120,
            key=f"{key_prefix}_manual_reference_text",
        )
        if st.button("Add Manual Reference Text", key=f"{key_prefix}_add_manual_text"):
            if not manual_reference_text.strip():
                st.warning("Enter manual reference text before adding it.")
            else:
                with st.spinner("Adding manual reference text to the vector store..."):
                    upload_manual_reference_text(
                        text=manual_reference_text,
                        vector_store_id=vector_store_id,
                    )
                st.success("Manual reference text was added to the vector store.")
                st.rerun()

        if st.button("Reset Playground Vector Files", key=f"{key_prefix}_reset_vector_files"):
            with st.spinner("Deleting files added by this playground..."):
                reset_results = reset_tracked_vector_files(vector_store_id)
            st.success(f"Reset complete. Removed {len(reset_results)} tracked file(s).")
            st.rerun()

        top_k = st.number_input(
            "Top-K retrieval count",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            key=f"{key_prefix}_top_k",
        )
        min_match_score = st.number_input(
            "Minimum match score",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05,
            key=f"{key_prefix}_min_match_score",
            help="Only matches at or above this score affect the decision.",
        )
        show_raw = st.checkbox(
            "Show raw vector response",
            value=True,
            key=f"{key_prefix}_show_raw_vector",
        )

    return {
        "vector_store_id": vector_store_id,
        "uploaded_files": uploaded_files,
        "manual_reference_text": manual_reference_text,
        "top_k": top_k,
        "min_match_score": min_match_score,
        "show_raw_output": show_raw,
    }


def _render_tracked_vector_files(vector_store_id: str) -> None:
    try:
        tracked_files = tracked_files_for_store(vector_store_id)
    except Exception:
        tracked_files = []

    st.write("**Files added by this playground**")
    if not tracked_files:
        st.caption("No playground-added vector store files tracked yet.")
        return

    st.dataframe(
        [
            {
                "Filename": item.get("filename"),
                "File ID": item.get("file_id"),
                "Source": item.get("source"),
                "Created at": item.get("created_at"),
            }
            for item in tracked_files
        ],
        use_container_width=True,
    )


def render_regex_customization(
    key_prefix: str,
    mechanism_key: str,
    default_rules: list[dict],
    entity_label: str = "Rule name",
) -> dict:
    with st.expander("Regex customization", expanded=True):
        st.write("**Default rules**")
        st.dataframe(
            [
                {
                    entity_label: rule["name"],
                    "Pattern": rule["pattern"],
                    "Explanation": rule["explanation"],
                    "Case-sensitive": rule.get("case_sensitive", False),
                }
                for rule in default_rules
            ],
            use_container_width=True,
        )

        active_custom_rules = load_custom_rules(mechanism_key)
        st.write("**Saved custom rules**")
        if active_custom_rules:
            _render_custom_rules_table(
                key_prefix,
                mechanism_key,
                active_custom_rules,
                entity_label,
            )
            active_custom_rules = load_custom_rules(mechanism_key)
        else:
            st.caption("No custom regex rules added yet.")

        if st.button("Reset Custom Rules", key=f"{key_prefix}_reset_rules"):
            reset_custom_rules(mechanism_key)
            st.rerun()

        st.write("**Add custom rule**")
        with st.form(f"{key_prefix}_add_rule_form", clear_on_submit=True):
            rule_name = st.text_input(entity_label, value="")
            pattern = st.text_input("Regex pattern", value="")
            explanation = st.text_area("Explanation message", value="", height=80)
            case_sensitive = st.checkbox(
                "Case-sensitive matching",
                value=False,
                help="When off, the rule matches uppercase and lowercase text.",
            )
            add_clicked = st.form_submit_button("Add Custom Rule")

        show_matches = st.checkbox(
            "Show matched text",
            value=True,
            key=f"{key_prefix}_show_matches",
        )

        if add_clicked:
            if not rule_name.strip() or not pattern.strip():
                st.warning("Enter both a name and a regex pattern before adding a rule.")
            else:
                add_custom_rule(
                    mechanism_key,
                    {
                        "name": rule_name.strip(),
                        "pattern": pattern.strip(),
                        "explanation": explanation.strip(),
                        "case_sensitive": case_sensitive,
                        "enabled": True,
                        "source": "custom",
                    },
                )
                st.rerun()

    return {
        "custom_rules": active_custom_rules,
        "rule_name": rule_name,
        "pattern": pattern,
        "explanation": explanation,
        "case_sensitive": case_sensitive,
        "show_matches": show_matches,
        "show_raw_output": True,
    }


def _render_custom_rules_table(
    key_prefix: str,
    mechanism_key: str,
    custom_rules: list[dict],
    entity_label: str,
) -> None:
    table_rows = []

    for index, rule in enumerate(custom_rules):
        table_rows.append(
            {
                "Enabled": rule.get("enabled", True),
                "Rule number": index,
                entity_label: rule.get("name", f"Custom rule {index + 1}"),
                "Pattern": rule.get("pattern", ""),
                "Explanation": rule.get("explanation", ""),
                "Case-sensitive": rule.get("case_sensitive", False),
            }
        )

    edited_rows = st.data_editor(
        table_rows,
        hide_index=True,
        use_container_width=True,
        disabled=[entity_label, "Pattern", "Explanation", "Case-sensitive", "Rule number"],
        column_config={
            "Enabled": st.column_config.CheckboxColumn("Enabled"),
            "Rule number": None,
        },
        key=f"{key_prefix}_custom_rules_editor",
    )

    if hasattr(edited_rows, "to_dict"):
        rows = edited_rows.to_dict("records")
    else:
        rows = edited_rows

    updated_rules = [dict(rule) for rule in custom_rules]
    for row in rows:
        updated_rules[row["Rule number"]]["enabled"] = row["Enabled"]

    save_custom_rules(mechanism_key, updated_rules)


def render_applyguardrails_display_options(key_prefix: str) -> dict:
    with st.expander("ApplyGuardrails output", expanded=True):
        st.caption("ApplyGuardrails uses OCI configuration from `.env`.")
        show_raw = st.checkbox(
            "Show raw OCI response",
            value=True,
            key=f"{key_prefix}_show_raw_oci",
        )

    return {"show_raw_output": show_raw}
