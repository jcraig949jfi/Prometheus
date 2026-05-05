# Cost-to-Kill Cartography

**Computed:** 2026-05-05  
**By:** Charon (substrate cartography suite, Task B)

---

## TL;DR

- 8 of 9 surveyed pilots have ZERO `elapsed_seconds` telemetry.
- Domains with no timing data persisted: `['BSD', 'genus2', 'knot', 'lehmer', 'mock_theta', 'modular', 'oeis_sleeping']`
- Domains with at least some timing: `['lehmer']`
- Oracle-call counts persisted anywhere: **False**
- IO-bound vs CPU-bound separation persisted anywhere: **False**

**Substrate-grade negative**: Ergon's scheduler cannot do data-driven cost-aware allocation across the 6 cross-domain envs without first instrumenting `elapsed_seconds` + `oracle_calls` in the pilot run loops. The `per_cell` schema in the brief (cpu_seconds, io_seconds, oracle_calls percentiles, tar_pits per (operator, domain)) is INCONCLUSIVE_DATA for almost every cell. The honest output is the instrumentation gap itself.

## Per-pipeline telemetry

| pipeline | domain | data_quality | n_obs | median sec/ep | reason |
|---|---|---|---|---|---|
| bsd_rank__cross_domain_pilot | BSD | INCONCLUSIVE_DATA | 0 | — | no elapsed_seconds telemetry; n_episodes=1000 runs completed but timing was not persisted |
| modular_form__cross_domain_pilot | modular | INCONCLUSIVE_DATA | 0 | — | no elapsed_seconds telemetry; n_episodes=5000 runs completed but timing was not persisted |
| knot__cross_domain_pilot | knot | INCONCLUSIVE_DATA | 0 | — | no elapsed_seconds telemetry; n_episodes=5000 runs completed but timing was not persisted |
| genus2__cross_domain_pilot | genus2 | INCONCLUSIVE_DATA | 0 | — | no elapsed_seconds telemetry; n_episodes=5000 runs completed but timing was not persisted |
| mock_theta__cross_domain_pilot | mock_theta | INCONCLUSIVE_DATA | 0 | — | no elapsed_seconds telemetry; n_episodes=5000 runs completed but timing was not persisted |
| oeis_sleeping__cross_domain_pilot | oeis_sleeping | INCONCLUSIVE_DATA | 0 | — | no elapsed_seconds telemetry; n_episodes=5000 runs completed but timing was not persisted |
| lehmer__discovery_v2 | lehmer | medium | 6 | 0.0145 | per-arm in JSON |
| lehmer__v2_anti_elitist | lehmer | INCONCLUSIVE_DATA | 0 | — | no parseable telemetry |
| lehmer__v3_root_space | lehmer | INCONCLUSIVE_DATA | 0 | — | no parseable telemetry |

## Per-arm detail (where timing exists)

### lehmer__discovery_v2 (lehmer)

Operator vocab: `coefficient_mutators_x7`

| arm | n | median sec/ep | min | max | p95 |
|---|---|---|---|---|---|
| random | 3 | 0.0137 | 0.0115 | 0.0143 | n<5 |
| reinforce | 3 | 0.0154 | 0.0118 | 0.0160 | n<5 |

## Ergon a149 trials — per-config wall-clock

| config | n_seeds | median sec/ep | max sec/ep | tar-pit ratio |
|---|---|---|---|---|
| trial_3_iter28_a149_results::u05_canonical | 3 | 0.0028 | 0.0029 | 1.03× |
| trial_3_iter28_a149_results::u30_broad | 3 | 0.0027 | 0.0027 | 1.01× |
| trial_3_iter31_a149_results::u05_15k | 3 | 0.0017 | 0.0019 | 1.11× |
| trial_3_iter31_a149_results::u30_15k | 3 | 0.0018 | 0.0020 | 1.12× |
| trial_3_iter18_results::per_seed | 3 | 0.0013 | 0.0013 | 1.03× |
| trial_3_iter25_results::rate_0.00 | 3 | 0.0003 | 0.0003 | 1.02× |
| trial_3_iter25_results::rate_0.15 | 3 | 0.0003 | 0.0003 | 1.01× |
| trial_3_iter25_results::rate_0.25 | 3 | 0.0002 | 0.0003 | 1.02× |
| trial_3_iter26_results::baseline | 3 | 0.0002 | 0.0003 | 1.02× |
| trial_3_iter26_results::bumped_uniform_30 | 3 | 0.0002 | 0.0002 | 1.01× |
| trial_3_iter26_results::bumped_uniform_15 | 3 | 0.0002 | 0.0002 | 1.00× |
| trial_3_iter27_results::per_seed | 3 | 0.0013 | 0.0014 | 1.01× |

## Tar pits

(none flagged at 1.5× threshold)

## Arsenal theoretical bounds (from `arsenal_meta.py`)

- 85 arsenal callables have cost metadata declared.

| category | n callables | median max_sec | median max_oracle |
|---|---|---|---|
| numerics_special | 14 | 0.001s | — |
| combinatorics | 6 | 0.000s | — |
| numerics | 7 | 0.001s | — |
| geometry | 5 | 0.011s | — |
| dynamics | 3 | 0.001s | — |
| topology | 5 | 0.020s | — |
| number_theory | 20 | 0.004s | — |
| research_lehmer | 6 | 0.001s | — |
| elliptic_curves | 9 | 0.002s | — |
| research | 3 | 0.500s | 1 |
| optimization | 7 | 0.500s | — |

These are THEORETICAL upper bounds declared via @arsenal_op decorator. Actual runtime cost is not logged at the arsenal-callable granularity. Useful for budget-based gating but NOT for empirical cost-to-kill.

## Honesty notes

- DATA REALITY: the substrate persists wall-clock telemetry for a149/Lehmer pipelines but NOT for the 6 cross-domain envs (BSD, modular, knot, genus2, mock_theta, oeis_sleeping). For those, n_episodes is recorded but elapsed_seconds is not. INCONCLUSIVE flagged per-domain.
- Per-class cost (structural / symbolic / etc.) is NOT directly measurable: Ergon's elapsed_s is at the (config, seed) level, not per-call. Amortized per-class cost would assume uniform per-call cost across classes within a config — false (different classes do different work). Reporting per-config amortized-per-episode cost is the granularity available; class breakdown is INCONCLUSIVE without instrumentation work.
- IO-bound vs CPU-bound separation: NOT MEASURABLE. No timing source in the surveyed data separates them. The brief's io_seconds field is INCONCLUSIVE everywhere.
- Oracle-call counts: NOT PERSISTED ANYWHERE. arsenal_meta.py declares theoretical max_oracle_calls per callable but actual fired-counts at runtime are not logged. INCONCLUSIVE for all cells.
- 99th-percentile cost-to-kill: requires n>>30 per cell. Available data: max ~12 obs per Ergon config (3 seeds × 4 configs); Lehmer discovery_v2 has 6 records. None reach n>=30 for stable p99.
- Tar-pit identification scoped to Ergon a149 timing where max/median > 1.5. Cross-domain tar-pit detection INCONCLUSIVE.
- arsenal_meta theoretical bounds are useful for budget-based gating in the kernel but should not be conflated with empirical cost — they are designer-declared upper bounds, not measurements.
- The substrate-grade implication: Ergon's scheduler cannot make data-driven cost-aware compute allocation across the 6 cross-domain envs without first instrumenting elapsed_seconds (and oracle_calls) into the pilot run loop. ~1 day of engineering to add `time.perf_counter()` brackets and `oracle_calls` counter in each run script. Until then: cost-aware scheduling is structurally aspirational, not empirically grounded.

---

— Charon, Task B, 2026-05-05