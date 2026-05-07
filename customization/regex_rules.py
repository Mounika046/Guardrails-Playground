"""Load and save custom regex rules for the playground."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CUSTOM_RULES_FILE = Path("data/custom_regex_rules.json")


def load_custom_rules(mechanism_key: str) -> list[dict[str, Any]]:
    all_rules = _load_all_rules()
    return all_rules.get(mechanism_key, [])


def save_custom_rules(mechanism_key: str, rules: list[dict[str, Any]]) -> None:
    all_rules = _load_all_rules()
    all_rules[mechanism_key] = rules
    CUSTOM_RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    CUSTOM_RULES_FILE.write_text(json.dumps(all_rules, indent=2), encoding="utf-8")


def add_custom_rule(mechanism_key: str, rule: dict[str, Any]) -> None:
    rules = load_custom_rules(mechanism_key)
    rules.append(rule)
    save_custom_rules(mechanism_key, rules)


def reset_custom_rules(mechanism_key: str) -> None:
    save_custom_rules(mechanism_key, [])


def _load_all_rules() -> dict[str, list[dict[str, Any]]]:
    if not CUSTOM_RULES_FILE.exists():
        return {}

    try:
        data = json.loads(CUSTOM_RULES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    return {
        str(key): value
        for key, value in data.items()
        if isinstance(value, list)
    }
