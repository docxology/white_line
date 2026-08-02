# Review protocol: from state to responsible follow-up {#sec:review-protocol}

The evaluator reports a state; it does not decide what a person or project may
do. White Line therefore keeps a second record explicit: a bounded review
directive for each finding. `review_directives(report)` (formalized as
[@def:directive] and [@prop:bounded-follow-up]) maps
`NOT_RECORDED` to recording or explicitly scoping the unreviewed category,
`UNRESOLVED` to reopening or bounding the question, `WITHHELD` to honoring and
confirming the boundary without seeking disclosure, and `NAMED` to retaining
the naming without treating it as resolution. None of these directives is an
approval, compliance, safety, or truth verdict.

![The bounded White Line review protocol maps each state to human follow-up without producing permission, compliance, or safety approval. It is derived from the state enumeration and review directives, not from observed safety data.](../output/figures/white_review_protocol.png){#fig:white-review-protocol width=100%}

The operator loop is deliberately short:

1. Fix a review date and retain the registry digest.
2. Supply only observations the reviewer is authorized to record.
3. Inspect every typed intake event; a set-aside input is a limitation of the
   review, not an invisible rejection.
4. Read every finding and its directive, preserving withholding where a duty,
   consent condition, or safety boundary requires it.
5. Re-run after material context changes or after a dated naming passes its
   review horizon.

The resulting report is useful precisely because it does not collapse these
steps into a score. The protocol makes the next human question visible while
leaving independent verification, consent, security review, and domain
judgment where they belong.
