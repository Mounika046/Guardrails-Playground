"""File operations for OCI Vector Store customization data."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import BinaryIO

from customization.vector_store_manifest import (
    add_tracked_file,
    clear_tracked_files,
    list_tracked_files,
    remove_tracked_file,
)
from integrations.vector_store.client import (
    VectorStoreConfigError,
    create_vector_store_clients,
    get_vector_store_id,
)


class VectorStoreFileError(RuntimeError):
    """Raised when vector store file operations fail."""


def upload_reference_file(
    file_obj: BinaryIO,
    filename: str,
    vector_store_id: str = "",
    source: str = "upload",
) -> dict:
    selected_store_id = get_vector_store_id(vector_store_id)
    _, dp_client = create_vector_store_clients()

    uploaded = dp_client.files.create(file=file_obj, purpose="assistants")
    vector_file = dp_client.vector_stores.files.create(
        vector_store_id=selected_store_id,
        file_id=uploaded.id,
    )
    completed = wait_for_vector_file(
        vector_store_id=selected_store_id,
        file_id=vector_file.id,
    )

    add_tracked_file(
        vector_store_id=selected_store_id,
        file_id=completed.id,
        filename=filename,
        source=source,
    )

    return {
        "file_id": completed.id,
        "filename": filename,
        "source": source,
        "status": getattr(completed, "status", None),
    }


def upload_manual_reference_text(
    text: str,
    vector_store_id: str = "",
) -> dict:
    if not text.strip():
        raise VectorStoreFileError("Manual reference text is empty.")

    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".txt",
        prefix="manual_reference_",
        delete=False,
        encoding="utf-8",
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)

    try:
        with temp_path.open("rb") as file_obj:
            return upload_reference_file(
                file_obj=file_obj,
                filename=temp_path.name,
                vector_store_id=vector_store_id,
                source="manual_text",
            )
    finally:
        temp_path.unlink(missing_ok=True)


def wait_for_vector_file(
    vector_store_id: str,
    file_id: str,
    max_attempts: int = 30,
    delay_seconds: int = 5,
):
    _, dp_client = create_vector_store_clients()
    last_status = None
    for _ in range(max_attempts):
        current = dp_client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )
        last_status = getattr(current, "status", None)
        if last_status == "completed":
            return current
        if last_status in {"failed", "cancelled"}:
            raise VectorStoreFileError(
                f"Vector store file {file_id} ended with status {last_status}."
            )
        time.sleep(delay_seconds)

    raise VectorStoreFileError(
        f"Vector store file {file_id} did not complete. Last status: {last_status}."
    )


def reset_tracked_vector_files(vector_store_id: str = "") -> list[dict]:
    selected_store_id = get_vector_store_id(vector_store_id)
    _, dp_client = create_vector_store_clients()
    tracked_files = list_tracked_files(selected_store_id)
    results = []

    for item in tracked_files:
        file_id = item["file_id"]
        file_result = {
            "file_id": file_id,
            "filename": item.get("filename", ""),
            "vector_store_file_deleted": False,
            "underlying_file_deleted": False,
        }

        try:
            deleted = dp_client.vector_stores.files.delete(
                vector_store_id=selected_store_id,
                file_id=file_id,
            )
            file_result["vector_store_file_deleted"] = bool(
                getattr(deleted, "deleted", False)
            )
        except Exception as exc:
            file_result["vector_store_file_error"] = str(exc)

        try:
            deleted_file = dp_client.files.delete(file_id)
            file_result["underlying_file_deleted"] = bool(
                getattr(deleted_file, "deleted", False)
            )
        except Exception as exc:
            file_result["underlying_file_error"] = str(exc)

        remove_tracked_file(selected_store_id, file_id)
        results.append(file_result)

    clear_tracked_files(selected_store_id)
    return results


def tracked_files_for_store(vector_store_id: str = "") -> list[dict]:
    selected_store_id = get_vector_store_id(vector_store_id)
    return list_tracked_files(selected_store_id)
