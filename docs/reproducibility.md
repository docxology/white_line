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
3. Follow the [development guide](development.md#render-and-validate-the-manuscript)
   to register White Line with the pinned template, render the PDF and HTML
   from `docs/manuscript/`, and validate both outputs.
4. Run `scripts/audit_project.py --require-render --write-manifest --report`
   after a fresh render. It checks figure links and labels, bibliography keys,
   source headings, and required PDF/HTML artifacts. The source manifest records
   a content fingerprint for the manuscript and generated figure inputs. A later
   source edit invalidates it.

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
