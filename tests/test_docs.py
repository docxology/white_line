"""Execute review-protocol recipes against the real package.

Each fenced ``python`` block in ``docs/review_protocol.md`` must be followed
immediately by a fenced ``text`` block. The text block is the exact stdout
contract for that recipe; this test executes the code without mocks or network
access and compares the captured stdout byte-for-byte.
"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = PROJECT_ROOT / "docs/review_protocol.md"
RECIPE_RE = re.compile(
    r"```python\n(?P<source>.*?)\n```\n\n```text\n(?P<expected>.*?)\n```",
    re.DOTALL,
)
PYTHON_BLOCK_RE = re.compile(r"```python\n.*?\n```", re.DOTALL)


def test_review_protocol_recipes_match_documented_stdout() -> None:
    """Keep every executable protocol recipe aligned with its adjacent output."""

    text = PROTOCOL.read_text(encoding="utf-8")
    recipes = list(RECIPE_RE.finditer(text))
    assert recipes
    assert len(recipes) == len(PYTHON_BLOCK_RE.findall(text))
    for recipe in recipes:
        stdout = StringIO()
        with redirect_stdout(stdout):
            exec(recipe.group("source"), {"__name__": "__main__"})
        assert stdout.getvalue() == f"{recipe.group('expected')}\n"
