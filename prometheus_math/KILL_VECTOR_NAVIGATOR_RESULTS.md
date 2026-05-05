# Kill-Vector Navigator — Day 5 Results

**Date:** 2026-05-04
**Module:** `prometheus_math/kill_vector_navigator.py` (~600 LOC)
**Tests:** `prometheus_math/tests/test_kill_vector_navigator.py` (18 tests, all passing)
**Verdict:** **B** — margin mode validated *only* on the deg14 ±5 step
DiscoveryEnv region; the other 6 regions are categorical-only and the
categorical signal is known-uninformative there.

---

## Setup

The navigator is the substrate's first explicit policy primitive: given
a region (degree, alphabet_width, reward_shape, env), return a ranked
list of operators by *expected kill magnitude* (lower-is-better). It
ships behind a stable `recommend()` API so future native pilots in
new regions plug in without changing consumers.

Two-mode policy, dispatched per-region:

* **margin mode** ranks operators by
  E[‖kill_vector‖_margin | region, operator] using
  `KillVector.magnitude(unit_aware=True)` — the squashed-L2 over
  triggered components. Driven by *native pilot* records that carry
  real, continuous margins.
* **categorical mode** ranks operators by E[triggered_count |
  region, operator] using legacy archaeology aggregates. This is the
  fallback when no native data is available for a region.

Why two modes? The 2026-05-04 native pilot (deg14 ±5 step env, 24K
episodes) measured **126,983×** more pairwise distinguishability
between operators in margin space than in categorical space (KL=4.4e-2
vs KL=3.5e-7). On the legacy ledger 99.9% of the categorical mass sits
in `out_of_band`, which collapses operator distinguishability to
noise. Margin mode exploits the continuous near-miss signal that
categorical throws away.

In auto mode the navigator returns margin-mode rankings whenever
native data is available, and falls back to categorical otherwise.

---

## Coverage

* **Sources loaded:** `_native_kill_vector_pilot.json`,
  `_gradient_archaeology_results.json`
* **Total regions:** 8
* **Regions with margin data:** **2** (`DiscoveryEnv|deg14|w5|step`,
  `DiscoveryEnvV2|deg14|w5|step` — both from the 2026-05-04 native
  pilot)
* **Categorical-only regions:** 6

| Region                                 | Modes               | n_operators | n_records (margin / categorical) |
|----------------------------------------|---------------------|-------------|----------------------------------|
| `DiscoveryEnv\|deg14\|w5\|step`        | margin, categorical | 3           | 18000 / 18000                    |
| `DiscoveryEnvV2\|deg14\|w5\|step`      | margin, categorical | 1           | 6000 / 6000                      |
| `discovery_pipeline\|deg14\|w5\|step`  | categorical         | 5           | 0 / 73931                        |
| `four_counts\|deg10\|w5\|shaped`       | categorical         | 2           | 0 / 59999                        |
| `four_counts\|deg10\|w5\|step`         | categorical         | 2           | 0 / 89967                        |
| `four_counts\|deg10\|w7\|step`         | categorical         | 2           | 0 / 18000                        |
| `four_counts\|deg12\|w5\|step`         | categorical         | 2           | 0 / 25074                        |
| `four_counts\|deg14\|w5\|step`         | categorical         | 2           | 0 / 48000                        |

The native pilot's `ga_elitist_v2` records were emitted under
`DiscoveryEnvV2`, so they sit in a separate region from the
`DiscoveryEnv` (V1) records that house `ppo_mlp`, `reinforce_linear`,
and `random_uniform`. The two are *not* directly comparable through
the navigator because they describe different envs; ranking happens
within a region by design.

---

## Top-3 recommendation per region

### Native-data regions (margin mode authoritative)

#### `DiscoveryEnv|deg14|w5|step` — the canonical native-pilot region

**Margin mode (auto):**

| # | Operator           | E[‖k‖]   | 95% CI             | n_episodes |
|---|--------------------|----------|--------------------|------------|
| 1 | `ppo_mlp`          | 0.3632   | [0.3562, 0.3720]   | 6000       |
| 2 | `random_uniform`   | 0.8375   | [0.8365, 0.8388]   | 6000       |
| 3 | `reinforce_linear` | 0.8630   | [0.8622, 0.8638]   | 6000       |

**Categorical mode (legacy fallback semantics):**

| # | Operator           | E[#triggered] | 95% CI             | n_episodes |
|---|--------------------|---------------|--------------------|------------|
| 1 | `ppo_mlp`          | 0.9972        | [0.9955, 0.9985]   | 6000       |
| 2 | `random_uniform`   | 1.0000        | [1.0000, 1.0000]   | 6000       |
| 3 | `reinforce_linear` | 1.0000        | [1.0000, 1.0000]   | 6000       |

The two modes **agree on the rank order** (PPO < random < REINFORCE),
but the *spread* is materially different: 0.4998 in margin (PPO sits
half a unit below the others) vs 0.0028 in categorical (all three
saturate at one triggered component each, the dominant `out_of_band`
kill).

This matches the headline pilot finding. Mean raw margins:
PPO=+1.08 (touched the band, min -0.001); random=+5.58; REINFORCE=+6.69.
Squashed via the unit-aware `m / (m + 1)` map this becomes 0.36 / 0.84
/ 0.86. The categorical view *cannot* see this because all three are
killed by the same falsifier (`out_of_band`).

#### `DiscoveryEnvV2|deg14|w5|step`

| # | Operator         | E[‖k‖]   | 95% CI             | n_episodes | Notes                                              |
|---|------------------|----------|--------------------|------------|----------------------------------------------------|
| 1 | `ga_elitist_v2`  | 0.7526   | [0.7512, 0.7541]   | 6000       | single operator in region — no comparative ranking |

GA_elitist_v2 lives under DiscoveryEnvV2, so within its own region it
has no peers to rank against. Its mean raw margin is +3.18 (between
PPO and random in the V1 env), squashed to 0.7526.

### Categorical-only regions (legacy fallback)

In each of these regions categorical mode reports E[#triggered]
≈ 1.0 with effectively zero spread — the legacy ledger only records
the *first-failing* falsifier, so triggered_count is always 1, and the
CI collapses. The recommendation is alphabetic by tie-break.

| Region                                 | top-1                   | top-2              |
|----------------------------------------|-------------------------|--------------------|
| `discovery_pipeline\|deg14\|w5\|step`  | `random_seeded`         | `random_uniform`   |
| `four_counts\|deg10\|w5\|shaped`       | `random_null`           | `reinforce_agent`  |
| `four_counts\|deg10\|w5\|step`         | `random_null`           | `reinforce_agent`  |
| `four_counts\|deg10\|w7\|step`         | `random_null`           | `reinforce_agent`  |
| `four_counts\|deg12\|w5\|step`         | `random_null`           | `reinforce_agent`  |
| `four_counts\|deg14\|w5\|step`         | `random_null`           | `reinforce_agent`  |

These rankings are **not navigationally meaningful**: the categorical
distinguishability is the very signal Day 4 showed is decorative. The
navigator returns them because the API contract is "give me a ranking
in this region", but the consumer should treat these regions as
"navigation undefined; awaiting native data".

---

## Calibration (margin vs categorical, where both modes are present)

| Region                            | margin top-1     | categorical top-1 | agree top-1 | Kendall τ | Notes                                          |
|-----------------------------------|------------------|-------------------|-------------|-----------|------------------------------------------------|
| `DiscoveryEnv\|deg14\|w5\|step`   | `ppo_mlp`        | `ppo_mlp`         | yes         | +1.000    | Same rank order, *very* different spread       |
| `DiscoveryEnvV2\|deg14\|w5\|step` | `ga_elitist_v2`  | `ga_elitist_v2`   | yes         | 0.000     | One operator, no τ defined                     |

**n_top1_disagree = 0 / 2.** The two modes don't disagree on *which*
operator wins — they disagree on *how much*. In `DiscoveryEnv`, margin
mode reports a 0.4998-unit gap between PPO and random; categorical
reports a 0.0028-unit gap. This is the operationally meaningful
difference: a downstream sampler that allocates budget proportional
to the gap will route ~178× more attention to PPO in margin mode than
in categorical mode.

The calibration view is consistent with the native pilot's
distinguishability number (KL=4.4e-2 in margin vs KL=3.5e-7 in
categorical, a 126,983× ratio): margin and categorical agree on
*direction*, but the *signal-to-noise* is orders of magnitude better
in margin space.

---

## Verdict: **B — deg14 ±5 step validation only**

The 2026-05-04 native pilot validated margin-mode ranking on **one
underlying env config (deg14, alphabet width 5, step reward)**, split
across two region keys (V1: 3 algorithms; V2: ga_elitist_v2). On every
other region the navigator falls back to categorical, where the signal
is known to be near-zero.

* **Verdict A (margin works everywhere):** ruled out — only 2 / 8
  regions have margin data.
* **Verdict B (margin works on the validated region; others wait):**
  matches the empirical state of the artifacts.
* **Verdict C (calibration bug):** ruled out — within the validated
  region, margin and categorical agree on the top-1 winner; they
  disagree on *spread*, exactly as the pilot's distinguishability
  measurement predicted.

This is the right shape: the navigator ships now as a usable policy
primitive (PPO is the validated recommendation for the deg14 ±5 step
env), while every other region gets a categorical fallback that
self-flags as low-information until a native pilot reaches it.

### Operational implication

The navigator is **usable today** as the substrate's policy primitive
for the one region where the native pilot landed; for all other
regions, this same module re-ranks automatically as new native pilots
emit `KillVector` records. No consumer code needs to change as more
margin data accrues.

---

## Files

* `prometheus_math/kill_vector_navigator.py` — module
* `prometheus_math/tests/test_kill_vector_navigator.py` — 18 tests
  (3 authority + 4 property + 5 edge + 4 composition + 2 helper)
* `prometheus_math/_native_kill_vector_pilot.json` — input (24K
  episodes, 4 algorithms, 3 seeds)
* `prometheus_math/_gradient_archaeology_results.json` — input (legacy
  aggregates over 6 regions)
