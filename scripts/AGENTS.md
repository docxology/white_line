# Script contract

Every file in `scripts/` is a thin CLI over `src/`. Business logic belongs in
`src/white_line/`, not here.

## Files

- `__init__.py` — package marker
- `audit_project.py` — runs the publication audit gate (source/render consistency)
- `build_figures.py` — calls `white_line.figures.build_figures()` and prints the output paths
- `check_figure_layout.py` — verifies figure layout constraints (legibility, page fit)
- `check_registry.py` — runs structural checks over `WHITE_RECORDS` and verifies the digest

## Canonical commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
uv run python scripts/check_registry.py
uv run python scripts/build_figures.py
uv run python scripts/audit_project.py --report
```
