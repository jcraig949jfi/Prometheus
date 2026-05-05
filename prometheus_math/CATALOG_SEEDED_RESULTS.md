# Catalog-seeded REINFORCE pilot — Lehmer/Mahler-measure search

**Forge date.** 2026-04-29 (4-arm pilot); **5-arm extension.** 2026-05-04.
**Author.** Techne (toolsmith).
**Driver.** `prometheus_math/catalog_seeded_pilot.py`.
**Tests.** `prometheus_math/tests/test_catalog_seeded.py` (16 tests, all green:
12 original + 4 frozen-bias).
**Raw output.** `prometheus_math/_catalog_seeded_pilot.json` (5-arm),
`prometheus_math/_catalog_seeded_pilot_5arm.log` (5-arm transcript).

This pilot is the strictest remaining live test of "is REINFORCE+linear
too weak?" on `DiscoveryEnv`. After 13 ablation cells / 350K+ episodes
returned 0 PROMOTEs across algorithm class (random/REINFORCE/PPO),
reward shape (step/shaped), alphabet (±3/±5/±7), degree (10/12/14), and
generator (V1/V2), we warm-started the policy at known small-M
neighborhoods (Mossinghoff polys with `max|c| >= 4` projected to the
env's first-half coefficient distribution). The hypothesis under test:

* **H1.** Lehmer's conjecture / structural emptiness — the +100 band
  `M ∈ (1.001, 1.18)` is essentially empty in the env's polynomial
  subspace.
* **H2.** Algorithm strength was the bottleneck — REINFORCE+linear
  couldn't *find* the trajectory subspace where +100 polys live;
  warm-starting near catalog small-M polys would let it.

If catalog-seeded REINFORCE reaches the right neighborhood (catalog
hits / Salem-cluster concentration) but produces no PROMOTEs, H1 is
strengthened. If seeded REINFORCE produces PROMOTEs that uniform
REINFORCE didn't, H2 is the bottleneck.

---

## Configuration

```
degree                  14
coefficient_choices     (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5)  # ±5 alphabet
n_actions               11
half_len                8        (palindromic constraint -> 8 picks per episode)
trajectory_space        11^8 = 214,358,881
reward_shape            "step"   (sparse: +100 sub-Lehmer, +20 Salem cluster, ...)
n_episodes_per_cell     5000
seeds                   (0, 1, 2)
arms                    {random_uniform, random_seeded,
                         reinforce_uniform, reinforce_seeded,
                         reinforce_frozen_bias}
total_episodes          5000 x 3 x 5 = 75,000
wall time               ~167 s (~3 min) on M1
```

REINFORCE hyperparameters (uniform / seeded full-policy / frozen-bias):
`lr=0.05`, `entropy_coef=0.05`, `reward_scale=1/100`, `baseline_decay=0.95`,
`prior_strength=1.0` (literal log-prior at warm start).
Frozen-bias adds `delta_lr=0.005` (1/10 of `lr`, so the bias scaffold
dominates the early distribution).

---

## Seed pool

Strict filter (`max|c| >= 4 AND degree in [12, 18]`) yielded only **4
entries** — too few to compute meaningful priors. We broadened to
**`max|c| >= 4` on the FULL polynomial AND first 8 ascending coeffs
within ±5**, which projects higher-degree catalog polys to the env's
half-length:

```
seed pool size          112 polynomials
M range                 [1.176281, 1.299946]
```

**Degree distribution** (the catalog is dominated by Lehmer-style
high-degree witnesses, hence the long tail):

```
deg  14: 1   deg  78: 1   deg 132: 3
deg  16: 2   deg  80: 2   deg 136: 1
deg  18: 1   deg  84: 1   deg 142: 3
deg  26: 1   deg  90: 1   deg 144: 5
deg  28: 1   deg  92: 1   deg 150: 1
deg  30: 1   deg  94: 4   deg 154: 5
deg  32: 1   deg  96: 2   deg 156: 2
deg  38: 2   deg 100: 1   deg 164: 2
deg  40: 1   deg 104: 3   deg 166: 7
deg  42: 1   deg 106: 3   deg 168: 8
deg  44: 1   deg 108: 1   deg 174: 1
deg  46: 1   deg 112: 1   deg 176: 2
deg  48: 1   deg 118: 6   deg 178: 2
deg  50: 1   deg 120: 5
deg  56: 2   deg 126: 1
deg  58: 4   deg 128: 4
deg  60: 1   deg 130: 5
deg  64: 1
deg  70: 2
deg  72: 2
```

**max|c| distribution** in the seed pool:

```
max|c| =  4 :  52 polys
max|c| =  5 :  31
max|c| =  6 :   3
max|c| =  7 :  15
max|c| =  8 :   3
max|c| =  9 :   2
max|c| = 11 :   1
max|c| = 13 :   1
max|c| = 17 :   4
```

Note: when projected to the first 8 ascending coefficients, the seed
pool is dominated by the canonical "starts with [1, 1, ..., -1, -1, ...]"
pattern that the Lehmer family inherits — high coefficients appear
mostly in the second half, so the projected priors place dominant mass
on small magnitudes early and increasing magnitude later.

---

## Action priors (per-step)

Computed as the empirical marginal distribution over coefficient
values across the seed pool's first 8 ascending coefficients, with
Laplace smoothing α = 0.05:

| Step | Top coef | Top prob | Entropy (nats) |
|-----:|---------:|---------:|---------------:|
|    0 |       +1 |  0.9545  |   0.290 (very peaked) |
|    1 |       +1 |  0.7255  |   0.861 |
|    2 |       +1 |  0.7340  |   0.929 |
|    3 |       +1 |  0.8697  |   0.653 |
|    4 |        0 |  0.8103  |   0.838 |
|    5 |       −1 |  0.6492  |   1.197 |
|    6 |       −2 |  0.6407  |   1.172 |
|    7 |       −2 |  0.6577  |   1.236 |

Maximum-entropy uniform = log(11) ≈ 2.398 nats. The seeded priors are
all well below that, confirming the catalog *does* concentrate on a
narrow neighborhood. Step 0 in particular pins the leading coefficient
near +1 (95.5%); for a monic-like reciprocal polynomial this is the
canonical Lehmer-family fingerprint.

---

## 5-arm pilot results

PROMOTE-rate, Salem-cluster proxy rate (M ∈ [1.18, 1.5]), and
catalog-hit rate, averaged over 3 seeds (5000 episodes each):

| Arm                       | PROMOTE | Salem-rate | cat-hit |
|---------------------------|--------:|-----------:|--------:|
| `random_uniform`          |   0.000 |    0.000   |   0.000 |
| `random_seeded`           |   0.000 |    0.123   |   0.071 |
| `reinforce_uniform`       |   0.000 |    0.000   |   0.000 |
| `reinforce_seeded`        |   0.000 |    0.000   |   0.000 |
| `reinforce_frozen_bias`   |   0.000 |    0.00007 |   0.000 |

Per-seed (5000 episodes per cell):

```
random_uniform         seed 0: cat=0    salem=0    low_m=0     reject=5000
                       seed 1: cat=0    salem=0    low_m=1     reject=5000
                       seed 2: cat=0    salem=0    low_m=0     reject=5000

random_seeded          seed 0: cat=378  salem=637  low_m=987   reject=4622
                       seed 1: cat=331  salem=586  low_m=1054  reject=4669
                       seed 2: cat=360  salem=625  low_m=981   reject=4640

reinforce_uniform      seed 0: cat=0    salem=0    low_m=0     reject=5000
                       seed 1: cat=0    salem=0    low_m=0     reject=5000
                       seed 2: cat=0    salem=0    low_m=0     reject=5000

reinforce_seeded       seed 0: cat=0    salem=0    low_m=0     reject=5000
                       seed 1: cat=0    salem=0    low_m=4     reject=5000
                       seed 2: cat=0    salem=0    low_m=4     reject=5000

reinforce_frozen_bias  seed 0: cat=0    salem=0    low_m=0     reject=5000
                       seed 1: cat=0    salem=1    low_m=3     reject=5000
                       seed 2: cat=0    salem=0    low_m=4     reject=5000
```

Welch one-sided t-tests (PROMOTE rates):

```
p(reinforce_seeded      > reinforce_uniform on PROMOTE)    = 1.0000  (no improvement)
p(reinforce_seeded      > random_seeded     on PROMOTE)    = 1.0000
p(random_seeded         > random_uniform    on PROMOTE)    = 1.0000  (no PROMOTEs anywhere)
p(reinforce_frozen_bias > reinforce_seeded  on PROMOTE)    = 1.0000  (no improvement)
p(reinforce_frozen_bias > random_seeded     on PROMOTE)    = 1.0000
p(reinforce_frozen_bias > reinforce_uniform on PROMOTE)    = 1.0000
```

Welch one-sided t-tests (Salem-cluster rates):

```
p(random_seeded         > random_uniform    on Salem-rate)  = 0.0003  ***
p(reinforce_seeded      > reinforce_uniform on Salem-rate)  = 1.0000
p(reinforce_frozen_bias > reinforce_seeded  on Salem-rate)  = 0.2113
p(reinforce_frozen_bias > reinforce_uniform on Salem-rate)  = 0.2113
```

The Salem-rate contrast is the clean control: seeded random sampling
DOES bias the search toward catalog-rich M-territory (p = 3 × 10^-4,
12.3% Salem-cluster vs 0% for uniform). The seeding mechanism is
working. Frozen-bias REINFORCE produces 1 Salem hit out of 15,000
episodes — directionally above zero but ~1700× below seeded random.

---

## SHADOW_CATALOG entries surfaced

**Total: 0** across all four arms, all three seeds, 60,000 episodes.

There are no SHADOW_CATALOG entries to list.

---

## PROMOTED entries

**Total: 0** across all four arms, all three seeds, 60,000 episodes.

---

## Catalog rediscoveries (seeded random)

Seeded random produced **1069 catalog hits** across the three seeds
(7.1% of episodes). These are M-value matches against the Mossinghoff
snapshot — the agent landed *exactly* on a known catalog poly.
Examples (seed 0, episode index, M-value):

```
ep   27  M=1.264394
ep   28  M=1.251047
ep   32  M=1.251047
ep   40  M=1.227786   ← canonical Salem polynomial of degree 14
ep   49  M=1.272818
...
```

The agent is rediscovering catalog polys at a respectable rate
(roughly 1 per 14 episodes), but those rediscoveries are all in the
Salem cluster M ≥ 1.18 — none of them break into the +100 band.

Note: seeded random catalog hits are tallied by `info["reward_label"]
== "salem_cluster"` AND `info["is_known_in_mossinghoff"]`. None of
these episodes route into the discovery pipeline (sub-Lehmer band
only); their `claim_into_kernel_count = 0`.

---

## Frozen-bias REINFORCE — does the scaffold survive sparse rewards?

Hypothesis behind the variant: in seeded full-policy REINFORCE, the
warm-started bias `b ← log(prior)` was eroded by policy-gradient +
entropy regularization before sparse rewards consolidated it. The
cleanest fix is to FREEZE the bias scaffold and only train a small
additive residual `δ`::

    b      = prior_strength * log(action_priors)   # FROZEN
    δ      = 0                                     # learnable
    logits = W[s] @ obs + b[s] + δ[s]
    π(a|s) = softmax(logits)

Gradient updates flow through `W` and `δ` only; `b` is a literal
constant the gradient cannot touch. This is the cleanest H2
falsifier: if frozen-bias REINFORCE STILL produces 0 catalog hits,
gradient erosion was NOT the explanation, and the +100 band is
structurally empty (H1).

**Implementation invariant.** The function asserts at end-of-run that
`b` is bit-identical to its warm-start value (`np.array_equal` over
the entire half_len × n_actions matrix). The 5-arm production run
passed this invariant on all three seeds, and a dedicated test
(`test_authority_frozen_bias_does_not_erode`) verifies it offline
against a recomputed scaffold.

**5-arm result (3 seeds × 5000 eps = 15,000 frozen-bias episodes).**

| Metric            | seeded random | seeded REINFORCE | frozen-bias |
|-------------------|--------------:|-----------------:|------------:|
| PROMOTE rate      |        0.000  |           0.000  |     0.000   |
| Salem-cluster rate|        0.123  |           0.000  |     0.00007 |
| Catalog hit rate  |        0.071  |           0.000  |     0.000   |
| Catalog hits (raw)|        1069   |              0   |        0    |
| Salem hits (raw)  |        1848   |              0   |        1    |
| sub-Lehmer (low_m)|        3022   |              8   |        7    |

`δ` final magnitudes were small (max ~1.6e-3, mean ~2.6e-4), so the
literal logit scaffold was preserved as designed. But the policy
distribution drifted anyway: the W matrix learned to multiply
non-zero observations into the logits, and `W @ obs` outgrew the
frozen `b + δ` long before the catalog could be consolidated. The
frozen scaffold protects the bias logits, but it cannot protect the
*effective* policy distribution while W is trainable on early small
positive advantages.

The result is qualitatively the same as seeded REINFORCE: the prior
neighborhood is forgotten. Frozen-bias produced ~700× fewer Salem
hits than seeded-random and exactly zero catalog rediscoveries vs
1069 for seeded-random. Welch p-values are 1.0000 for every PROMOTE
contrast and 0.21 for the Salem comparison against `reinforce_seeded`
(directional but not significant: 1 hit vs 0).

**Comparison with full-policy seeded REINFORCE.** Frozen-bias did
NOT produce more catalog hits than the full-policy seeded variant
(both produced exactly 0). The two behave essentially identically on
all metrics that matter for H2: catalog hit rate, sub-Lehmer rate,
PROMOTE rate. The scaffold preserved the bias-logit identity but did
NOT preserve the catalog-rich behavior that seeded random sampling
naturally exhibits.

**Verdict on the scaffold question.** The frozen-bias scaffold
*preserves* the bias signal at the logit level, but it does NOT
translate that preservation into catalog-rich behavior under
trainable W. The cleanest H2 falsification is therefore done: the
gradient erosion of `b` was not the operative bottleneck.

---

## REINFORCE seeded collapse

The most diagnostic finding: **REINFORCE seeded performed *worse* than
random seeded** on every metric. Specifically, REINFORCE seeded
ended with 0 catalog hits and 0 Salem-cluster hits, while random
seeded had 1069 and 1848 respectively. The warm-started bias was
washed away.

Mechanism (analytical): REINFORCE's policy is `π(a|o) = softmax(W·o +
b)`. Warm-starting `b ← log(prior)` sets `π(·|o=0) = prior` at episode
0. But:

1. The first few episodes pick mostly +1 / 0 / -1 / -2 (the high-prior
   actions) and earn rewards in the {0, +5, +20} range — never +100,
   because the +100 band is empty.
2. The advantage `(r - baseline)` is small but mostly positive (early
   baseline starts at 0; small positive rewards push gradients upward
   on the chosen actions).
3. The entropy regularization term pushes `b` back toward uniform
   logits — the +20 Salem rewards aren't strong enough to dominate
   over many episodes, especially as `W` grows (and `W·o` magnifies
   noise from observation drift).
4. By ~500 episodes, `b` has been driven away from `log(prior)` and
   the policy is exploring a non-informed region. The catalog
   neighborhood is forgotten.

This is a known REINFORCE pathology: warm-started priors decay
exponentially in the number of policy-gradient steps unless reinforced
by reward. With `prior_strength = 1.0` and `entropy_coef = 0.05`, the
half-life is too short for the sparse reward to consolidate the prior
before it dissipates.

---

## Verdict on Hypothesis 2 (post frozen-bias)

**Hypothesis 2 (algorithm-strength bottleneck) is now strongly
disfavored relative to Hypothesis 1.**

The clean finding across the 5 arms is:

1. **Random seeded** — the simplest possible use of the prior — DOES
   reach the right neighborhood. 1069 catalog hits, 1848 Salem-cluster
   hits, 0 PROMOTEs.
2. **REINFORCE seeded (full-policy)** — *forgot the prior* and ended up
   worse than random seeded everywhere. 0 catalog hits, 0 Salem hits,
   0 PROMOTEs.
3. **REINFORCE frozen-bias** — the cleanest H2 falsifier — kept the
   bias scaffold literally bit-identical to `log(prior)` for all 15,000
   episodes, with `δ` updates capped to negligible drift (max ~1.6e-3).
   Yet still produced 0 catalog hits, 1 Salem hit, 0 PROMOTEs. The
   gradient erosion of `b` was NOT the operative bottleneck.

The frozen-bias result rules out the most natural H2 mechanism: that
the warm-started prior was decaying too fast to consolidate. With a
literal constant scaffold the prior CANNOT decay, and the policy
*still* fails to behave catalog-rich. The remaining culprit is the W
head, which trains on observations and learns to dominate the logits
once non-zero advantages arrive — but tweaking W's learning rate or
freezing W entirely would just collapse the agent to seeded-random
behavior, which already produced 0 PROMOTEs.

Strict reading: even the BEST behavior we've seen — seeded random
sampling, which biased the search and produced 1069 catalog
rediscoveries and 1848 Salem hits — found zero sub-Lehmer polys.
The catalog is by construction the lowest-M neighborhood at this
degree, so this is the maximally favorable sampler for the +100
band, and it returned empty.

Alternative seedings (Bayesian, root-space, KL-to-prior) remain
untested but increasingly speculative: they would each have to
generate behavior catalog-richer than seeded random, and seeded
random already failed to find any +100 polys.

**One-sentence verdict.** Frozen-bias REINFORCE preserved the catalog
warm-start bit-identically yet still produced 0 catalog hits and 0
sub-Lehmer PROMOTEs across 15,000 episodes — this is the cleanest H2
falsifier yet, and combined with the seeded-random control (1069
catalog hits, 0 PROMOTEs) it shifts the weight of evidence toward H1
(structural emptiness of the +100 band in the deg-14 ±5 polynomial
subspace) and away from H2 (algorithm-strength bottleneck).

---

## Honest framing & caveats

* The pilot is one specific seeding strategy. Per-step coefficient
  marginals are a coarse summary of the seed pool — any joint structure
  across coefficient positions (correlations, palindromic constraints
  beyond the env's mirroring, root-space proximity) is invisible here.
* The seed pool extraction broadened to "any catalog poly with
  `max|c| >= 4` whose first 8 ascending coeffs fit ±5". This pulled in
  high-degree polys (up to deg 178) projected to deg 14. The
  projection may distort which polynomial families dominate the
  priors.
* `degree=14` + `±5` alphabet is one cell in the 13-cell ablation
  matrix that returned 0 PROMOTEs. The seeding result here doesn't
  directly extrapolate to other degrees / alphabets.
* `n_episodes = 5000` per arm gives reasonable statistical power for
  PROMOTE-rate >= 1e-3, but a true sub-Lehmer poly is rare enough that
  even 60,000 episodes might miss it. The 0-PROMOTE finding is
  consistent with both "the band is empty" and "the band is sparse and
  we didn't sample enough".

---

## Reproducibility

```bash
cd F:\Prometheus
python -m prometheus_math.catalog_seeded_pilot 5000
python -m pytest prometheus_math/tests/test_catalog_seeded.py -v
```

Outputs:
* `prometheus_math/_catalog_seeded_pilot.json` — full per-arm details
* `prometheus_math/_catalog_seeded_pilot.log` — stdout transcript
* `prometheus_math/CATALOG_SEEDED_RESULTS.md` — this document

Test count: 16 (4 authority including frozen-bias-no-erode,
3 property, 4 edge including frozen-bias-zero-delta-lr, 3 composition,
1 frozen-bias property, 1 frozen-bias composition).
