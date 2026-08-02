# Manuscript contract

This folder owns source manuscript sections, bibliography, and
`config.yaml`—the paper-version authority. It does not own rendered PDF/HTML,
figure pixels, registry content, or package behavior.

`config.yaml` provides the paper version; it must equal package and installed
metadata. Numbered `.md` files are labelled sections, `preamble.md` supplies
front matter, and `references.bib` supplies citation keys. Figures are embedded
as `../output/figures/<name>.png`; every registered figure must be embedded and
every embed must be registered. Do not hand-edit rendered output or change the
registry/package version in a manuscript-only edit.

The prose may describe states only as records under a supplied review contract,
never people, motives, safety, legality, permission, or hidden causes. After a
manuscript or figure input change, render through the external `docxology/template`
checkout as described in
[../docs/reproducibility.md](../docs/reproducibility.md), then run
`uv run python scripts/audit_project.py --write-manifest --report`.

Read [README.md](README.md), [../AGENTS.md](../AGENTS.md),
[../docs/claim_boundaries.md](../docs/claim_boundaries.md), and
[../docs/reproducibility.md](../docs/reproducibility.md). `output/` is generated,
git-ignored, and disposable; it carries no folder contract of its own.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
