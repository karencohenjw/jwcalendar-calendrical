"""Stable topology signatures, independent of Python's randomized hash()."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from ..week.models import WeekModel
from .topology import month_topology, year_topology


def _fingerprint(payload: object) -> dict[str, str]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return {"signature": canonical.decode("ascii"), "sha256": hashlib.sha256(canonical).hexdigest()}


def month_fingerprint(year: int, month: int, model: WeekModel) -> dict[str, str]:
    """Return canonical JSON signature and SHA-256 digest for a month layout."""
    payload = asdict(month_topology(year, month, model))
    payload.pop("year")
    payload.pop("month")
    return _fingerprint(payload)


def year_fingerprint(year: int, model: WeekModel) -> dict[str, str]:
    """Return canonical JSON signature and SHA-256 digest for a year topology."""
    payload = asdict(year_topology(year, model))
    payload.pop("year")
    return _fingerprint(payload)
