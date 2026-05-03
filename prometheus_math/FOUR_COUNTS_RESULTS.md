# FOUR_COUNTS_RESULTS — §6.2 + §6.4 Pilot

Spec: `harmonia/memory/architecture/discovery_via_rediscovery.md` §6.2 + §6.4
Harness: `prometheus_math/four_counts_pilot.py` (commit f42a2c30)
Driver (basic): `prometheus_math/demo_four_counts.py`
Driver (rich, per-seed + shadow capture): `prometheus_math/_run_10k_rich.py`
Tests: `prometheus_math/tests/test_four_counts_pilot.py` (16 tests, all green)

## Runs catalogued here

| run | date | degree | episodes/cell | seeds | wall-clock | promote rate | doc tag |
|---|---|---:|---:|---:|---:|---:|---|
| pilot 1K | 2026-04-29 | 10 | 1,000 | 3 |   4.3s | 0/3000 | initial |
| pilot 10K | 2026-04-29 | 10 | 10,000 | 3 |  45.5s | 0/30000 | original 10K |
| degree 12 | 2026-04-29 | 12 | 5,000 | 3 |  22.5s | 0/15000 | DEGREE_SWEEP |
| degree 14 | 2026-04-29 | 14 | 3,000 | 3 |  13.7s | 0/9000  | DEGREE_SWEEP |
| pilot 10K shaped | 2026-04-29 | 10 | 10,000 | 3 | 107.6s | 0/30000 | SHAPED_REWARD |
| width ±5  | 2026-05-03 | 10 |  5,000 | 3 |  59.8s | 0/30000 | COEFFICIENT_WIDTH |
| width ±7  | 2026-05-03 | 10 |  3,000 | 3 |  35.3s | 0/18000 | COEFFICIENT_WIDTH |
| deg14×±5  | 2026-05-03 | 14 |  5,000 | 3 |  50.4s | 0/30000 | D14_W5 (path A) |

Raw JSON: `prometheus_math/four_counts_pilot_run.json` (1K snapshot, retained),
`prometheus_math/four_counts_pilot_run_10k.json` (10K step-reward, rich format),
`prometheus_math/four_counts_pilot_run_10k_shaped.json` (10K shaped-reward, rich format),
`prometheus_math/four_counts_width_{5,7}.json` (coefficient-set width ablation),
and `prometheus_math/degree_sweep_results.json` (degree 12 + 14).
Cross-docs: `prometheus_math/DEGREE_SWEEP_RESULTS.md` (full degree-sweep analysis),
`prometheus_math/SHAPED_REWARD_RESULTS.md` (full reward-shape ablation),
`prometheus_math/COEFFICIENT_WIDTH_RESULTS.md` (full coefficient-set width ablation),
`prometheus_math/D14_W5_RESULTS.md` (degree 14 + ±5 alphabet, path-A pilot).

---

## Reward shape ablation (2026-05-03)

Re-ran the §6.2 four-counts pilot at 10K × 3 with `reward_shape='shaped'`
(continuous M-gradient + sub-Lehmer +50 bonus) instead of the default
`step` reward. Same harness, same seeds {0, 1, 2}, same 10K budget;
only the reward fn differs. Full analysis lives in
`prometheus_math/SHAPED_REWARD_RESULTS.md`. Headline:

| metric | step (10K × 3) | shaped (10K × 3) |
|---|---:|---:|
| total wall time | 45.5s | 107.6s |
| random_null PROMOTE | 0/30000 | 0/30000 |
| reinforce_agent PROMOTE | 0/30000 | 0/30000 |
| SHADOW_CATALOG entries | 0 | 0 |
| random_null Salem-band hits | 35 | 66 |
| reinforce Salem-band hits | 19,855 | 1 |
| Salem proxy concentration (REINFORCE/random) | **567×** | **0.015× (INVERTED)** |
| reinforce dominant band | salem_cluster (66.18%) | functional (99.94%) |
| reinforce mean episode reward | n/a (sparse) | 21.16 (avg of 3 seeds) |

**The shaped reward did not break the 0-PROMOTE ceiling.** It also did
not sharpen the proxy concentration — it *inverted* it. REINFORCE
under shaped reward slid down the continuous gradient `50·(5-M)/4` to
the M ≈ 2-3 plateau (functional band, where trajectory volume is
largest) and abandoned the Salem cluster entirely. The +50 sub-Lehmer
bonus was insufficient to pull a linear contextual policy past the
local optimum.

**Verdict:** reward shape isn't the bottleneck — the algorithm /
action-set is. Step reward's discontinuities at the band boundaries
were doing useful work for this policy class. Next intervention:
widen the action set (currently Discrete(7) over {-3..3}), then
consider stronger algorithms (PPO / MCTS).

See `prometheus_math/SHAPED_REWARD_RESULTS.md` for full details,
side-by-side tables, M-band distributions, and per-seed reward stats.

---

## Coefficient-set width ablation (2026-05-03)

Tested whether the `{-3..3}` per-step coefficient alphabet (7 actions)
is structurally too narrow to reach the sub-Lehmer band by widening
to `{-5..5}` (11 actions, 1.77M trajectories at deg 10) and `{-7..7}`
(15 actions, 11.4M trajectories). Same step-reward harness, same
seeds {0, 1, 2}; only the env's `coefficient_choices` changes. Full
analysis in `prometheus_math/COEFFICIENT_WIDTH_RESULTS.md`. Headline:

| metric | ±3 (10K) | ±5 (5K) | ±7 (3K) |
|---|---:|---:|---:|
| n_actions | 7 | 11 | 15 |
| trajectory space | 117K | 1.77M | 11.4M |
| total wall time | 45.5s | 59.8s | 35.3s |
| random_null PROMOTE | 0/30000 | 0/15000 | 0/9000 |
| reinforce_agent PROMOTE | 0/30000 | 0/15000 | 0/9000 |
| SHADOW_CATALOG entries | 0 | 0 | 0 |
| random catalog-hits | 32 (0.107%) | 1 (0.007%) | 0 |
| catalog hits with max\|c\| ≥ 4 | n/a | **0** | **0** |
| reinforce Salem-band hits | 19,855 | 0 | 0 |

**Pre-flight from Known180 (8625 entries):** entries with at least
one |c| ≥ 4 = 112; ≥ 5 = 60; ≥ 6 = 29; ≥ 7 = 26. **At degree 10
specifically, every catalog entry has max|c| = 1.** The wider-alphabet
hypothesis is structurally weak at degree 10 by construction; it
would only bite at degree ≥ 14.

**Verdict:** alphabet is **not the bottleneck** at degree 10. The
0-PROMOTE ceiling held across {-3..3, -5..5, -7..7}. Catalog-hit
density *dropped* with width (dilution) — the opposite of what an
alphabet bottleneck would produce. The single ±5 catalog hit was a
deg-10 polynomial with max|c| = 3, which {-3..3} could already reach.
**Zero catalog hits at any width came from polynomials that {-3..3}
was structurally excluding.**

Next intervention to try: pair widening alphabet with raising degree
(e.g., degree 14 × {-5..5}), since that is where Known180 has entries
with max|c| ≥ 4. Or change the algorithm class (PPO / MCTS) — the
linear contextual REINFORCE policy is also showing dilution failure
in this sweep, completely losing the Salem-cluster signal at ±5/±7.

See `prometheus_math/COEFFICIENT_WIDTH_RESULTS.md` for the full
pre-flight magnitude distribution, per-seed breakdowns, kill-pattern
shifts across widths, and the 1-line summary of the lone ±5 catalog hit.

---

## Degree 14 + ±5 alphabet ablation (2026-05-03) — path (A) pilot

Triple #3 closed with a triple-#3 pause and three branching paths
(A / B / C). Path (A): pilot DiscoveryEnv at **degree=14 +
coefficient_choices=(-5..5)** — the single cell of the (degree,
alphabet) grid where the curated Known180 + phase1 catalog has
small-M Salem polynomials with max|c| ≥ 4. Full analysis lives in
`prometheus_math/D14_W5_RESULTS.md`. Headline:

| metric | deg10 ±3 (10K) | deg10 ±5 (5K) | deg14 ±3 (3K) | **deg14 ±5 (5K)** |
|---|---:|---:|---:|---:|
| n_actions | 7 | 11 | 7 | **11** |
| trajectory space | 117K | 1.77M | 5.76M | **214M** |
| total wall time | 45.5s | 59.8s | 13.7s | **50.4s** |
| random_null PROMOTE | 0/30000 | 0/15000 | 0/9000 | **0/15000** |
| reinforce_agent PROMOTE | 0/30000 | 0/15000 | 0/9000 | **0/15000** |
| SHADOW_CATALOG entries | 0 | 0 | 0 | **0** |
| random catalog-hits | 32 | 1 | 8 | **0** |
| reinforce Salem-band hits | 19,855 | 0 | 1 | **0** |
| Salem proxy concentration (RFC/rand) | **567×** | **0×** | **0.13×** | **n/a (both zero)** |
| reinforce dominant kill-pattern | salem_cluster (66.18%) | functional/cyclo | cyclo | **cyclotomic_or_large (99.68%)** |

**Pre-flight from combined catalog:** at degree 14 there is exactly
**ONE** entry with max|c| ≥ 4 — the deg-14 representation of the
Lehmer polynomial (M = 1.176281, max|c| = 5,
`coeffs=[1,2,2,1,0,-2,-4,-5,-4,-2,0,1,2,2,1]`). The hypothesis
"+100 band exists at degree ≥ 14 but our policy class hadn't
reached it" is therefore testable but tight: the alphabet
restriction was a real exclusion (the witness cannot be reached
from {-3..3}), but the catalog target is small (one specific
poly).

**Verdict:** **degree 14 + ±5 did NOT break the 0-PROMOTE ceiling.**
30K episodes, 0 PROMOTEs, 0 SHADOW_CATALOG, 0 catalog hits across
both arms × 3 seeds. Hypothesis 2 specifically — that the +100 band
is reachable at degree 14 once the alphabet widens to ±5 — does
**not** survive this run; the agents failed even to rediscover the
single deg-14 Lehmer rep that should now be in the trajectory space.
Hypothesis 1 (Lehmer's conjecture / structural emptiness for this
policy class) is now the parsimonious read. **REINFORCE collapsed
onto the cyclotomic_or_large basin in 99.68% of its 15K episodes**,
uniformly across all 3 seeds — a clean failure signature, not a
single-seed pathology.

**Cumulative score across all 4-counts ablations:**

| sweep dimension | regimes tested | total episodes | PROMOTEs | SHADOW | catalog hits |
|---|---|---:|---:|---:|---:|
| degree (10/12/14, ±3, step) | 3 | 108,000 | 0 | 0 | 32 |
| reward shape (shaped, deg10, ±3) | 1 | 30,000 | 0 | 0 | 32 |
| alphabet (±5/±7, deg10, step) | 2 | 48,000 | 0 | 0 | 1 |
| **deg14 ± alphabet (this run)** | **1** | **30,000** | **0** | **0** | **0** |
| **TOTAL** | **7 cells** | **216,000** | **0** | **0** | **65** |

**The configuration knobs are exhausted.** Next-interventions ranked:
algorithm class change (MCTS / PPO with structured masks /
heuristic warm-start) > generator change (drop reciprocity
constraint, filter via kill-path) > more degree+alphabet sweep.

See `prometheus_math/D14_W5_RESULTS.md` for the full pre-flight
catalog distribution at degrees {10, 12, 14, 16, 18, 20}, the deg-14
catalog entry list with max|c| in {2,3,4,5}, per-seed PROMOTE +
SHADOW + catalog-hit + kill-pattern breakdown, the run log, and the
ranked recommendation list.

---

## Multi-degree results (degree 10 / 12 / 14, side-by-side)

Triple #2 of the just-finished session widened the polynomial degree to
test whether more action-space real estate breaks the structural
0-PROMOTE ceiling at degree 10. Full per-degree analysis lives in
`prometheus_math/DEGREE_SWEEP_RESULTS.md`. Headline:

### PROMOTE rates

| degree | trajectory space | random_null PROMOTE | reinforce_agent PROMOTE | total episodes |
|---:|---:|---:|---:|---:|
| 10 | 117K   | 0/30000 | 0/30000 | 60K |
| 12 | 824K   | 0/15000 | 0/15000 | 30K |
| 14 | 5.76M  | 0/9000  | 0/9000  | 18K |

**0 PROMOTEs across 108,000 total episodes** spanning all three degrees,
both arms.

### Salem-cluster proxy concentration (REINFORCE / random)

| degree | random Salem | reinforce Salem | concentration ratio |
|---:|---:|---:|---:|
| 10 | 35 / 30000 (0.117%) | 19,855 / 30000 (66.18%) | **567x** |
| 12 | 21 / 15000 (0.140%) | 4,904 / 15000 (32.69%) | **234x** (mode-collapse-inflated; one seed memorised one polynomial) |
| 14 | 8 / 9000 (0.089%)   | 1 / 9000 (0.011%)     | **0.13x INVERTED** (REINFORCE worse than random) |

The proxy concentration **monotonically degrades** as degree widens.
At degree 14 the policy is genuinely *worse than random* at finding
the Salem cluster — the trajectory space expanded 49x but the
policy class collapsed faster than the space grew.

### Per-episode wall time

| degree | per-ep (ms) | est 5K x 3 |
|---:|---:|---:|
| 10 | 0.580 | 8.7 s |
| 12 | 0.598 | 9.0 s |
| 14 | 0.678 | 10.2 s |

Companion-matrix `O(d^3)` cost was negligible compared to substrate
BIND/EVAL overhead. **Wall time is not the bottleneck at any tested
degree** — the 30-min budget could comfortably run degree 14 at 50K
x 3 if the structural ceiling demanded it. It does not.

### SHADOW_CATALOG entries

**Zero across all degrees and seeds.** No CLAIM minted, no
DiscoveryPipeline records produced. The sub-Lehmer band remains
empty under uniform-random and contextual-REINFORCE search at
Discrete(7) over {-3..3} for any tested degree.

### Verdict

Widening the degree did not break the 0-PROMOTE ceiling. It made the
proxy concentration *worse*. Next interventions: action-set width
(`|c| >= 4` polynomials), stronger algorithms (PPO / MCTS), continuous
reward shape — not more degree.

---

## 10K Configuration

```
degree            = 10         (half_len = 6, ~117K trajectories)
episodes per cell = 10000      (spec target reached)
seeds per cond    = 3          ({0, 1, 2})
lr                = 0.05
entropy_coef      = 0.05
cost_seconds      = 0.5
total wall time   = 45.5s      (rich harness; basic harness reports 45.9s)
arm wall-clock:
  random_null     = 18.76s     (no policy gradient updates)
  reinforce_agent = 26.70s     (1.42x slower / episode — policy update overhead)
```

Two conditions, run through identical `DiscoveryEnv` + `DiscoveryPipeline`:

- `random_null` — uniform-random sampler over `Discrete(7)` action space.
  Doubles as §6.4's "non-LLM mutation source" (alias
  `run_non_llm_mutation_source`).
- `reinforce_agent` — contextual REINFORCE (obs-conditioned linear policy
  with entropy regularization), the §6.2 "LLM-driven REINFORCE agent".

---

## Results — 10K x 3 seeds

### The four counts (mean over 3 seeds, 10K episodes each)

| condition | PROMOTE rate | catalog-hit rate | claim-into-kernel rate |
|---|---:|---:|---:|
| random_null      | 0.0000 ± 0.0000 | 0.00107 | 0.0000 |
| reinforce_agent  | 0.0000 ± 0.0000 | 0.00000 | 0.0000 |

### Per-seed breakdown (PROMOTE / catalog-hit / claim — counts and rates)

**random_null (10K episodes per seed):**

| seed | PROMOTE | catalog-hit | claim-into-kernel | rejected | elapsed |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 8  | 0 | 9992 | 6.54s |
| 1 | 0 | 12 | 0 | 9988 | 6.27s |
| 2 | 0 | 12 | 0 | 9988 | 5.95s |
| **rates** | **0/30000** | **32/30000 = 0.107%** | **0/30000** | — | — |

**reinforce_agent (10K episodes per seed):**

| seed | PROMOTE | catalog-hit | claim-into-kernel | rejected | elapsed |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 10000 | 10.37s |
| 1 | 0 | 0 | 0 | 10000 |  8.32s |
| 2 | 0 | 0 | 0 | 10000 |  8.01s |
| **rates** | **0/30000** | **0/30000** | **0/30000** | — | — |

### Welch t-test on PROMOTE rates (10K x 3)

```
random_null  vs  reinforce_agent:  p = 1.000  lift = +0.00x
TIED-AT-ZERO (both PROMOTE rates 0; tighter joint upper bound on
discovery rate at this configuration: < 1 / 30000)
```

### Kill-pattern breakdown (cumulative across 3 seeds = 30,000 episodes)

**random_null:**

```
upstream:functional         26027    (M in [2, 5))
upstream:cyclotomic_or_large 3325    (M ≈ 1 or M >= 5)
upstream:low_m                581    (M in [1.5, 2))
upstream:salem_cluster         35    (M in [1.18, 1.5))   <-- 35 known Salem hits
```

**reinforce_agent:**

```
upstream:salem_cluster      19855    (M in [1.18, 1.5))   <-- 567x random
upstream:low_m               9943    (M in [1.5, 2))
upstream:functional           182    (M in [2, 5))
upstream:cyclotomic_or_large   20    (M ≈ 1 or M >= 5)
```

REINFORCE concentrates **66.18%** of its episodes in the Salem cluster
band; random_null lands there in **0.12%** of episodes — a 567x
concentration ratio.

### SHADOW_CATALOG / PROMOTED records surfaced at 10K x 3

**Zero.** See `prometheus_math/SHADOW_CATALOG_FINDINGS.md` and the
empty record list in `prometheus_math/four_counts_10k_shadow.json`.

---

## 1K vs 10K — comparison

### Headline rates

| metric | 1K x 3 (3000 eps total) | 10K x 3 (30000 eps total) | direction |
|---|---:|---:|---|
| random_null PROMOTE rate              | 0.0000 (0/3000)  | 0.0000 (0/30000) | unchanged at zero |
| reinforce_agent PROMOTE rate          | 0.0000 (0/3000)  | 0.0000 (0/30000) | unchanged at zero |
| random_null catalog-hit rate          | 0.00167 (5/3000) | 0.00107 (32/30000) | within seed noise |
| reinforce_agent catalog-hit rate      | 0.0000 (0/3000)  | 0.0000 (0/30000) | unchanged at zero |
| Welch p (one-sided, PROMOTE)          | 1.000 | 1.000 | TIED-AT-ZERO |

### Kill-pattern shape

| kill_pattern | random_null 1K | random_null 10K | reinforce 1K | reinforce 10K |
|---|---:|---:|---:|---:|
| upstream:functional         | 2597 | 26027 | 182  | 182   |
| upstream:cyclotomic_or_large| 334  |  3325 | 20   | 20    |
| upstream:low_m              | 60   |   581 | 943  | 9943  |
| upstream:salem_cluster      | 4    |    35 | 1855 | 19855 |

random_null counts scale ~10x as expected (uniform sampler is
stationary). REINFORCE counts also scale ~10x for the bands it cares
about (`low_m`, `salem_cluster`) but the off-target bands (`functional`,
`cyclotomic_or_large`) are essentially flat (182/20 → 182/20). This is
the policy's footprint: by 1000 episodes it has already collapsed onto
the Salem-cluster + low-M region and stays there.

### Salem-cluster concentration ratio (REINFORCE / random_null)

| scale | REINFORCE Salem | random Salem | concentration |
|---|---:|---:|---:|
| 1K x 3   | 1,855  | 4  | **463.75x** |
| 10K x 3  | 19,855 | 35 | **567.29x** |

**The 463x concentration STRENGTHENED to 567x at 10x the data.** This
is consistent with REINFORCE having locked in on the Salem cluster
proxy by ~1K episodes and continuing to mine it; the random-null
denominator is sampling-variance bounded, so as N grows the ratio
tightens around the policy's true asymptotic concentration.

### Did 10K break the 0/0 PROMOTE tie?

**No.** Both arms remained at 0 PROMOTE / 0 SHADOW_CATALOG / 0
claim-into-kernel across all 30,000 episodes (10K x 3 seeds x 2
conditions = 60,000 total episodes ran).

The honest reading: this is a **tighter joint upper bound on the
discovery rate at this configuration: < 1 / 30000.** It is not a
calibration failure — it is the joint upper bound the spec §6.2.5
asks for, now ten times tighter than the 1K result.

The structural ceiling is real. Neither the LLM prior nor the
random null produces sub-Lehmer-band catalog-misses at degree 10
with cost_seconds=0.5 and the current battery. To break this floor
the next move is **widening the action set, raising degree, or
loosening the battery** — not increasing episode count further
within the same env.

### Was random_null suddenly producing PROMOTEs that REINFORCE wasn't?

**No** — the alarm condition called out in the brief did not fire.
random_null still has zero PROMOTEs; it produces *catalog hits*
(known Mossinghoff entries in the Salem-cluster band) at rate
0.107%, but those are catalog hits routed upstream of the pipeline
and never become CLAIMs. The LLM prior is **not** "actively steering
away from sub-Lehmer" — both priors land sub-Lehmer with equal
frequency (zero); the §6.4 pivot framing remains intact.

---

## Honest interpretation: what does 10K reveal?

Per spec §6.4: "If non-LLM source produces signal-class survivors at
higher rate than LLM source, the LLM prior is too tight; if LLM source
dominates, the prior is well-tuned to the search problem."

**Reading at 10K x 3 (now the spec-grade scale):**

- On the **PROMOTE-rate** dimension: still tied at zero. The §6.4
  comparison is uninformative on this dimension at this configuration.
  This is the deeper joint upper bound the spec calls out — at 10K x 3,
  the action space + prior + battery jointly admit fewer than
  ~1/30000 sub-Lehmer survivors. **The structural ceiling is real and
  is now named: < 1/30000 at degree 10 / cost_seconds=0.5.**
- On the **claim-into-kernel** dimension: also tied at zero. It's the
  kernel CLAIM-mint rate that's near zero, not the post-CLAIM survival
  rate. Nothing made it INTO the kernel for the battery to evaluate.
- On the **Salem-cluster proxy**: REINFORCE dominates random by 567x.
  This is **strong, scaled evidence** the prior is well-tuned to low-M
  structure in general — and the concentration ratio TIGHTENED with
  more data, ruling out the "1K was a small-sample artifact" hypothesis.
- On the **catalog-hit** dimension: random_null caught 32 known
  Mossinghoff Salem entries (rediscovery signal); REINFORCE caught 0.
  This is the same wrinkle as 1K, scaled — REINFORCE explores the
  *neighborhood* of the band rather than landing on the canonical
  Mossinghoff representatives. The contextual softmax has learned
  the M-shape but not the discrete fingerprints.

In §6.4's framing: **the prior is well-tuned for the proxy task**
(low-M discovery as measured by Salem-cluster hits) but **insufficient
for the strict task** (sub-Lehmer discovery at degree 10 / Discrete(7)
/ cost_seconds=0.5). The 10x scale-up confirms this isn't a sampling
artifact — it's a structural property of the env and the policy class.

---

## What the 10K result implies (action items)

1. **§6.2 spec target met.** The 10K-episode spec target is now
   accomplished. The PROMOTE comparison at this scale is firmly
   TIED-AT-ZERO with a Welch p of 1.000. We stop scaling episodes in
   this env config.

2. **The proxy-task evidence is now publishable at scale.** The 567x
   lift on Salem-cluster concentration (up from 463x at 1K) is a
   genuine learning signal that **strengthens with data.** This rules
   out the "1K was small sample" interpretation. The four-counts
   harness's value is unconditional on nonzero PROMOTE rates.

3. **§6.4 verdict at scale: the LLM prior is not too tight.**
   REINFORCE dominates random on every observable proxy
   (claim-band concentration, M-shape exploration, low-M residency);
   the prior's resolution gap (Salem ≠ sub-Lehmer) is a function of
   the reward shape and the env's combinatorial reach, not the
   prior class.

4. **The catalog-hit rate is the calibration-grade observable, but
   it does NOT route through the pipeline.** At 10K x 3, random_null
   caught 32 known Mossinghoff entries — none of which became CLAIMs
   (catalog hits are intercepted upstream by the env's
   Mossinghoff cross-check). For the harness to surface a CLAIM the
   policy must hit the sub-Lehmer band AND miss all 5 catalogs —
   empirically zero out of 60,000 episodes at this config.

5. **Next-move list (in priority order):**
   - Widen the action set beyond Discrete(7) — currently coefficients
     are constrained to {-3, -2, -1, 0, 1, 2, 3}; many known Lehmer-
     adjacent polynomials need |c| >= 4.
   - Raise degree from 10 (where 117K trajectories are exhaustively
     searchable in principle) to degree 14 or 16, where the
     trajectory space is genuinely sparse.
   - Loosen the F1/F6/F9/F11 battery thresholds; the 0/30000
     CLAIM rate suggests the battery may be over-tightened.
   - Track per-band M-distribution histograms across seeds to
     confirm the policy is uniform within the Salem cluster (or
     concentrating on a sub-band).

6. **The 10K-x-3 result is the calibration anchor §6.2.5 needed —
   in the negative direction.** It firmly establishes the joint
   upper bound. Future env-mod runs (wider action set, higher
   degree, loosened battery) measure their effect against this
   floor: any nonzero PROMOTE rate at 10K x 3 is a sub-1/30000
   improvement and is significant against this baseline.

---

## Provenance note

The pilot's pipeline records (`env.pipeline_records()`) totalled
**0** across all 6 (condition, seed) cells. This is consistent with
the 0 claim-into-kernel rate — pipeline records are only minted when
an episode produces a sub-Lehmer band polynomial that's NOT in
Mossinghoff (i.e., a catalog miss in the strict +100 band). At this
configuration that population is empty.

The kernel's symbol/claim/evaluation row counts therefore match the
expected formula: **episodes_run x conditions x seeds = 60000 episodes,
0 of which produced kernel CLAIMs.** No CLAIM was minted, so no
claim/evaluation rows were written by the pipeline; symbol rows
correspond to the env's per-step EVALs and are not relevant to the
PROMOTE comparison.

## Files shipped this iteration

- `prometheus_math/four_counts_pilot.py` — harness (unchanged from 1K).
- `prometheus_math/demo_four_counts.py` — basic CLI driver (unchanged).
- `prometheus_math/_run_10k_rich.py` — rich runner (per-seed +
  shadow + arm-timing capture).
- `prometheus_math/four_counts_pilot_run.json` — 1K snapshot (retained).
- `prometheus_math/four_counts_pilot_run_10k.json` — 10K rich JSON.
- `prometheus_math/four_counts_10k_per_seed.json` — per-seed dump.
- `prometheus_math/four_counts_10k_shadow.json` — SHADOW_CATALOG /
  PROMOTED records (empty at this scale).
- `prometheus_math/four_counts_10k_stdout.log` — basic stdout capture.
- `prometheus_math/four_counts_10k_rich_stdout.log` — rich stdout capture.
- `prometheus_math/SHADOW_CATALOG_FINDINGS.md` — convention doc (zero
  entries; template + 10K negative-result note).
- `prometheus_math/FOUR_COUNTS_RESULTS.md` — this file.

---

## Original 1K snapshot (retained for comparison)

The text below is the as-shipped 2026-04-29 1K result, preserved verbatim
so the 10K-vs-1K comparison above can be cross-checked against the
original source-of-truth.

### 1K Configuration (original)

```
degree            = 10         (half_len = 6, ~117K trajectories)
episodes per cell = 1000       (spec target = 10000; 1000 keeps dev loop < 5 min)
seeds per cond    = 3          ({0, 1, 2})
lr                = 0.05
entropy_coef      = 0.05
cost_seconds      = 0.5
total runtime     = 4.3s
```

### 1K — The four counts (mean over 3 seeds)

| condition | PROMOTE rate | catalog-hit rate | claim-into-kernel rate |
|---|---:|---:|---:|
| random_null      | 0.0000 ± 0.0000 | 0.0017 | 0.0000 |
| reinforce_agent  | 0.0000 ± 0.0000 | 0.0000 | 0.0000 |

### 1K — Welch one-sided t-test on PROMOTE rates

```
random_null  vs  reinforce_agent:  p = 1.000  lift = +0.00x
TIED-AT-ZERO (both PROMOTE rates 0; joint upper bound on discovery rate)
```

### 1K — Kill-pattern breakdown (cumulative across 3 seeds = 3000 episodes)

**random_null:**

```
upstream:functional         2597    (M in [2, 5))
upstream:cyclotomic_or_large 334    (M ≈ 1 or M >= 5)
upstream:low_m                60    (M in [1.5, 2))
upstream:salem_cluster         4    (M in [1.18, 1.5))   <-- 4 known Salem hits
```

**reinforce_agent:**

```
upstream:salem_cluster      1855    (M in [1.18, 1.5))   <-- 463x random
upstream:low_m               943    (M in [1.5, 2))
upstream:functional          182    (M in [2, 5))
upstream:cyclotomic_or_large  20    (M ≈ 1 or M >= 5)
```
