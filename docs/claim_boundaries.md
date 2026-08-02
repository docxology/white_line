# Claim boundaries and evidence

White Line is easiest to misread when a claim about the package is allowed to
sound like a claim about the world. This page is the compact claim register for
the current release. It separates what the repository can demonstrate from
what requires observation, domain expertise, consent, or a different research
design.

| Claim class | What this release supports | Evidence | What it does not support |
| --- | --- | --- | --- |
| Implementation behavior | The assessor accepts typed observations, records intake events, reconciles duplicates, applies the defined caution order, ages dated `NAMED` observations, and emits one finding per current registry record. | Source code, formal definitions, tests, and rendered state diagrams. | That the input is true, complete, representative, or ethically adequate. |
| Structural consistency | The current registry satisfies six defined invariants; its canonical digest, generated registry artifact, figure metadata, manuscript links, and rendered bundle agree at the release gate. | `pytest`, `check_registry.py`, `audit_project.py`, the template validator, and the source manifest. | That the invariants are sufficient for every possible defect or that a passing gate certifies a research conclusion. |
| Scholarly translation | Work on situated knowledge, produced and strategic ignorance, missing-data mechanisms, classification, epistemic injustice, resistance, refusal, contextual integrity, opacity, and contemplative restraint motivates design constraints and non-claims. | The cited bibliography and the bounded synthesis in `manuscript/01c_scholarship.md`. | That these traditions form one theory, or that citation alone validates the software or a social judgment. |
| Empirical or causal claim | None is asserted by the current package. The registry and examples are designed inputs for a review protocol. | Explicit scope statements, no-claim captions, and the absence of a world-observation dataset. | A hidden cause, motive, population rate, completeness score, safety status, consent, justice, or disclosure entitlement. |

The operational rule is therefore: type the limit, bound the inference, and
revisit with context. `NAMED`, `UNRESOLVED`, `WITHHELD`, and `NOT_RECORDED`
describe the ledger's state of a record under a supplied review contract; they
are not truth labels for a person, population, institution, or unseen
mechanism. In particular, `WITHHELD` is not evidence of deception, and
`NOT_RECORDED` is not evidence that nobody knew or that nothing happened.

The scholarship is deliberately used as constraint rather than ornament. Work
on situated knowledge asks where an account is located; epistemologies of
ignorance ask how gaps can be produced and sustained; missing-data methodology
makes inference depend on assumptions about the process generating missingness;
classification studies show that categories organize visibility; and work on
epistemic injustice, resistance, refusal, contextual integrity, and opacity
places limits on whose information may be demanded. White Line converts those
cautions into review prompts and refusal rules, not into automated diagnoses.
See the full mapping in [scholarship_map.md](scholarship_map.md) and the cited
sources in [references.bib](../manuscript/references.bib).

For release review, use the following evidence order:

1. Read the claim in the manuscript or documentation.
2. Identify whether it is implementation, structural, scholarly, or empirical.
3. Check the corresponding source, citation, test, artifact, or explicit
   absence of evidence.
4. Reject any interpretation that crosses the boundary without a new dataset,
   method, responsible human review, and an updated claim.
