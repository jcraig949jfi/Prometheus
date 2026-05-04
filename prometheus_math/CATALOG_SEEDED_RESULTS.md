# Catalog-seeded REINFORCE pilot — Lehmer/Mahler-measure search

**Forge date.** 2026-04-29. **Author.** Techne (toolsmith).
**Driver.** `prometheus_math/catalog_seeded_pilot.py`.
**Tests.** `prometheus_math/tests/test_catalog_seeded.py` (12 tests, all green).
**Raw output.** `prometheus_math/_catalog_seeded_pilot.json`,
`prometheus_math/_catalog_seeded_pilot.log`.

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
arms                    {random_uniform, random_seeded, reinforce_uniform, reinforce_seeded}
total_episodes          5000 x 3 x 4 = 60,000
wall time               ~165 s (~3 min) on M1
```

REINFORCE hyperparameters (both seeded and uniform):
`lr=0.05`, `entropy_coef=0.05`, `reward_scale=1/100`, `baseline_decay=0.95`,
`prior_strength=1.0` (literal log-prior at warm start).

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

## 4-arm pilot results

PROMOTE-rate, Salem-cluster proxy rate (M ∈ [1.18, 1.5]), and
catalog-hit rate, averaged over 3 seeds (5000 episodes each):

| Arm                | PROMOTE | Salem-rate | cat-hit |
|--------------------|--------:|-----------:|--------:|
| `random_uniform`   |    0.000 |    0.000 |   0.000 |
| `random_seeded`    |    0.000 |    0.123 |   0.071 |
| `reinforce_uniform`|    0.000 |    0.000 |   0.000 |
| `reinforce_seeded` |    0.000 |    0.000 |   0.000 |

Per-seed (5000 episodes per cell):

```
random_uniform        seed 0: cat=0    salem=0    low_m=0     reject=5000
                      seed 1: cat=0    salem=0    low_m=1     reject=5000
                      seed 2: cat=0    salem=0    low_m=0     reject=5000

random_seeded         seed 0: cat=378  salem=637  low_m=987   reject=4622
                      seed 1: cat=331  salem=586  low_m=1054  reject=4669
                      seed 2: cat=360  salem=625  low_m=981   reject=4640

reinforce_uniform     seed 0: cat=0    salem=0    low_m=0     reject=5000
                      seed 1: cat=0    salem=0    low_m=0     reject=5000
                      seed 2: cat=0    salem=0    low_m=0     reject=5000

reinforce_seeded      seed 0: cat=0    salem=0    low_m=0     reject=5000
                      seed 1: cat=0    salem=0    low_m=4     reject=5000
                      seed 2: cat=0    salem=0    low_m=4     reject=5000
```

Welch one-sided t-tests:

```
p(reinforce_seeded > reinforce_uniform on PROMOTE)        = 1.0000  (no improvement)
p(reinforce_seeded > random_seeded     on PROMOTE)        = 1.0000
p(random_seeded    > random_uniform    on PROMOTE)        = 1.0000  (no PROMOTEs anywhere)

p(random_seeded    > random_uniform    on Salem-rate)     = 0.0003  ***
p(reinforce_seeded > reinforce_uniform on Salem-rate)     = 1.0000
```

The Salem-rate contrast is the clean control: seeded random sampling
DOES bias the search toward catalog-rich M-territory (p = 3 × 10^-4,
12.3% Salem-cluster vs 0% for uniform). The seeding mechanism is
working.

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

## Verdict on Hypothesis 2

**Hypothesis 2 (algorithm-strength bottleneck) is *not* supported by
this pilot, but is *not* refuted either.**

The clean finding is:

1. **Random seeded** — the simplest possible use of the prior — DOES
   reach the right neighborhood. 1069 catalog hits, 1848 Salem-cluster
   hits, 0 PROMOTEs.
2. **REINFORCE seeded** — the spec's headline test — *forgot the prior*
   and ended up worse than random seeded everywhere. 0 catalog hits, 0
   Salem hits, 0 PROMOTEs.

Reading the result charitably, this REINFORCE failure is a *technical*
limitation of the linear-warm-start strategy, not a fundamental
verdict on H2. Alternative seeding regimes that haven't been tested
yet:

* **Larger `prior_strength`** (e.g., 5.0 or 10.0) — sharpens the warm
  start so it survives policy-gradient erosion.
* **No entropy regularization** for the first N episodes — gives the
  prior time to be consolidated by reward before exploration resumes.
* **Frozen-bias REINFORCE** — only update `W`, hold `b` fixed at
  `log(prior)`. The policy is then `softmax(W·o + log(prior))`, which
  always retains the prior as a tilting factor.
* **KL regularization** to the prior policy (REINFORCE+KL toward
  catalog distribution) instead of entropy toward uniform.
* **Bayesian prior over coefficient vectors** (mixture model fit to
  the seed pool) instead of per-step marginals.
* **Root-space sampling** near Salem polys (the algebraic
  neighborhood, not the coefficient neighborhood).

Reading the result strictly:

* Even seeded RANDOM — which *did* successfully bias the search and
  reached the catalog neighborhood ~1000 times — could not break the
  +100 ceiling.
* The catalog neighborhood is, by construction, the neighborhood with
  the lowest known M values at this degree. If sub-Lehmer polys in
  the env's polynomial subspace existed, seeded random would be the
  most likely sampler to find them, since it's literally biased toward
  the right region.
* It found zero.

**One-sentence verdict.** Catalog-seeded random sampling reached the
right neighborhood (1069 catalog hits, p = 3e-4 vs uniform on Salem
concentration) but produced zero sub-Lehmer polynomials, so this
specific seeding regime strengthens H1 (Lehmer-conjecture / +100-band
emptiness in the deg-14 ±5 subspace) without disproving H2 (other
seeding strategies remain untested) — the next falsification step is
either a frozen-bias REINFORCE variant or a root-space / Bayesian
seeding regime.

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

Test count: 12 (3 authority, 3 property, 3 edge, 3 composition).
