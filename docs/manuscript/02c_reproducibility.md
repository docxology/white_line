# Reproducibility boundary and release chain {#sec:reproducibility}

A White Line result is reproducible only when its context travels with it.
Every `WhiteReport` records the ISO `review_date`, the order-independent
`registry_digest`, and typed `intake_events` (see [@prop:context-traceability]).
The date fixes staleness
accounting; the digest fixes which registry defined each id. A report without
those fields can still be read, but it should not be treated as a complete
review record.

The publication artifacts follow the same source-to-output chain. The live
registry generates the deterministic figures and their registry JSON; the
manuscript names those figures and its bibliography keys; the sibling template
renders PDF and HTML; and `scripts/audit_project.py` checks that the generated
bundle contains the source headings, figure links, bibliography keys, and
required artifacts. A source manifest is written only after that audit passes,
and its content fingerprint becomes stale after any manuscript or figure-input
change.

The gate is structural, not epistemic. It can detect that a rendered bundle is
missing a source section or that a figure no longer matches the ledger. It
cannot verify a reviewer's note, establish independent evidence, justify a
withholding, or prove that a project is safe. Those are separate human and
domain-governed questions.
