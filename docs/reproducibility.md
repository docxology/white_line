# Reproducibility and release ordering

The minimum reproducible object is not a figure or a PDF alone. It is the
chain:

```text
registry + model + assessor
            │
            ├── report (review date + registry digest + intake events)
            ├── deterministic figures + figure registry
            └── manuscript + references
                         │
                    template render
                         │
                    PDF / HTML bundle
                         │
                    source/artifact audit
```

Use this order:

1. Run the tests and the registry check.
2. Build figures from the live registry. The generated registry JSON and
   figure registry carry the registry digest; the figure builder has no clock
   or random seed in its output.
3. Render the bundle with the external `docxology/template` engine. Clone or
   locate that repository anywhere on disk, link this checkout in under its
   `projects/working/white_line`, and run
   `uv run python scripts/pipeline/stage_03_render.py --project working/white_line`
   from the template root — `working/white_line` is the qualified project name
   the template resolves, not a path relative to this repository. The exact
   commands are in [development.md](development.md). This step, and only this
   step, requires a tool outside this repository; steps 1, 2, and the source
   side of step 4 all run from this checkout alone.
4. Run `scripts/audit_project.py`. It checks that figure links, labels,
   bibliography keys, section labels, source headings, and required PDF/HTML
   artifacts agree. A stale source manifest is expected after a source edit;
   missing artifacts and other errors must be repaired first.
5. After a fresh render and a clean audit aside from manifest staleness, run
   `--write-manifest --report`. The source manifest records a content
   fingerprint for the manuscript and generated figure inputs. A later source
   edit invalidates it.

The exact numeric contract values used by the formal and distributional sections
are declared in `data/claim_ledger.json`; this keeps the template evidence
registry fail-closed without treating the values as observations about the
world.

The audit is intentionally local. It can detect source/render disagreement and
registry drift; it cannot establish that a note is true, that an observation is
independent, that a withheld boundary is justified, or that a person has
consented. Those are human and domain-governed questions.

For report archives, [witness_contracts.md](witness_contracts.md) distinguishes
exact retained serialization from input replay and separates matching,
contract validity, and trusted archival integrity. Release evidence records
the actual Python, uv, lint/type, rasterizer, and template revision used.
