"""Search operations for OCI Vector Store."""

from __future__ import annotations

from integrations.vector_store.client import create_vector_store_clients, get_vector_store_id


def search_vector_store(
    query: str,
    vector_store_id: str = "",
    top_k: int = 5,
) -> dict:
    selected_store_id = get_vector_store_id(vector_store_id)
    _, dp_client = create_vector_store_clients()

    response = dp_client.vector_stores.search(
        vector_store_id=selected_store_id,
        query=query,
        max_num_results=top_k,
        rewrite_query=False,
    )

    results = []
    for item in getattr(response, "data", []):
        content_items = getattr(item, "content", None) or []
        text_chunks = []
        for content_item in content_items:
            text = getattr(content_item, "text", None)
            if text:
                text_chunks.append(text)

        results.append(
            {
                "file_id": getattr(item, "file_id", None),
                "score": getattr(item, "score", None),
                "text": "\n".join(text_chunks),
            }
        )

    return {
        "vector_store_id": selected_store_id,
        "query": query,
        "top_k": top_k,
        "results": results,
        "raw_output": _to_dict(response),
    }


def _to_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return str(value)
