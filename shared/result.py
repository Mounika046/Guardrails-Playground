"""Common result shape returned by every safety approach."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GuardrailResult:
    """A small, reusable result object for all playground checks."""

    decision: str
    explanation: str
    raw_output: Any | None = None
    matches: list[dict[str, Any]] = field(default_factory=list)


def placeholder_result(mechanism: str, approach: str) -> GuardrailResult:
    """Return a consistent placeholder while implementations are added."""

    return GuardrailResult(
        decision="not_implemented",
        explanation=(
            f"{mechanism} using {approach} is wired in the UI, "
            "but the implementation has not been added yet."
        ),
        raw_output={
            "mechanism": mechanism,
            "approach": approach,
            "status": "placeholder",
        },
    )
