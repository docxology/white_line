# Worked ledger entries {#sec:examples}

An absence can be recorded directly:

```python
from white_line import AbsenceObservation, AbsenceState, assess_absence

report = assess_absence([
    AbsenceObservation(
        "withheld-material",
        AbsenceState.WITHHELD,
        "The identifying details remain outside the publication.",
    ),
])
```

The result distinguishes `WITHHELD` from `NOT_RECORDED`. A record for an
unobserved dependency can remain `UNRESOLVED` while investigation continues, and
a named contemplative space can remain `NAMED` without implying that an unseen
agent, field, or force exists.

The staging shows itself under adversarial or careless input. Suppose two
reviewers disagree about the same record — one calls it `NAMED`, another
`UNRESOLVED`. The ledger keeps `UNRESOLVED`, the more cautious of the two, and
writes a note explaining that it did so; it never quietly upgrades an open
question into a settled naming. Suppose an input asserts `NOT_RECORDED`
directly: intake sets it aside, because that state is reserved for records no one
observed, and again leaves a note rather than absorbing the claim.

Staleness is dated, not assumed. A `NAMED` observation carrying an
`observed_on` date is compared against the review date:

```python
report = assess_absence(
    [AbsenceObservation("unobserved-dependency", AbsenceState.NAMED,
                        "Checked the upstream feed.", observed_on="2025-01-01")],
    as_of="2026-07-18",
)
```

Because the naming is far older than the record's ninety-day horizon, it is
reported `UNRESOLVED` with a reason that states its age and horizon. Nothing
about the record has been discovered to be wrong; the ledger has simply stopped
treating an eighteen-month-old check as though it were made this morning.

The note is contextual evidence for the ledger, not a license to expose what was
withheld. In a real project, access controls and consent obligations live
outside this small pure-data instrument.

The state-to-action boundary is explicit rather than implied:

```python
from white_line import review_directives

for directive in review_directives(report):
    if directive.requires_follow_up:
        print(directive.record_id, directive.action.value)
```

This emits bounded follow-up such as `REOPEN_OR_BOUND` or
`HONOR_AND_CONFIRM_BOUNDARY`; it never emits permission or a safety verdict.
The report also carries `review_date`, `registry_digest`, and typed
`intake_events`, which should travel with the human review record.
