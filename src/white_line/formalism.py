"""Read the manuscript's fenced formalism blocks and the references to them.

The manuscript states its definitions and propositions as fenced Divs::

    ::: {.definition #def:kinds title="Kinds"}
    The kind alphabet is the set ...
    :::

    By [@def:kinds], every record carries one of three kinds.

The renderer's ``formalism.lua`` filter numbers those blocks per kind in
document order and resolves each ``[@label]`` reference from the label, so no
number is ever written in the source. This module reproduces the same reading
inside the package, for three consumers that must not disagree:

* the audit, which extracts bibliography citation keys from the manuscript and
  would otherwise treat ``def:kinds`` as a missing bibliography entry;
* the test suite, which checks that every block carries a label, that every
  reference resolves, and that no hand-written number survives;
* the release report, which lists each block with its label and the number the
  renderer will print.

Nothing here renders anything. It parses the source the renderer consumes and
reports what that source declares, which is the only way a check on the source
can be a check on what will be printed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: The block classes the renderer's filter numbers, mapped to the printed
#: title it gives each one. Held here so the package's reading of a manuscript
#: cannot drift from the renderer's without this table changing.
FORMALISM_TITLES: dict[str, str] = {
    "definition": "Definition",
    "proposition": "Proposition",
    "theorem": "Theorem",
    "lemma": "Lemma",
    "corollary": "Corollary",
    "remark": "Remark",
    "axiom": "Axiom",
    "claim": "Claim",
    "example": "Example",
}

#: The label prefix each class must use. The renderer accepts any prefix and
#: resolves from the label alone; this project pins one per class so a reader
#: can tell what ``[@prop:totality]`` points at before following the link.
FORMALISM_PREFIXES: dict[str, str] = {
    "definition": "def",
    "proposition": "prop",
    "theorem": "thm",
    "lemma": "lem",
    "corollary": "cor",
    "remark": "rem",
    "axiom": "ax",
    "claim": "clm",
    "example": "ex",
}

_CLASSES = "|".join(sorted(FORMALISM_TITLES))

#: Opening fence of a formalism Div. The identifier and the title attribute are
#: optional in the syntax; this module reports their absence rather than
#: refusing to parse, because "a block with no label" is exactly the defect the
#: test suite has to be able to name.
_OPEN_RE = re.compile(
    r"^::: *\{ *\.(?P<kind>" + _CLASSES + r")(?P<attrs>[^}]*)\} *$",
    re.MULTILINE,
)
_LABEL_RE = re.compile(r"#([A-Za-z][A-Za-z0-9:_-]*)")
_TITLE_RE = re.compile(r'title="([^"]*)"')
_UNNUMBERED_RE = re.compile(r"\.unnumbered\b")
_CLOSE_RE = re.compile(r"^::: *$", re.MULTILINE)

#: A citation as pandoc parses it. Both the plain ``[@key]`` form and the
#: members of a group ``[@a; @b]`` are matched, because the filter partitions a
#: group and this module has to see the same members it does.
_CITATION_RE = re.compile(r"@([A-Za-z][A-Za-z0-9_:-]*)")

#: A hand-written formalism number: ``Definition 4``, ``Proposition B``. The
#: whole point of the fenced syntax is that no such literal exists in the
#: source, so this pattern is what the guard searches for.
_HAND_NUMBER_RE = re.compile(
    r"\b(" + "|".join(sorted(FORMALISM_TITLES.values())) + r")\s+([0-9]+|[A-Z])\b"
)

#: Fenced code blocks, which are quoted material rather than prose. A code
#: sample may legitimately contain any of the shapes above.
_CODE_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class FormalismBlock:
    """One fenced formalism block as the source declares it.

    ``number`` is the value the renderer's per-kind counter will reach for this
    block, computed the same way: blocks of one class are numbered from one in
    document order, and an ``.unnumbered`` block consumes no number and carries
    ``None``.
    """

    kind: str
    label: str
    title: str
    body: str
    source: str
    number: int | None

    @property
    def printed(self) -> str:
        """Return the marker the renderer prints for this block."""

        head = FORMALISM_TITLES[self.kind]
        if self.number is not None:
            head = f"{head} {self.number}"
        return f"{head} ({self.title})" if self.title else head


def strip_code(text: str) -> str:
    """Return ``text`` with fenced and inline code replaced by blanks.

    Blanks rather than deletions: the replacement keeps the surrounding prose
    at the same offsets, so a match reported against the stripped text still
    points at the right place in the original.
    """

    without_fences = _CODE_FENCE_RE.sub(
        lambda match: "\n" * match.group(0).count("\n"), text
    )
    return _INLINE_CODE_RE.sub(lambda match: " " * len(match.group(0)), without_fences)


def parse_blocks(sources: dict[str, str]) -> tuple[FormalismBlock, ...]:
    """Return every formalism block declared across ``sources``.

    Args:
        sources: File name to file text, iterated in sorted key order — the
            order the renderer combines the manuscript in, and therefore the
            order its counters advance in.

    Returns:
        One entry per block, in document order, each carrying the number the
        renderer will print for it.

    Raises:
        ValueError: If an opening fence is never closed. A block whose fence is
            unbalanced swallows the rest of the section in the rendered output,
            so guessing an end here would hide a real defect.
    """

    blocks: list[FormalismBlock] = []
    counters: dict[str, int] = {}
    for name in sorted(sources):
        text = sources[name]
        for opening in _OPEN_RE.finditer(text):
            closing = _CLOSE_RE.search(text, opening.end())
            if closing is None:
                raise ValueError(f"{name}: unclosed formalism fence at {opening.end()}")
            attrs = opening.group("attrs")
            kind = opening.group("kind")
            label_match = _LABEL_RE.search(attrs)
            title_match = _TITLE_RE.search(attrs)
            if _UNNUMBERED_RE.search(attrs):
                number = None
            else:
                counters[kind] = counters.get(kind, 0) + 1
                number = counters[kind]
            blocks.append(
                FormalismBlock(
                    kind,
                    label_match.group(1) if label_match else "",
                    title_match.group(1) if title_match else "",
                    text[opening.end() : closing.start()].strip("\n"),
                    name,
                    number,
                )
            )
    return tuple(blocks)


def declared_prefixes(blocks: tuple[FormalismBlock, ...]) -> frozenset[str]:
    """Return the label prefixes the manuscript actually declares.

    The renderer claims a citation only when its prefix belongs to a declared
    formalism label, so this is the set that decides which ``@name`` tokens are
    formalism references and which are bibliography keys.

    Section (``sec``) and figure (``fig``) references are always treated as
    structural references, not bibliography keys — pandoc resolves them as
    internal links before the citation machinery sees them.
    """

    return frozenset(
        label.split(":", 1)[0]
        for block in blocks
        if ":" in (label := block.label)
    ) | {"sec", "fig"}


def split_citations(
    text: str, prefixes: frozenset[str]
) -> tuple[frozenset[str], frozenset[str]]:
    """Partition every ``@name`` token into formalism references and bib keys.

    The partition is the renderer's: a token whose prefix is one the document
    declares for a formalism label is a formalism reference and never reaches
    the bibliography machinery; everything else is a bibliography key.

    Returns:
        A pair of (formalism references, bibliography keys).
    """

    references: set[str] = set()
    keys: set[str] = set()
    for token in _CITATION_RE.findall(text):
        prefix, separator, _rest = token.partition(":")
        if separator and prefix in prefixes:
            references.add(token)
        else:
            keys.add(token)
    return frozenset(references), frozenset(keys)


def hand_written_numbers(text: str) -> tuple[str, ...]:
    """Return every hand-written formalism number in ``text``, code excluded.

    ``Definition 4`` or ``Proposition B`` written into prose is the defect the
    fenced syntax exists to remove: the renderer would not renumber it, so it
    goes stale the moment a block is inserted above it.
    """

    return tuple(
        match.group(0) for match in _HAND_NUMBER_RE.finditer(strip_code(text))
    )


def read_manuscript(manuscript_dir: Path) -> dict[str, str]:
    """Return every manuscript source file's text, keyed by file name."""

    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(manuscript_dir.glob("*.md"))
    }


__all__ = [
    "FORMALISM_PREFIXES",
    "FORMALISM_TITLES",
    "FormalismBlock",
    "declared_prefixes",
    "hand_written_numbers",
    "parse_blocks",
    "read_manuscript",
    "split_citations",
    "strip_code",
]
