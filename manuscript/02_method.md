# Method: three kinds of absence, four ledger states {#sec:method}

An absence record has an identifier, a title, a kind, a bounded description, a
reviewer's `prompt`, and a `review_horizon_days` bound. The kind answers what
sort of limit is being recorded:

- **Epistemic absence** concerns what has not been observed, measured,
  accessed, or resolved.
- **Ethical restraint** concerns what is withheld, unrepresented, or not
  disclosed because a duty of care, consent, or safety boundary matters.
- **Contemplative negative space** concerns what is intentionally left open
  beyond a useful claim. It does not assert a literal invisible force.

An observation assigns a record one state. `NAMED` says the absence has been
made explicit. `UNRESOLVED` says it is known but not settled. `WITHHELD` says
material is intentionally not disclosed. `NOT_RECORDED` is emitted when no
observation exists — and it is reserved for the ledger itself, so an observation
that tries to assert it is set aside at intake. The analyzer does not infer
intent from silence, promote a gap to a cause, or use one kind of absence as
evidence for another.

The assessment is staged rather than a single lookup. Intake normalizes and
screens the input, matching keeps at most one contract-passing observation per
record, and scoring assigns each record its state. Two rules run through the
whole pipeline. First, nothing is discarded quietly: every set-aside input,
resolved conflict, and same-state duplicate leaves a typed event and a note in
the report. Second, caution only rises: when observers disagree the ledger keeps
the more cautious state, and a dated `NAMED` observation that ages past its
record's horizon is reported `UNRESOLVED` until it is re-reviewed. Under this
contract no input can make an absence look more settled than its most cautious
observer reported. A malformed custom registry or an invalid review date fails
closed. The formal-method section states each of these behaviors, and the six
structural invariants that guard the registry's shape, as definitions and
propositions.

The registry is deliberately finite and versioned. Projects can extend it, but
an extension should state its kind, its scope, and the non-claim it protects;
the evaluator refuses an extension that fails the structural checks. The report's
date and registry digest should be stored with any downstream review.

![The White Line review atlas: type the limit, reconcile the record, and open a bounded next question. Counts and actions are derived from the live registry, state alphabet, and review protocol; the atlas is not a summary of an observed population.](../output/figures/white_review_atlas.png){#fig:white-review-atlas width=100%}
