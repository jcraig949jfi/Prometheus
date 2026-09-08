# Archaeon Stage 0 — prospective-fragility survey of the real corpus

**Verdict: KILL.** Run 2026-09-06 (UTC) against SFE `var/engine.db`.
Reproduce with `python -m archaeon.stage0_fragility_survey`.
Machine-readable result: `archaeon/ledgers/stage0_survey_2026-09-05.json`.

Stage 0 answered one prerequisite:

> Does the real Prometheus substrate contain enough observable structure for
> the frozen S17 prospective-fragility primitive to produce meaningful
> within-dimension orderings at all?

**It does not.** Zero eligible claim-units, at every threshold tested.
Stage 1 must not be built on this substrate yet.

This is a statement about **corpus structure**. It is *not* a finding that
fragility is absent, that the S17 rules fail to transport, or that the
substrate is uninteresting. Those questions remain open and untested.

---

## 1. The instrument was inherited, not reimplemented

Loaded from a **pinned git blob** rather than a filesystem path — S17/S18 live
on `origin/main`, which is not an ancestor of this branch, so a path import
would not resolve at all; and an object id cannot drift under the reader.

    commit            21fbeffbbcb3ae7a0e729e591688066b895eff84
    instrument blob   0e2d654851ae11413f37f97d7087d747be4c394d
    ledger blob       261b91e6b2830d1c9adda0a8c28ae3292f2d0c74
    predictor hash    0106e035868bbe10...  RECOMPUTED AND VERIFIED

S17 imports stdlib only (`argparse hashlib json math random statistics sys`),
so there was no package-dependency obstacle to report.

Three checks ran before any feature was computed:

1. source blob matches the pinned object id;
2. `predictor_hash` **recomputed** from the predictor object equals the recorded
   `0106e035868bbe10…` — the predictor in hand is byte-identical to the one
   evaluated out-of-sample;
3. **positive control PASSED** — the imported `features()` computed cleanly on a
   claim from S17's own generator.

Check 3 is what makes the verdict interpretable. Without it, "zero eligible"
from an unsupportive corpus and "zero eligible" from a broken adapter are the
same number. The gate is also tested in the **PASS** direction against a
synthetic supportive corpus (`archaeon/tests/test_stage0_survey.py`), because a
gate that can only return KILL is indistinguishable from a broken one.

## 2. Why nothing was eligible

S17's `features(cl)` requires **two arms**, `cl["A"]` and `cl["B"]`, each a list
of worlds, each world an ordered trajectory. `hedges()` calls
`statistics.variance` on the per-arm world means, so **each arm needs ≥2
worlds**. There is no single-arm mode: an empty arm raises, and all five
dimensions are defined over both arms. A claim-unit therefore needs a
**contrast**, and the contrast has to come from the record.

Three arm rules were tried. None invents a split — a rule that halved unrelated
worlds would manufacture the very comparison the survey exists to discover.

    TOPOLOGY_SPLIT   0 units   no topology_group has >= 4 usable worlds
    FORK             0 units   parent arm holds 1 world; needs >= 2 per arm
    SPEC_ARM         0 units   no experiment on any usable world carries spec.arm

The blocking fact is structural and sharp:

- 180 worlds carry scored observations; 132 have ≥4 (needed for lag-1
  autocorrelation).
- Every topology group containing scored worlds has **at most 3** of them.
- The four groups that *do* have ≥4 worlds (sizes 36, 5, 5, 5) have **zero
  scored observations**.

So the groups with the structure have no data, and the groups with data have no
structure. **Insensitive to the threshold**: KILL at `min_obs` ∈ {2, 3, 4, 6, 8,
12}; max group size is 3 at every setting.

## 3. Per-dimension eligibility

    dimension   frozen feature    direction        eligible   orderable
    estimator   rel_se            LOWER=fragile        0         no
    transform   kurtosis          higher=fragile       0         no
    horizon     within_between    higher=fragile       0         no
    unit        serial_ac         LOWER=fragile        0         no
    noise       NO_RULE           --                   0      UNKNOWN

`noise` carries **NO_RULE** (0 fragile cases on S17's dev population). That is
`UNKNOWN` — not evidence of robustness — and its budget must not be reallocated
without a new pre-registered policy.

No feature values, distributions or spreads are reported, because none were
computable. Reporting an ordering over 0 or 1 units would be forcing a policy
onto data that cannot carry one, which is the outcome the kill condition exists
to prevent. The gate treats a single unit as **not orderable** for the same
reason, and that case is pinned by a test.

## 4. Evidence class

Of 3241 scored observations: **2934 `ENGINE_WORK_RESULT`, 307 `CLIENT_ASSERTED`**
(90.5% engine-attested). The survey labels any claim-unit spanning both as
`MIXED(...)` rather than collapsing it. Per SFE's archaeology note,
`CLIENT_ASSERTED` reads as *not engine-attested*, never as *false*.

## 5. Epistemic typing

Written as **values, never by omission** — an absent field reads as "nothing to
report", which is the reassuring negative the S14/S15 boundary forbids.

- `OBSERVED` — corpus counts, world grouping, evidence class, feature values.
- `INFERRED` — any fragility prediction; also the `TOPOLOGY_SPLIT` contrast,
  since SFE never says those halves were meant to be compared.
- `UNKNOWN` — the `noise` dimension, and **`upstream_selection_history`, stamped
  on every survey**: selection performed upstream of submission can be
  information-theoretically absent from the record, so every feature is
  conditioned on a submitted sample whose selection history is unobservable.

## 6. What would change the verdict

The gate flips as soon as the corpus contains, in one comparable group:

- **≥4 worlds** carrying scored observations (two arms of ≥2), with
- **≥4 observations per world** (lag-1 autocorrelation), and
- **≥2 such groups**, since an ordering over one unit carries no information.

That is a small target — roughly 8 worlds × 4 observations, correctly grouped.
The cheapest sources are an explicit `spec.arm` on experiments, or a
`topology_group` with ≥4 populated worlds. Neither needs new engine machinery;
both are properties of how experiments are *issued*.

Note separately that a full S18-style contrast needs far more: the measured
effect (random 0.288 → frozen rules 0.462) needs ~118 experiments per arm, and
budget must stay a small fraction of the candidate universe or the arms overlap
and the contrast degenerates by construction. That is a later question and is
**not** the success criterion for the first live loop.

## 7. Open item for Harmonia

**Narrative/ledger direction discrepancy — flagged, unresolved.** S17's commit
narrative reads as though *higher* serial dependence predicts unit fragility.
The frozen ledger sets `serial_ac.higher_is_fragile = false` (**lower** is
fragile), and `rel_se` likewise. S18's scorer applies
`score = v if higher_is_fragile else -v`, so an inverted direction makes the
policy anti-predictive rather than merely mis-worded.

**This survey uses the ledger**, and the directions are pinned by a test. The
frozen artifact was not altered to make the prose agree. Harmonia to reconcile
the wording against the artifact and issue a correction if appropriate.
