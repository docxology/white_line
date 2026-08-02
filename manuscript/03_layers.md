# The three White Line layers {#sec:layers}

The initial registry keeps three layers distinct:

1. **Epistemic:** the ledger records a gap rather than inventing its value or
   cause. Its records — an unobserved dependency, an unmeasured uncertainty, a
   missing null result, an unasked question — all name something a reviewer could
   in principle go and check.
2. **Ethical:** withheld material, an unrepresented perspective, uncredited
   labor, and an unacknowledged limitation concern obligations to people, not
   merely missing data. Some of these absences are duties to keep rather than
   gaps to close.
3. **Contemplative:** negative space, fallow ground, and an ineffable remainder
   protect the possibility that a useful account can remain incomplete without
   being secretly completed by the author. Their long review horizons reflect
   that they are meant to be revisited slowly, not resolved on a sprint.

![White Line separates three kinds of absence: epistemic absence, ethical restraint, and contemplative space. Each panel is generated from the `AbsenceKind` vocabulary and the shared kind glosses, with its record count and review-horizon range read from the live versioned registry, and each panel keeps a guard against overclaiming. The lower dotted field represents an open boundary rather than a hidden mechanism. The figure is a deterministic schematic of the typology; it is not evidence of a causal force, a completeness score, or a diagnosis of the people involved.](../output/figures/white_absence_layers.png){#fig:white-absence-layers width=100%}

The current registry is small, finite, and reviewable in full. Each record names
one bounded category of absence, states the reviewer's question, and declares
how long a dated naming stays fresh before it must be looked at again. The
review horizons are graded by kind: epistemic gaps and ethical restraints both
come due within 90–180 days of a dated naming, while contemplative spaces are
given a full year because they are meant to ripen rather than be closed.

![The current versioned absence registry, grouped by kind, with every record's review horizon in days. The figure is generated directly from the registry data structure; the audit gate binds the figure registry, its digest, and the raster bytes of each shipped image, so a stale or hand-edited plate fails the gate rather than passing quietly. A record's presence names a category worth reviewing; it is never a claim that the category is populated in any particular work.](../output/figures/white_registry_taxonomy.png){#fig:white-registry-taxonomy width=100%}

Stating the grading as a per-kind range understates how differently the three
behave. Placed on a shared days axis, the epistemic and ethical records spread
across three horizon values each, while all three contemplative records sit on
one. That uniformity is a commitment rather than an accident: there is no useful
sense in which one ineffable remainder ripens faster than another, so the ledger
asks about all of them on the same annual cadence.

![Every registry record placed on a shared days axis by its `review_horizon_days`, grouped into one band per `AbsenceKind` and keyed by colour and by marker shape, with each kind's median horizon marked. Read from `WHITE_RECORDS`. The dispersion shows a structural asymmetry the per-kind range compresses away: the contemplative horizons are uniform at one value while the epistemic and ethical horizons spread across several. A horizon is the cadence on which the ledger asks about a record again; it is not a claim about how fast the world changes, and a longer horizon is not a lower priority.](../output/figures/white_horizon_dispersion.png){#fig:white-horizon-dispersion width=100%}
