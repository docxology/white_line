"""Session setup for the White Line suite.

``output/`` is git-ignored and disposable — see the tracked ``.gitignore`` — so
a clean checkout, or a render host that wipes generated output before running
the tests, arrives with no ``output/figures``. The manuscript/registry
figure-link gate reads that directory and fails there for a reason that has
nothing to do with the property under test. Without this fixture the suite
reports failures against a source tree that is in fact correct, purely because
the figures had not been built yet.

The rebuild uses this project's own deterministic builder and nothing else. It
is a rebuild of an ignored artifact, not a stand-in: the same bytes the
committed registry already pins. If the builder cannot run — a missing
``rsvg-convert``, say — the error surfaces here rather than being swallowed,
because a broken figure build is a real defect and must not be masked.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "output" / "figures" / "figure_registry.json"


@pytest.fixture(scope="session", autouse=True)
def _ensure_generated_figures() -> None:
    """Rebuild ``output/figures`` when the ignored directory is absent."""

    if REGISTRY.exists():
        return

    from white_line.figures import build_figures

    build_figures(ROOT)
