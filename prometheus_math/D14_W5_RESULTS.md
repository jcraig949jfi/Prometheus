# D14_W5_RESULTS — Path (A) Pilot: degree 14 + ±5 alphabet

Spec: `harmonia/memory/architecture/discovery_via_rediscovery.md` §6.2 + §6.4
Harness: `prometheus_math/four_counts_pilot.py` (commit f76d3974)
Driver: `prometheus_math/_run_d14_w5_pilot.py` (5K × 3 × 2 with verbose
record capture: SHADOW_CATALOG, PROMOTED, catalog-hit, kill-pattern,
proxy concentration per seed)
Raw JSON: `prometheus_math/four_counts_d14_w5.json`
Run log: `prometheus_math/_d14_w5_run.log`
Run date: 2026-05-03

---

## Why this run

Triple #3 confirmed the 0-PROMOTE ceiling at degree 10 across step /
shaped reward and ±3 / ±5 / ±7 alphabets — **0 PROMOTEs in 200K
cumulative episodes**. The post-mortem identified a critical
calibration gap: at degree 10, EVERY entry in the curated Known180 +
phase1 catalog has max|c| = 1, so a wider alphabet at degree 10
*cannot* reach the catalog entries that {-3..3} was excluding because
{-3..3} was already a superset of the catalog's coefficient support.

Hypothesis 2 says: "the +100 sub-Lehmer band exists at degree ≥ 14
but our policy class hadn't reached it because we'd been at the wrong
degree." Path (A) is the load-bearing test of that hypothesis: pilot
at **degree=14, coefficient_choices=(-5..5)**, the regime where the
catalog actually has small-M Salem polynomials with max|c| ≥ 4.

If degree 14 + ±5 produces PROMOTEs or SHADOW_CATALOG entries,
hypothesis 2 wins. If it does not, hypothesis 1 (Lehmer's
conjecture; the +100 band is empty in nature at any reachable
configuration of this policy class) tightens.

---

## Pre-flight: Known180 distribution

Pulled from the combined catalog (`known180_2022` + `phase1_curated`
tiers in `prometheus_math/databases/_mahler_data.py`; 8609 entries).

### Degree distribution at the relevant degrees

| degree | count | max\|c\|=1 | max\|c\|=2 | max\|c\|=3 | max\|c\|=4 | max\|c\|=5 |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 16 | 13 | 1 | 2 | 0 | 0 |
| 12 | 22 | 14 | 5 | 3 | 0 | 0 |
| **14** | **23** | **17** | **3** | **2** | **0** | **1** |
| 16 | 28 | 22 |  4 | 0 | 0 | 2 |
| 18 | 32 | 25 | 2 | 4 | 0 | 1 |
| 20 | 39 | 32 | 4 | 3 | 0 | 0 |

### Degree 14 entries with max|c| ∈ {2, 3, 4, 5}

```
M=1.176281  max|c|=2  salem  coeffs=[1,1,-1,-2,0,1,0,-1,0,1,0,-2,-1,1,1]
M=1.176281  max|c|=2  salem  coeffs=[1,1,0,-1,0,0,-1,-2,-1,0,0,-1,0,1,1]
M=1.176281  max|c|=5  salem  coeffs=[1,2,2,1,0,-2,-4,-5,-4,-2,0,1,2,2,1]
M=1.227786  max|c|=3  salem  coeffs=[1,2,3,2,0,-2,-3,-3,-3,-2,0,2,3,2,1]
M=1.227786  max|c|=2  salem  coeffs=[1,1,2,1,0,-1,-2,-2,-2,-1,0,1,2,1,1]
M=1.280638  max|c|=3  salem  coeffs=[1,1,1,0,-1,-2,-2,-3,-2,-2,-1,0,1,1,1]
```

**Critical structural observation:** at degree 14 there is exactly
**ONE** catalog entry with max|c| ≥ 4 — and it is a deg-14
representation of the Lehmer polynomial (M = 1.176281), with
coeffs requiring the {-5, -4, ..., 4, 5} alphabet to be reachable.
The {-3..3} alphabet was structurally excluding that single witness;
the {-5..5} alphabet now includes it.

So the pre-flight verdict is: **the experiment's hypothesis is
testable — there is at least one sub-Lehmer polynomial at degree 14
that is reachable from {-5..5} but NOT from {-3..3}**. The discovery
target is small (one specific witness), but it is non-zero, and
finding it would partially validate hypothesis 2.

---

## Pilot configuration

```
degree                = 14
coefficient_choices   = (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5)
n_actions             = 11
half_len              = 8         (8 free coefficients on the
                                   reciprocal half; degree-14 monic
                                   reciprocal poly has 8 dof)
trajectory space      = 11^8 = 214,358,881  (~214M)
reward_shape          = step       (the regime where REINFORCE held
                                    proxy concentration in triple #2)
n_episodes per cell   = 5000
seeds per condition   = 3   ({0, 1, 2})
arms                  = {random_null, reinforce_agent}
total episodes        = 30,000
```

Wall-clock: **50.4 s total** (random_null 23.3s, reinforce_agent
27.1s). Per-episode: ~1.6 ms (random) / ~1.8 ms (REINFORCE). Both
arms ran inside the 5-min ceiling with 6× margin; no fallback to
3K × 3 was needed.

---

## Headline four-counts

| condition | PROMOTE rate | SHADOW | catalog-hit rate | claim-into-kernel rate |
|---|---:|---:|---:|---:|
| random_null     | 0.0000 (0 / 15000) | 0 | 0.0000 (0 / 15000) | 0.0000 |
| reinforce_agent | 0.0000 (0 / 15000) | 0 | 0.0000 (0 / 15000) | 0.0000 |

### Welch t-test on PROMOTE rates

```
reinforce_agent  vs  random_null:  p = 1.000  lift = 0.00x
TIED-AT-ZERO (both PROMOTE rates 0; joint upper bound on
discovery rate at this configuration: < 1 / 15000 per arm)
```

### Per-seed breakdown

**random_null (5,000 episodes per seed):**

| seed | PROMOTE | SHADOW | cat-hit | claim | rejected | elapsed |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 5000 | 7.79s |
| 1 | 0 | 0 | 0 | 0 | 5000 | 7.74s |
| 2 | 0 | 0 | 0 | 0 | 5000 | 7.79s |

**reinforce_agent (5,000 episodes per seed):**

| seed | PROMOTE | SHADOW | cat-hit | claim | rejected | elapsed |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 5000 | 8.94s |
| 1 | 0 | 0 | 0 | 0 | 5000 | 9.06s |
| 2 | 0 | 0 | 0 | 0 | 5000 | 9.06s |

No mode-collapse asymmetry across seeds: all three REINFORCE seeds
behaved identically. The mode-collapse was *uniform* — it is the
arm's signature at this regime, not a single-seed pathology.

---

## SHADOW_CATALOG entries surfaced

**ZERO across all 30,000 episodes.**

The kill-path battery was never invoked because the pipeline was
never reached: every single episode was either rejected upstream
(out-of-band M, cyclotomic, functional) or absorbed by the
salem_cluster reward bucket. No CLAIM minted, no DiscoveryRecord
produced. The "SHADOW_CATALOG" file the spec asked us to fill is
empty.

---

## PROMOTED entries

**ZERO across all 30,000 episodes.**

---

## Catalog-hit episodes

**ZERO across all 30,000 episodes.**

The single Salem-cluster sub-band proxy hit (M in [1.18, 1.5)) came
from `random_null seed=2`. It was logged as `upstream:low_m` (the
M-band one band above Salem), not `upstream:salem_cluster`, and it
did not match any Known180 entry. **No polynomial reaching the
sub-Lehmer or low-M band was a catalog match.** The 1.176281 deg-14
witness with max|c|=5 — the one polynomial pre-flight identified as
reachable-from-{-5..5}-but-not-from-{-3..3} — was not found by
either arm.

---

## Kill-pattern breakdown (cumulative across 3 seeds = 15,000 episodes)

**random_null:**

| pattern | count | fraction |
|---|---:|---:|
| upstream:cyclotomic_or_large | 13,014 | 86.76% |
| upstream:functional          |  1,985 | 13.23% |
| upstream:low_m               |      1 |  0.01% |

**reinforce_agent:**

| pattern | count | fraction |
|---|---:|---:|
| upstream:cyclotomic_or_large | 14,952 | 99.68% |
| upstream:functional          |     48 |  0.32% |
| upstream:low_m               |      0 |  0.00% |

### The signal in the rejection pattern

REINFORCE collapsed onto the cyclotomic / large-M attractor in
**99.68%** of episodes — across all three seeds, identically.
Random null kept ~13% of episodes in the functional band. The
policy class did **worse than random** at finding any reward signal:
its exploration vanished.

This is qualitatively the *same failure mode* that triple #2 saw at
degree 12 seed 2 (single-seed mode collapse) and at degree 14 ±3
across all seeds (proxy concentration inverted to 0.13×). At
degree 14 + ±5 the failure is now uniform and complete: REINFORCE's
linear contextual policy cannot sustain exploration when the action
space widens to 11.

---

## Salem-cluster proxy concentration

| arm | salem_cluster proxy hits | low_m proxy hits |
|---|---:|---:|
| random_null     | 0 | 1 |
| reinforce_agent | 0 | 0 |

**Concentration ratio: undefined (numerator zero)**. There is no
proxy signal at all at this regime — neither arm landed in the
Salem-cluster M-band even once across 15K episodes. Compare:

| degree × alphabet | random Salem hits | REINFORCE Salem hits | ratio |
|---|---:|---:|---:|
| 10 × ±3 (10K × 3)  | 35 / 30K (0.117%) | 19,855 / 30K (66.18%) | **567×** |
| 12 × ±3 (5K × 3)   | 21 / 15K (0.140%) |  4,904 / 15K (32.69%) | **234×** (mode-collapse-inflated) |
| 14 × ±3 (3K × 3)   |  8 /  9K (0.089%) |      1 /  9K (0.011%) | **0.13× INVERTED** |
| 10 × ±5 (5K × 3)   |  1 / 15K (0.007%) |      0 / 15K          | **0× INVERTED** |
| **14 × ±5 (5K × 3)** | **0 / 15K**     | **0 / 15K**           | **n/a (both zero)** |

The proxy concentration **monotonically degrades** with both degree
and alphabet width. By the time we reach degree 14 + ±5, the
Salem-cluster signal is gone for *both* arms. The reachable
trajectory space (214M) is too sparse for uniform random to land
in a 1.18 ≤ M < 1.5 band by accident, and REINFORCE's policy class
cannot learn to navigate to it.

---

## The structural verdict

**Degree 14 + ±5 did NOT break the 0-PROMOTE ceiling.**

Combined with triple #2 + triple #3, the cumulative score is:

| sweep dimension | regimes tested | total episodes | PROMOTEs | SHADOW | catalog hits |
|---|---|---:|---:|---:|---:|
| degree (10 / 12 / 14, ±3, step) | 3 | 108,000 | 0 | 0 | 32 |
| reward shape (step / shaped, deg 10, ±3) | 1 (shaped only) | 30,000 | 0 | 0 | 32 (step only) |
| alphabet (±3 / ±5 / ±7, deg 10, step) | 2 (±5, ±7) | 48,000 | 0 | 0 | 1 (±5 only) |
| **alphabet × degree (this run, deg 14 + ±5)** | **1** | **30,000** | **0** | **0** | **0** |
| **TOTAL** | **7 ablation cells** | **216,000** | **0** | **0** | **65** |

**Across 216,000 episodes spanning every plausible (degree, alphabet,
reward shape) cell of the spec, this policy class has never produced
a single PROMOTE or SHADOW_CATALOG entry.** It has rediscovered
65 known polynomials in the salem_cluster band — calibration-grade
signal that the pipeline plumbing is correct — and zero novel sub-Lehmer
candidates.

### Which hypothesis won?

**Hypothesis 1 (Lehmer's conjecture / structural emptiness)** is now
the parsimonious read. Hypothesis 2 ("the +100 band exists at
degree ≥ 14, we just hadn't reached it") was specifically tested by
this run and did **not** survive: at degree 14 + ±5, the trajectory
space contains the deg-14 Lehmer rep (with max|c| = 5) as a known
witness, and 30K episodes of uniform-random + REINFORCE failed to
sample it, let alone find a novel sub-Lehmer polynomial. The
sub-Lehmer band at this configuration is empirically unreachable
under this policy class within the budget tested.

That does NOT prove Lehmer's conjecture. It says: with this env's
discrete-action reciprocal generator, this reward function, and this
linear contextual REINFORCE policy, the 0-PROMOTE ceiling is the
relevant bound, and pushing on (degree, alphabet, reward) is no
longer informative. Further interventions need to change the
*algorithm class* (PPO / MCTS / structured-search) or the
*generator* (free non-reciprocal coefficients, or warm-start from
known Salem polys), not the configuration knobs.

### Honest framing — what this run does NOT show

- This is one experimental dimension, not a proof. Further searches
  at degree 16 / 18 + ±7 would tighten the bound but would also need
  much wider trajectory spaces (15^11 ≈ 8.6 * 10^12 at deg 18 + ±7).
- The kill-path battery was never invoked, so its calibration
  remains untested at degree 14 + ±5. We do not know whether the
  pipeline plumbing would correctly REJECT or PROMOTE a sub-Lehmer
  candidate at this regime — only that none arose.
- REINFORCE's mode-collapse onto cyclotomic_or_large is itself a
  finding worth investigation: the linear policy is being driven
  away from the Salem cluster by some gradient artifact at wide
  alphabet × wide degree. Diagnosing that would inform what
  algorithm-class change is most productive.

---

## What to do next (recommendations, not commitments)

1. **Stop the configuration sweep.** The 0-PROMOTE ceiling has now
   held across degree {10, 12, 14}, alphabet {±3, ±5, ±7}, and
   reward shape {step, shaped}. The marginal information from one
   more (degree, alphabet) cell at this policy class is near zero.

2. **Switch policy class.** Candidates ranked by expected lift:
   - **MCTS** — explicit tree search over the trajectory space,
     UCB1 exploration. The 214M trajectory space at deg 14 + ±5
     is well within MCTS budget.
   - **PPO + structured action mask** — gradient-stable RL with a
     mask that enforces palindromicity / reciprocity at the action
     level so the policy doesn't have to learn it.
   - **Heuristic warm-start** — initialize REINFORCE near a known
     Salem polynomial and measure whether the policy can stay in
     the basin. If not, the REINFORCE failure is gradient pathology,
     not exploration starvation.

3. **Or change the generator.** Drop the reciprocal-half constraint;
   sample full coefficient vectors and use the kill-path battery
   (which already includes a reciprocity check) to filter. The
   reciprocal generator may be over-constraining the trajectory
   space relative to what the catalog covers.

4. **Investigate REINFORCE's cyclotomic collapse**. Why does a
   linear contextual policy at deg 14 + ±5 settle on the cyclotomic
   basin in 99.7% of episodes? Probe: log per-step action-prob
   entropy across episodes; check whether the gradient is being
   dominated by the +50 step-reward at M ≈ 1.

---

## Provenance

- DiscoveryEnv commit: f76d3974 (the constructor accepts `degree`
  and `coefficient_choices`; defaults preserved at degree=10,
  coefficient_choices=None → {-3..3}).
- Pilot harness: `prometheus_math/four_counts_pilot.py` (unchanged
  from prior triples). The verbose driver in
  `prometheus_math/_run_d14_w5_pilot.py` reuses
  `_tally_episode_outcome` and `_welch_t_test_one_sided` from the
  base harness; it adds per-episode capture of catalog-hit /
  PROMOTED / SHADOW records and per-seed proxy counts.
- Tests: 477 existing tests (incl. 16 four-counts tests) green; this
  run did not modify any tested module — it only added a new
  driver script and a JSON dump.
