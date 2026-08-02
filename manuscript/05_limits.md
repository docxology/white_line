# Limits and safeguards {#sec:limits}

White Line is unusually easy to misuse, because people project meaning into
gaps. A blank space invites a story, and the most dangerous story reads absence
as confirmation. The scope is narrow on purpose:

- `NOT_RECORDED` means only that no observation was supplied to this function.
  It does not mean absent, false, secret, or irrelevant.
- `UNRESOLVED` is not proof that a hidden cause exists. It is how the ledger
  holds a question open, including after a naming has gone stale.
- `WITHHELD` must never be reverse-engineered into disclosure. The accompanying
  note is context for review, not a key to the material.
- `NAMED` does not make an absence harmless, complete, or spiritually
  significant.
- A record may describe an unrepresented perspective without speaking for it.
  Naming a gap is not filling it.

The registry's finiteness sits behind all of these. Eleven records name eleven
categories a reviewer is prompted about; absences outside that list are not
tracked, not flagged, and not counted as missing. Taleb's point about
consequential events falling outside an anticipated possibility space applies
directly to a fixed category list [@taleb2007], and it cuts against this
instrument rather than for it. A full ledger with every record reviewed and
every horizon current is evidence about eleven questions, not about the ones no
one thought to add. Extending the registry is the only remedy, and an extension
is a human judgment the package cannot make.

The machinery has its own boundaries. The caution order resolves disagreement;
it is not a severity score, and a higher rung means more restraint was reported
rather than that more danger is present. The registry digest lets a later
checkout be compared against a stored manifest; it carries no security or safety
semantics and proves nothing about authorship or intent. The staleness horizon
is a review cadence, not a truth about when knowledge expires. The six
structural invariants check the registry's shape, and the shipped defect battery
shows each one refusing the defect it was written for — which establishes
detection of that defect and nothing about faults no check was written for.

None of this replaces security review, consent processes, source criticism,
accessibility work, or consultation with affected people. Red Line sets explicit
prohibitions and White Line cannot weaken them. Golden Line's aspirations cannot
fill an absence, and Black Line's evidence discipline cannot turn non-disclosure
into data. White Line's only promise is to keep the negative space legible so
the other lines cannot silently paint over it.

The distributional views in `white_line.analysis` inherit every boundary above
and add one. A cross-tabulation or an event tally rearranges a report; it is not
new evidence, and the rearrangement invites a specific misreading — a filled
`NAMED` row as diligence, a filled `NOT_RECORDED` column as negligence, a zero
event count as trustworthy input. None of those readings is supported. The decay
sweep is the same contract applied at many review dates, so a fully decayed
cohort means the namings are due for re-review, not that anything was discovered
to be wrong. Anyone ranking teams, projects, or people by these counts has left
the instrument's scope entirely.

The refresh queue is the sharpest case, because it looks forward. It orders by
days remaining under a declared horizon, which is a statement about cadence and
not about importance, risk, or how fast the underlying situation moves. It is
also not a picture of everything due: a naming the evaluator could not date
cannot expire and never enters the queue, and a naming already past its horizon
has left by decaying. Both omissions are drawn as labelled bands rather than
dropped, because in a work about absence a silently missing row is the worst
failure available, and the undated naming is exactly the one a reader assumes is
current. The two positive-control batteries carry the mirror-image limit: each
is constructed so that every code, and every check, fires. They establish
reachability and detection, and say nothing about how often a real review would
reach one.

Reproducibility has the same shape. A matching registry digest and a fresh
rendered bundle show that the local artifacts agree with one another; they do
not turn local notes into independent evidence. The source-to-artifact audit is
a release-consistency gate, not a research-validity certificate.
