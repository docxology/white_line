# Abstract {#sec:abstract}

White Line is a typed ledger for the edge of a claim. It records what is
unknown or unobserved, what is intentionally withheld or unrepresented, and
what is left open as contemplative negative space. It asks what a document must
refuse to imply when the evidence, the obligation, or the language is not
there. A gap is never treated as proof that a hidden cause exists.

The executable instrument is a small, pure-data Python package: a versioned
registry of eleven absence records and a staged evaluator, `assess_absence`. It
is a tested prototype for structured review, not a validated measurement
instrument and not an observation of the world. Each record carries one of three
kinds — `EPISTEMIC`, `ETHICAL`, or `CONTEMPLATIVE` — and a dated observation
assigns it one of four states: `NAMED`, `UNRESOLVED`, `WITHHELD`, or
`NOT_RECORDED`. Intake sets aside any input that fails the contract, whether a
non-observation, an unknown record, an untyped state, or an attempt to assert
the ledger-reserved `NOT_RECORDED`, and records why. Conflicting and duplicate
observations leave the same visible trace.

Staleness is the second stage. A dated naming that ages past its record's review
horizon decays back to `UNRESOLVED`, because an old naming is no longer current
evidence for a settled state. Six structural invariants guard the registry's
shape, and a shipped battery hands each one a registry carrying exactly the
defect it guards against, so a check that has never rejected anything is not
counted as protection. A bounded follow-up protocol makes the next human action
explicit without issuing an approval.

The result is a ledger, not a detector of hidden causes, and not a claim that an
absence by itself supports an inference beyond the record's scope. Reports
retain their review date and registry digest so a later reader can tell a
reproducible rerun from an unanchored assertion. White Line is the fourth work
in the line set, deliberately non-redundant with Red Line's security boundary,
Black Line's positive practice, and Golden Line's aspirational direction: where
those lines fill, commit, and reach, White Line marks the edge and holds it
open.
