# White Line documentation

This folder explains the source contract and publication workflow. Start with
[architecture.md](architecture.md) for the executable model, then read
[review_protocol.md](review_protocol.md) before interpreting a report. The
technical folder contract is [AGENTS.md](AGENTS.md); repository orientation is
the root [README.md](../README.md) and its working rules are in
[AGENTS.md](../AGENTS.md).

- [architecture.md](architecture.md) — module layout, the staged
  `assess_absence` semantics, report traceability, typed intake events, the
  review protocol, the invariant battery with defined-defect detection tests, and
  the registry digest/manifest.
- [review_protocol.md](review_protocol.md) — the human follow-up loop and its
  explicit non-claims.
- [reproducibility.md](reproducibility.md) — source, figure, render, and audit
  ordering for a reviewable publication bundle.
- [visual_language.md](visual_language.md) — the editorial visual system,
  non-claim safeguards, and preview/promotion workflow for generated figures.
- [scholarship_map.md](scholarship_map.md) — the scholarship-to-design
  translation and explicit boundaries around what the package does not claim
  to solve.
- [claim_boundaries.md](claim_boundaries.md) — the release claim register,
  evidence classes, and explicit empirical non-claims.
- [correspondence.md](correspondence.md) — external design reviews received
  and the adopted/deferred/declined decision record.
- [development.md](development.md) — how to run tests, registry checks,
  figure generation, and the source/artifact audit.
- [AGENTS.md](AGENTS.md) — technical ownership, document boundaries, and
  verification commands for this folder.

The typed vocabulary lives in `src/white_line/model/`, the eleven-record
ledger in `src/white_line/registry.py`, the staged assessor in
`src/white_line/assessor.py`, the structural checks in
`src/white_line/invariants.py`, and the canonical serialization plus review
manifest in `src/white_line/serialization.py`. The bounded human follow-up
protocol lives in `src/white_line/protocol.py`. Pure descriptive analyses —
decay-horizon sweeps (`decay_timeline`, `decay_transition_offsets`), the
ordered-pair conflict table (`reconciliation_matrix`), and per-report
distributions (`events_tally`, `coverage_matrix`, `expiry_horizon`) — live in
`src/white_line/analysis.py`; they are computed through `assess_absence` and
back five of the generated figures plus the manuscript's distributional-views
section. The witness layer lives beside them: the state factorization in
`src/white_line/facets.py`, return contracts in `src/white_line/returns.py`,
and the cross-instrument report envelope in `src/white_line/envelope.py`,
pointing at the complete-report serialization in
`src/white_line/serialization.py`. Two shipped batteries —
`invariant_defect_battery` in
`src/white_line/invariants.py` and `scoring_branch_battery` in
`src/white_line/worked_examples.py` — run the structural checks against planted
defects and the scoring rule against one input per branch, and back two more
figures. `src/white_line/formalism.py` reads the manuscript's fenced
definition and proposition blocks the way the renderer's numbering filter does,
so the audit and the tests share one reading of them.
`white_line.figures.build_figures` writes its assets to `output/figures/`, and
`white_line.audit.audit_project` checks source/render agreement;
`scripts/build_figures.py` and `scripts/audit_project.py` are their
command-line entry points. The plate count lives in
[development.md](development.md) and in `tests/test_figures.py`, the only two
places to update when a plate is added.

Agent-facing operating guidance: the repository-root [AGENTS.md](../AGENTS.md)
(working contract and invariants) and the local skill at
[.agents/skills/white-line/SKILL.md](../.agents/skills/white-line/SKILL.md).

Boundaries and cross-references among the works are stated inside this
repository in
[manuscript/01b_line_set_relationship.md](../manuscript/01b_line_set_relationship.md).
Each companion work is its own repository:
[red_line](https://github.com/docxology/red_line),
[black_line](https://github.com/docxology/black_line),
[golden_line](https://github.com/docxology/golden_line), and the set reader
[line_set](https://github.com/docxology/line_set), which carries the shared
framing for all five. Nothing here imports or depends on them.
