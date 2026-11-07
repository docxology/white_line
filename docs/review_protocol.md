# Review protocol

White Line has two distinct layers:

1. `assess_absence` computes a typed report from supplied observations.
2. `review_directives` states the smallest responsible human follow-up for
   each finding.

The second layer exists because a state is not an action and an action is not
an authorization. The package deliberately has no `COMPLIANT`, `SAFE`, or
`APPROVED` state.

| State | Directive | Follow-up |
| --- | --- | --- |
| `NOT_RECORDED` | `RECORD_OR_EXPLICITLY_SCOPE` | Record an observation or state that the category was not reviewed. |
| `NAMED` | `RETAIN_NAMED_SCOPE` | Keep the absence explicit; do not treat naming as resolution or evidence of cause. |
| `UNRESOLVED` | `REOPEN_OR_BOUND` | Revisit, bound, or explain why the question remains open. |
| `WITHHELD` | `HONOR_AND_CONFIRM_BOUNDARY` | Honor the boundary and confirm its duty, consent, or safety basis without seeking disclosure. |

## Operator loop

1. Define the review date and the registry version being used.
2. Supply observations that the reviewer is authorized to record. Do not put
   confidential material into a note merely to make a record look complete.
3. Run `assess_absence` and retain `review_date`, `registry_digest`, findings,
   and `intake_events` together.
4. Inspect every intake event. A set-aside input is an explicit limitation of
   the review, not an invisible rejection. ``UNDATED_OBJECT`` is different:
   the observation is retained, but its non-ISO date object is not coerced and
   cannot participate in staleness accounting. Correct the source to an ISO
   date string if aging is required; the event makes the existing fail-open
   behavior visible rather than changing what the ledger accepts.
5. Run `review_directives(report)`. Complete only the bounded follow-up that is
   appropriate to the context; preserve a withholding when disclosure would
   violate a duty.
6. Retain exact prior return-contract keys and record human/domain acceptance
   separately, as in the recipe below. Matching a key does not fulfill it.
7. Re-run after material context changes or after a dated naming passes its
   review horizon. A new assessment uses its complete supplied cohort; it does
   not patch or inherit an earlier report.

```python
from white_line import AbsenceObservation, AbsenceState, assess_absence, review_directives

report = assess_absence(
    [
        AbsenceObservation(
            "unmeasured-uncertainty",
            AbsenceState.NAMED,
            "Uncertainty is reported in the methods appendix.",
            observed_on="2026-07-18",
        )
    ],
    as_of="2026-07-18",
)

for directive in review_directives(report):
    if directive.requires_follow_up:
        print(directive.record_id, directive.action.value)
```

```text
unobserved-dependency RECORD_OR_EXPLICITLY_SCOPE
missing-null-results RECORD_OR_EXPLICITLY_SCOPE
unasked-question RECORD_OR_EXPLICITLY_SCOPE
withheld-material RECORD_OR_EXPLICITLY_SCOPE
silenced-perspective RECORD_OR_EXPLICITLY_SCOPE
uncredited-labor RECORD_OR_EXPLICITLY_SCOPE
unacknowledged-limit RECORD_OR_EXPLICITLY_SCOPE
negative-space RECORD_OR_EXPLICITLY_SCOPE
fallow-ground RECORD_OR_EXPLICITLY_SCOPE
ineffable-remainder RECORD_OR_EXPLICITLY_SCOPE
```

## Exact returns and a partial remainder

The caller owns acceptance and the outstanding-key register; White Line does
not evaluate fulfillment, infer standing, or merge reports. Retain the immutable
prior report and its producing registry. Key every obligation by
`(originating_report_ref, record_id)`, including unobserved categories. Do not
remove an obligation just because a matching return arrived.

In this example, a responsible reviewer has separately accepted the explanation
that a question remains open. A boundary confirmation has arrived too, but has
not yet been accepted by the responsible human. Neither step requests or stores
the protected material. The literal acceptance sets below represent explicit
human decisions in this example, not decisions made by the matcher.

```python
import white_line as w

prior = w.assess_absence((
    w.AbsenceObservation("unasked-question", w.AbsenceState.UNRESOLVED, "Still open."),
    w.AbsenceObservation("withheld-material", w.AbsenceState.WITHHELD, "Duty boundary."),
), as_of="2026-07-18")
contracts = {
    (c.originating_report_ref, c.record_id): c
    for c in w.return_contracts(prior)
}
reference = w.report_digest(prior)
question_key = (reference, "unasked-question")
boundary_key = (reference, "withheld-material")
question_return = w.AbsenceObservation(
    "unasked-question", w.AbsenceState.UNRESOLVED,
    "The question remains open within the stated scope.", "2026-07-19",
)
boundary_confirmation = "The duty boundary still holds."
assert w.return_matches_contract(contracts[question_key], prior, *question_key)
assert w.return_matches_contract(contracts[boundary_key], prior, *boundary_key)

# Human decision: accept the bounded explanation, not yet the confirmation.
human_accepted_keys = {question_key}
outstanding = {key: c for key, c in contracts.items() if key not in human_accepted_keys}
assert set(outstanding) == set(contracts) - human_accepted_keys
assert boundary_key in outstanding
print(len(outstanding), boundary_key in outstanding)

# Later, someone with standing separately accepts only the boundary confirmation.
# Its text is not parsed to infer standing, consent, truth, or acceptance.
human_accepted_keys.add(boundary_key)
outstanding = {key: c for key, c in contracts.items() if key not in human_accepted_keys}
assert set(outstanding) == set(contracts) - human_accepted_keys
print(len(outstanding), boundary_key in outstanding)

# This is a fresh partial cohort, NOT an update or a discharge of prior keys.
fresh = w.assess_absence((question_return,), as_of="2026-07-19")
assert fresh.finding_for("unasked-question").state is w.AbsenceState.UNRESOLVED
assert fresh.finding_for("withheld-material").state is w.AbsenceState.NOT_RECORDED
assert prior.finding_for("withheld-material").state is w.AbsenceState.WITHHELD
print(fresh.finding_for("withheld-material").state.value)
```

```text
10 True
9 False
NOT_RECORDED
```

All nine other prior keys remain outstanding, regardless of the fresh report.
To reassess a continuing review, supply the complete authorized cohort, including
any boundary confirmations appropriate to that review; do not recover protected
contents to fill a gap. An accepted unresolved return may leave a question open,
and an accepted boundary confirmation may leave the record `WITHHELD`.
See [witness_contracts.md](witness_contracts.md) for the exact binding boundary.

## Distributional analysis recipes

The helpers in `white_line.analysis` are pure, additive summaries. They are
computed through the public assessment contract or the defined caution order;
they do not change a report's state assignment.

### Decay sweep and transition offsets

This illustrative cohort gives every live record the same dated naming. The
sweep re-runs the public assessor, so offsets 91, 121, 181, and 366 are one
day beyond the live 90-, 120-, 180-, and 365-day horizons. It is deliberately
not the shared intake fixture: that fixture demonstrates conflict and intake,
whereas this one makes every horizon visible.

```python
from white_line import AbsenceObservation, AbsenceState
from white_line.analysis import decay_timeline, decay_transition_offsets
from white_line.registry import WHITE_RECORDS

cohort = tuple(
    AbsenceObservation(record.id, AbsenceState.NAMED, "dated naming", "2026-01-01")
    for record in WHITE_RECORDS
)
points = decay_timeline(cohort, "2026-01-01", "2027-01-02")
print([
    (point.offset_days, point.tally[AbsenceState.NAMED], point.tally[AbsenceState.UNRESOLVED])
    for point in points
    if point.offset_days in (0, 90, 91, 120, 121, 180, 181, 365, 366)
])
print(decay_transition_offsets(points))
```

```text
[(0, 11, 0), (90, 11, 0), (91, 8, 3), (120, 8, 3), (121, 6, 5), (180, 6, 5), (181, 3, 8), (365, 3, 8), (366, 0, 11)]
(91, 121, 181, 366)
```

The sweep describes the supplied cohort under the staleness contract. It does
not describe a population, establish completeness or diligence, or say why
any absence exists.

### Ordered-pair reconciliation

The matrix is ordered by held and incoming states. One cell shows that an
incoming `WITHHELD` observation is kept when the held observation is `NAMED`.

```python
from white_line import AbsenceState
from white_line.analysis import reconciliation_matrix

matrix = reconciliation_matrix()
print(matrix[(AbsenceState.NAMED, AbsenceState.WITHHELD)].value)
```

```text
WITHHELD
```

This is the defined caution-order result for two supplied state assertions. It
does not rank people, seriousness, safety, or the truth of either observation.

### Intake-event tally

The shared worked fixture supplies seven inputs and one pinned review date.
This view keeps every intake code available, while the printout selects only
codes that occurred in this report.

```python
from white_line.analysis import events_tally
from white_line.worked_examples import worked_report

print({code.value: count for code, count in events_tally(worked_report()).items() if count})
```

```text
{'NON_OBSERVATION': 1, 'UNKNOWN_RECORD': 1, 'RESERVED_STATE': 1, 'CONFLICTING_STATES': 1, 'DUPLICATE_STATE': 1}
```

An event tally describes how supplied inputs were handled. It is not a
completeness, diligence, negligence, safety, or permission score for a person
or project.

### Kind-by-state coverage matrix

The same worked report can be read by kind and current state. Zero cells are
present in the returned matrix; the printout omits them only to make this
example legible.

```python
from white_line.analysis import coverage_matrix
from white_line.worked_examples import worked_report

print({
    kind.value: {state.value: count for state, count in row.items() if count}
    for kind, row in coverage_matrix(worked_report()).items()
})
```

```text
{'EPISTEMIC': {'UNRESOLVED': 1, 'NOT_RECORDED': 3}, 'ETHICAL': {'WITHHELD': 1, 'NOT_RECORDED': 3}, 'CONTEMPLATIVE': {'NOT_RECORDED': 3}}
```

The matrix locates ledger states in the supplied registry kinds. It does not
measure coverage, completeness, diligence, safety, or negligence.

### Expiry horizon

`expiry_horizon` is a refresh schedule for current dated namings. This
purpose-built report contains one fresh naming, one undated naming, and one
naming already past its horizon. Only the fresh naming appears: an undated
naming has no age to schedule, while the old one is already reported
`UNRESOLVED`.

```python
from white_line import AbsenceObservation, AbsenceState, assess_absence
from white_line.analysis import expiry_horizon

report = assess_absence((
    AbsenceObservation("unmeasured-uncertainty", AbsenceState.NAMED, "freshly reviewed", "2026-07-18"),
    AbsenceObservation("negative-space", AbsenceState.NAMED, "left undated"),
    AbsenceObservation("unobserved-dependency", AbsenceState.NAMED, "past its horizon", "2026-04-18"),
), as_of="2026-07-18")
print([(entry.record_id, entry.observed_on, entry.days_remaining) for entry in expiry_horizon(report)])
print([(finding.record_id, finding.state.value) for finding in report.findings if finding.record_id in {"negative-space", "unobserved-dependency"}])
```

```text
[('unmeasured-uncertainty', '2026-07-18', 120)]
[('unobserved-dependency', 'UNRESOLVED'), ('negative-space', 'NAMED')]
```

The schedule describes when supplied dated namings should be revisited under
the registry contract. It does not establish that an undated naming is less
important, that an aged naming is false, or that any record is complete or
safe.

This loop does not establish independent truth, infer intent, replace consent
or security review, or decide whether a project may proceed. It makes the next
human question visible while preserving the boundary around what the tool
cannot know.
