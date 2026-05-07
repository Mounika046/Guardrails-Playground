"""Track vector store files added by this playground."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_FILE = Path("data/vector_store_files.json")


def list_tracked_files(vector_store_id: str) -> list[dict[str, Any]]:
    manifest = _load_manifest()
    return manifest.get(vector_store_id, [])


def add_tracked_file(
    vector_store_id: str,
    file_id: str,
    filename: str,
    source: str,
) -> None:
    manifest = _load_manifest()
    files = manifest.setdefault(vector_store_id, [])
    if any(item.get("file_id") == file_id for item in files):
        return

    files.append(
        {
            "file_id": file_id,
            "filename": filename,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    _save_manifest(manifest)


def remove_tracked_file(vector_store_id: str, file_id: str) -> None:
    manifest = _load_manifest()
    files = manifest.get(vector_store_id, [])
    manifest[vector_store_id] = [
        item for item in files if item.get("file_id") != file_id
    ]
    _save_manifest(manifest)


def clear_tracked_files(vector_store_id: str) -> None:
    manifest = _load_manifest()
    manifest[vector_store_id] = []
    _save_manifest(manifest)


def _load_manifest() -> dict[str, list[dict[str, Any]]]:
    if not MANIFEST_FILE.exists():
        return {}

    try:
        data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    return data if isinstance(data, dict) else {}


def _save_manifest(manifest: dict[str, list[dict[str, Any]]]) -> None:
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
