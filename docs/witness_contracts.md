# Bound witness records

The report is the authority for its retained assessment. `report_facets`,
`return_contracts`, and `expiry_horizon` materialize the supplied registry once,
check its structural invariants and canonical digest, and require exactly one
typed finding per record with the matching kind. Review dates and the shared
finding assertion/date consistency check apply to all consumers, including
all-unobserved reports. Direct facet derivation also rejects matching invalid
kind or identifier values and nonpositive or untyped horizons. Registry order may differ;
registry content may not. Reports without a digest are explicitly rejected.
Reassess from authorized inputs to create a bound report; a consumer never
silently substitutes a new registry or reconstructs missing provenance.

The native serialization is `white-line.report/1.1`. Each finding now carries
`asserted_state`: the retained assertion, or `None` for `NOT_RECORDED`.
`finding_facets` checks the state, kind, date, and typed assertion against the
record and review date. A stale `NAMED`, dated `NOT_RECORDED`, or inconsistent
decay is rejected. Display reasons are not interpreted. Hand-built findings
from the older schema lacking an assertion are rejected when an observation
would be required; there is no inference from an English reason string.
Reasons remain display data, so editing them cannot change typed provenance.
`project_facets` requires actual enum members and rejects strings and objects.
The projection rule over valid enum members is unchanged.

Return contracts use `white-line.return-contract/1.1` and carry
`originating_report_ref = report_digest(report)`. To record a return, retain
that reference and `record_id` beside the returned material, then call
`return_matches_contract(contract, prior_report, reference, record_id,
records=original_registry)`. This checks identity and the deterministic
contract terms, not fulfillment, standing, truth, or approval. No standalone
contract identifier is needed: the exact report reference and record ID name
the contract. An honest return may remain unresolved; a withholding asks only
for boundary confirmation. A due date outside Python's representable calendar
raises `ValueError`; it is never wrapped or converted to an empty due date.

## Three envelope checks

The common tuple remains `line.report-envelope/1.0`; its shape is unchanged.
The stronger local checks do not claim that sibling instruments implement them.

| Check | What it checks | What it cannot establish |
| --- | --- | --- |
| `envelope_matches_report` | Exact native report digest, review date, registry digest, ordered native statuses | Schema, line identity, non-claims, subject/source edits, truth |
| `validate_envelope_contract` | Supported schema and line, ISO date, digest syntax, version/digest policy, unique slug/state pairs, required non-claims, subject/reference shapes | Correspondence with a report, source custody, authorship, authority |
| `envelope_digest` compared with a separately trusted digest | Changes to any serialized envelope field | Who changed it or whether either version is true |

Only the pinned built-in registry digest receives `LEDGER_VERSION`. Every
other digest receives `custom/unknown`; caller-provided version labels are
not vouched for. The contract validator checks shape, not completeness of a
custom registry; matching and registry binding provide the other checks.
Subject and snapshot references are stored as unverified caller provenance.
A snapshot collection must be an iterable of nonblank strings, never a scalar
string or bytes. Keep the envelope digest in a separately trusted archival
manifest (or sign that manifest); storing a newly computed digest beside an
editable envelope does not authenticate it.

## Retention and producer boundary

`canonical_report` preserves the complete `WhiteReport` object, not the input
history. For example, supply `NAMED` with note A followed by `WITHHELD` with
note B. Replacing only displaced note A gives the same canonical report:
the displaced state survives, but its note, date, and source identity do not.
Original non-string date objects also do not survive serialization.
`test_archive_intentionally_loses_displaced_notes_but_refs_can_distinguish`
executes this pair. A minimal archive may retain neither displaced note.
Where authorized replay is required, callers may retain opaque
`source_snapshot_refs` under their own retention, access, and deletion policy.
Distinct authorized references distinguish the two archives without copying
protected contents into reports. A reference is not proof that a source is true.

Observations must come from a finite, well-behaved iterable. An exception
raised while consuming a producer propagates; no partial report is returned.
Intake rejection, reconciliation replacement, and accepted undated input are
separate dispositions. Unsupported date objects are accepted undated without
coercion or equality calls and cannot age. This boundary does not sandbox
arbitrary Python producers or methods on subclasses.
