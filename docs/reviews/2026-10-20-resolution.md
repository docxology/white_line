# Review disposition (2026-10-21)

Review target: `88072dcfbe585d8c402cbfea1acf532dfd48525d`.
Verbatim email body SHA-256:
`6bfde62b9ccdeb435836ee4520c4fd814bab51cdb129fa75ed76f3194290d44d`.
The original review was static. The tests below were executed before fixes;
they are measured reproductions, not historical coverage claims.

| Priority / item | Disposition | Regression and decision |
| --- | --- | --- |
| 1 registry binding | Done | `test_review_binding.py`: changed horizon/kind/description/prompt, duplicates, no digest, finding identity; same-registry reversal is accepted. Shared validator materializes once, checks structural invariants and digest; no reassessment. Initial run: 27 failed, 6 passed. |
| 2 exact return identity | Done | `test_exact_return_reference_distinguishes_notes_and_events`, `test_recorded_return_checks_the_contract_and_report_pair`; exact content reference plus record ID identifies a contract. Existing withholding/open-question controls remain. Return schema advances independently from registry content. |
| 3 envelope boundaries | Done | `test_review_identity.py` mutates every field independently. Matcher remains narrow; local contract validator checks required non-claims, schema, identity, states, and version policy. Whole-envelope digest is meaningful only against a separately trusted manifest. Custom registries use `custom/unknown`; scalar snapshot collections fail. Initial identity run: 16 failed. Common envelope tuple and schema string stay unchanged for transport compatibility. |
| 4 facet boundary | Done | `test_review_robustness.py` rejects strings/None/objects, stale NAMED, dated NOT_RECORDED, bad state/kind, and inconsistent typed assertion/date transitions. Typed `asserted_state` replaces reason parsing; display edits do not change facets. Existing enum truth table and branch projection tests remain. Older observed findings without typed provenance fail explicitly. |
| 5 date object / iterator | Done; iterable remedy adapted | Equality-raising object reproduces and now stays accepted-undated; date/datetime controls do not age. Producer failure already propagated: the test passed before changes. Finite well-behaved producers are required and exceptions propagate without any partial report. No bounded ingestion service is added. |
| 6A slug grammar | Done | Whole-string match; newline whole assessment fails. Carriage return, whitespace, Unicode lookalikes, hyphens, and valid multi-segment IDs have controls. |
| 6B defect-battery prose | Adapted | Narrowed the exclusivity sentence to targeted detection plus reported `also_failed`, matching the existing code. No allowed-collateral-failure policy is claimed. A compound-defect test demonstrates collateral failures are reported and permitted. |
| 7 date range | Done | Singleton date.max, near-endpoint, huge step, custom huge horizon, and existing H/H+1 evaluator controls. Sweep checks remaining days before stepping; unrepresentable contract due dates raise explicit ValueError. |
| 8 retained archive | Adapted | Loss of displaced note/date is intentional minimization. Executed paired histories have equal report bytes; authorized opaque snapshot references distinguish envelopes. Existing references suffice; no protected data collection or replay authority is added. |
| interpreter matrix / release | Done in configuration; measured release results in release packet | Standing floor/current Python jobs run coverage, lint, types, registry, figures, source audit and upload logs. Rendering remains a separate declared external dependency. Actual local/hosted runs and engine/tool versions are reported in the release packet. |

The initial robustness run had 19 failures and 9 passing controls. Full failing
and fixed logs accompany the release evidence. The first broad suite ran while
new regression files were being written, so it is not treated as pristine
baseline evidence. Its lexical-guard failure was caused by the newly introduced
compatibility wording; the wording was corrected without weakening the gate.

No state alphabet, caution rank, registry content, withheld-material demand,
empirical claim, or scientific citation changed. `LEDGER_VERSION` therefore
stays pinned to its existing content digest. The requested
`docs/manuscript/config.yaml` does not exist in this standalone layout;
`manuscript/config.yaml` remains the version authority per `AGENTS.md`.

Cross-repo finding: consumers in `witness_register` and `line_set` should
recognize custom/unknown registry versions and keep matching, contract validity,
and trusted archival integrity separate. No sibling was edited or tested here.
All local contract details are in [witness_contracts.md](../witness_contracts.md).

## Independent audit response

The independent read-only audit required changes: return/expiry consumers did
not enforce the facet consistency check, direct facets admitted matching
invalid kind/identifier values, and publication examples conflated the
candidate with the retained DOI. New controls first produced 13 failures and
31 passing controls. Finding well-formedness and review-date validation now
live in the shared binding boundary; all consumers reject malformed reports.
Direct facets validate typed kinds, canonical string IDs, and positive integer
horizons before deriving temporality. Candidate citations now use repository
references with an unreleased label; the verified deposition is cited separately.
The focused post-fix run passed all 172 tests, with clean lint and type checks.
This response does not clear the independently blocked external publication gate.

## Publication gate resolution

On resumption the unchanged engine's native pipe call still hung across the
available macOS interpreters. The exact reproduction succeeded in Linux on
the same input and returned the same output byte count. The complete Stage 04
validator then passed in a compatible Linux environment after supplying its
documented source epoch and Git provenance through an independent detached
engine checkout. The canonical engine was not changed. A truncated-PDF control
on a disposable project clone exited 1; the canonical artifact hash was
unchanged. The declared Python 3.10 floor also passed all 491 tests without
skips. Final release commands, custody, and remaining DOI work are recorded
in the release packet and validation recipe.
