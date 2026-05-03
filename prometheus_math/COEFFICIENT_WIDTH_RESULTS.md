# COEFFICIENT_WIDTH_RESULTS — coefficient-set width ablation (§6.2)

Date: 2026-05-03
Spec: `harmonia/memory/architecture/discovery_via_rediscovery.md` §6.2
Harness: `prometheus_math/_run_coefficient_width_pilot.py`
Env change: `prometheus_math/discovery_env.py` — `DiscoveryEnv` now accepts
`coefficient_choices: Optional[Tuple[int, ...]]` (default `None` -> module-level
`COEFFICIENT_CHOICES = (-3..3)`, preserving full backward compatibility).
New test: `tests/test_discovery_env.py::test_authority_widened_coefficient_choices_action_space`
(27 tests, all green).

Raw JSON:
- `prometheus_math/four_counts_pilot_run_10k.json`  (baseline, ±3, 10K x 3)
- `prometheus_math/four_counts_width_5.json`        (±5, 5K x 3)
- `prometheus_math/four_counts_width_7.json`        (±7, 3K x 3)

---

## Hypothesis under test

The default coefficient alphabet `{-3, -2, -1, 0, 1, 2, 3}` (7 actions per
step, `7^6 ≈ 117K` trajectories at degree 10) might structurally exclude
entire trajectory families containing sub-Lehmer or small-Mahler
polynomials whose coefficients have absolute values 4–7. The recently-
refreshed Mossinghoff "Known180" snapshot at
`prometheus_math/databases/_mahler_data.py` grew from 178 to 8625 entries
on 2026-04-29; many higher-degree small-M Salem polynomials in that
snapshot use coefficients with |c| ≥ 4. If the alphabet is the bottleneck,
widening it should produce catalog hits that {-3..3} could not reach.

---

## Pre-flight: Known180 coefficient-magnitude distribution (8625 entries)

Counts of catalog entries with at least one coefficient of magnitude ≥ k:

| threshold k | count | fraction of catalog |
|---:|---:|---:|
| ≥ 4 | 112 | 1.30% |
| ≥ 5 |  60 | 0.70% |
| ≥ 6 |  29 | 0.34% |
| ≥ 7 |  26 | 0.30% |
| ≥ 8 |  11 | 0.13% |

`max(|coef|)` distribution across the catalog:

| max\|c\| | entries |
|---:|---:|
| 1 | 7935 (92.0%) |
| 2 |  444 |
| 3 |  134 |
| 4 |   52 |
| 5 |   31 |
| 6 |    3 |
| 7 |   15 |
| 8 |    3 |
| 9 |    2 |
| 11 |   1 |
| 13 |   1 |
| 17 |   4 |

**Critical filter on the hypothesis: the pilot uses degree 10. At
degree 10, every Known180 entry has max|c| = 1.** The 112 entries with
|c| ≥ 4 are concentrated at degree 14 and above (first deg-10 entry with
max|c| ≥ 2 has M = 1.281; max|c| stays ≤ 3 across the whole deg-10 row).

This means: even if the agent could perfectly enumerate every
deg-10 polynomial with coefficients in {-7..7}, it cannot find a new
catalog match outside what {-3..3} already covers — except via
`_check_mossinghoff`'s tolerance match, which is by Mahler measure
*value* (1e-5 tolerance), not by coefficient identity. So a deg-10
polynomial with max|c| ≥ 4 can still register as a "catalog hit" if
its M happens to coincide with a known higher-degree entry's M (rare).

The hypothesis is therefore **structurally weak at degree 10 by
construction**. Strong test would require widening degree alongside
alphabet (deferred to a future sweep).

---

## Per-width results

| width | n_actions | trajectory space (deg 10) | episodes × seeds | wall clock |
|---:|---:|---:|---:|---:|
| ±3 | 7  | 117K     | 10000 × 3 (baseline) | 45.5s |
| ±5 | 11 | 1.77M    | 5000 × 3            | 59.8s (26.8s + 33.0s) |
| ±7 | 15 | 11.4M    | 3000 × 3            | 35.3s (16.4s + 18.9s) |

### PROMOTE rate (random + REINFORCE)

| width | random_null | reinforce_agent | combined episodes | combined PROMOTEs |
|---:|---:|---:|---:|---:|
| ±3 | 0 / 30000 | 0 / 30000 | 60000 | **0** |
| ±5 | 0 / 15000 | 0 / 15000 | 30000 | **0** |
| ±7 | 0 / 9000  | 0 / 9000  | 18000 | **0** |

**0 PROMOTEs across all three widths, both arms, 108,000 cumulative episodes.**

### Catalog-hit episodes

| width | random catalog hits | reinforce catalog hits | hits with max\|c\| ≥ 4 |
|---:|---:|---:|---:|
| ±3 | 32 / 30000 (0.107%) | 0 / 30000 (0.000%) | n/a |
| ±5 |  1 / 15000 (0.007%) | 0 / 15000           | **0** |
| ±7 |  0 /  9000          | 0 /  9000           | **0** |

The catalog-hit rate **drops** as the alphabet widens — exactly as
expected, because the trajectory space expands quadratically while
the high-density Salem cluster (which is dominated by small-coefficient
polynomials) does not. A uniform sampler over a 1.77M-trajectory space
is much less likely to land in the Salem cluster than one over a 117K
space.

### Salem-cluster proxy (random / reinforce)

| width | random Salem | reinforce Salem | concentration ratio |
|---:|---:|---:|---:|
| ±3 | 35 / 30000 (0.117%) | 19,855 / 30000 (66.18%) | 567x |
| ±5 | 26 / 15000 (0.173%) |     0 / 15000 (0.00%)    | INVERTED — REINFORCE never visits the cluster |
| ±7 |  1 /  9000 (0.011%) |     0 /  9000            | INVERTED |

REINFORCE **completely loses the Salem-cluster signal** at the wider
alphabets. With more actions, gradient signal per action is diluted; the
+20 Salem-cluster reward is diluted across ~11x or ~15x as many policy
weights, and entropy regularisation prevents convergence onto any
narrow basin within the 5K (resp. 3K) episode budget.

### Random-null kill pattern by reward-label band

| width | functional ([2, 5)) | cyclotomic_or_large | low_m ([1.5, 2)) | salem_cluster ([1.18, 1.5)) |
|---:|---:|---:|---:|---:|
| ±3 | 26027 | 3325 | 581 | 35 |
| ±5 |  4151 | 10822 | 26 | 0 (cluster falls into upstream:salem_cluster: 0; one cat-hit) |
| ±7 |   589 | 8410  |  1 | 0 |

The mass shifts from "functional" (M ∈ [2, 5)) to "cyclotomic_or_large"
(M ≈ 1 or M ≥ 5) as the alphabet widens — at width ±7, the typical
random palindromic polynomial has Mahler measure either very close to
1 (lots of cancellation) or very large (≥ 5). The interior bands
collapse almost entirely.

### Welch one-sided p-values (PROMOTE rate)

All three widths have both arms tied at zero:
- ±3: NaN (variance zero)
- ±5: NaN (variance zero)
- ±7: NaN (variance zero)

No statistical separation possible. The 0-PROMOTE ceiling is the
joint upper bound across all three widths.

### Per-seed mode-collapse check

| width | arm | seed 0 | seed 1 | seed 2 |
|---:|---|---:|---:|---:|
| ±5 | random_null     | 0 cat-hit | 0 cat-hit | 1 cat-hit |
| ±5 | reinforce_agent | 0 cat-hit | 0 cat-hit | 0 cat-hit |
| ±7 | random_null     | 0         | 0         | 0         |
| ±7 | reinforce_agent | 0         | 0         | 0         |

No per-seed mode-collapse signature (unlike the deg-12 sweep where one
seed locked onto one polynomial). All seeds tied at zero PROMOTE.

### SHADOW_CATALOG entries

**Zero entries at every width.** No CLAIM ever entered the kernel
because the +100 sub-Lehmer band (M ∈ (1.001, 1.18)) was never reached.

### The single catalog-hit at ±5

`run_random_null` seed 2, episode 1095:

```
coeffs = [-1, 3, -3, 1, 1, -2, 1, 1, -3, 3, -1]
M = 1.4012683852737824   (Salem-cluster band)
max |c| = 3              <-- structurally reachable by ±3 alphabet
```

`max|c| = 3` — this polynomial would have been reachable by the
{-3..3} alphabet too. **Zero catalog hits at any width came from
polynomials the {-3..3} alphabet was structurally excluding.**

---

## Verdict on the alphabet hypothesis

**The alphabet hypothesis is rejected at degree 10.**

Three concrete reasons:

1. **Pre-flight ruled it out structurally.** All Known180 deg-10
   entries have max|c| = 1. The wider alphabet has nothing new to
   discover at this degree — at most it could match a high-degree
   entry's M-value via tolerance, but that's not what "alphabet was
   the bottleneck" means.

2. **Catalog-hit density dropped, not rose.** Random catalog-hit
   rate fell from 0.107% (±3) → 0.007% (±5) → 0.000% (±7), exactly
   the dilution pattern expected when widening a non-bottleneck
   alphabet. If the alphabet had been the bottleneck, hit rate
   should have *risen* with width.

3. **The one ±5 hit had max|c| = 3.** Reachable from ±3.

## Did the wider alphabet break the 0-PROMOTE ceiling?

**No.** 0/108,000 PROMOTEs across {-3..3, -5..5, -7..7}. The structural
ceiling is not at the alphabet — it's at the +100 sub-Lehmer band itself
(empirically near-empty at degree 10, consistent with Lehmer's
conjecture).

## Honest caveats

- **Degree 10 is the wrong test bed for this hypothesis.** The
  alphabet question only bites at degree ≥ 14, where Known180 has
  entries with max|c| ≥ 4. A future sweep should pair widening
  alphabet with raising degree (e.g., degree 14 × {-5..5}) to give
  the hypothesis a fair test.
- **The sibling shaped-reward experiment is orthogonal to this
  result.** Verdict on shaped-vs-step reward requires its own data;
  this pilot is on the default `reward_shape="step"` only.
- **3K episodes at ±7 may not be enough for REINFORCE to converge.**
  Trajectory space is 11.4M; 3K episodes visits ~0.026% of it.
  REINFORCE looking flat at ±7 is partly under-budget and not
  necessarily a permanent failure mode. (The 0-PROMOTE ceiling
  holds either way — REINFORCE cannot promote what it cannot
  reach; widening the alphabet did not put any new sub-Lehmer
  polynomials into reach at degree 10.)
