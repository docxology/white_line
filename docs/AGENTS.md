# Documentation folder contract

This folder owns the project-facing explanation of the ledger contract and
release workflow. It does not own assessment semantics, registry content,
generated figures, or rendered artifacts; those belong respectively to
[`../src/white_line/`](../src/white_line/),
[`../src/white_line/registry.py`](../src/white_line/registry.py), and
[`../output/`](../output/).

## Contents and boundaries

- `architecture.md` explains the staged assessor and data model.
- `review_protocol.md` owns the human follow-up loop and executable recipes.
  Every fenced `python` block is followed immediately by a fenced `text` block
  illustrating stdout. Exercise recipes as disposable native smoke runs;
  behavioral regressions belong in the native API tests, not copied-output tests.
- `claim_boundaries.md` is the claim register; preserve its boundary that
  states describe records under a supplied review contract, never people,
  motives, safety, legality, permission, or hidden causes.
- `development.md` and `reproducibility.md` name the verification and render
  order. `visual_language.md` describes figure presentation; `scholarship_map.md`
  identifies bounded design sources.

When source behavior changes, update only statements established by the
implementation and tests. Do not turn a tally, directive, or passing audit
into a completeness, diligence, safety, or negligence result.

## Verification

Exercise the recipes in a disposable native environment, then run
`uv run pytest -q` for the project suite. Read [README.md](README.md) for the
document index, [../AGENTS.md](../AGENTS.md) for repository invariants, and
[../src/white_line/AGENTS.md](../src/white_line/AGENTS.md) before documenting a
package surface.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
