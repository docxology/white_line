<!-- Note (2026-07-29): reviewer attribution has been anonymized pending explicit
consent for inclusion in permanently archived DOI records. Attribution will be
restored on confirmation. -->

# Correspondence: design reviews received

This page records external design reviews of White Line and what this
repository did about them. It is a decision record, not an endorsement chain:
each item names what was adopted, what was deferred with a reason, and what
was declined with a reason.

## 2026-07-29 — "The Space Between the Lines" (an external reviewer, with an analytic reader)

A two-voiced review of the collected line set (dated source: *The Line Set:
The Collected Volume*, 2026-07-27). Its reading of White Line: this is the
most explicit witness instrument in the set — it types the limit, leaves a
trace for rejected input, keeps the more cautious reading under conflict, and
gives each state a bounded human next question. Its sharpest technical
pressure lands here too: the total caution order (`NOT_RECORDED < NAMED <
UNRESOLVED < WITHHELD`) is coherent as a cautious report rule but lossy as a
complete ontology, because `UNRESOLVED` and `WITHHELD` answer different
questions — a record can be both — and a review horizon is a clock where a
learning system needs a return.

**Adopted here:**

- *The factorization.* `facets.py` separates the rich state from the cautious
  projection exactly as the review proposes: epistemic settlement ×
  disclosure stance × temporal status, with `project_facets` recovering the
  shipped state and the decay rule recovered as `NAMED` + `STALE` projecting
  to `UNRESOLVED`. The single ordered state remains what the assessor emits;
  the facets are a derived view of recorded data, never new observations.
- *Contradiction as co-present data.* Reconciliation events now carry the
  displaced observation's state typed (`IntakeEvent.displaced_state`), so a
  conflict is preserved as two surfaces, not merely a note that conflict
  occurred. The cautious resolution is unchanged.
- *Return-bearing witness.* `returns.py` upgrades the review horizon from
  calendar to obligation: trigger, due date (proven against the assessor at
  the decay boundary), expected return, and an acceptance condition under
  which remaining `UNRESOLVED` is an honest outcome and a `WITHHELD` return
  is boundary confirmation, never disclosure. Each contract points back at
  the report that set it.
- *The common report envelope.* `envelope.py` exports the review's first
  implementable piece under `line.report-envelope/1.0`, with
  `canonical_report`/`report_digest` added so the envelope has a complete
  native record to point at, and the instrument's non-claims riding inside.

**Answers to the review's direct questions (its "For Daniel" table):**

- *Is the caution order the full ontology or a safe projection?* A safe
  projection, now stated in code: `facets.py` is the factorization and
  `project_facets` is the projection.
- *Can one record be simultaneously `UNRESOLVED` and `WITHHELD`, first-class?*
  As an emitted state, no — the alphabet is unchanged, deliberately. As
  recorded data, yes: the facet space represents it, and a conflict between
  the two assertions now survives typed on the intake event.
- *Should any joint next-use posture exist in code here?* No. Nothing in this
  repository computes a cross-line posture; that belongs to the separate
  register work, if it is built at all.

**Deferred (stated in TODO):** manuscript formalism definitions for the
facets, return contracts, and envelope await the next manuscript window;
pre-categorical holding (`UNCLASSIFIED_HELD` outside the state alphabet) is
noted as a candidate for the register work rather than this ledger, whose
intake already leaves a typed trace for every rejected input.

*Update, 2026-07-29 (later window):* the deferred formalism shipped. The
manuscript's formal-method section now defines the facet alphabets and the
`WitnessFacets` tuple, the projection rule with its fail-closed cell, the
factorization proposition proven over the live scoring battery, the
`ReturnContract` tuple with the horizon-as-clock versus return-as-obligation
distinction, the `ReportEnvelope` tuple with `canonical_report`/`report_digest`,
and the `IntakeEvent` tuple carrying `displaced_state`; each block is bound to a
named test in the claim-to-test table, and a new derived plate
(`white_facets_lattice`) draws the full 24-cell projection with the live
battery's findings marked. Pre-categorical holding remains deferred to the
register work.

**Declined, by design:**

- The shared witness register itself. The review is explicit that it should
  not be smuggled into any existing line; White Line ships its envelope
  export and stops.
- Any widening of the emitted state alphabet or softening of the caution
  order. The projection stays the action-facing contract; the facets make
  its losses inspectable without making the ledger emit multiple verdicts.


### Wave-3 update (2026-07-29, later the same day)

The window above was independently re-verified: every measured number
reproduced (352 passed, 100.00% branch, byte-identical double figure build,
audit passed with zero errors and warnings), three fresh drifts planted in
the real formalism prose each failed exactly their named test, and the
facets-lattice plate was checked cell-by-cell against its registration. One
number in the window's own log was corrected during that pass: the truth
table has 21 projecting cells and three fail-closed cells, not 23 and one
(TODO.md log records the re-derivation). The skill descriptor gained the
envelope surface. The companion register now exists and accepted this
line's actually-exported envelope unmodified.
