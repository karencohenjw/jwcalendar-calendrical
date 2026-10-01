# Architecture notes

The implementation is layered so civil arithmetic stays auditable:

1. `CivilDate` validates the public proleptic Gregorian domain.
2. `gregorian_to_fixed` and `fixed_to_gregorian` convert through an integer coordinate.
3. Ordinal, ISO week, grid, holiday, business, and query layers build on those primitives.
4. Export and CLI code serialize immutable results; no locale or system clock is consulted.

The supported year range is positive Python integers subject to available memory and runtime. Very large values are exact in the core but may be impractical in range scans.
