"""Immutable normalized sets of inclusive civil-date intervals."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from ..core.civil import CivilDate


@dataclass(frozen=True, slots=True, order=True)
class DateInterval:
    start: CivilDate
    end: CivilDate

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("interval end must not precede start")

    def contains(self, date: CivilDate) -> bool:
        return self.start <= date <= self.end

    def __iter__(self) -> Iterator[CivilDate]:
        current = self.start
        while current <= self.end:
            yield current
            current = current.add_days(1)


@dataclass(frozen=True, slots=True)
class DateSet:
    intervals: tuple[DateInterval, ...] = ()

    def __post_init__(self) -> None:
        ordered = sorted(self.intervals, key=lambda i: i.start)
        merged: list[DateInterval] = []
        for interval in ordered:
            if merged and interval.start <= merged[-1].end.add_days(1):
                merged[-1] = DateInterval(merged[-1].start, max(merged[-1].end, interval.end))
            else:
                merged.append(interval)
        object.__setattr__(self, "intervals", tuple(merged))

    def contains(self, date: CivilDate) -> bool:
        return any(i.contains(date) for i in self.intervals)

    def union(self, other: DateSet) -> DateSet:
        return DateSet(self.intervals + other.intervals)

    def intersection(self, other: DateSet) -> DateSet:
        out = []
        for a in self.intervals:
            for b in other.intervals:
                lo, hi = max(a.start, b.start), min(a.end, b.end)
                if lo <= hi:
                    out.append(DateInterval(lo, hi))
        return DateSet(tuple(out))

    def difference(self, other: DateSet) -> DateSet:
        pieces = list(self.intervals)
        for cut in other.intervals:
            next_pieces = []
            for item in pieces:
                if cut.end < item.start or cut.start > item.end:
                    next_pieces.append(item)
                    continue
                if item.start < cut.start:
                    next_pieces.append(DateInterval(item.start, cut.start.add_days(-1)))
                if cut.end < item.end:
                    next_pieces.append(DateInterval(cut.end.add_days(1), item.end))
            pieces = next_pieces
        return DateSet(tuple(pieces))

    def dates(self) -> Iterator[CivilDate]:
        for interval in self.intervals:
            yield from interval
