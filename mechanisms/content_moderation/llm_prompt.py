"""Content moderation using an OCI-hosted chat model and prompts."""

from integrations.llm.prompt_runner import run_prompt_check
from shared.result import GuardrailResult


DEFAULT_SYSTEM_PROMPT = """
You are a content moderation classifier.
Evaluate whether the user text should be allowed or blocked.
Return only valid JSON.
""".strip()

DEFAULT_POLICY_TEXT = """
Flag text that contains threats, harassment, hateful content, explicit sexual
content, self-harm content, or instructions for wrongdoing. If the text is
ambiguous and could violate the policy, choose blocked.
""".strip()

DEFAULT_FEW_SHOT_EXAMPLES = """
Input: I need help updating my billing address.
Output: {"decision": "allowed", "explanation": "The text is a normal support request.", "matches": []}

Input: I want to threaten someone online.
Output: {"decision": "blocked", "explanation": "The text expresses intent to threaten someone.", "matches": [{"category": "threat"}]}
""".strip()


def moderate_content_with_llm(
    text: str,
    system_prompt: str,
    policy_text: str,
    few_shot_examples: str,
    model_id: str,
    temperature: float,
    max_tokens: int,
) -> GuardrailResult:
    return run_prompt_check(
        text=text,
        system_prompt=system_prompt,
        policy_text=policy_text,
        few_shot_examples=few_shot_examples,
        model_id=model_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )
