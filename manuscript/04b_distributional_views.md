# Reading one report distributionally {#sec:distributional}

The worked entries above read a report record by record. A reviewer auditing a
whole ledger usually needs the complementary view: *how was the input handled
in aggregate, and where do the states currently sit across the three kinds of
absence?* The `white_line.analysis` module answers with three distributional
summaries, each computed either through the public `assess_absence` call or
directly from the defined caution order: a per-code tally of intake events
(`events_tally`), a kind-by-state cross-tabulation of findings
(`coverage_matrix`), and the review-date sweep (`decay_timeline`) presented
alongside [@prop:staleness] in the formal-method section. All three are pure and
additive. Nothing in the module changes what the ledger records or how a state
is assigned; the summaries only make the existing contract inspectable. They
are descriptive displays in Tukey's sense — arrangements of what happened,
offered before and instead of inference [@tukey1977] — not scores of any kind.

## A worked intake under careless and adversarial input

The intake stage is easiest to see when the input deliberately exercises its
screening rules. The following seven inputs — assessed against the live
registry with `as_of="2026-07-18"` — include a two-observer conflict, a
same-state duplicate, a typo'd record id, an attempt to assert the reserved
state, and one object that is not an observation at all:

```python
from white_line import (
    coverage_matrix,
    events_tally,
    worked_intake_observations,
    worked_report,
)

observations = worked_intake_observations()
report = worked_report()
```

`events_tally(report)` returns a count for **every** intake code, including
the codes that did not fire — a zero is reported, never omitted. For this
input the distribution is:

| Intake code           | Count | What happened here                                                          |
| --------------------- | ----: | --------------------------------------------------------------------------- |
| `NON_ITERABLE_INPUT`  |     0 | The input container itself was iterable.                                    |
| `NON_OBSERVATION`     |     1 | The bare string was set aside; it is not an observation.                    |
| `UNKNOWN_RECORD`      |     1 | `no-such-record` names no registry id.                                      |
| `UNTYPED_STATE`       |     0 | Every remaining state was a genuine `AbsenceState` member.                  |
| `RESERVED_STATE`      |     1 | The asserted `NOT_RECORDED` was screened out ([@prop:reserved-meta-state]). |
| `UNDATED_OBJECT`      |     0 | Every dated observation carried a parseable ISO string.                     |
| `CONFLICTING_STATES`  |     1 | The `NAMED`/`UNRESOLVED` disagreement kept `UNRESOLVED`.                    |
| `DUPLICATE_STATE`     |     1 | The agreeing `WITHHELD` pair kept the last-listed note.                     |

Eight rows for eight codes, five events, and exactly five matching intake
notes — [@prop:no-silent-discard] made
countable. The conflict row is [@prop:caution-monotonicity] in one line: the two observers of
`unobserved-dependency` disagreed, and the record's reported state is
`UNRESOLVED`, the more cautious of the pair, exactly as the conflict-lattice
figure in the formal-method section tabulates for all nine ordered pairs. The
resulting state tally is `NAMED` $0$, `UNRESOLVED` $1$, `WITHHELD` $1$, and
`NOT_RECORDED` $9$: eleven findings, one per record, as [@prop:totality]
requires.

An important reading rule follows directly from the table: an event count is
audit data about *input handling*, never a verdict on whoever supplied the
input. A ledger whose event tally is all zeros has clean input mechanics; it
has not thereby earned trust for its content. And a nonzero `UNKNOWN_RECORD`
row may mean a typo, a stale registry checkout, or an extension that was never
registered — the code names what the intake stage did, not why the mismatch
exists.

## A zero row is untriggered, not unreachable

Three of the eight rows above are zero, which leaves a reader with a question
the table cannot answer: is the code merely untriggered by this input, or is it
dead code that nothing can reach? A reporting convention that prints zeros
honestly is worth very little if some of those zeros can never become anything
else. The battery below settles it. Each row supplies one input constructed to
reach exactly one code, runs it through `assess_absence`, and prints the input
beside the typed note the evaluator returned. Every member of the enumeration
fires, so the zeros in the worked tally mean untriggered here.

![A positive control for the intake contract: one constructed input per `IntakeCode`, each run through `assess_absence`, drawn as one row with the input quoted beside the typed note the evaluator produced for it. Every member of the live enumeration fires, so a zero in the worked tally above means the code was not triggered by that input rather than that the code is unreachable. The battery is built to exercise the contract; it is not observed input, and no note is a verdict on whoever supplied an input.](../output/figures/white_intake_reachability.png){#fig:white-intake-reachability width=100%}

The battery is a demonstration of reachability and nothing more. It shows that
each code *can* be produced, not that any real review would produce it, and
certainly not that a review producing it has gone wrong. `NON_ITERABLE_INPUT`
appears only when the whole input, rather than one of its members, cannot be
iterated, which is why the battery supplies whole inputs rather than a single
list.

## Where the states sit across the three kinds

`coverage_matrix(report)` cross-tabulates the same eleven findings by kind and
state, with every cell present even at zero. For the worked input above:

| Kind            | `NAMED` | `UNRESOLVED` | `WITHHELD` | `NOT_RECORDED` | Row sum |
| --------------- | ------: | -----------: | ---------: | -------------: | ------: |
| `EPISTEMIC`     |       0 |            1 |          0 |              3 |       4 |
| `ETHICAL`       |       0 |            0 |          1 |              3 |       4 |
| `CONTEMPLATIVE` |       0 |            0 |          0 |              3 |       3 |
| **Column sum**  |   **0** |        **1** |      **1** |          **9** |  **11** |

The margins are not decoration; they are the consistency check. Row sums
($4$, $4$, $3$) equal the registry's partition by kind from [@def:registry], and
column sums equal the report's own `tally` — the test suite asserts both
identities against real assessments. The same helper applied to an
empty-input assessment gives the baseline every review starts from: all
eleven records `NOT_RECORDED`, distributed $4/4/3$ down the final column,
every other cell zero.

What the matrix supports is a bounded reviewer question, asked kind by kind:
*the ethical row currently holds one `WITHHELD` and three `NOT_RECORDED`
records — have those three simply not been reviewed this cycle, or is the
review itself avoiding them?* The matrix cannot answer that question, and it
is not meant to. A full `NOT_RECORDED` column is not negligence, a full
`NAMED` row is not diligence, and no cell count is a completeness or coverage
*score* of any work. The numbers describe records in a ledger; the judgment
about what the distribution means belongs to the humans conducting the
review, with the report's `review_date` and `registry_digest` attached so a
later reviewer can tell which registry and which day the distribution
describes ([@prop:context-traceability]).

![The two distributional views of the worked seven-input example, computed live through `assess_absence`, `events_tally`, and `coverage_matrix` at review date 2026-07-18: intake-event counts per code in the upper panel, with zeros reported rather than omitted, and the kind-by-state coverage matrix in the lower panel, with row sums matching the registry's partition by kind and column sums matching the report's own tally. The figure draws the same computation as the two tables above, over the same eight intake codes. Neither an event count nor a cell count is a completeness score, a safety score, or a verdict on whoever supplied the input.](../output/figures/white_distribution_panels.png){#fig:white-distribution-panels width=100%}

The third view — sweeping the review date while holding the observations fixed
— appears with the staleness proposition in the formal-method section, where
its four transition days ($91$, $121$, $181$, $366$) are read off the
registry's horizon multiset. The three views cover the report's three axes of
variation: how input became findings, how findings distribute over the
typology, and how a fixed input's findings move as the review date advances.
None of them adds information the report did not already carry, which is
exactly what makes them safe to automate.

## What comes due next, and what cannot come due at all

A reviewer holding a report also needs a prospective view: of the namings
recorded today, which one reaches its review boundary first?
`expiry_horizon(report)` answers that, returning one entry per current dated
`NAMED` finding, ordered nearest-boundary-first, each carrying the record's
horizon, the naming's age, and the days that remain. Its omissions carry as
much information as the queue. A naming the evaluator could not date cannot
expire, so it never enters — not because it is fresh, but because staleness
accounting has nothing to measure against. A naming already past its horizon is
reported `UNRESOLVED` rather than `NAMED`, so it has left by decaying. Both are
drawn as labelled bands beneath the queue rather than dropped, because a
silently absent row would be a strange failure in a work about absence, and the
undated naming is the one a reviewer is most likely to assume is current.

![The refresh queue computed by `expiry_horizon` over one assessed report: every current dated `NAMED` finding, ranked nearest-boundary-first, with its kind shown by colour and by marker shape, its age drawn as a filled portion of its own review horizon, and its remaining days stated in words. The helper's two documented omissions are drawn as labelled bands rather than dropped: a naming the evaluator could not date cannot expire, and a naming already past its horizon is reported `UNRESOLVED`. Queue position is a review cadence, not importance, risk, or a completeness score.](../output/figures/white_expiry_queue.png){#fig:white-expiry-queue width=100%}

The queue ranks by days remaining, not by weight. A record near the top is one
the ledger will ask about soon, which is a statement about the cadence its
horizon declares and about nothing else. Two records with identical remaining
days sort by id, so the order is total and the figure is reproducible.

## The state as a safe projection: the witness layer

Every view above reads the single caution-ordered state, and that state is a
deliberate compression. Strong support and strong resistance co-present in a
record are not the same situation as no evidence at all, yet a lone ordered
value cannot say so. The witness layer ([@def:facets] through [@def:envelope]
in the formal-method section) makes the compression inspectable without
widening what the evaluator emits: `finding_facets` factors each finding into
its epistemic settlement, disclosure stance, and temporal status;
`project_facets` states the rule that recovers the shipped state from them;
`return_contracts` reads each record's review horizon forward as an obligation
with a due date proven at the decay boundary; and `report_envelope` wraps the
complete report for co-registration beside the other lines, pointing at the
canonical report by digest and never reinterpreting it. A conflict likewise
survives reconciliation as typed data: the intake event keeps the displaced
observation's asserted state, so the more cautious resolution stands without
erasing what it displaced.

The lattice below draws the whole projection at once. Each cell is one facet
combination and carries the state `project_facets` returns for it; the three
cells for an undisclosed settlement without a stated withholding fail closed,
because that is not a state this ledger can have recorded; and the marked
cells are where the live scoring battery's findings land when each is factored
through `finding_facets` at build time. The one cell in which a `NAMED`
settlement projects to `UNRESOLVED` is the staleness decay, recovered here as
a projection rather than a rewrite — the prior naming and its age survive as
facets ([@prop:factorization]).

![The full facet lattice computed by running `project_facets` over every settlement, disclosure-stance, and temporal-status combination: each cell is coloured and labelled by the single caution-ordered state the projection returns, the cells for an `UNDISCLOSED` settlement without a stated withholding are drawn hatched because that combination fails closed rather than projecting, and the cells inhabited by the live scoring battery are marked by factoring each of its findings through `finding_facets` at build time. The one cell where a `NAMED` settlement projects to `UNRESOLVED` is the staleness decay recovered as a projection. The lattice is a projection table of recorded-data facets; it is not a claim that richer states exist in the world, and an inhabited cell is a fact about the battery's constructed inputs, never about any observed work.](../output/figures/white_facets_lattice.png){#fig:white-facets-lattice width=100%}

None of this ranks anything. The facets are derived views of recorded data,
never new observations; a return contract earns a re-review, never a pass; and
envelopes from different lines must not be compared, averaged, or merged — the
envelope exists so that a separate register, if one is ever built, can
co-register complete reports without any line reinterpreting another.
