# Gradient Archaeology — Substrate Ledger Audit

Read-only analysis. Asks whether the existing pilot logs already
contain visible structure on Aporia's six negative-space gradient
axes, or whether each gradient requires new instrumentation.

Generated 2026-05-04. No substrate code or pilot data modified.

## Setup

Six gradient axes (Aporia's framework):

1. Distance-to-target (M distribution near Lehmer's 1.17628)
2. Battery-survival depth (kill_pattern information density)
3. Negative space (operator x falsifier contingency)
4. Method-utility per operator class
5. Cross-domain bridge (proximity-to-catalog vs M-gap)
6. Computational-verification depth

## Data Sources

- Pilot JSONs loaded: **22**
- Total episodes/samples aggregated: **492,987**
- Schemas covered: catalog_seeded, four_counts, degree_sweep, v2 (anti-elitist), v3 (root-space), discovery_v2, lehmer_smoke, cross_domain_means.

Per-candidate M values were only persisted by:

- `_catalog_seeded_pilot.json` `random_seeded` arm (1,069 catalog hits)
- `_lehmer_smoke_results.json` brute-force band hits (11 polys)

Other arms log only aggregate kill_pattern counts and summary statistics. This sparseness is itself a finding.

## Gradient 1 — Distance-to-Target

[SIGNAL_PRESENT]
  M values cluster into 5 bins; modal bin holds 64.1% of mass. Distribution is far from uniform — strong concentration near catalog modes.

- M records aggregated: **1,075**
- M range: [1.1763, 1.4013], median=1.2510, mean=1.2465
- M values in Lehmer band (1.001, 1.18): **21**
- M values within 0.004 of Lehmer's M (1.17628): **21**

Top per-arm contribution to M records:

- `catalog_seeded::random_seeded`: 1069 M values
- `lehmer_brute_force_smoke`: 6 M values

## Gradient 2 — Battery-Survival Depth (kill_path)

[SIGNAL_PRESENT]
  Kill_path is heavily structured: top-1 falsifier carries 41.3% of 314,971 total kills; top-3 carries 86.4%. Per-arm distributions diverge from overall (max KL=1.790 bits).

- Total kills aggregated: **314,971**
- Top-1 kill_pattern share: **41.3%**
- Top-3 kill_pattern share: **86.4%**

Overall kill_pattern distribution:

- `upstream:cyclotomic_or_large`: 129,993 (41.3%)
- `upstream:functional`: 85,538 (27.2%)
- `upstream:shaped_continuous`: 56,672 (18.0%)
- `upstream:salem_cluster`: 25,619 (8.1%)
- `upstream:low_m`: 13,822 (4.4%)
- `upstream:large_m`: 3,174 (1.0%)
- `upstream:cyclotomic`: 153 (0.0%)

Per-arm kill-pattern entropy (lower = more deterministic):

- `four_counts::reinforce_agent`: H=2.120 bits, modal=`upstream:shaped_continuous` (35.7%), n=84,000
- `four_counts::random_null`: H=1.817 bits, modal=`upstream:functional` (36.6%), n=83,966
- `catalog_seeded::random_uniform`: H=0.555 bits, modal=`upstream:cyclotomic_or_large` (87.1%), n=15,000
- `catalog_seeded::reinforce_uniform`: H=0.031 bits, modal=`upstream:cyclotomic_or_large` (99.7%), n=15,000
- `catalog_seeded::reinforce_seeded`: H=0.058 bits, modal=`upstream:cyclotomic_or_large` (99.4%), n=15,000
- `catalog_seeded::reinforce_frozen_bias`: H=0.923 bits, modal=`upstream:cyclotomic_or_large` (66.8%), n=15,000
- `four_counts_per_arm::random_null`: H=0.565 bits, modal=`upstream:cyclotomic_or_large` (86.8%), n=15,000
- `four_counts_per_arm::reinforce_agent`: H=0.031 bits, modal=`upstream:cyclotomic_or_large` (99.7%), n=15,000
- `degree_sweep::deg12::random_null`: H=0.745 bits, modal=`upstream:functional` (82.2%), n=14,989
- `catalog_seeded::random_seeded`: H=1.660 bits, modal=`upstream:functional` (53.0%), n=13,931
- `degree_sweep::deg12::reinforce_agent`: H=1.055 bits, modal=`upstream:functional` (50.7%), n=10,085
- `degree_sweep::deg14::random_null`: H=0.840 bits, modal=`upstream:functional` (75.5%), n=9,000
- `degree_sweep::deg14::reinforce_agent`: H=0.090 bits, modal=`upstream:functional` (99.0%), n=9,000

Per-arm KL divergence vs overall (higher = arm kills differently from population):

- `degree_sweep::deg14::reinforce_agent`: KL=1.790 bits
- `degree_sweep::deg12::reinforce_agent`: KL=1.674 bits
- `catalog_seeded::reinforce_uniform`: KL=1.248 bits
- `four_counts_per_arm::reinforce_agent`: KL=1.248 bits
- `catalog_seeded::reinforce_seeded`: KL=1.224 bits
- `degree_sweep::deg12::random_null`: KL=1.067 bits
- `degree_sweep::deg14::random_null`: KL=0.908 bits
- `catalog_seeded::random_uniform`: KL=0.800 bits
- `four_counts_per_arm::random_null`: KL=0.792 bits
- `catalog_seeded::random_seeded`: KL=0.772 bits
- `four_counts::reinforce_agent`: KL=0.558 bits
- `catalog_seeded::reinforce_frozen_bias`: KL=0.556 bits
- `four_counts::random_null`: KL=0.306 bits

## Gradient 3 — Operator x Falsifier Contingency

[SIGNAL_PRESENT]
  Contingency table has visible structure: mutual_info(arm; falsifier)=0.725 bits, chi^2/df=4234.5, 41 systematically closed (arm,falsifier) pairs, 1 systematically over-represented pairs.

- Arms: 13, Falsifiers: 7, Cells: 91 (41 empty)
- Mutual info (arm; falsifier) = **0.725 bits**
- chi^2 = 304886.5 (df=72, per-df = 4234.5)

Top systematically-empty (closed) (arm, falsifier) pairs:

- `catalog_seeded::random_seeded` x `upstream:cyclotomic`: 0 kills (arm has 13,931, falsifier has 153 elsewhere)
- `catalog_seeded::random_seeded` x `upstream:large_m`: 0 kills (arm has 13,931, falsifier has 3,174 elsewhere)
- `catalog_seeded::random_seeded` x `upstream:shaped_continuous`: 0 kills (arm has 13,931, falsifier has 56,672 elsewhere)
- `catalog_seeded::random_uniform` x `upstream:cyclotomic`: 0 kills (arm has 15,000, falsifier has 153 elsewhere)
- `catalog_seeded::random_uniform` x `upstream:large_m`: 0 kills (arm has 15,000, falsifier has 3,174 elsewhere)
- `catalog_seeded::random_uniform` x `upstream:salem_cluster`: 0 kills (arm has 15,000, falsifier has 25,619 elsewhere)
- `catalog_seeded::random_uniform` x `upstream:shaped_continuous`: 0 kills (arm has 15,000, falsifier has 56,672 elsewhere)
- `catalog_seeded::reinforce_frozen_bias` x `upstream:cyclotomic`: 0 kills (arm has 15,000, falsifier has 153 elsewhere)
- `catalog_seeded::reinforce_frozen_bias` x `upstream:large_m`: 0 kills (arm has 15,000, falsifier has 3,174 elsewhere)
- `catalog_seeded::reinforce_frozen_bias` x `upstream:shaped_continuous`: 0 kills (arm has 15,000, falsifier has 56,672 elsewhere)

Top systematically-over-represented (open) (arm, falsifier) pairs:

- `degree_sweep::deg12::reinforce_agent` x `upstream:salem_cluster`: 4,904 obs vs 820.3 expected (ratio=6.0x)

## Gradient 4 — Method-Utility per Operator Class

[SIGNAL_PRESENT]
  Lehmer PROMOTE rate is identically 0 across 39 arm/seed cells (consistent with the substrate's 350K-episode null result). Catalog-hit-rate is non-zero in 7 arms and varies by 1-2 orders of magnitude across operator classes. Cross-domain test means span 2.8..91.2 across algorithms. Method-utility heterogeneity is real.

- Lehmer arm records: 49
- Cross-domain records: 8
- Arms with PROMOTE = 0: 39/39

Lehmer arms ranked by promote_rate_mean (all 0 in current data):

- `random_uniform` (_catalog_seeded_pilot.json): promote_rate=0.0
- `random_seeded` (_catalog_seeded_pilot.json): promote_rate=0.0
- `reinforce_uniform` (_catalog_seeded_pilot.json): promote_rate=0.0
- `reinforce_seeded` (_catalog_seeded_pilot.json): promote_rate=0.0
- `reinforce_frozen_bias` (_catalog_seeded_pilot.json): promote_rate=0.0
- `random_null` (four_counts_pilot_run_10k.json): promote_rate=0.0
- `reinforce_agent` (four_counts_pilot_run_10k.json): promote_rate=0.0
- `random_null` (four_counts_pilot_run_10k_shaped.json): promote_rate=0.0

Cross-domain test means ranked (where the gradient lives):

- `knot_trace_field` / `reinforce`: score=91.213
- `oeis_sleeping_beauty` / `growth`: score=73.103
- `knot_trace_field` / `test_reinforce`: score=70.933
- `oeis_sleeping_beauty` / `test_growth`: score=70.175
- `knot_trace_field` / `test_ppo`: score=70.133
- `bsd_rank` / `majority`: score=52.233
- `genus2` / `test_reinforce`: score=49.667
- `genus2` / `reinforce`: score=47.200
- `bsd_rank` / `reinforce`: score=46.267
- `genus2` / `test_ppo`: score=43.833
- `mock_theta` / `reinforce`: score=41.473
- `mock_theta` / `test_reinforce`: score=37.500
- `mock_theta` / `test_ppo`: score=36.333
- `genus2` / `ppo`: score=34.407
- `genus2` / `random`: score=33.107
- `genus2` / `test_random`: score=31.333
- `bsd_rank` / `random`: score=20.367
- `knot_trace_field` / `ppo`: score=19.460
- `knot_trace_field` / `random`: score=13.873
- `knot_trace_field` / `test_random`: score=13.133

## Gradient 5 — Cross-Domain Bridge (Distance-to-Catalog vs M-Gap)

[SIGNAL_PRESENT]
  Pearson(Hamming-to-catalog, |M-target|) = 0.374 over 1075 candidates. Proximity to catalog measurably predicts M-gap (positive correlation = closer-in-coefficient-space implies closer-to-target-M).

- Candidates analyzed: 1075
- Pearson rho = **0.374**

Per Hamming-distance bin (mean |M-target|):

- HD=0: n=355, mean_m_gap=0.0511, min_m_gap=0.0000
- HD=1: n=132, mean_m_gap=0.0925, min_m_gap=0.0910
- HD=2: n=97, mean_m_gap=0.0965, min_m_gap=0.0965
- HD=3: n=471, mean_m_gap=0.0736, min_m_gap=0.0000
- HD=4: n=9, mean_m_gap=0.0424, min_m_gap=0.0000
- HD=5: n=10, mean_m_gap=0.0643, min_m_gap=0.0000
- HD=7: n=1, mean_m_gap=0.1044, min_m_gap=0.1044

## Gradient 6 — Computational-Verification Depth

[NEEDS_NEW_INSTRUMENTATION]
  F1-F11 verdicts are persisted as boolean pass/fail. No depth/precision axis is captured in DiscoveryRecord, the kernel verdict, or any pilot JSON. To read this gradient we must add (a) verifier-precision tier per claim, (b) permutation-null sample-count actually used, (c) catalog scan completeness, and (d) populate verdict_runtime_ms with real values.

Specific evidence:
- DiscoveryRecord.check_results stores (bool, rationale) tuples only — no N or precision field.
- Pilot JSONs aggregate by_kill_pattern with NO depth dimension.
- Kernel verdict_runtime_ms is set to 0 in discovery_pipeline.py Phase 4 (synthetic verdict short-circuit).

## Per-region structure

Day 1-2 of the 5-day kill-vector plan. The aggregate gradient 3 result (0.725 bits MI across all kills) lumps together every (degree, alphabet_width, reward_shape) cell. We disaggregate by (env, degree, width, reward_shape) and compute per-region MI(operator; kill_pattern), each operator's emergent kill distribution (its 'coordinate chart'), and the region x operator interaction. Read-only: only Lehmer-family pilots tagged in `PER_FILE_METADATA` are included; cross-domain pilots have no kill_pattern aggregation and are excluded from this section.

- Regions identified: **6** (from 60 region-tagged kill records)
- Per-region MI(operator; kill_pattern) range: min=0.000, median=0.341, max=0.461 bits
- Per-region KL(kill_dist || global_kill_dist) range: min=0.525, max=2.392 bits
- Most distinctive region: `four_counts|deg10|w5|shaped`
- Weighted-mean per-region MI: **0.264 bits**

Per-region summary (sorted by KL vs global):

- `four_counts|deg10|w5|shaped`: n=59,999, operators=2, kill_patterns=3, MI=0.057 bits, KL_vs_global=2.392 bits
- `four_counts|deg10|w7|step`: n=18,000, operators=2, kill_patterns=3, MI=0.021 bits, KL_vs_global=1.075 bits
- `four_counts|deg12|w5|step`: n=25,074, operators=2, kill_patterns=4, MI=0.341 bits, KL_vs_global=0.970 bits
- `four_counts|deg14|w5|step`: n=48,000, operators=2, kill_patterns=4, MI=0.000 bits, KL_vs_global=0.540 bits
- `four_counts|deg10|w5|step`: n=89,967, operators=2, kill_patterns=4, MI=0.461 bits, KL_vs_global=0.527 bits
- `discovery_pipeline|deg14|w5|step`: n=73,931, operators=5, kill_patterns=4, MI=0.397 bits, KL_vs_global=0.525 bits

### Operator coordinate charts

Each operator's emergent coordinate chart on the search space — its mean kill distribution across all regions where it was deployed. Pairs with high JSD have nearly orthogonal charts (different views of the search space); pairs with low JSD have collapsed to the same chart.

- Operators charted: **7**
- Median pairwise JSD: **0.263 bits**

Per-operator chart summary (sorted by total kill mass):

- `random_null`: n_kills=122,955, regions_present=5, H=1.732 bits, modal=`upstream:functional` (42.2%)
- `reinforce_agent`: n_kills=118,085, regions_present=5, H=2.220 bits, modal=`upstream:cyclotomic_or_large` (28.9%)
- `random_uniform`: n_kills=15,000, regions_present=1, H=0.555 bits, modal=`upstream:cyclotomic_or_large` (87.1%)
- `reinforce_uniform`: n_kills=15,000, regions_present=1, H=0.031 bits, modal=`upstream:cyclotomic_or_large` (99.7%)
- `reinforce_seeded`: n_kills=15,000, regions_present=1, H=0.058 bits, modal=`upstream:cyclotomic_or_large` (99.4%)
- `reinforce_frozen_bias`: n_kills=15,000, regions_present=1, H=0.923 bits, modal=`upstream:cyclotomic_or_large` (66.8%)
- `random_seeded`: n_kills=13,931, regions_present=1, H=1.660 bits, modal=`upstream:functional` (53.0%)

Most orthogonal operator pairs (high JSD = different charts):

- `random_seeded||reinforce_uniform`: JSD=0.602 bits
- `random_seeded||reinforce_seeded`: JSD=0.590 bits
- `reinforce_agent||reinforce_uniform`: JSD=0.495 bits
- `reinforce_agent||reinforce_seeded`: JSD=0.486 bits
- `random_null||reinforce_uniform`: JSD=0.453 bits

Most collapsed operator pairs (low JSD = same chart):

- `reinforce_seeded||reinforce_uniform`: JSD=0.001 bits
- `random_uniform||reinforce_frozen_bias`: JSD=0.043 bits
- `random_uniform||reinforce_seeded`: JSD=0.053 bits
- `random_uniform||reinforce_uniform`: JSD=0.058 bits
- `reinforce_frozen_bias||reinforce_seeded`: JSD=0.170 bits

### Region x operator interaction

- Aggregate MI(operator; kill_pattern) = **0.391 bits** (operator-only marginalization over regions; differs from gradient 3's 0.725 bits because g3 keeps the file/condition prefix as part of the arm label, while here we strip it to expose the underlying operator class)
- Conditional MI(operator; kill_pattern | region) = **0.264 bits**
- MI(region; kill_pattern) = **0.950 bits**
- MI(region; operator) = **0.788 bits** (measures how unevenly operators are allocated to regions)
- Interaction delta = aggregate - conditional = **+0.127 bits**
- Triple table cells (region x operator x kill_pattern): 50 non-zero of 50 populated

### Verdict: **B — Region-specific operator behavior**

Per-region MI = 0.264 bits is substantially below aggregate MI = 0.391 bits (delta = +0.127); region carries MI(region; kp) = 0.950 bits in its own right. Operator behavior is region-dependent: kill-vector design must include region context (state, operator) -> kill_vector.

## Cross-Gradient Observations

- `g2_g4_consistent`: True
- `g3_implies_g4`: True
- `sparse_per_candidate`: True
- `per_region_verdict`: B_REGION_SPECIFIC

## The Empirical Answer

The substrate's existing ledger contains gradient signal on **axes 2, 3, and 4** (kill_path density, operator x falsifier contingency, method-utility per operator) and partial signal on **axis 1** (M distribution, but only for the catalog_seeded arm). **Axis 5** is borderline — the data exists for the catalog_seeded arm but not for cross-domain pilots (which log only summary accuracies, not per-episode predictions). **Axis 6** is fully missing: we do not log verifier depth/precision anywhere.

**Per-region verdict: B — region-specific.** Region carries more kill-pattern information than operator does; kill-vector design MUST include region context. The navigation policy is (state, operator) -> kill_vector, not operator -> kill_vector.

## Implications for Layer 2 Repair

Tomorrow's gradient field can be partly built from the existing ledger (axes 2-4 are immediately readable; axis 1 needs the per-episode M to be persisted in EVERY arm, not just catalog_seeded::random_seeded). Bridging the cross-domain axis (5) requires logging per-episode predictions in the BSD/genus-2/knot/modular-form/mock-theta/OEIS pilots. Axis 6 is the work the substrate hasn't yet been asked to do; adding verifier-depth instrumentation is a prerequisite for closing the gradient field.

**Implication for kill-vector design (verdict B):** The feature set must concatenate (region_features, operator_id) BEFORE the kill_pattern prediction head. A pure operator-only encoder would lose the dominant axis (MI(region; kill_pattern) = 0.95 bits vs MI(operator; kill_pattern | region) = 0.26 bits in current data). Concretely: each region's training tuple is (degree, alphabet_width, reward_shape, operator) -> kill_vector. Existing data covers 6 regions; the unsampled regions (e.g. degree-12 with shaped reward, alphabet width 9, cross-domain envs with kill_pattern aggregation) are negative-space holes that the next round of pilots should fill before kill-vector training is locked in.

**Honest sparseness note:** The 6 regions identified are thinly populated in the operator dimension (most have only 2 operators: random_null and reinforce_agent). Only the discovery_pipeline|deg14|w5|step region samples 5 operators. Two regions (`four_counts|deg10|w5|shaped`, `four_counts|deg14|w5|step`) have MI close to 0 because the two operators in those regions converge to similar kill distributions there — that may itself be a region-specific operator-collapse finding worth investigating, not noise.
