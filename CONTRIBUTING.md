# Contributing

Please open an issue before proposing a change to public date or week semantics. Keep civil-date arithmetic deterministic and independent of local time zones. Add regression tests for boundary behavior and document assumptions where a rule is jurisdiction-specific.

Run `python -m pytest`, `python -m ruff check .`, and `python -m mypy src` before submitting a change. Optional adapters must not become core dependencies.
