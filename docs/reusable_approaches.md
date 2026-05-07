# Reusable Approach Map

This project is organized so each implementation approach can be copied without
bringing the whole playground UI with it.

## Shared Result Shape

Most approach functions return:

```python
GuardrailResult(
    decision="allowed",
    explanation="...",
    raw_output={},
    matches=[],
)
```

Shared file:

```text
shared/result.py
```

You can keep this dataclass or replace it with your own response shape.

## Regex Approaches

Regex matching is shared here:

```text
shared/regex_utils.py
```

Custom regex rule loading is here:

```text
customization/regex_rules.py
```

The mechanism-specific default rules are here:

```text
mechanisms/content_moderation/regex.py
mechanisms/pii_detection/regex.py
mechanisms/prompt_injection_detection/regex.py
```

To copy only the PII regex approach, start with:

```text
mechanisms/pii_detection/regex.py
shared/regex_utils.py
shared/result.py
```

If you want saved custom rules too, also copy:

```text
customization/regex_rules.py
```

## LLM / System-Prompt Approaches

The shared prompt runner is here:

```text
integrations/llm/prompt_runner.py
integrations/llm/client.py
```

Mechanism-specific prompts are here:

```text
mechanisms/content_moderation/llm_prompt.py
mechanisms/prompt_injection_detection/llm_prompt.py
```

To copy only content moderation with the LLM approach, start with:

```text
mechanisms/content_moderation/llm_prompt.py
integrations/llm/prompt_runner.py
integrations/llm/client.py
shared/result.py
config/settings.py
```

The OCI-specific chat request is isolated in:

```text
integrations/llm/client.py
```

## ApplyGuardrails Approaches

The OCI API call is isolated here:

```text
integrations/applyguardrails/oci_client.py
integrations/applyguardrails/wrapper.py
```

Mechanism-specific usage is here:

```text
mechanisms/content_moderation/applyguardrails.py
mechanisms/pii_detection/applyguardrails.py
mechanisms/prompt_injection_detection/applyguardrails.py
```

To copy only prompt injection detection with ApplyGuardrails, start with:

```text
mechanisms/prompt_injection_detection/applyguardrails.py
integrations/applyguardrails/wrapper.py
integrations/applyguardrails/oci_client.py
shared/result.py
config/settings.py
```

## Embeddings Approach

The content moderation embeddings approach is here:

```text
mechanisms/content_moderation/embeddings.py
```

OCI Vector Store client and search code are here:

```text
integrations/vector_store/client.py
integrations/vector_store/search.py
```

File upload, manual reference text upload, polling, and reset helpers are here:

```text
integrations/vector_store/files.py
customization/vector_store_manifest.py
```

To copy only content moderation with embeddings, start with:

```text
mechanisms/content_moderation/embeddings.py
integrations/vector_store/client.py
integrations/vector_store/search.py
shared/result.py
config/settings.py
```

If you also want the reference file customization workflow, copy:

```text
integrations/vector_store/files.py
customization/vector_store_manifest.py
```

## UI Wiring

The Streamlit pages are intentionally separate from the reusable approach code:

```text
pages_ui/
app_components/
```

You do not need these files if you are copying an approach into another backend
or service.
