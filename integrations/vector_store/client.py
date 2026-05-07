"""OCI OpenAI-compatible Vector Store clients."""

from __future__ import annotations

from urllib.parse import urlparse

from config.settings import get_oci_settings


class VectorStoreConfigError(RuntimeError):
    """Raised when OCI Vector Store settings are incomplete."""


def get_vector_store_id(vector_store_id: str = "") -> str:
    settings = get_oci_settings()
    selected = vector_store_id.strip() or settings.vector_store_id
    if not selected:
        raise VectorStoreConfigError("OCI_VECTOR_STORE_ID is required.")
    return selected


def create_vector_store_clients():
    """Return control-plane and data-plane OCI OpenAI-compatible clients."""

    try:
        from oci_openai import OciOpenAI, OciUserPrincipalAuth
    except ImportError as exc:
        raise VectorStoreConfigError(
            "The oci-openai package is not installed. Install dependencies with "
            "`python -m pip install -r requirements.txt`."
        ) from exc

    settings = get_oci_settings()
    if not settings.compartment_id:
        raise VectorStoreConfigError("OCI_COMPARTMENT_ID is required.")
    if not settings.project_id:
        raise VectorStoreConfigError("OCI_PROJECT_ID is required.")

    region = _region_from_endpoint(settings.genai_endpoint)
    if not region:
        raise VectorStoreConfigError("OCI_GENAI_ENDPOINT must include an OCI region.")

    auth = OciUserPrincipalAuth(
        config_file=settings.config_file or "~\\.oci\\config",
        profile_name=settings.config_profile,
    )
    cp_client = OciOpenAI(
        auth=auth,
        service_endpoint=f"https://generativeai.{region}.oci.oraclecloud.com/20231130",
        compartment_id=settings.compartment_id,
        project=settings.project_id,
    )
    dp_client = OciOpenAI(
        auth=auth,
        service_endpoint=f"https://inference.generativeai.{region}.oci.oraclecloud.com/20231130",
        compartment_id=settings.compartment_id,
        project=settings.project_id,
    )
    return cp_client, dp_client


def _region_from_endpoint(endpoint: str) -> str:
    host = urlparse(endpoint).hostname or ""
    marker = ".generativeai."
    if marker not in host:
        return ""

    return host.split(marker, 1)[1].split(".oci.oraclecloud.com", 1)[0]
