# Cycle 055 — LANE A VERDICTS (targeted review, source only)

**Committed BEFORE Lane B is written.** This commit is the blind.
One question per function: *what does this mean on an empty domain, and is that semantically
different from its ordinary negative result?*

## Verdicts

**1. `ergon/meta/trajectory.py::stall_fraction` — FLAG.**
`len(positions) < 2 -> 0.0`. With fewer than two positions there are **no steps**, so the
fraction is 0/0. Returning 0.0 asserts *"never stalled"*. A trajectory that terminated
immediately — arguably the most stalled outcome — reads as perfectly healthy, and `featurize`
feeds this straight into a feature vector where the two are indistinguishable.

**2. `ergon/learner/descriptor.py::compute_fill_rates` — FLAG (weak).**
Empty coordinates -> no flagged axes. The function's purpose is flagging over-concentration, so
an **empty archive** — maximally degenerate — reports as *"well spread, nothing flagged"*.
Disambiguator exists: `axis_concentrations == {}`.

**3. `ergon/learner/triviality.py::compute_trigger_rate` — FLAG (weak).**
Empty matches -> `trigger_rate 0.0`. The docstring's own acceptance criterion reads *"5-30% of
all kills (lower bound: detector is doing meaningful work)"*, so 0.0 **fails the criterion** —
but 0.0 from no data means *no data*, not a broken detector. Disambiguator `n_total: 0` is
returned alongside.

**4. `ergon/learner/diagnostics/per_class_hit_rates.py::per_seed_rates` — FLAG.**
`n_att == 0` -> all three rates 0.0. **A class the scheduler never attempted is
indistinguishable from a class attempted many times that never promoted.** Disambiguator
`n_attempts` is in the record.

**5. `ergon/meta/fitness.py::compute_disagreement` — FLAG (strongest, three conflations).**
- `traj_divergence = 0.0` when n < 2 -> *"perfect agreement"* from one or zero trajectories.
- `basin_entropy = 0.0` when no valid basins -> *"all landed in the same basin"*, i.e. maximum
  certainty, when **none reported a basin at all**.
- `speed_variance = 0.0` when < 2 reached epsilon -> *"equally fast"* when none finished.
- Plus `vals.std()` on an empty array -> **unguarded NaN**.

**A landscape where every optimizer FAILED looks identical to one where they all agreed** — and
this feeds fitness.

**6. `ergon/learner/operators/anti_prior.py::compute_genome_atom_frequencies` — CLEAN.**
Empty nodes -> `{}`. Honest: no atoms, no frequencies. An empty dict cannot be mistaken for a
uniform distribution or for zero-frequency atoms. **Refusal-by-emptiness, done correctly.**

**7. `ergon/learner/inference/ablation_e007_ab.py::_hit_rate` — FLAG.**
No expected keywords -> 0.0, the **worst possible score**. With no rubric, every answer
trivially satisfies the (empty) requirement — 0/0. It penalises an answer for a question that
had no expected keywords.

**8. `charon/diagnostics/compute_per_domain_pi0.py::bootstrap_ci_from_seed_means` — FLAG.**
Empty input propagates to `.mean()` on an empty array -> unguarded NaN throughout. **The worse
case is n = 1**: resampling one seed with replacement returns that seed every time, so the
percentile CI **collapses to near-zero width** — a spuriously *tight* confidence interval
derived from a single observation. Not an empty-domain crash but a confident-looking wrong
answer, which is worse.

**CONTROL. `charon/.../_mahler_composition_helpers.py::survival_fraction` — CLEAN (with a caveat
that weakens my own control).**
Empty values -> 0.0, and `test_survival_fraction_empty` pins it. Scored CLEAN per the
pre-registered definition (*degenerate case known-handled*).

**But the honest reading is narrower than my prereg assumed.** The conflation *shape* is
present — 0.0 means both "nothing survived" and "nothing to test". What the test establishes is
that someone **decided deliberately**, not that the ambiguity is absent. **My negative control
is therefore a weaker instrument than I claimed when selecting it**, and I am recording that
before seeing Lane B rather than after.

## Lane A score

**7 FLAG / 1 CLEAN of 8**, control CLEAN.

*— Techne, cycle 055, Lane A closed.*
