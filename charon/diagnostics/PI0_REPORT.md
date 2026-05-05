# Per-Domain π₀ Calibration Report

**Computed:** 2026-05-05
**Author:** Charon (instantiated for π₀ calibration task)
**Data:** `per_domain_pi0.json` (this directory)
**Code:** `compute_per_domain_pi0.py` (this directory)

---

## TL;DR

| Domain | n (train) | π₀ (Jeffreys) | 95% CI | Interpretation |
|---|---:|---:|---|---|
| Lehmer / Mahler discovery | 30 000 | **0.9989** | [0.9986, 0.9993] | near-unity |
| OEIS Sleeping | 15 000 | **~0.929** | [0.886, 0.972] (bounded) | high (bounded) |
| modular_form | 15 000 | **0.950** | [0.947, 0.954] | high |
| mock_theta | 15 000 | **0.966** | [0.964, 0.969] | high (test set thin: 39) |
| knot_trace_field | 15 000 | **0.861** | [0.856, 0.867] | high (test set thin: 42) |
| BSD_rank | 3 000 | **0.796** | [0.781, 0.810] | moderate |
| genus2 | 15 000 | **0.669** | [0.661, 0.677] | moderate |

A PROMOTE in a high-π₀ domain (where most candidates would fail under a null
generator) is strong evidence; in a low-π₀ domain it is weaker. The current
estimates suggest that the domains differ by an order of magnitude in their
expected information content per surviving CLAIM.

---

## 1. Method and why

### Method choice: beta-binomial, not Storey

The substrate's current cross-domain rediscovery envs (BSD, modular, knot,
genus2, OEIS, mock_theta) report **one experiment-level p-value per pilot**
(REINFORCE-vs-random-null arm comparison), not per-prediction p-values.
Storey 2002's q-value approach requires a histogram of p-values from the
hypothesis-test family, which the substrate does not currently expose at
the rediscovery-env level.

I fall back to **beta-binomial estimation** of π₀ as the population error
rate of the random null arm: under a learner with no signal, what fraction
of test items are predicted incorrectly? This is the substrate-relevant
proxy for π₀ — the expected proportion of CLAIMs that would fail the battery
under a null generator.

### Why π₀ here is an upper bound on substrate claim-stream π₀

Storey's π₀ is the proportion of *true H0* in a multi-test family. The
quantity I compute is the *fraction of wrong-under-null predictions*. These
are equal only if every wrong-under-null prediction maps 1-to-1 to a substrate
CLAIM that gets battery-tested. In practice the substrate is selective — it
does not promote every prediction; it claims patterns. The true substrate
π₀ is therefore ≤ the values reported here.

The estimates here should be read as:

> "If the substrate claimed indiscriminately on every random-null prediction
> in this domain, the false-conjecture base rate would be π₀."

This is a calibration upper bound, not a tight estimate. It is still
operationally useful for weighting PROMOTE confidence across domains.

### Priors

- **Primary:** Jeffreys Beta(0.5, 0.5) — invariance-friendly, slightly tighter
  near edges, conventional for proportion estimation.
- **Alternative:** Uniform Beta(1, 1) — reported in `per_domain_pi0.json`
  for sensitivity. Differences between the two are <0.001 for all domains
  except possibly thin tails.

Both priors are weakly informative; the data dominates for n ≥ 3000. For
the thin-test-set domains (knot, mock_theta, OEIS), prior choice is more
visible.

### CI methods

Three are reported per domain:

1. **Beta-posterior central 95%** — primary; what the JSON's `pi0_ci` carries.
2. **Wilson score** — for cross-checking the binomial inference; included
   in the per-domain JSON record.
3. **Parametric bootstrap over per-seed accuracies** — sanity check that
   per-seed variance is not larger than the binomial CI suggests. With
   only 3 seeds per domain, bootstrap CIs are loose and not used as the
   primary estimate.

For the Lehmer domain (0 promotes / 30000 episodes), the **rule of three**
upper bound on the promote rate is also reported (0.0001 at one-sided 95%).

---

## 2. Per-domain results

### 2.1 BSD_rank

- **n = 3000** (3 seeds × 1000 train episodes)
- **Random-arm accuracy = 20.4%** → **π₀ = 0.796** [0.781, 0.810]
- Test-split sanity: π₀_test = 0.800 [0.773, 0.825], n=900. Consistent.
- Interpretation: **moderate**. 5-way classification (rank 0..4); uniform
  random gives ~20% accuracy, so π₀ ≈ 0.80 is the structural expectation.
- A PROMOTE in BSD_rank carries less evidential weight than in modular or
  Lehmer, because the prior probability of a correct guess is higher.

### 2.2 modular_form

- **n = 15 000** (3 seeds × 5000 train episodes)
- **Random-arm accuracy = 5.0%** → **π₀ = 0.950** [0.947, 0.954]
- Test-split sanity: π₀_test = 0.953 [0.938, 0.966], n=900.
- Interpretation: **high**. Prediction space is much wider than BSD;
  random guesses rarely match. PROMOTE here is strong evidence.

### 2.3 knot_trace_field

- **n = 15 000** (3 seeds × 5000 train episodes — but corpus is small)
- **Random-arm accuracy = 13.9%** → **π₀ = 0.861** [0.856, 0.867]
- Test-split sanity: **n_test = 42** (3 seeds × 14 items). Wide CI on
  test alone. Reported as `thin_data` interpretation tag.
- Interpretation: **high but thin**. The 48-record knot corpus is a known
  data-thinness condition; per-CLAIM evidence in this domain is noisier
  than the train-population π₀ alone suggests.

### 2.4 genus2

- **n = 15 000** (3 seeds × 5000 train episodes)
- **Random-arm accuracy = 33.1%** → **π₀ = 0.669** [0.661, 0.677]
- Test-split sanity: π₀_test = 0.687 [0.665, 0.708], n=1800.
- Interpretation: **moderate**. Random-arm baseline is unusually high
  (~3-way classification likely); reduces the surprise per PROMOTE.
- Of the seven domains, genus2 has the lowest π₀. Substrate claims here
  need stricter battery thresholds to clear the same evidential bar.

### 2.5 OEIS_sleeping

- **n = 15 000** (3 seeds × 5000 train episodes)
- **Ternary reward** (HIT=100, NEAR=25, MISS=0) prevents point estimation
  from mean reward alone.
- **Bounds on π₀ (train): [0.886, 0.972]** (ci_width = 0.085)
- Test-split bounds: [0.853, 0.963], n=150. Consistent.
- Reported `pi0_mean` is the bound midpoint (0.929) for sortability.
- The bounds are *exact* under the achievable-distribution constraint
  (mean = 100·p_hit + 25·p_near with p_hit + p_near + p_miss = 1).
- **Honesty note:** to convert to a point estimate, the env must log
  per-prediction outcome (HIT|NEAR|MISS) rather than aggregate mean reward.
  This is a substrate-level instrumentation gap.

### 2.6 mock_theta

- **n = 15 000** (3 seeds × 5000 train episodes; test corpus = 13 items)
- **Random-arm accuracy = 3.4%** → **π₀ = 0.966** [0.964, 0.969]
- Test-split sanity: **n_test = 39**. Wide CI on test alone.
- Interpretation: **high but thin**. The test corpus of 13 items is the
  thinnest of the seven domains. The train-population π₀ is well-determined,
  but per-CLAIM evidence on individual mock theta predictions is noisy.

### 2.7 Lehmer_Mahler_discovery

- **n = 30 000** (3 seeds × 10 000 random_null episodes from four_counts pilot)
- **0 promotes / 30 000 episodes** → **π₀ ≈ 0.9989** [0.9986, 0.9993]
- **Rule-of-three upper 95% on promote rate: 0.0001**
- REINFORCE arm: also 0/30000 promotes; π₀ ≈ 0.9999.
- Kill-pattern decomposition (random_null arm):

| Kill pattern | Count | Fraction |
|---|---:|---:|
| upstream:functional | 26 027 | 86.8% |
| upstream:cyclotomic_or_large | 3 325 | 11.1% |
| upstream:low_m | 581 | 1.9% |
| upstream:salem_cluster | 35 | 0.12% |

- **Operational note:** π₀ ≈ 1.0 in this domain is consistent with both
  hypotheses: (a) the substrate is competent and the domain genuinely lacks
  sub-Lehmer non-cyclotomic polynomials (Lehmer's conjecture); (b) the
  substrate is undersampling the sub-Lehmer band. The current data cannot
  distinguish these. The kill-pattern decomposition confirms that the
  substrate at least reaches the Salem cluster (35 entries) and the low-M
  band (581 entries) under random sampling, so the hypothesis "substrate
  never gets near the right region" is falsified — the substrate is
  searching the right region; the region appears genuinely empty under
  current scale.

---

## 3. Operational implications for the substrate

π₀ becomes a per-domain weight on PROMOTE confidence. The Bayes-factor-style
interpretation: a PROMOTE survivor in domain D updates posterior credence
by a factor proportional to π₀_D / (1 − π₀_D) (the prior odds against the
null in that domain). Higher π₀ → higher per-PROMOTE evidence.

**Concrete weightings:**

| Domain | π₀ | Prior odds (π₀ : 1−π₀) | Per-PROMOTE evidence |
|---|---:|---:|---|
| Lehmer/discovery | 0.999 | 1000 : 1 | extremely strong (per-PROMOTE) |
| mock_theta | 0.97 | 32 : 1 | very strong (but n_test thin) |
| modular_form | 0.95 | 19 : 1 | strong |
| OEIS_sleeping | 0.93 | 13 : 1 | strong (bounded; resolution gap) |
| knot_trace_field | 0.86 | 6 : 1 | moderate (n_test thin) |
| BSD_rank | 0.80 | 4 : 1 | moderate |
| genus2 | 0.67 | 2 : 1 | weakest |

**Action implications for the substrate:**

1. **Domain-aware battery thresholds.** A claim that PROMOTEs in genus2
   should require stricter battery passage than one in modular_form to
   reach the same posterior confidence. The current battery does not
   condition on domain π₀; this report is the data needed to begin doing so.

2. **Multiple-testing correction.** Cross-domain comparisons of PROMOTE
   counts must be weighted by π₀. A PROMOTE rate of 1% in Lehmer is
   genuinely surprising; the same rate in genus2 is barely above the
   null-arm noise floor.

3. **Resolution gap on OEIS_sleeping.** The env must be modified to log
   per-prediction outcome (HIT|NEAR|MISS) rather than aggregate mean reward.
   Until then π₀ on OEIS is bounded, not pinpointed. This is a substrate
   instrumentation defect surfaced by the calibration exercise.

4. **Storey upgrade path.** When the substrate begins logging per-claim
   p-values from F1/F6/F9/F11 battery tests (as opposed to per-experiment
   p-values), Storey's q-value method becomes applicable and will produce
   tighter, more interpretable estimates. This report is the placeholder
   until that instrumentation lands.

5. **Thin-domain follow-up.** knot_trace_field (n_test=42) and mock_theta
   (n_test=39) have fundamentally narrow evidence per individual PROMOTE.
   Substrate decisions about cross-domain comparisons involving these two
   should explicitly carry the thin-data caveat.

---

## 4. Honesty notes

These are reproduced from `per_domain_pi0.json` for convenience.

1. The π₀ computed here is **not** Storey's strict null-proportion in a
   multi-test family. It is the population error rate of the random null
   model per domain — an upper bound on substrate claim-stream π₀ under the
   assumption that every wrong-under-null prediction maps to a substrate
   CLAIM.

2. The substrate's actual CLAIM stream is filtered (the substrate does not
   promote every prediction); true substrate π₀ is therefore ≤ these
   estimates. The estimates here are best read as "what π₀ would be if the
   substrate claimed indiscriminately."

3. All cross-domain rediscovery pilots use n_seeds=3. Bootstrap CIs over only
   3 seeds are loose. Wilson and beta-posterior CIs on aggregated counts are
   tighter but assume i.i.d. predictions, which holds within a seed but not
   strictly across seeds.

4. OEIS_sleeping ternary reward (HIT/NEAR/MISS) prevents point estimation
   from mean reward alone. Bounds reported. To convert to a point estimate,
   the env must log per-prediction outcome.

5. Lehmer_Mahler_discovery has 0 promotes in 60000 episodes (across both
   random_null and reinforce arms). π₀ ≈ 1.0 may be a substrate competence
   claim OR a structural property of Lehmer's conjecture. Cannot distinguish
   from the current data; flagged in the per-domain operational_note.

6. Thin domains (knot test=42, mock_theta test=39, OEIS_sleeping test=150):
   Wilson CIs are wide. Reported `ci_width` to be visible.

7. Method choice (beta-binomial vs Storey) is data-availability driven, not
   preference. If/when the substrate begins logging per-claim p-values from
   F1/F6/F9/F11 battery tests, recompute with Storey for tighter and more
   interpretable estimates.

---

## 5. Calibrated negative

The most important finding of this exercise is **what the substrate currently
cannot measure**:

- **No per-claim p-value stream exists yet** for the cross-domain rediscovery
  envs. Each pilot exposes one experiment-level p-value, not the per-prediction
  p-values needed for Storey.
- **OEIS_sleeping cannot be point-estimated** under current instrumentation;
  the env must be modified to log per-prediction outcome.
- **Per-CLAIM ledger across all 6 envs does not exist**; the four-counts
  pilot is the only domain with a proper kill-pattern stream.

The π₀ values in §2 are a calibration upper bound. They are operationally
useful as PROMOTE confidence weights, but the substrate would benefit from
the instrumentation upgrades named above before treating them as tight.

In Charon discipline: this report calibrates a knob that the substrate did
not previously have; the negatives it surfaces are themselves substrate-grade
data about where the substrate's instrumentation is currently blind.

— Charon, 2026-05-05
