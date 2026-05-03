# DEGREE_SWEEP_RESULTS — Triple #2: widen the polynomial degree

Spec: replace #2 of the just-finished triple. Stream A's 10K pilot showed
PROMOTE rate is 0/30000 at degree 10. The hypothesis was that widening
the polynomial degree gives the search more polynomial-root real estate,
which would (a) move PROMOTE rate off zero, or at minimum (b) tighten
proxy concentration further.

Driver: `prometheus_math/_run_degree_sweep.py`
Raw JSON: `prometheus_math/degree_sweep_results.json`
Shadow records JSON: `prometheus_math/degree_sweep_shadow.json` (empty)
Stdout: `prometheus_math/degree_sweep_stdout.log`

Date: 2026-04-29.

---

## Configuration

| degree | half_len | trajectory_space | episodes/cell | seeds | total cells |
|---:|---:|---:|---:|---:|---:|
| 10 (baseline; FOUR_COUNTS 10K run) | 6 | 117,649 | 10,000 | 3 | 6 |
| 12 (this run) | 7 | 823,543 | 5,000 | 3 | 6 |
| 14 (this run) | 8 | 5,764,801 | 3,000 | 3 | 6 |

Other params held constant: `cost_seconds=1.0`, `lr=0.05`,
`entropy_coef=0.05`, action set Discrete(7) over coefficients
{-3, -2, -1, 0, 1, 2, 3}, palindromic constraint, full DiscoveryPipeline
on candidates that hit the sub-Lehmer band.

Total wall time for degree 12 + degree 14 sweep: **36.2 s** (well
under the 30-min cap; per-episode time at degree 14 is only 1.13x
slower than degree 10, contradicting the worry that companion-matrix
eigval cost would dominate).

---

## Step 1 — Per-episode wall time

Benchmark via uniform-random rollouts, after warm-up:

| degree | per-episode (ms) | est 5K x 3 seeds | est 10K x 3 seeds |
|---:|---:|---:|---:|
| 10 | 0.580 | 8.7 s | 17.4 s |
| 12 | 0.598 | 9.0 s | 17.9 s |
| 14 | 0.678 | 10.2 s | 20.3 s |

The companion-matrix `O(d^3)` cost is real but tiny in absolute terms
at these degrees — `mahler_measure` evaluation is a small fraction of
the per-step BIND/EVAL substrate overhead. **Wall-time scaling is NOT
the bottleneck.** This decisively refutes the hypothesis that degree
14 is "too slow at 3K x 3 seeds" — we could comfortably run degree 14
at 50K x 3 seeds within the 30-min budget if the structural ceiling
demanded it.

---

## Step 2 — PROMOTE rates and four-counts table

### Headline (mean over 3 seeds; both arms)

| degree | random_null PROMOTE | reinforce_agent PROMOTE | random cat-hit | reinforce cat-hit |
|---:|---:|---:|---:|---:|
| 10 (baseline) | **0/30000** | **0/30000** | 32 (0.107%) | 0 (0%) |
| 12 (this run) | **0/15000** | **0/15000** | 11 (0.073%) | 4915 (32.77%) |
| 14 (this run) | **0/9000** | **0/9000** | 0 (0%) | 0 (0%) |

The PROMOTE column is the load-bearing signal: **0 across all 78,000
episodes total** (60K at degree 10 + 30K at degree 12 + 18K at degree 14).
Widening the degree did not break the structural ceiling.

### Salem-cluster proxy concentration (kill_pattern = `upstream:salem_cluster`)

| degree | random_null Salem | reinforce_agent Salem | concentration ratio |
|---:|---:|---:|---:|
| 10 (baseline 10K x 3) | 35 / 30000 = 0.117% | 19,855 / 30000 = 66.18% | **567x** |
| 12 (5K x 3) | 21 / 15000 = 0.140% | 4,904 / 15000 = 32.69% | **234x** |
| 14 (3K x 3) | 8 / 9000 = 0.089% | 1 / 9000 = 0.011% | **0.13x (inverted)** |

This is the most significant empirical result of the sweep. The
Salem-cluster proxy concentration **monotonically degrades** as degree
widens: the policy's ability to steer into the proxy band collapses
from 567x (degree 10) → 234x (degree 12) → **inverted 0.13x at
degree 14** (REINFORCE produces *fewer* Salem-band hits than the
uniform-random null). At degree 14 the policy isn't just losing the
Salem cluster — the policy is *worse than random* at hitting it.

That is the **worst-case outcome** the brief flagged: "higher degree
expands the search space FASTER than the policy can navigate it —
argues for stronger algorithms (PPO, MCTS) before more degrees."
The empirical answer is: yes, that's exactly what's happening.

---

## Step 3 — Per-seed detail and degree-12 mode-collapse note

### Degree 12 — reinforce_agent, per seed

| seed | catalog_hit | salem_cluster | rejected | elapsed |
|---:|---:|---:|---:|---:|
| 0 | 0 | (in 5116 functional + 45 cyclo + 20 low_m bands) | 5000 | 4.12s |
| 1 | 0 | (in 5116 functional + 45 cyclo + 20 low_m bands) | 5000 | 4.22s |
| 2 | **4915** | **4904** | 85 | 4.90s |

Seeds 0 and 1 ran the policy out of the Salem cluster band entirely
(the policy collapsed onto large-M / cyclotomic regions). Seed 2 is
the *opposite* failure mode: the policy locked onto a single Salem
cluster polynomial and produced 4915 catalog-hits — meaning it kept
re-emitting the same known Mossinghoff polynomial 4915 / 5000 = 98.3%
of the time. **This is mode-collapse, not concentration improvement.**

The 234x concentration ratio at degree 12 is therefore misleading at
the population level: it's not 32% of episodes spreading across the
Salem cluster, it's **one seed memorising one entry**. Without that
single seed the Salem-cluster total at degree 12 would be 0 episodes
out of 10,000 — strictly *worse* than degree 10's distributed
concentration.

### Degree 14 — full collapse

All six (degree 14, condition, seed) cells produced **zero** catalog
hits and ≤ 8 Salem-cluster hits each. The policy explored almost
exclusively the `upstream:functional` (M ∈ [2, 5)) band:

| label | functional | cyclotomic_or_large | low_m | salem_cluster |
|---:|---:|---:|---:|---:|
| random_null (9000 ep) | 6799 | 2158 | 35 | 8 |
| reinforce_agent (9000 ep) | 8908 | 76 | 15 | 1 |

REINFORCE successfully avoids large-M and the cyclotomic boundary
(76 vs 2158 for random) — it has learned *something* about M-shape —
but cannot find the Salem cluster band at all. The trajectory space
expanded 49x from degree 10 (117K → 5.76M) and the policy class
(linear softmax in obs) cannot navigate that space with reward shape
sparse enough that <1/9000 episodes touched the Salem cluster.

---

## SHADOW_CATALOG entries surfaced

**Zero across all degrees and seeds.**

`prometheus_math/degree_sweep_shadow.json` reports `count: 0`. No
candidate hit the strict sub-Lehmer band (M ∈ (1.001, 1.18)), so the
DiscoveryPipeline minted no CLAIMs and produced no SHADOW_CATALOG /
PROMOTED records. The structural ceiling is unbroken.

---

## Verdict

**Did widening the polynomial degree alone break the 0-PROMOTE
ceiling?** **No.**

Worse than no: the proxy concentration *degrades* with degree — 567x
(degree 10) → 234x (degree 12, mode-collapse-inflated) → inverted at
degree 14 (REINFORCE worse than random). The data falsifies the
"need more real estate" hypothesis cleanly: at degree 14 there are
49x more polynomials to find than at degree 10, but the policy class
+ reward shape jointly cannot exploit that real estate. Returns are
not just diminishing — they are negative.

This is the brief's **worst-case middle ground**: PROMOTE rate stays
0 AND proxy concentration weakens at higher degree. The implication
is direct: **the structural intervention required is on the
algorithm / reward / action-set axis, not the degree axis.** Specifically:

1. **Action set width.** Many known Lehmer-adjacent polynomials need
   `|c| >= 4`; Discrete(7) on {-3..3} permanently excludes them.
   Trying Discrete(11) on {-5..5} or Discrete(15) on {-7..7} is the
   most direct intervention.

2. **Stronger algorithms.** Linear-softmax REINFORCE cannot navigate
   the degree-14 trajectory space with the current reward sparsity.
   PPO or MCTS over the trajectory tree would be the next step.

3. **Reward shape.** The `shaped` variant (`reward_shape="shaped"`)
   provides a continuous gradient toward low M; that variant was not
   tested here. Re-running the sweep under `reward_shape="shaped"`
   would isolate whether the issue is sparse-reward or
   action-set/policy-class.

4. **Battery loosening.** The 0/30K + 0/15K + 0/9K joint result at
   the kernel boundary suggests the F1/F6/F9/F11 thresholds may also
   be over-tightened — but the empirical signal here is that nothing
   makes it INTO the kernel. The battery cannot be the bottleneck if
   the upstream filter has already rejected everything.

**One-line verdict for the report:** widening the polynomial degree
expanded the trajectory space 49x but the policy class collapsed
faster than the space grew — the structural ceiling is binding on
algorithm/action-set, not degree.

---

## Test posture

The DiscoveryEnv default-degree=10 test posture is unchanged. The
sweep instantiates the env at non-default degrees explicitly via the
`degree` kwarg; no env defaults were touched. `pytest
prometheus_math/tests/test_discovery_env.py` and
`prometheus_math/tests/test_four_counts_pilot.py` should both stay green.

(See pivot stack confirmation at the end of this iteration.)
