"""Check manuscript bibliography identity and reference integrity."""

from __future__ import annotations

import re
from pathlib import Path

from white_line.figures.legibility import manuscript_dir
from white_line.formalism import split_citations

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = manuscript_dir(PROJECT_ROOT)


# --------------------------------------------------------------------------- #
# Bibliography integrity in both directions
# --------------------------------------------------------------------------- #
def test_every_bibliography_key_is_cited_and_every_citation_is_in_the_bibliography() -> (
    None
):
    """Both directions, with formalism references partitioned out first.

    ``[@def:kinds]`` is a citation as far as pandoc's parser is concerned; the
    renderer's filter consumes it before the bibliography machinery sees it.
    The partition here is the filter's own — a prefix the manuscript declares
    for a formalism label is a formalism reference — so this check cannot start
    reporting a definition label as a missing bibliography entry.
    """

    from white_line.formalism import declared_prefixes, parse_blocks, read_manuscript

    bibliography = (MANUSCRIPT / "references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\{\s*([^,\s]+)", bibliography))
    sources = read_manuscript(MANUSCRIPT)
    prose = "\n".join(sources[name] for name in sorted(sources))
    references, cited = split_citations(prose, declared_prefixes(parse_blocks(sources)))
    assert keys, "the bibliography must not be empty"
    assert references, "the manuscript must reference its own formalism blocks"
    assert sorted(keys - cited) == [], "bibliography entries never cited"
    assert sorted(cited - keys) == [], "citations with no bibliography entry"


def test_translated_sources_cite_the_edition_year_not_the_composition_year() -> None:
    """A composition year paired with a modern publisher renders incoherently."""

    bibliography = (MANUSCRIPT / "references.bib").read_text(encoding="utf-8")
    entries = re.split(r"\n(?=@)", bibliography)
    for entry in entries:
        if "translator" not in entry:
            continue
        year = int(re.search(r"year = \{(\d+)\}", entry).group(1))
        assert year >= 1900, entry.splitlines()[0]
