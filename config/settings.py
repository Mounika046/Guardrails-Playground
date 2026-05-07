"""Simple environment-based settings for OCI-backed approaches."""

from __future__ import annotations

import os
from dataclasses import dataclass


try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


@dataclass(frozen=True)
class OciSettings:
    config_file: str
    config_profile: str
    compartment_id: str
    genai_endpoint: str
    default_llm_model_id: str
    vector_store_id: str
    project_id: str


def get_oci_settings() -> OciSettings:
    return OciSettings(
        config_file=os.getenv("OCI_CONFIG_FILE", ""),
        config_profile=os.getenv("OCI_CONFIG_PROFILE", "DEFAULT"),
        compartment_id=os.getenv("OCI_COMPARTMENT_ID", ""),
        genai_endpoint=os.getenv("OCI_GENAI_ENDPOINT", ""),
        default_llm_model_id=os.getenv("OCI_LLM_MODEL_ID", ""),
        vector_store_id=os.getenv("OCI_VECTOR_STORE_ID", ""),
        project_id=os.getenv("OCI_PROJECT_ID", ""),
    )
