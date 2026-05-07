"""Content moderation using OCI Vector Store semantic search."""

from __future__ import annotations

from integrations.vector_store.client import VectorStoreConfigError
from integrations.vector_store.search import search_vector_store
from shared.result import GuardrailResult


def moderate_content_with_embeddings(
    text: str,
    vector_store_id: str = "",
    top_k: int = 5,
    min_match_score: float = 0.7,
) -> GuardrailResult:
    try:
        search_result = search_vector_store(
            query=text,
            vector_store_id=vector_store_id,
            top_k=top_k,
        )
    except VectorStoreConfigError as exc:
        return GuardrailResult(
            decision="configuration_error",
            explanation=str(exc),
            raw_output={"error": str(exc)},
        )
    except Exception as exc:
        return GuardrailResult(
            decision="vector_store_error",
            explanation=f"OCI Vector Store search failed: {exc}",
            raw_output={
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )

    all_results = search_result["results"]
    matches = []
    for item in all_results:
        score = item.get("score")
        if score is not None and score >= min_match_score:
            matches.append(
                {
                    "file_id": item.get("file_id"),
                    "score": score,
                    "matched_text": item.get("text"),
                }
            )

    search_result["min_match_score"] = min_match_score
    search_result["decision_driving_matches"] = matches

    decision = "blocked" if matches else "allowed"
    explanation = (
        f"{len(matches)} reference match(es) met the minimum score of {min_match_score}."
        if matches
        else (
            "No vector store matches met the minimum score of "
            f"{min_match_score}. Retrieved lower-score context is available in raw output."
        )
    )

    return GuardrailResult(
        decision=decision,
        explanation=explanation,
        raw_output=search_result,
        matches=matches,
    )
