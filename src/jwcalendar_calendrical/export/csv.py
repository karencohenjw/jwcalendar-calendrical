"""Stable CSV serialization for structured records."""

from __future__ import annotations

import csv
import dataclasses
import io
from collections.abc import Iterable
from datetime import date as _date
from enum import Enum
from typing import Any, cast


def to_csv(values: Iterable[Any]) -> str:
    def plain(value: Any) -> Any:
        if dataclasses.is_dataclass(value):
            return {
                field.name: plain(getattr(value, field.name)) for field in dataclasses.fields(value)
            }
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, (tuple, list)):
            return ";".join(str(plain(item)) for item in value)
        if isinstance(value, _date):
            return value.isoformat()
        return value

    rows = [
        plain(v)
        if dataclasses.is_dataclass(v)
        else {k: plain(value) for k, value in dict(cast(Any, v)).items()}
        for v in values
    ]
    if not rows:
        return ""
    keys = sorted({key for row in rows for key in row})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=keys, lineterminator="\r\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in keys})
    return stream.getvalue()
