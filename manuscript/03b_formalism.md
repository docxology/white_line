# Formal method: the evaluator and its invariants {#sec:formalism}

The three kinds ([@def:kinds]) and four states ([@def:states]) just described are restated formally below.

This section states, as definitions and propositions, exactly what the
executable instrument computes. The formalism describes the code; it does not
extend it. Every enumerated value, decision branch, and structural check below
is present in the `white_line` package, each named guarantee is exercised by a
test, and where the prose states a count, that count is re-derived from the
registry and the enumerations rather than typed. Numbering is generated at
render time from the labels, so a block inserted here renumbers every reference
to it.

## Domain objects

::: {.definition #def:kinds title="Kinds"}
The kind alphabet is the set
$K = \{\texttt{EPISTEMIC}, \texttt{ETHICAL}, \texttt{CONTEMPLATIVE}\}$, with
$|K| = 3$. A kind answers *what sort of limit* a record describes.
:::

::: {.definition #def:states title="States"}
The state alphabet is
$S = \{\texttt{NAMED}, \texttt{UNRESOLVED}, \texttt{WITHHELD}, \texttt{NOT\_RECORDED}\}$,
with $|S| = 4$. `NOT_RECORDED` is reserved for the ledger itself and marks the
meta-gap of a record for which no observation was supplied; an observation may
not assert it.
:::

::: {.definition #def:record title="Absence record"}
An absence record is a frozen tuple
$r = (\mathit{id}, \mathit{title}, \mathit{kind}, \mathit{description},
\mathit{prompt}, \mathit{review\_horizon\_days})$ with
$\mathit{kind} \in K$ and a review horizon
$\mathit{review\_horizon\_days} \in \mathbb{Z}^{+}$ measured in days. The
`prompt` is the question a reviewer sits with; the horizon bounds how long a
dated naming stays fresh.
:::

::: {.definition #def:registry title="Registry"}
The registry is the finite ordered tuple $R = (r_1, \dots, r_{11})$ of $11$
records. Partitioned by kind it contains
exactly $4$ epistemic, $4$ ethical, and $3$ contemplative records,
and every horizon lies in $\{90, 120, 180, 365\}$ days. The registry is
versioned; its canonical digest is a change-review instrument with no safety
semantics.
:::

::: {.definition #def:caution-order title="Caution order"}
Caution is the total order induced by the rank map $c : S \to \{0,1,2,3\}$,

$$c(\texttt{NOT\_RECORDED}) = 0 < c(\texttt{NAMED}) = 1 < c(\texttt{UNRESOLVED}) = 2 < c(\texttt{WITHHELD}) = 3.$$

Withholding outranks an open question, which outranks a settled naming, which
outranks silence.
:::

![The defined caution order, read directly from `caution_rank`. When observers of one record disagree, the evaluator keeps the higher rung; staleness moves a naming from `NAMED` to `UNRESOLVED`, toward greater caution. Each rung also reports, live from `reconciliation_matrix`, in how many of the nine ordered pairs it is the kept state; the rules that use the order are drawn in the conflict-lattice and decay-timeline figures. A higher rung means more restraint, not more danger. The figure is a deterministic schematic generated from the state enumeration, not a severity score.](../output/figures/white_caution_ladder.png){#fig:white-caution-ladder width=100%}

::: {.definition #def:observation title="Observation"}
An observation is a tuple
$o = (\mathit{record\_id}, \mathit{state}, \mathit{note}, \mathit{observed\_on})$,
where `observed_on` is an optional ISO date. Undated observations are accepted
but cannot participate in staleness accounting.
:::

::: {.definition #def:finding title="Finding"}
A finding is a frozen tuple
$f = (\mathit{record\_id}, \mathit{kind}, \mathit{state}, \mathit{reasons},
\mathit{observed\_on})$ carrying the assessed state together with the ordered
trail of reasons that produced it.
:::

::: {.definition #def:report title="Report"}
A report is a tuple
$(\mathit{findings}, \mathit{intake\_notes}, \mathit{review\_date},
\mathit{registry\_digest}, \mathit{intake\_events})$. Its `tally` maps every
state in $S$ to a count, including states that occur zero times. The review
date anchors staleness accounting; the registry digest identifies the record
schema that was assessed; typed intake events preserve how input was handled.
:::

::: {.definition #def:event title="Intake event"}
An intake event is a frozen tuple
$e = (\mathit{code}, \mathit{message}, \mathit{position}, \mathit{record\_id},
\mathit{state}, \mathit{displaced\_state})$ recording one intake or
reconciliation decision. The `code` ranges over the intake code alphabet the
intake stage partitions; the `position` names the input position when one
exists. For the two match-stage codes, `displaced_state` carries the asserted
state of the observation the reconciliation replaced, so a conflict survives
as two co-present typed surfaces rather than only as a note that a conflict
occurred; it is empty for every set-aside and dating event, where nothing was
displaced. An event is descriptive audit data, never a verdict on whoever
supplied the input.
:::

## The staged evaluator

::: {.definition #def:assessment-map title="Assessment map"}
The evaluator is the function

$$\texttt{assess\_absence} : \mathrm{Obs}^{*} \cup \{\bot\} \;\times\; R^{*} \;\times\; (\mathrm{ISO} \cup \mathrm{Date} \cup \{\bot\}) \;\longrightarrow\; \mathrm{Report},$$

whose three parameters are `observations`, `records`, and `as_of`. The third
resolves to a review date $d$ (today when $\bot$), and an invalid date fails
closed. Before intake, a custom registry must satisfy all $6$ structural
checks. The computation then runs in three stages: intake normalization,
matching, then scoring.
:::

::: {.definition #def:intake title="Intake stage"}
Intake $\Pi$ consumes the raw input in positional order and produces a map
$A : \mathit{id} \to o$ of at most one accepted observation per record,
together with typed events and one note per event. An input that cannot be
iterated at all is refused whole, yielding an empty $A$ and a single
`NON_ITERABLE_INPUT` event. Otherwise an input at position $i$ is set aside,
with an event, when any of the following holds:

1. it is not an absence observation (`NON_OBSERVATION`);
2. its `record_id` is not the id of some record in $R$ (`UNKNOWN_RECORD`);
3. its `state` is not a member of $S$ (`UNTYPED_STATE`);
4. its `state` is `NOT_RECORDED`, the reserved meta-state (`RESERVED_STATE`).

An accepted observation whose `observed_on` is neither absent nor a string is
kept and scored but emits `UNDATED_OBJECT`: acceptance is not dating. When two
accepted observations name the same record with differing states, $\Pi$ keeps
$\arg\max_{o} c(o.\mathit{state})$ — the more cautious — and records a
`CONFLICTING_STATES` event. When states agree, the last-listed observation is
kept and `DUPLICATE_STATE` records that replacement. The rule is positional,
not chronological: it depends on input order, not on either observation's date.

Intake therefore uses the whole code alphabet and partitions it:
`NON_ITERABLE_INPUT`, `NON_OBSERVATION`, `UNKNOWN_RECORD`, `UNTYPED_STATE`, and
`RESERVED_STATE` refuse an input; `UNDATED_OBJECT` keeps one whose date it
cannot use; `CONFLICTING_STATES` and `DUPLICATE_STATE` reconcile two that were
kept. No input is ever dropped without a note. When $\Pi$ reconciles two
accepted observations, the resulting event also carries the displaced
observation's asserted state as typed data ([@def:event]), preserving the
conflict as co-present surfaces; the cautious resolution is unchanged.
:::

::: {.definition #def:date-resolution title="Date resolution"}
Given `observed_on` and review date $d$, the resolution rule $\delta$ returns a
pair (parsed-date-or-$\bot$, issue-note). Absent input — `None` or the empty
string — yields $(\bot, \varepsilon)$: an undated observation is ordinary, and
there is nothing to report. A non-string object yields $(\bot,$
`UNDATED_OBJECT`$)$: the observation is accepted and scored, but its date
cannot age. An unparseable ISO string yields $(\bot,$ "unreadable"$)$, and a
date $t$ with $t > d$ yields $(\bot,$ "after the review date"$)$. Otherwise
$\delta$ yields $(t, \varepsilon)$. A future date never counts as evidence.

$\delta$ has exactly one implementation,
`white_line.dates.usable_observation_date`. Scoring calls it, and so does the
`expiry_horizon` view when it reads a report back, so no view can age an
observation the evaluator refused to age.
:::

::: {.definition #def:scoring title="Scoring rule"}
For a record $r$ with horizon $H$, its accepted observation $o$ (possibly
absent), and review date $d$, the scoring rule $\varphi$ reports:

1. **No observation** ($o = \bot$): state `NOT_RECORDED`, reason
   `no absence note was recorded`.
2. **$o.\mathit{state} = \texttt{WITHHELD}$**: state `WITHHELD`, reason
   `material is intentionally withheld`; and if the note is blank, the added
   reason `no boundary is stated for the withholding; restraint should name its duty`.
3. **$o.\mathit{state} = \texttt{UNRESOLVED}$**: state `UNRESOLVED`, reason
   `the absence is named but not resolved`.
4. **$o.\mathit{state} = \texttt{NAMED}$** with $\delta = (t, \cdot)$ and
   $\mathit{age} = (d - t)$ in days: reason `the absence is explicitly named`
   when the naming is current, and otherwise the decay stated below.

$$\varphi_{\texttt{NAMED}}(r, o, d) = \begin{cases} \texttt{UNRESOLVED} & \text{if } t \neq \bot \text{ and } \mathit{age} > H \quad (\text{staleness decay}),\\ \texttt{NAMED} & \text{otherwise.}\end{cases}$$

Any date issue note from $\delta$ and any recorded note are appended to the
finding's reasons in that order.
:::

::: {.definition #def:directive title="Review directive"}
The protocol maps each finding to one bounded action $\rho$ without producing
an approval state:

$$
\begin{aligned}
\rho(\mathrm{NAMED}) &= \mathrm{RETAIN\_NAMED\_SCOPE}\\
\rho(\mathrm{UNRESOLVED}) &= \mathrm{REOPEN\_OR\_BOUND}\\
\rho(\mathrm{WITHHELD}) &= \mathrm{HONOR\_AND\_CONFIRM\_BOUNDARY}\\
\rho(\mathrm{NOT\_RECORDED}) &= \mathrm{RECORD\_OR\_EXPLICITLY\_SCOPE}
\end{aligned}
$$

The action is a prompt for human review, not a claim that the observation is
true, safe, authorized, or complete.
:::

![The staged evaluator's decision path: intake sets aside untrusted input while leaving a typed note, matching keeps at most one — and the more cautious — observation per record, and scoring assigns exactly one of the four ledger states. The set-aside and match categories name every `IntakeCode` member, and the figure build fails if that enumeration changes, so the panels cannot silently drift from the intake rules. The labeled staleness arrow shows a dated `NAMED` naming decaying to `UNRESOLVED` once it ages past its horizon. The figure is generated from the evaluator contract, not from observed safety data; the reading rule beneath it is essential when the visual is read without the surrounding prose.](../output/figures/white_state_machine.png){#fig:white-state-machine width=100%}

![One row per branch of the scoring rule, each computed by a live `assess_absence` call and drawn with the ordered reason trail the evaluator returned. The two conditional reasons appear only in the branch that adds them: a blank-note withholding gains the duty reason, and a dated naming gains either its age line or the decay line. The plate quotes what the evaluator wrote, so a reworded reason moves the figure rather than leaving the prose behind. A reason is an explanation of one scoring decision, never a judgment of the observation or of whoever supplied it.](../output/figures/white_reason_trail.png){#fig:white-reason-trail width=100%}

## Semantic guarantees

Each proposition below is a property of the maps just defined and is covered by
the evaluator test suite.

::: {.proposition #prop:reserved-meta-state title="Reserved meta-state"}
No observation can cause the report to assign `NOT_RECORDED` to a record. It is
emitted only in the first branch of $\varphi$, for a record with no accepted
observation. *Reason:* $\Pi$ discards any observation whose state is
`NOT_RECORDED` ([@def:intake], clause 4), so the state can never reach
$\varphi$ through an input.
:::

::: {.proposition #prop:caution-monotonicity title="Caution monotonicity"}
The state a record receives is never less cautious than the most cautious
accepted observer of that record. Conflict resolution keeps the higher-caution
state ([@def:intake]), and the only state rewrite in scoring is the staleness
decay $\texttt{NAMED} \to \texttt{UNRESOLVED}$, which raises caution from $1$
to $2$. The ledger therefore never resolves a disagreement, or an aging naming,
by making an absence look *more settled* than it was reported.
:::

The reconciliation half of [@prop:caution-monotonicity] is small enough to
exhibit exhaustively. The pure helper `reconciliation_matrix` in
`white_line.analysis` returns the full ordered-pair resolution table over the
three assertable states — $9$ ordered pairs, each resolving to $\arg\max$ under
$c$ — and the test suite checks every cell against a real two-observer
`assess_absence` call in both arrival orders. The table is symmetric with an
identity diagonal, and `NOT_RECORDED` appears in no pair and no cell, because
intake screens it out before reconciliation can see it.

![The full ordered-pair conflict-resolution table for assertable states, generated from `caution_rank` via `reconciliation_matrix`. Every cell keeps the more cautious input, the table is symmetric under swapping the observers — arrival order carries no authority — and the ledger-reserved `NOT_RECORDED` appears nowhere because observations may not assert it. The lattice records the reconciliation contract, not a severity score or a judgment of any observer.](../output/figures/white_conflict_lattice.png){#fig:white-conflict-lattice width=100%}

::: {.proposition #prop:staleness title="Staleness"}
A dated `NAMED` observation whose age exceeds its record's horizon is reported
`UNRESOLVED`, never `NAMED` ([@def:scoring], clause 4). The old naming is no
longer current evidence for a settled state.
:::

Because the report is anchored by an explicit review date,
[@prop:staleness] can be made visible by holding one observation set fixed and
sweeping the review date — the `decay_timeline` helper in `white_line.analysis`
re-runs `assess_absence` at each date and tallies the resulting ledgers. For an
illustrative cohort in which every record receives a `NAMED` observation dated
on day $0$, the swept ledger changes on exactly four days —
offsets $91$, $121$, $181$, and $366$ — one day after each of the registry's
four horizon values ($\{90, 120, 180, 365\}$ from [@def:registry]) expires. The
`NAMED` count steps $11 \to 8 \to 6 \to 3 \to 0$ while `UNRESOLVED` gains the
same records, and at every review date the four state counts still sum to $11$
([@prop:totality]). The sweep is a view of the contract applied to supplied
observations; it is not observed data about any work, and a fully decayed
cohort is not a finding that anything is wrong — only that the namings are due
for re-review.

![Staleness decay computed by sweeping `assess_absence` over review dates via `decay_timeline`: every registry record receives a `NAMED` observation dated 2026-01-01, and the same input is re-assessed at each later date. Each dashed crossing is one review horizon expiring — days 91, 121, 181, and 366, one day past the horizons 90, 120, 180, and 365 — moving records from `NAMED` to `UNRESOLVED`. Decay only raises caution; the curve describes the staleness contract applied to an illustrative cohort, not observed data about any work.](../output/figures/white_decay_timeline.png){#fig:white-decay-timeline width=100%}

::: {.proposition #prop:no-silent-discard title="No silent discard"}
Every set-aside input, resolved conflict, and same-state duplicate contributes
a typed event and a note to `intake_notes`. Discarding is therefore always
visible in the report.
:::

::: {.proposition #prop:totality title="Totality"}
Every record in $R$ yields exactly one finding, and `tally` accounts for all
four states of $S$. The report is a total map over the current registry, not a
complete account of the world or a filtered list of hits.
:::

::: {.proposition #prop:context-traceability title="Context traceability"}
Every report produced by the evaluator carries the resolved review date and the
canonical digest of the validated registry used to produce it. Two reports with
different review dates or registry contents are therefore not silently
interchangeable.
:::

::: {.proposition #prop:bounded-follow-up title="Bounded follow-up"}
`review_directives` maps every finding to exactly one action in
[@def:directive] and never maps a state to `COMPLIANT`, `SAFE`, or `APPROVED`.
The package describes a review boundary; it does not enforce a decision.
:::

## The witness layer

The caution order of [@def:caution-order] is a safe projection, not the whole
state space: a single ordered value compresses how settled the record is,
whether disclosure is being withheld, and how current the recorded observation
is. The definitions below state that compression exactly — the facets it loses,
the rule that recovers the shipped state from them, the obligation a review
horizon reads forward to, and the envelope that makes a complete report
transportable. Nothing in this layer changes what the evaluator records or
emits; every object is derived from data a report already carries.

::: {.definition #def:facets title="Witness facets"}
The facet alphabets are the epistemic settlement
$E = \{\texttt{NOT\_RECORDED}, \texttt{NAMED}, \texttt{UNRESOLVED},
\texttt{UNDISCLOSED}\}$, the disclosure stance
$D = \{\texttt{OPEN}, \texttt{WITHHELD}\}$, and the temporal status
$T = \{\texttt{CURRENT}, \texttt{STALE}, \texttt{UNDATED}\}$, with
$|E| = 4$, $|D| = 2$, and $|T| = 3$. A witness facet record is a frozen tuple
$w = (\mathit{record\_id}, \mathit{settlement}, \mathit{disclosure},
\mathit{temporality})$. `UNDISCLOSED` is the settlement behind a stated
withholding — a statement about what the ledger can see, never a suspicion —
and `STALE` describes the age of a recording under the record's horizon,
through the same date-resolution rule $\delta$ of [@def:date-resolution],
never the world the record points at. The facets describe recorded data only:
`finding_facets` derives them from a finding the evaluator produced and fails
closed on a finding this evaluator could not have written.
:::

::: {.definition #def:projection title="Projection rule"}
The projection $\pi : E \times D \times T \to S$ is partial and restates the
caution order as a projection of the facets:

$$\pi(w) = \begin{cases} \texttt{WITHHELD} & \text{if } w.\mathit{disclosure} = \texttt{WITHHELD},\\ \bot \text{ (fails closed)} & \text{if } w.\mathit{settlement} = \texttt{UNDISCLOSED} \text{ otherwise},\\ \texttt{NOT\_RECORDED} & \text{if } w.\mathit{settlement} = \texttt{NOT\_RECORDED},\\ \texttt{UNRESOLVED} & \text{if } w.\mathit{settlement} = \texttt{UNRESOLVED},\\ \texttt{UNRESOLVED} & \text{if } w.\mathit{temporality} = \texttt{STALE} \quad (\text{staleness decay}),\\ \texttt{NAMED} & \text{otherwise.}\end{cases}$$

Of the $24$ combinations in $E \times D \times T$, $21$ project and $3$ fail
closed: an `UNDISCLOSED` settlement without a `WITHHELD` stance is not a state
this ledger can have recorded, and `project_facets` refuses it rather than
guessing. The full table is pinned cell by cell in the test suite and drawn,
with the fail-closed cells hatched, in the facets-lattice figure of the
distributional-views section.
:::

::: {.proposition #prop:factorization title="Factorization"}
For every finding $f$ a live `assess_absence` call produces, with record $r$
and review date $d$,
$\pi(\texttt{finding\_facets}(f, r, d)) = f.\mathit{state}$. In particular the
staleness decay of [@def:scoring] is recovered as a projection rather than a
rewrite: a dated naming aged past its horizon factors as settlement
`NAMED` with temporality `STALE` and projects to `UNRESOLVED`, so the prior
naming and its age survive the decay as facets instead of being replaced by
asserted doubt. The property is proven branch by branch over the live scoring
battery, not against a restatement of the rules.
:::

::: {.definition #def:return title="Return contract"}
A return contract is a frozen tuple
$(\mathit{record\_id}, \mathit{state}, \mathit{action}, \mathit{trigger},
\mathit{due\_on}, \mathit{expected\_return}, \mathit{acceptance\_condition},
\mathit{review\_date}, \mathit{registry\_digest})$, one per finding, derived
deterministically from the finding, its record, and the report's own review
date through the same $\delta$ of [@def:date-resolution] the evaluator scored
with. The action is the protocol's own directive from [@def:directive]; the
trigger, expected return, and acceptance condition are the pinned module
constants a live contract carries; and the review date and registry digest
point back at the producing report, so a return answers an exact prior state
rather than rewriting history. Fulfilling a contract earns a re-review, never
a pass: an `UNRESOLVED` return may honestly leave the question open, and a
`WITHHELD` contract's return is boundary confirmation, never disclosure.
:::

A review horizon, by itself, is a clock: it says when to look again and
nothing else. A return contract is the same horizon read forward as an
obligation — what must come back, what would count as an earned change, and
which review state it returns to. For a current dated naming the two meet at
one boundary: under the strict $\mathit{age} > H$ rule of [@def:scoring],
`due_on` is the observation date plus the horizon — the *last* review date on
which the naming is still current, since a review one day later decays it.
The binding test proves the boundary through the evaluator itself, assessing
the same observation on `due_on` (still `NAMED`) and one day after
(`UNRESOLVED`), rather than restating the arithmetic.

::: {.definition #def:envelope title="Report envelope"}
The canonical report is a stable serialization of a complete report —
findings, reasons, intake events, and notes — whose SHA-256 digest is the
report's `report_digest`. The report envelope is the tuple
$(\mathit{schema\_version}, \mathit{line\_id}, \mathit{subject\_id},
\mathit{review\_date}, \mathit{registry\_version}, \mathit{registry\_digest},
\mathit{native\_status}, \mathit{report\_ref},
\mathit{source\_snapshot\_refs}, \mathit{scope\_and\_nonclaims})$ exported
under the schema string `line.report-envelope/1.0`, where `report_ref` is
that digest: the envelope points at the complete native report and never
reinterprets it. `native_status` is deliberately typed in this line's own
vocabulary — the complete ordered per-record states, because this instrument
has no single overall verdict — and the transportable non-claims ride inside,
so a stored envelope cannot quietly outgrow what the instrument was allowed
to say. Sibling instruments export the same shape by publishing the same
schema string, never by importing one another, and envelopes from different
lines must not be compared, ranked, averaged, or merged.
:::

## Structural invariants

Beyond any single assessment, six pure-compute checks validate the *shape* of
the registry. Let $\mathrm{ledger\_sound}(R) = \bigwedge_{i=1}^{6} P_i(R)$.

- **$P_1$ — distinct ids.** No two records share an id; a duplicate makes
  findings ambiguous and makes the digest order-dependent.
- **$P_2$ — canonical slug ids.** Every id matches the reviewed spelling
  `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`.
- **$P_3$ — inhabited fields.** `id`, `title`, `description`, and `prompt` are
  non-blank strings; a blank prompt gives a reviewer nothing to sit with.
- **$P_4$ — valid, covered kinds.** Every `kind` is a genuine member of $K$
  (a frozen dataclass does not type-check its fields), and all three kinds are
  present, so no whole kind of absence is silently lost.
- **$P_5$ — positive horizons.** Every horizon is a positive integer and not a
  boolean, so staleness arithmetic is well defined.
- **$P_6$ — stable serialization.** The canonical form builds, parses as JSON,
  and produces a digest independent of record order.

::: {.proposition #prop:defect-detection title="Defined-defect detection"}
Each invariant $P_i$ is accompanied by a planted-defect registry: a registry
carrying exactly the defect $P_i$ guards against is constructed, and $P_i$
fails on it while passing on the real registry $R$. A check that has never
rejected a bad input is not counted as protection. This is the whole of the
claim — the battery establishes detection of the planted defects, not the
absence of every conceivable structural fault.
:::

The battery is not only a test fixture. `invariant_defect_battery` in
`white_line.invariants` constructs each defective registry, runs the whole
check suite over it, and refuses to return unless the targeted check failed and
every other check that the defect does not implicate still passed. The plate
below draws what that call returned, so the claim above is visible rather than
merely asserted.

![One row per structural invariant, computed by running the whole check battery over the live registry and then over a registry carrying exactly the defect that invariant guards against. Each row shows the check's verdict on the real registry and the detail string it returned when it rejected the planted defect, so a check that stopped rejecting would empty its own row rather than pass quietly. The plate demonstrates detection of the planted defects; it is not a claim that the six checks exhaust the structural faults a registry could carry.](../output/figures/white_invariant_battery.png){#fig:white-invariant-battery width=100%}

## Where each claim is checked

A claim in prose is not a checked claim. Every definition and proposition above
names the test that exercises it, keyed by the block's own label, and
`tests/test_formalism.py` asserts that each row names a test that exists and
that no block is missing a row — so a renamed test breaks the build rather than
leaving a claim quietly unbound.

| Claim | Test |
| --- | --- |
| [@def:kinds] | `test_formalism.py::test_the_kind_alphabet_in_prose_is_the_enumeration` |
| [@def:states] | `test_formalism.py::test_the_state_alphabet_in_prose_is_the_enumeration` |
| [@def:record] | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:registry] | `test_manuscript_bindings.py::test_registry_definition_counts_re_derive_from_the_registry` |
| [@def:caution-order] | `test_formalism.py::test_the_caution_order_in_prose_is_caution_rank` |
| [@def:observation] | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:finding] | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:report] | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:assessment-map] | `test_formalism.py::test_the_assessment_map_matches_the_assessor_signature` |
| [@def:intake] | `test_formalism.py::test_the_intake_definition_partitions_the_live_code_alphabet` |
| [@def:date-resolution] | `test_formalism.py::test_every_date_resolution_branch_matches_the_shared_helper` |
| [@def:scoring] | `test_formalism.py::test_every_quoted_scoring_reason_is_produced_by_the_assessor` |
| [@def:directive] | `test_formalism.py::test_the_directive_map_in_prose_is_the_protocol_map` |
| [@prop:reserved-meta-state] | `test_assessor.py::test_observations_cannot_assert_not_recorded` |
| [@prop:caution-monotonicity] | `test_analysis.py::test_reconciliation_matrix_agrees_with_the_assessor_in_both_orders` |
| [@prop:caution-monotonicity] at higher arity | `test_assessor.py::test_three_or_more_observers_resolve_to_the_most_cautious` |
| [@prop:staleness] | `test_assessor.py::test_stale_naming_decays_to_unresolved_past_the_horizon` |
| [@prop:staleness] swept over review dates | `test_analysis.py::test_decay_timeline_migrates_named_records_at_each_horizon_crossing` |
| [@prop:no-silent-discard] | `test_analysis.py::test_events_tally_counts_real_intake_events_per_code` |
| [@prop:totality] | `test_assessor.py::test_report_covers_every_record_and_tally_counts_all_states` |
| [@prop:context-traceability] | `test_serialization.py::test_digest_is_order_independent_and_repeatable` |
| [@prop:bounded-follow-up] | `test_protocol.py::test_review_protocol_maps_states_to_bounded_follow_up` |
| [@prop:defect-detection] | `test_invariants.py::test_the_defect_battery_rejects_every_planted_defect` |
| [@def:event] | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:facets] alphabets | `test_formalism.py::test_the_facet_alphabets_in_prose_are_the_enumerations` |
| [@def:facets] as a tuple | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:projection] cell counts | `test_formalism.py::test_the_projection_cell_counts_re_derive_from_the_code` |
| [@def:projection] full table | `test_witness_layer.py::test_the_projection_truth_table_is_total_except_the_unrecordable_cell` |
| [@prop:factorization] | `test_formalism.py::test_the_factorization_proposition_holds_over_a_live_battery` |
| [@def:return] as a tuple | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:return] at the boundary | `test_witness_layer.py::test_the_due_date_is_the_last_current_day_proven_through_the_assessor` |
| [@def:envelope] as a tuple | `test_formalism.py::test_every_tuple_definition_lists_its_dataclass_fields` |
| [@def:envelope] points, never reinterprets | `test_witness_layer.py::test_the_envelope_points_at_the_native_report_without_reinterpreting_it` |
