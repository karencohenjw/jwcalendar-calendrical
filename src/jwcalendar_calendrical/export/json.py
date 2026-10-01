"""Deterministic JSON and JSON Lines serializers."""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Iterable
from enum import Enum
from typing import Any, cast


def _plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {k: _plain(v) for k, v in dataclasses.asdict(cast(Any, value)).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def to_json(value: Any, *, indent: int | None = 2) -> str:
    return json.dumps(_plain(value), ensure_ascii=False, sort_keys=True, indent=indent)


def to_jsonl(values: Iterable[Any]) -> str:
    return "".join(
        json.dumps(_plain(v), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for v in values
    )
