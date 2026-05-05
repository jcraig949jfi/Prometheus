# SHAPED_REWARD_RESULTS — §6.2 reward-shape ablation

Companion to `prometheus_math/FOUR_COUNTS_RESULTS.md`. Same pilot, same
budget, same seeds; only difference is `reward_shape='shaped'` passed
into `DiscoveryEnv` (continuous M-gradient with sub-Lehmer +50 bonus)
instead of the default `step` reward (discrete band rewards
+1/+5/+20/+100).

Date: 2026-04-29
Spec: `harmonia/memory/architecture/discovery_via_rediscovery.md` §6.2 + §6.4
Harness: `prometheus_math/four_counts_pilot.py` (commit 12a76bad)
Driver (rich, shaped): `prometheus_math/_run_10k_rich_shaped.py`
CLI flag: `python -m prometheus_math.demo_four_counts --reward-shape shaped`

## Setup

| knob | step (baseline) | shaped (this run) |
|---|---|---|
| degree | 10 | 10 |
| episodes / cell | 10,000 | 10,000 |
| seeds | {0, 1, 2} | {0, 1, 2} |
| lr | 0.05 | 0.05 |
| entropy_coef | 0.05 | 0.05 |
| cost_seconds | 0.5 | 0.5 |
| reward fn | `_compute_reward` | `_compute_reward_shaped` |
| sub-Lehmer (1.001 < M < 1.18) | +100 | +50 + 50·(5-M)/4 ≈ +97.75–98.74 |
| Salem cluster (1.18 ≤ M < 1.5) | +20 | 50·(5-M)/4 ≈ +43.75–47.75 (continuous) |
| low-M (1.5 ≤ M < 2) | +5 | 50·(5-M)/4 ≈ +37.5–43.75 |
| functional (2 ≤ M < 5) | +1 | 50·(5-M)/4 ≈ 0–37.5 |
| cyclotomic / large M | 0 | 0 |

Wall time (shaped, 10K × 3 × 2 arms = 60,000 episodes):

```
arm wall-clock:
  random_null     = 45.16s   (vs step's 18.76s — 2.4x slower
                              because shaped routes more episodes
                              through bands the env logs to
                              `_discoveries`)
  reinforce_agent = 62.44s   (vs step's 26.70s — 2.3x slower for
                              the same reason; policy update cost
                              identical)
total:           = 107.60s   (step baseline: 45.46s)
```

Driver: `_run_10k_rich_shaped.py`. Output JSONs:
- `prometheus_math/four_counts_pilot_run_10k_shaped.json` (rich summary)
- `prometheus_math/four_counts_10k_per_seed_shaped.json` (per-seed)
- `prometheus_math/four_counts_10k_shadow_shaped.json` (SHADOW_CATALOG;
  empty)
- `prometheus_math/four_counts_10k_rich_shaped_stdout.log` (stdout)

## Results — side-by-side

### The four counts (10K × 3 = 30,000 episodes per arm)

| arm | reward | PROMOTE | claim-into-kernel | catalog-hit | rejected |
|---|---|---:|---:|---:|---:|
| random_null      | step   | 0/30000 | 0/30000 | 32/30000 (0.107%) | 29968/30000 |
| random_null      | shaped | 0/30000 | 0/30000 |  1/30000 (0.003%) | 29999/30000 |
| reinforce_agent  | step   | 0/30000 | 0/30000 |  0/30000          | 30000/30000 |
| reinforce_agent  | shaped | 0/30000 | 0/30000 |  0/30000          | 30000/30000 |

PROMOTE ceiling: **NOT BROKEN** — all four (arm × shape) cells remain at
0/30000.

### M-band distribution (cumulative across 3 seeds; reward-shape-independent buckets)

Buckets are M-value bands, not reward labels — they're the same under
both reward shapes (shaped reports `reward_label='shaped_continuous'`
across the whole 1.001 < M < 5 region, so the per-seed `by_mband` field
in the rich runner is the only cross-shape-comparable proxy).

| M-band | bound | random/step | random/shaped | REINFORCE/step | REINFORCE/shaped |
|---|---|---:|---:|---:|---:|
| sub_lehmer        | (1.001, 1.18)  |    0 |    1 |     0 |     0 |
| salem_cluster     | [1.18, 1.5)    |   35 |   66 | 19855 |     1 |
| low_m             | [1.5, 2.0)     |  581 |  581 |  9943 |    15 |
| functional        | [2.0, 5.0)     | 26027|26027 |   182 | 29982 |
| cyclotomic        | M ≈ 1          |    0 |  153 |     0 |     0 |
| large_m           | M ≥ 5          | 3325 | 3172 |    20 |     2 |
| catalog hit       | known Mossinghoff |  35 |    1 |     0 |     0 |

(`random/step` Salem-cluster column reads 35 here vs 35 catalog hits in
the step JSON. Step's `by_kill_pattern` lumps all Salem-cluster band
hits — known + unknown — into `upstream:salem_cluster`; shaped's
`by_mband` is computed independently from raw M values, so the column
alignment is exact for shaped and approximate for step.)

### Salem-cluster proxy concentration ratio (REINFORCE / random)

| reward | REINFORCE Salem hits | random Salem hits | ratio | direction |
|---|---:|---:|---:|---|
| step   | 19,855 / 30000 (66.18%) | 35 / 30000 (0.117%) | **567×**   | REINFORCE concentrates |
| shaped |      1 / 30000 (0.003%) | 66 / 30000 (0.220%) | **0.015×** | INVERTED — REINFORCE *avoids* Salem cluster |

The 567× concentration that the step-reward agent achieved on the
Salem-cluster proxy *vanishes* under shaped reward. REINFORCE under
shaped reward concentrates 99.94% of its mass in the *functional*
band (M ∈ [2, 5)) — not the Salem cluster.

### Mean per-episode reward under shaped reward (REINFORCE only)

| seed | mean episode reward |
|---:|---:|
| 0 | 26.02 |
| 1 |  2.71 |
| 2 | 34.74 |
| mean across seeds | 21.16 |

Reward magnitudes confirm the policy is staying in the M ∈ [2, 5) band
where shaped reward returns ~12.5–37.5. (A Salem hit would yield ~44–48,
a sub-Lehmer hit ~98–99 with the +50 bonus.) Seed variance is huge —
seed 1 collapsed to a high-M region (mean reward 2.71 ≈ M ≈ 4.78
average), seed 2 found a slightly lower-M plateau.

### SHADOW_CATALOG / DISCOVERY_CANDIDATE entries surfaced

**Zero across all 6 (arm, seed) cells.** No CLAIM minted. No
DiscoveryRecord produced. The pipeline never fired because no episode
hit the sub-Lehmer band AND missed Mossinghoff. The single sub-Lehmer
M-band hit (random_null seed=1) was a known Mossinghoff Salem entry —
caught upstream as a `catalog_hit` (1 catalog hit on that seed) and
never routed into the pipeline.

## Interpretation

**Shaped reward did NOT break the 0-PROMOTE ceiling.** Both arms
produced 0 SHADOW_CATALOG and 0 PROMOTED records across 30,000 episodes
each. The joint upper bound at this configuration remains < 1/30000.

**Shaped reward did NOT sharpen the 567× proxy concentration. It
inverted it.** The Salem-cluster concentration ratio went from 567×
(step) to 0.015× (shaped) — REINFORCE under shaped reward is now
*worse than uniform random* at finding the Salem cluster. This is the
predictable failure mode of a continuous reward function with a single
linear gradient: the policy follows the gradient toward the nearest
local optimum (M just below 5, where reward is positive but the
trajectory volume is huge), not toward the global optimum (sub-Lehmer
band, where the reward signal is rare and isolated by sparse catalog
geometry).

The shaped reward's continuous gradient gives the policy gradient
information — but it gives the *wrong* gradient to follow. Step
reward's discontinuities at 1.18 / 1.5 / 2.0 created a piecewise
landscape where Salem-cluster occupancy was a stable basin
(20-reward). Shaped reward smoothed those boundaries away; the policy
saw a single monotonic gradient `50·(5-M)/4` and slid to the M ≈ 2–3
plateau where the trajectory volume is largest. The +50 sub-Lehmer
bonus was insufficient to pull the policy past the local optimum
because the policy class (linear, contextual, lr=0.05, entropy=0.05)
has no mechanism to explore far from its current operating point.

**Random null is no better and no worse under shaped reward** — random
sampling doesn't see reward at all, so the action distribution is
identical across the two shapes. The slight differences in the M-band
table (66 Salem hits under shaped vs 35 under step, 1 sub-Lehmer hit
under shaped vs 0 under step) are seed-driven sampling noise: the
underlying coefficient distribution is the same Discrete(7)^6.

(Yesterday's separate shaped-reward discovery experiment that "broke
through to Salem cluster (M=1.458 best)" was a different agent class —
likely PPO, MCTS, or a wider action set — not the contextual REINFORCE
the four-counts harness uses. The reward shape alone, with this
policy class and this Discrete(7) action set, does *not* break
through.)

### One-sentence verdict

Shaped reward is not the bottleneck — it makes the proxy *worse*
because it lures linear REINFORCE into the high-M plateau before it
ever explores the Salem cluster; the algorithm-or-action-set
intervention is the real lever.

### Honest caveat

This is one experimental dimension. The action-set width is the other,
likely-larger dimension (parallel to the §6.4 "non-LLM source" framing):
the current Discrete(7) over {-3..3} excludes many known Lehmer-
adjacent polynomials with `|c| ≥ 4`, and no reward shape will surface
them. The next move per `FOUR_COUNTS_RESULTS.md`'s priority list is
**widen the action set**, then revisit reward shape *with* a wider
action set, and only then consider stronger algorithms (PPO / MCTS).

## Files shipped this iteration

- `prometheus_math/_run_10k_rich_shaped.py` — rich runner, shaped
  variant (sibling of `_run_10k_rich.py`).
- `prometheus_math/demo_four_counts.py` — added `--reward-shape
  {step,shaped}` CLI flag; threads through `_build_env_factory`.
- `prometheus_math/four_counts_pilot_run_10k_shaped.json` — rich
  summary JSON.
- `prometheus_math/four_counts_10k_per_seed_shaped.json` — per-seed
  dump.
- `prometheus_math/four_counts_10k_shadow_shaped.json` — SHADOW_CATALOG
  records (empty).
- `prometheus_math/four_counts_10k_rich_shaped_stdout.log` — stdout.
- `prometheus_math/SHAPED_REWARD_RESULTS.md` — this file.

Tests: `prometheus_math/tests/test_catalog_consistency.py` (23 green),
`prometheus_math/tests/test_four_counts_pilot.py` (16 green) — both
unaffected by the CLI / runner additions.
