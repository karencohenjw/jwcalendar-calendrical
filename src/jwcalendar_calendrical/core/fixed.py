"""Fixed-day coordinate helpers.

Day 1 is Gregorian 0001-01-01; day 0 is the preceding day. Coordinates are
unbounded Python integers, though public Gregorian conversion requires year >= 1.
"""

from __future__ import annotations

from typing import NewType

FixedDay = NewType("FixedDay", int)
EPOCH_DESCRIPTION = "Fixed day 1 is proleptic Gregorian 0001-01-01 (Monday)."
