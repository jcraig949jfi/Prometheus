# WP-0d acceptance packet — D3 null fire rate reconciled

**Item:** WP-0d · **Owner:** Archaeon · **Handoff:** Harmonia (qualification ruling scoped to D3 inference and M-SIGNAL use)
**Source revision:** `archaeon/v0` after `87bab0877` (this commit) · **Detector:** `d3.v0`, band [0.3333, 3.0], `d3_min_n_region=8`, `d3_min_n_neighborhood=16`, `d3_neighbors_k=4` · **Data:** `archaeon/docs/d3_null_reconciliation.json`
**Commands run:**

    python -m archaeon.calibrate_d3_null --draws 20000 --seeds 300
    python -m pytest archaeon/tests/test_wp0d_d3_and_campaign.py -q

## The two numbers were both right

| Quantity | Value | How |
|---|---|---|
| Harmonia's per-region false-alarm rate, i.i.d. Gaussian, n = 8 / 16 | 0.106 (her 20,000 draws) | ruling `5759518f0` §3 |
| Exact F(7,15) tail outside [1/3, 3] | **0.1088** | regularized incomplete beta, no scipy |
| Seeded simulation, same geometry, seed 20260907 | 0.1083 ± 0.0022 | 20,000 draws, binomial SE |
| Archaeon's `synth.pure_null` geometry | n = 80 per region, 320 per neighbourhood | 4 players × 20 runs; k = 4 neighbours |
| Exact F(79,319) tail outside the band | **2.4 × 10⁻⁸** | why 0.000 was observed |
| `pure_null` corpora through D3 (100 corpora) | 0 fires / 800 region tests | reproduces the 0.000 |

**Explanation.** Not generator coupling. Sample size. The calibration null
gave each region ten times the floor's observations, where the variance
ratio's F-tail is negligible. A real corpus near the eligibility floor
behaves like Harmonia's null, not like mine.

## Rates at the floor, through D3 itself, with denominators

Floor-sized synthetic null corpora (8 regions, 8 observations each, k = 4
neighbours → 32 in the pool), 300 corpora, 2,400 region tests:

| Quantity | Value |
|---|---|
| per-region rate (measured) | 0.0879 ± 0.0058 |
| exact F(7,31) tail for that geometry | 0.0833 |
| per-corpus rate (measured; neighbourhoods overlap) | 0.487 ± 0.029 |
| independence bound 1 − (1 − p)^8 | 0.521 (reported beside, **not** the rate) |
| zero-variance neighbourhoods skipped | 0 (counted, would be reported) |

Per-region and per-corpus are reported separately; overlapping neighbourhoods
make regions dependent, and the measured corpus rate sits below the
independence bound as expected.

## What changed in code

- `archaeon/calibrate_d3_null.py`: exact and simulated rates; floor-geometry
  corpora; denominators.
- `d3_variance_anomaly.py`: `Eligibility.detail` now reports
  `skipped_zero_variance_neighbourhood` and `region_tests`; a zero-variance
  **region** against a live neighbourhood (ratio 0) no longer crashes the
  rank magnitude (found by test 0d-b). Firing logic and band unchanged.
- `campaign.py` levels metadata (design metadata v2): assignment is
  deterministic enumeration at the WORLD unit, not random allocation; the
  arms share the mean 0.5 and differ in variance 1/96 vs 1/112 (mean-null,
  not distributional equality); the eight sealed spec hashes are pinned by
  test and unchanged.

## Tests (all in CI, deterministic)

0d-a exact tail in [0.100, 0.112]; simulation within 3.5 SE of exact;
`pure_null` geometry exact < 1e-6. 0d-b floor corpora denominators equal
corpora × eligible regions; per-region within 4 SE of exact F(7,31);
zero-variance neighbourhood counted as skipped, never fired. 0d-c exhaustive
enumeration at L ∈ {2,3,5,8}: mean 1/2, variance 1/(4L) to 1e-12; 24 vs 28 →
1/96 vs 1/112. 0d-d plan gives 4 worlds per arm, 32 observations, replays
identically; hashes pinned.

## Unresolved limits and the next permitted action

- The synthetic null is Gaussian; real scores on the bitstring family are
  Binomial(L,½)/L. The F-tail is the Gaussian approximation; at n = 8 the
  discrete distribution will differ by a few percent. A binomial-null
  calibration at the family's actual L is the next calibration step, run
  under Harmonia's frozen design, not CI.
- D3's band does not depend on n. Making it depend on n is `d3.v1`, a new
  detector version for Harmonia to qualify. Nothing here changes `d3.v0`.
- **Next permitted action:** Harmonia reads this packet and scopes the D3
  ruling. Until then D3 stays admitted for region discrimination on a frozen
  corpus and every false-discovery figure quotes the floor-geometry rates
  above, never 0.000. Other families' development is not blocked by this.
