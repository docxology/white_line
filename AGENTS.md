# White Line project guidance

White Line is a standalone repository: a typed absence ledger whose source of
truth is `src/white_line/`, whose executable contract is tested under `tests/`,
and whose manuscript and generated figures must stay synchronized with the
versioned registry. It carries its own package, tests, documentation,
manuscript, references, and figure builder, and it depends on no sibling
project.

## Working contract

- Keep ledger logic in `src/white_line/`; `scripts/` are thin orchestrators.
- Preserve the absence boundary: `NAMED`, `UNRESOLVED`, `WITHHELD`, and
  `NOT_RECORDED` describe a record under a supplied review contract — never
  people, motives, safety, legality, permission, or hidden causes.
- Caution only rises: reconciliation and staleness decay must never make an
  absence look more settled than its most cautious observer reported. Any
  change touching `caution_rank`, intake, or decay needs tests that plant the
  violating input.
- `NOT_RECORDED` stays ledger-reserved; observations may not assert it.
- A registry, state, invariant, or protocol change must update tests, docs,
  manuscript, figures (`white_line.figures` → `output/figures/`), and
  the audit gate together, and bump `LEDGER_VERSION` when registry content
  changes.
- Paper-version authority is `manuscript/config.yaml`; the package and installed
  metadata must remain equal to it, and tests bind all three. The cover art
  derives its version text from `white_line.version.__version__`.
- `white_line.analysis` stays pure and additive: sweeps and tables computed
  *through* `assess_absence` or from `caution_rank`, never a second
  implementation of assessment semantics.
- The witness layer (`facets.py`, `returns.py`, `envelope.py`) is downstream
  of assessment in the same way: derived views over a report, never new
  observations and never a second evaluator. `project_facets` must keep
  recovering the shipped state from `finding_facets` output (the suite proves
  it branch-by-branch), a `ReturnContract` never authorizes anything, and the
  envelope points at `canonical_report` by digest without reinterpreting it.
  The shared witness register across the line set is a separate work by
  design; do not build cross-line logic here (`docs/correspondence.md`).
- Adding a figure touches, atomically: the plate builder, its `FIGURE_PLATES`
  registration, the count and label assertions in `tests/test_figures.py`, the
  count in `docs/development.md`, and an embed by filename in a
  `manuscript/*.md` file. A generated-but-unembedded figure is inert and
  forbidden; the audit fails on it in both directions. No module docstring
  carries a plate count — the count lives in `docs/development.md` and in
  `tests/test_figures.py`, which are the only two places to update.
- Every label a plate draws must print at or above six points on the page.
  `canvas.text` refuses a size below `MIN_TEXT_SIZE`, and
  `tests/test_figure_legibility.py` re-derives each plate's printed size from
  the manuscript embed width and `manuscript/config.yaml` geometry. Widening a
  canvas shrinks every label on it, so `MAX_CANVAS_WIDTH` is a hard cap: grow a
  plate downward, never sideways.
- The manuscript states every definition and proposition as a fenced Div —
  `::: {.definition #def:name title="Name"}` — and refers to them only as
  `[@def:name]`. Never write a formalism number into the source: the renderer's
  `formalism.lua` filter numbers blocks per kind in document order and resolves
  each reference from its label. Every block needs a label with its kind's
  prefix (`def:`, `prop:`), a row in the claim-to-test table keyed on that
  label, and a named test that fails if the code diverges.
  `tests/test_formalism.py` enforces all of it and `white_line.formalism`
  supplies the reading the audit and the tests share.
- Use `uv`; no mocks in tests; keep the package pure standard library.
- Do not copy prose, registries, or implementation code from Red, Black, or
  Golden Line, and do not import them; the set is linked by naming each work
  and its repository, never by a path or an import.

## Commands

The executable test, registry, figure, audit, and render sequence lives in
[docs/development.md](docs/development.md); the local skill carries the API
walkthrough and failure gotchas.

The project renders through the external `docxology/template` engine, cloned or
located anywhere on disk, with the qualified project name `working/white_line`
— a name the template resolves inside its own `projects/` tree, not a path
relative to this repository. [docs/development.md](docs/development.md) gives
the path-independent invocation. After rendering, run
`uv run python scripts/audit_project.py --write-manifest --report`. A passing
audit means the source and rendered bundle agree structurally; it is not
verification of any observation, boundary, or safety property.

The render is this project's only external dependency, and it is declared, not
hidden: without it the tests, coverage gate, registry check, figure build,
legibility gate, and source-side audit all still run. See
[STANDALONE.md](STANDALONE.md).

An agent-facing operating summary lives at
`.agents/skills/white-line/SKILL.md`.
