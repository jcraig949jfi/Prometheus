# Discovery V2 — GA-style generator results 2026-04-29

Path-D ablation for the v1 ceiling: 0 PROMOTEs across 7 ablation cells /
216K episodes hit `discovery_env.py`'s uniform reciprocal-half-coefficient
generator.  Hypothesis: a **richer generator** (mutation-driven population
search with structural inductive bias toward known low-M neighborhoods —
the GA-style search Mossinghoff used to find his original Salem polys)
might reach where uniform enumeration cannot.

**Headline:** GA-style generator did NOT break the ceiling at any arm.
0 SHADOW_CATALOG entries surfaced across 18K episodes (3K × 3 seeds × 2
arms) at degree 10 / population_size=8 / 12 mutations/ep.  But the
mechanism of failure is *informative and different from v1's failure* —
v1 ran into an enumeration sparsity wall; v2 runs into an **elitist-trap
attractor** where the population's elite walks down to cyclotomic
(M = 1.0 exactly) and then gets stuck.  Two different ceiling shapes,
neither of which the current configuration breaks.

## Generator design

V2 maintains a **population of N reciprocal polynomials** indexed by
their half-coefficient vectors over alphabet `{-3..3}`.  Each step
applies a **mutation operator** (chosen by the agent's action) to a
random population member; if the mutant's M is lower than the current
worst, the worst is evicted (elitist replacement).  Population is
initialized either uniform-random or seeded from the Mossinghoff
canonical low-M set (Lehmer + first three Salem-deg-10 entries).

**Mutation operator menu** (7 entries, in `MUTATION_OPERATORS`):

  1. `mutate_single_coef` — flip one coefficient to a fresh random alphabet entry
  2. `mutate_two_coefs` — flip two coefficients independently
  3. `swap_palindromic_pairs` — swap two half-coefficients (mirrored pair swaps too)
  4. `increment_at_index` — bump one coefficient by +1 (clipped to alphabet max)
  5. `decrement_at_index` — bump one coefficient by -1 (clipped to alphabet min)
  6. `zero_at_index` — set one coefficient to 0
  7. `identity` — no-op (anchors the property "agent-control matters")

**Reward shape** (non-negative on non-degenerate polys):
```
reward = max(0, 5 - elite_M)                  # gradient toward low M
       + max(0, prev_elite_M - elite_M) * 10  # population improvement bonus
       + 50 if 1.001 < elite_M < 1.18         # sub-Lehmer band bonus
       + 20 if SHADOW_CATALOG / PROMOTED      # catalog-miss + battery survival
```

**Episode shape:** `n_mutations_per_episode = 12` mutations are applied;
final step extracts elite + (if sub-Lehmer) routes through
`DiscoveryPipeline.process_candidate` for catalog cross-check + the
F1+F6+F9+F11 battery.

**Substrate discipline:** every M-evaluation goes through the
SigmaKernel via BIND/EVAL on the canonical
`techne.lib.mahler_measure:mahler_measure` binding.  Substrate-grade
the same way v1 is.

## V2 random vs V2 + REINFORCE — pilot results

Configuration:

| param | value |
|---|---|
| degree | 10 |
| population_size | 8 |
| n_mutations_per_episode | 12 |
| seed_with_known | False (random init) |
| n_episodes | 3000 per (arm, seed) |
| seeds | {0, 1, 2} |
| total elapsed | 248.4 s ≈ 4.1 min |

Per-arm best-M per seed:

| arm | seed=0 best M | seed=1 best M | seed=2 best M |
|---|---|---|---|
| random | 1.0000000 | 1.0000000 | 1.0000000 |
| reinforce | 1.0000000 | 1.0000000 | 1.0000000 |

Per-arm SHADOW_CATALOG entries per seed:

| arm | seed=0 | seed=1 | seed=2 |
|---|---|---|---|
| random | 0 | 0 | 0 |
| reinforce | 0 | 0 | 0 |

Per-arm sub-Lehmer-episode count per seed (sub-Lehmer = `1.001 < elite_M < 1.18`):

| arm | seed=0 | seed=1 | seed=2 |
|---|---|---|---|
| random | 0 | 0 | 0 |
| reinforce | 0 | 0 | 0 |

Per-arm mean reward per seed (signal of policy improvement):

| arm | seed=0 | seed=1 | seed=2 |
|---|---|---|---|
| random | 4.52 | 12.21 | 7.73 |
| reinforce | 4.69 | 13.72 | 8.06 |

REINFORCE's lift over random is small (+0.17 to +1.51 on mean reward,
+3-12% lift) — far below the +367.9% lift v1's contextual REINFORCE
achieved on the bandit env.  The REINFORCE policy weight norm stays
below 1.2 across seeds; the policy is barely diverging from uniform.

## What killed the runs

Across all 6 arms, the elite consistently walks down to **M = 1.0
exactly** — a cyclotomic.  The reward at M=1.0 is 0 (cyclotomics get
the sparse anchor), and elite_M < 1.001 is below the sub-Lehmer
threshold, so no episode produces a `sub_lehmer` flag and no candidate
enters the pipeline.

**This is a generator-trap finding distinct from v1's enumeration
sparsity.**  In v1 (uniform reciprocal-half-coefficient), the agent
enumerates trajectories and most miss the sub-Lehmer band by orders of
magnitude — the trajectory is too narrow to ever step into the band.
In v2, the population converges *in the wrong direction*: cyclotomics
satisfy elitist replacement (M=1 < anything else), so the population
locks onto cyclotomic factors rather than crossing the Lehmer
band.  The GA's "lower is better" elite criterion is too greedy for
the discovery target — it trips on the cyclotomic floor before ever
seeing Lehmer.

## Seeded-population sanity check

A separate 300-episode seeded run (seed=100, `seed_with_known=True`,
pipeline disabled) confirmed the env's mechanics:

| arm | best M | sub-Lehmer eps | identity-op count | total ops |
|---|---|---|---|---|
| random | 1.0000000 | 91 | 499 | 3600 |
| reinforce | 1.0000000 | 297 | 3294 | 3600 |

When Lehmer is in the initial population, REINFORCE *learns to prefer
identity* (3294/3600 mutations are no-ops), preserving the seeded
Lehmer elite — yielding 297 sub-Lehmer episodes (all rediscoveries of
Lehmer, REJECTED by catalog cross-check).  This is the policy
working as designed: it learned that *not mutating* Lehmer is the
high-reward action.  Random arm meanwhile drifts the population to
cyclotomic in 91 of 300 episodes.

The seeded check shows the env, reward shape, and REINFORCE policy
gradient all wire correctly — the policy *can* concentrate, the elite
*can* be preserved, and the pipeline *does* fire.  The unseeded run's
0 SHADOW_CATALOG result is therefore a finding about the
*generator-target alignment*, not an env bug.

## Comparison vs V1 baseline

| metric | V1 (uniform half-coef) | V2 (GA + REINFORCE) |
|---|---|---|
| total episodes (across seeds) | 216,000 (7 ablation cells × ~30K avg) | 18,000 (2 arms × 3 seeds × 3K) |
| best M found | n/a (M-distribution wide) | 1.0000000 (cyclotomic floor) |
| sub-Lehmer episodes | 0 | 0 |
| SHADOW_CATALOG entries | 0 | 0 |
| PROMOTE entries | 0 | 0 |
| failure mode | enumeration sparsity (band rarely hit) | elitist trap to cyclotomic |

V2's failure mode is *qualitatively* different but reaches the same
0-PROMOTE bound.  Neither generator broke the ceiling at this scale.

## Honest framing

This pilot tested **one** richer generator (GA-style population search
with mutation operators) and showed it has its own failure mode —
elitist-replacement greed pulls the population to cyclotomic, *under*
the sub-Lehmer band rather than into it.  The result does NOT
generalize to "all richer generators fail."  Specifically, two
generator families remain *untested*:

  1. **Root-space sampling.**  Sample roots on the unit circle directly,
     reconstruct the integer polynomial via the Newton identities,
     reject when the result is not a small-integer poly.  This skips
     the cyclotomic floor entirely (cyclotomics have all roots ON the
     unit circle; Salem polys have one inside-and-one-outside pair).
     The trap of v2 doesn't exist for this generator.

  2. **Salem-template construction.**  Start from a known Salem
     polynomial and apply *structure-preserving* edits (e.g., perturb
     the off-circle root by a small algebraic shift).  This is the
     analytical version of the seeded-population idea; the seeded
     pilot above is its noisy GA shadow.  A targeted-perturbation
     search rather than uniform mutation would never trip the
     cyclotomic trap.

Two future paths to test:
  * Modify v2's elitist criterion to penalize cyclotomics (e.g., keep
    elite *over* the sub-Lehmer band's lower bound) — this is a
    1-line edit to `_maybe_replace_worst`.
  * Build `discovery_env_v3.py` as the root-space sampler.

## Verdict

GA-style generator does not break the v1 ceiling at degree 10 /
population_size=8 / 12 mutations per episode / 3K episodes per (arm,
seed) — it produces a different-shaped 0 (elitist-cyclotomic-trap vs
v1's enumeration-sparsity), but the substrate-grade tally is the same.

## Files

  * Generator + env: `prometheus_math/discovery_env_v2.py`
  * Tests: `prometheus_math/tests/test_discovery_env_v2.py` (18 tests,
    18 pass)
  * Pilot driver: `prometheus_math/_run_discovery_v2_pilot.py`
  * Pilot output (unseeded, 3K × 3 seeds × 2 arms):
    `prometheus_math/_discovery_v2_pilot.json`
  * Seeded sanity check (300 ep × 1 seed × 2 arms, no pipeline):
    `prometheus_math/_discovery_v2_pilot_seeded.json`
