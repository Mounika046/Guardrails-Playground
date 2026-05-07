"""Prompt composition and response parsing for LLM-based checks."""

from __future__ import annotations

import json
import re
from typing import Any

from integrations.llm.client import OciLlmConfigError, chat_with_oci
from shared.result import GuardrailResult


def run_prompt_check(
    text: str,
    system_prompt: str,
    policy_text: str,
    few_shot_examples: str,
    model_id: str,
    temperature: float,
    max_tokens: int,
) -> GuardrailResult:
    prompt = build_prompt(
        policy_text=policy_text,
        few_shot_examples=few_shot_examples,
        text=text,
    )

    try:
        raw_response = chat_with_oci(
            prompt=prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except OciLlmConfigError as exc:
        return GuardrailResult(
            decision="configuration_error",
            explanation=str(exc),
            raw_output={"error": str(exc)},
        )
    except Exception as exc:
        return GuardrailResult(
            decision="oci_error",
            explanation=f"OCI Generative AI chat call failed: {exc}",
            raw_output={
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )

    parsed = _parse_model_json(raw_response.get("text", ""))
    if parsed is None:
        return GuardrailResult(
            decision="blocked",
            explanation="The model response was not valid JSON. Review the raw output.",
            raw_output=raw_response,
        )

    return GuardrailResult(
        decision=_normalize_decision(parsed.get("decision")),
        explanation=str(parsed.get("explanation", "")),
        raw_output=raw_response,
        matches=_as_match_list(parsed.get("matches", [])),
    )


def build_prompt(policy_text: str, few_shot_examples: str, text: str) -> str:
    return f"""
Policy:
{policy_text}

Few-shot examples:
{few_shot_examples or "No examples provided."}

Text to evaluate:
{text}

Return only JSON with this shape:
{{
  "decision": "allowed | blocked",
  "explanation": "short explanation",
  "matches": []
}}
""".strip()


def _parse_model_json(response_text: str) -> dict[str, Any] | None:
    try:
        value = json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response_text, flags=re.DOTALL)
        if not match:
            return None
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    return value if isinstance(value, dict) else None


def _as_match_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, dict)]


def _normalize_decision(value: Any) -> str:
    decision = str(value or "blocked").strip().lower()
    if decision in {"allowed", "safe", "no_pii_detected", "no_prompt_injection_detected"}:
        return "allowed"
    if decision in {
        "blocked",
        "unsafe",
        "needs_review",
        "pii_detected",
        "prompt_injection_detected",
    }:
        return "blocked"
    return decision
