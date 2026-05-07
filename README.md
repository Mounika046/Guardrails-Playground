# Guardrails Playground

A simple Streamlit reference project for trying multiple guardrail implementation
styles across three safety mechanisms:

1. Content Moderation
2. PII Detection
3. Prompt Injection Detection

The project is intentionally small and modular. Each approach lives in its own
file so another developer can copy only the part they need into a different
application.

## What The App Does

The UI lets a user:

- choose a safety mechanism
- choose one supported approach for that mechanism
- enter runtime text in a textarea
- run the selected check
- view the decision, explanation, matches, and raw output when available

Decisions are normalized across implemented safety checks:

- `allowed`
- `blocked`

Operational failures use explicit labels such as `configuration_error`,
`oci_error`, `vector_store_error`, or `rule_error`.

## Supported Mechanisms And Approaches

### Content Moderation

- LLM / system-prompt based
- Embeddings-based
- Regex-based
- ApplyGuardrails API

### PII Detection

- Regex-based
- ApplyGuardrails API

### Prompt Injection Detection

- LLM / system-prompt based
- Regex-based
- ApplyGuardrails API

## Run Locally

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a local environment file:

```bash
copy .env.example .env
```

Run the app:

```bash
streamlit run app.py
```

Regex approaches can run without OCI configuration. LLM, ApplyGuardrails, and
Vector Store approaches require OCI values in `.env`.

## OCI Environment Values

Set these in `.env` for OCI-backed approaches:

```bash
OCI_CONFIG_FILE=
OCI_CONFIG_PROFILE=DEFAULT
OCI_COMPARTMENT_ID=
OCI_GENAI_ENDPOINT=
OCI_VECTOR_STORE_ID=
OCI_PROJECT_ID=
OCI_LLM_MODEL_ID=
```

Notes:

- `OCI_CONFIG_FILE` is optional if the default OCI config path is used.
- `OCI_GENAI_ENDPOINT` is used for OCI Generative AI Inference calls.
- `OCI_VECTOR_STORE_ID` must point to an existing OCI Vector Store.
- The app does not create vector stores.

## Project Structure

```text
app.py
app_components/
  customization_panels.py
  inputs.py
  results.py
config/
  settings.py
customization/
  regex_rules.py
  vector_store_manifest.py
data/
  custom_regex_rules.json
  vector_store_files.json
integrations/
  applyguardrails/
  llm/
  vector_store/
mechanisms/
  content_moderation/
  pii_detection/
  prompt_injection_detection/
pages_ui/
samples/
shared/
docs/
examples/
```

## Customization

Regex approaches:

- show default rules in the UI
- allow custom regex rules
- store custom rules locally in `data/custom_regex_rules.json`

LLM approaches:

- allow editing the system prompt
- allow editing policy text
- allow editing few-shot examples
- allow setting model ID, temperature, and maximum output tokens

Embeddings approach:

- uses an existing OCI Vector Store
- lets users upload reference files
- lets users add manual reference text
- tracks only playground-added files in `data/vector_store_files.json`
- uses a minimum match score to decide whether runtime text is blocked

ApplyGuardrails approach:

- calls OCI ApplyGuardrails through a small wrapper
- does not expose custom policy controls in this app
- keeps the raw OCI response visible through a display toggle

## Example Test Material

The [examples](examples) folder contains optional sample regex rules, runtime
inputs, LLM prompt customizations, and embeddings reference files. These files
are not loaded automatically; they are there so users can quickly test
customization without preparing their own sample material first.

## Reusing Individual Approaches

Use [docs/reusable_approaches.md](docs/reusable_approaches.md) as the quick map
for copying only one approach into another project.

Examples:

- PII regex only:
  `mechanisms/pii_detection/regex.py`
- Prompt injection ApplyGuardrails only:
  `mechanisms/prompt_injection_detection/applyguardrails.py`
- Content moderation embeddings only:
  `mechanisms/content_moderation/embeddings.py`
