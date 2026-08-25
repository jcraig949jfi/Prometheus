# Diomedes — review-response audit RESULT: the reviewer was substantially right, and the disposition changes to KILL

**Filed:** 2026-08-25. **Pre-registration:** `REVIEW_RESPONSE_PREREG_2026-08-25.md`, committed at
`b9f0517c` **before** any audit ran. **Rows:** `review_response_run.py` →
`review_response_result.json`.

**Disposition: KILL**, replacing the PARK filed hours earlier. What died is named in §6.

---

## 1. A1 — proxy reconstruction. **PARTIAL, and materially against the thread.**

Can the candidate's admissible features reconstruct the **withheld tested invariant** well enough
that applying the **exact** relation predicate to that reconstruction reproduces local ranking?

Local `Z(x,a)` on the same rows: **0.7392**. Chance 0.5000. Permuted-companion null **0.4995**.

- **A1 literal** (the reviewer's specification — candidate's raw companion values only)
  - binary predicate **0.5180** → captures **7.5%** of the local above-chance span
  - continuous variant **0.5404** → **16.9%**
  - proxy regression quality (Spearman ρ) **0.3963**
- **A1b strongest form** (the full frozen 18-feature family → withheld invariant)
  - binary predicate **0.5367** → **15.3%**
  - **continuous variant 0.5979** → **40.9%**, ρ **0.4700**

**Pre-registered band: 0.55–0.65 ⇒ PARTIAL, "report as partial and do not round either way."**
Best variant 0.5979. **PARTIAL it is.**

**What this means, stated without softening.** Roughly **two fifths of the local signal's
above-chance span is reproducible by a route that contains no navigational content at all** — predict
the variable the benchmark deliberately withheld, then apply the benchmark's own arithmetic. The
reviewer's Interpretation 2 is **materially supported**. It is not established as the whole story:
0.5979 is well short of 0.7392, and ~59% of the span is not accounted for by this route. But
"candidate-conditioned features carry information about the oracle" can no longer be presented as
evidence of navigational structure without this caveat attached.

**The instrument was corrected against my own interest before it was believed.** The first
implementation fed the proxy `w(candidate) − w(parent)`, which is parent-contaminated because the
parent varies within a cell. That weakened the proxy and pushed A1 **down** — the direction that
flatters this thread. It was killed and rebuilt on raw `w(a)`; proxy quality rose ρ 0.26 → 0.40 and
the AUC rose 0.505 → 0.518, and A1b was added specifically to give the attack its strongest form. The
v1 numbers are discarded, not reported as evidence.

## 2. A2 — leave-one-cell-out, relation held fixed. **0.5646. No shared structure — but read the margin.**

Trained on all other invariant pairs carrying the same relation, pooled, with **no cell-identity
feature of any kind**; evaluated on an entirely unseen pair.

**LOCO 0.5646** (per-seed: 0.5645, 0.5640, 0.5641, 0.5651, 0.5651 — remarkably stable) against
local relearning **0.7392** and single-cell raw transfer within stratum C **0.5549**.

Pre-registered band ≤ 0.57 ⇒ "no shared structure; the locality reading survives this attack."
**The margin is 0.0054.** That is a gate sitting closer to the observed value than I would like, and
it is reported rather than rounded past. What the number says plainly: **pooling eleven source cells
buys 0.0097 over a single source cell, and leaves 0.1746 of the local gap unrecovered.** Whatever the
local models know, it is not shared across invariant pairs in a form this family can pool.

This also disposes of my own Interpretation 4 in the corrected form the reviewer specified: the
apparent locality is **not** an artifact of refusing to pool.

## 3. A3 — uncertainty on the correct unit. **The seed SE was overstating precision ~52×.**

Stratum C (different pair, **same** relation — the only clean coordinate-transport stratum, 264
ordered pairs), cluster bootstrap resampling **target cells**, 2,000 resamples, 24 clusters:

- point recovery **0.0909**
- **95% CI [−0.0357, 0.2252]**, half-width **0.1305**
- seed-level SE previously quoted: **0.0025** → the honest interval is **52.2× wider**

**Two things follow, and both are reported.** First, **the transport effect is not distinguishable
from zero** once cell-to-cell variability is accounted for — the interval includes 0. Second, **the
entire interval still lies below the 25% MIXED gate** (upper bound 0.2252). So the pre-registered
Q2 branch is unchanged, but the confidence with which I stated it was wrong.

**The claim "127 SE below the gate" is withdrawn.** It was computed across 5 re-splits of the same
24 cells and measured split noise, not sampling variability of the quantity of interest. This is
`feedback_se_on_the_wrong_unit` firing again on my own work.

## 4. Declared: a pre-registration gap

The prereg fixed three disposition branches: A1 ≥ 0.65 ⇒ KILL (broad casualty); A1 ≤ 0.55 **and**
A2 ≤ 0.57 ⇒ KILL (corpus-as-vehicle); A2 ≥ 0.68 ⇒ REDESIGN.

**Observed: A1 = PARTIAL (0.5979), A2 = 0.5646. No branch fires exactly** — the second branch
requires A1 ≤ 0.55 and A1 is above it. That is a gap in my own pre-registration and it is declared
rather than resolved by picking the branch I prefer.

**Resolution, and the reasoning offered for audit:** every branch had already withdrawn PARK, so the
question is only which KILL, or REDESIGN. REDESIGN required A2 ≥ 0.68 and A2 is 0.5646, so REDESIGN
is excluded by measurement. Between the two KILLs, the broad-casualty version requires A1 ≥ 0.65 and
A1 is 0.5979, so **the corpus-as-vehicle KILL is the supported one**, carrying the additional recorded
finding that ~41% of the local span is proxy-reconstructible. A reviewer who thinks 0.5979 should
have been binned upward is entitled to that view; the band was frozen at 0.65 before the number
existed and I am not moving it.

## 5. Prediction vs outcome

- **A1:** predicted 0.60–0.70. Actual best **0.5979** — just outside, in the conservative direction.
  Marginally wrong.
- **A2:** predicted 0.55–0.62. Actual **0.5646**. **Right.**
- **A3:** predicted "several times wider than the seed SE, still below 0.25". Actual **52× wider**,
  upper bound **0.2252**. **Right**, though "several" understated it by an order of magnitude.

First time on this thread that most of my pre-registered predictions held. Running total across six
filings: **nine substantive predictions wrong or overstated, three right.** The three right ones
arrived only after an external reviewer specified the experiments.

## 6. Disposition — KILL, with the casualty named exactly

**KILLED:** *"Use the current cross-catalog substitution corpus to determine whether mathematical
navigation structure is transferable."*

The identifying assumptions are not available here, and that is now measured rather than argued:
Q1's census found no population with both a non-arithmetic oracle and conditional headroom above 0.05
(b3 0.0012, b4 0.0011, b2 0.0265); A1 shows a substantial fraction of the local signal is surrogate
sensing of the withheld variable; A2 shows no poolable cross-cell structure; A3 shows the transport
effect is not separable from zero; and production never recorded the transition semantics needed to
study trajectories at all.

**NOT killed, and explicitly retained:**

- *State-only residue is action-insufficient by construction* — measured exactly 0.5000. A type fact.
- *Production omitted the transition semantics required to test its own thesis* — unaffected by any
  of this.
- *The parent claim that state-action representations matter* — untouched by this corpus's failure.
- *"Mathematical navigation structure does not exist"* — *never* claimed and not supported. This
  KILL is about a vehicle, not about the phenomenon.

**PARK is withdrawn.** PARK means "legitimate but not economically discriminable now," which implies
some obtainable population could change the identifying assumptions. The Q1 census says there is
none. A clean KILL that names its casualty is the honest close, and charter §13 prefers it.

## 7. The correction to the thread's headline, adopted from the reviewer

> **Cycles 001–005 demonstrated candidate-conditioned predictability, not navigational information.**

With the measured addition this audit supplies: **roughly two fifths of that predictability is
reconstructible as surrogate measurement of the variable the benchmark withheld.** The open causal
question — whether `Z(x,a)` predicts future attainable verified progress rather than serving as a
sensor for variables defining the current oracle — was never tested by cycles 001–005 and cannot be
tested in this corpus.

## 8. Consequences for the successor, adopted

- The oracle must be **bounded downstream verified reachability**, not immediate tactic success.
  `Q*_H(x,a)` defined by exhaustive search from `x'` to a kernel-verified proof within horizon `H`.
  "Did the tactic execute", goal-count deltas, expression-size deltas and match-the-human-proof all
  recreate exactly the defect A1 just measured: an easily reconstructed local property standing in
  for "right action."
- **`simp` is excluded from the initial vocabulary**, or its internal work is charged explicitly. A
  macro tactic hides search inside the action, which is the thing under test.
- Transport families are preregistered in **two declared classes**: `T_independent` (no target
  observations whatsoever) and `T_unsup` (unlabeled target `X` permitted, target `Y` forbidden).
  CORAL and optimal-transport alignment belong to the second and are legitimate **there** — they were
  correctly excluded from cycle 005's frozen arm, and retro-admitting them would have repaired the
  hypothesis after seeing the answer.
- Any stratified quantity is reported **with its own denominator and its cluster-bootstrap interval**,
  never a seed-level SE, and strata that change the objective are never averaged with strata that
  change the coordinates.

---

## Coordinate-Adequacy Record — CAR-006

```json
{
  "car_id": "CAR-006",
  "claim_id": "the cycle-001..005 decomposition measures navigational information in this corpus",
  "quantity_credited": "fraction of the local above-chance span reproducible without navigational content, plus poolable cross-cell structure, plus cell-clustered uncertainty on coordinate transport",
  "attainable_range": {"chance": 0.5, "local_Zxa": 0.7392, "oracle": 1.0},
  "measured": {"A1_literal_binary": 0.518, "A1_literal_continuous": 0.5404,
               "A1b_full18_binary": 0.5367, "A1b_full18_continuous": 0.5979,
               "A1_span_captured_best": 0.409, "A1_permuted_null": 0.4995,
               "A1_proxy_spearman": 0.3963, "A1b_proxy_spearman": 0.47,
               "A2_LOCO_relation_fixed": 0.5646, "A2_margin_to_gate": 0.0054,
               "A2_single_cell_raw_stratumC": 0.5549,
               "A3_stratumC_recovery": 0.0909,
               "A3_ci95": [-0.0357, 0.2252], "A3_halfwidth_vs_seed_se": 52.2},
  "controls": {"permuted_companion_null": 0.4995, "population_digest_verified": true,
               "proxy_instrument_corrected_against_own_interest": true,
               "strongest_form_A1b_added_before_banding": true},
  "measured_over_which_rows": "5 seeds, 24 cells, 264 stratum-C ordered pairs, ~38,000 states/seed, digest 1b4abb1a",
  "verdict": "PARTIAL-SURROGATE-MEASUREMENT; NO-POOLABLE-STRUCTURE; TRANSPORT-NOT-SEPARABLE-FROM-ZERO",
  "disposition": "KILL",
  "what_died": "use of the cross-catalog substitution corpus to determine whether mathematical navigation structure is transferable",
  "what_survived": "the 0.5000 type argument; the instrument finding; the parent claim that state-action representation matters",
  "prereg_defect": "no branch specified for A1 PARTIAL combined with A2 <= 0.57; declared in S4 and resolved by exclusion rather than by preference, with the 0.65 band left unmoved",
  "decision_this_changes": "the reconnaissance closes as KILL rather than PARK; the successor's oracle must be bounded downstream verified reachability, and stratified quantities must never average objective-changes with coordinate-changes",
  "rows_ref": "review_response_result.json"
}
```

*— Diomedes, review-response result, 2026-08-25. Disposition KILL.*
