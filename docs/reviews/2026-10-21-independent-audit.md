# Independent read-only audit receipt

The auditor reviewed the complete candidate diff before the response fixes.
The verdict was changes required for code and blocked for publication. The
confirmed findings were then reproduced and addressed as recorded in
[the response](2026-10-20-resolution.md#independent-audit-response).
This receipt records that audit; it is not a later approval of the fixes.
Machine-local citation paths have been converted to repository-relative links.

**Code verdict: changes required. Publication verdict: blocked independently by incomplete Stage 04 validation.** I found two runtime validation gaps and one documentation inconsistency.

1. **P2 — Return and expiry consumers accept findings rejected by the facet validator.**
   [binding.py:33](../../src/white_line/binding.py#L33) validates finding identity, kind, and state type, but omits assertion/date consistency. [return_contracts:147](../../src/white_line/returns.py#L147) and [expiry_horizon:206](../../src/white_line/analysis.py#L206) therefore accept a stale, fabricated `NAMED` finding. The expiry view returns negative remaining days; the return matcher accepts its generated contract.

   Executed counterexample:

   ```python
   from dataclasses import replace
   import white_line as w

   report = w.assess_absence((
       w.AbsenceObservation(
           "unobserved-dependency", w.AbsenceState.NAMED,
           "scope", "2026-07-01",
       ),
   ), as_of="2026-07-18")
   bad = replace(report, findings=(
       replace(report.findings[0], observed_on="2020-01-01"),
   ) + report.findings[1:])

   print(w.expiry_horizon(bad)[0].days_remaining)  # -2300
   contract = w.return_contracts(bad)[0]
   print(contract.due_on)                         # 2020-03-31
   print(w.return_matches_contract(
       contract, bad, contract.originating_report_ref, contract.record_id,
   ))                                           # True
   w.report_facets(bad)                          # ValueError
   ```

   Missing or contradictory `asserted_state` values are likewise accepted by returns and expiry. Separately, an all-`NOT_RECORDED` report with `review_date="not-a-date"` produces matching return contracts because date validation occurs only inside the `NAMED` branch.

   **Remedy:** apply shared finding well-formedness and review-date validation before deriving contracts or expiry entries. Preserve rejection rather than silently reassessing. Add these malformed-report controls across all three consumers.

2. **P2 — Direct facet derivation accepts invalid kinds when both supplied objects share them.**
   [_validate_finding:201](../../src/white_line/facets.py#L201) checks kind identity without checking `AbsenceKind` membership. The public direct API consequently accepts `None` or a bare string as both kinds, contradicting the malformed-kind rejection described in [witness_contracts.md:13](../../docs/witness_contracts.md#L13).

   Using the valid `report` above:

   ```python
   print(w.finding_facets(
       replace(report.findings[0], kind=None),
       replace(w.WHITE_RECORDS[0], kind=None),
       report.review_date,
   ))
   # Returns NAMED / OPEN / CURRENT instead of rejecting.
   ```

   Matching numeric IDs (`record_id=42`, `record.id=42`) also pass. This affects the direct API with malformed supplied objects; report-level registry validation rejects these cases.

   **Remedy:** validate the direct API’s record/finding kind and identifier fields explicitly, before temporal derivation. Plant matching-invalid-value controls, alongside the existing mismatched-kind control.

3. **P3 — Publication documentation calls the blocked candidate a release.**
   [docs/publication.md:30](../../docs/publication.md#L30) says “Version 0.8.0 is a repository release,” while [the candidate packet:3](../../docs/releases/v0.8.0.md#L3) explicitly says it is unreleased. The citation examples also present version 0.8.0 as a Zenodo publication using the retained earlier DOI.

   **Remedy:** label 0.8.0 consistently as a candidate and distinguish candidate repository citation from the last verified deposition. The later DOI caveat does not travel with copied citation examples.

The packet’s item dispositions are:

| Review item | Audit disposition |
| --- | --- |
| 1. Producing-registry binding | Implemented: changed content, duplicates, missing digest, finding identity, and reordering controls pass. Finding semantics remain incomplete as described above. |
| 2. Exact return identity | Implemented for valid reports: note/event changes alter references; wrong report, record, reference, and edited terms are tested. Subject to finding 1. |
| 3. Envelope boundaries | Implemented. Matching, contract validity, and trusted whole-envelope integrity remain distinct; custom-version and scalar-reference controls pass. |
| 4. Facet boundary | Partially complete: enum projection and assertion transitions are covered; direct malformed-kind/identity cases remain. |
| 5. Unsupported dates / producers | Accepted. Equality-raising objects remain undated; producer exceptions propagate without partial reports. |
| 6A. Slug matching | Implemented, including whole-assessment rejection and valid controls. |
| 6B. Defect-battery prose | Accepted adaptation: targeted detection plus reported collateral failures, without exclusivity. |
| 7. Calendar limits | Implemented; endpoint, huge-step, huge-horizon, and ordinary boundary controls pass. |
| 8. Archive retention | Accepted adaptation: displaced-note loss is demonstrated; authorized opaque references distinguish archives without retaining contents. |
| Documentation, schemas, figures, audit | Coordinated changes are present, including typed assertions, schema markers, formal tuples, claim bindings, figure wording, and audit control. Findings above prevent an unconditional “resolved” disposition. |
| Interpreter matrix | Python 3.10/3.14 workflow is configured. Hosted execution and a current candidate run on actual 3.10 remain unverified. |

My fresh read-only checks produced **174 passing focused tests**, clean Ruff, clean mypy over 33 files, and a passing native audit with `--require-render`. I inspected the supplied full-suite evidence: Python 3.14 reports **469 passed, no skips, 99.65% aggregate coverage**; Python 3.11 reports **468 passed, one skipped**. Those full-suite results are retained evidence, not fresh full-suite executions by this auditor.

The PDF, HTML, and source-manifest hashes match the candidate packet. I inspected the existing captures of changed witness/formalism pages; the tuples fit. All **9,501 archive files** in the template export match the archive identifying `4670c48cc490636455f2eac09ba4396baed9ffd7`.

The Stage 04 boundary is correctly retained: its log is incomplete, and the process samples support both Python and Git blocking while writing. The file-backed control diagnoses transport behavior; it does not complete publication validation. **No release, tag, or push should proceed on the native audit alone.** I did not patch the engine, waive the failure, or rerun the hanging pipeline.

No files were modified. The before/after digest snapshot of **205 candidate source and output files** was unchanged.
