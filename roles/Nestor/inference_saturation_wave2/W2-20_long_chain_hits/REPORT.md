# W2-20: random-hit copiers with long chains (W2-13 follow-up): is the power gap closed?

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files:** `PREREG.txt` (written 2026-10-01T01:25:30Z, sha256 858c29b6…), `search_late.py`, `lengths_late.py`, `composition.py`, `supplement.py`, `replay_w13.py`, verbatim copies of the W2-13 scripts, and their JSON and logs.
> - **Compute:** about 34 CPU-min of the 60 budgeted.

## Answer
**The pre-registered rule returns UNRESOLVED.** It misses T3-SUFFICIENT by a hair:
- c_EVO = **−0.45 pp, 95% CI [−1.59, +0.704]**, against the pre-stated SUFFICIENT bar of an upper bound < +0.70.
- Across 10 bootstrap seeds the upper bound runs 0.698–0.763 (mean 0.727). Only 1 of the 10 falls below 0.7.

What the result does establish:
- **T4(c′) is not supported.**
- **An evolved excess as large as the raw gap (+1.39 pp) is excluded.**
- **The point estimate is now negative.**

## Search
- **Scheme S_late.** Draw uniform random genomes and screen only those whose first copy-op site is at position ≥ 35.
  - In random hits, L_pre ≈ the position of the first copy op.
  - So this conditions on a static covariate that is blind to the outcome.
  - Every S_late hit enters RAND, whatever its traced L_pre (pre-registered).
- **Yield.**
  - 386,140 genomes drawn; 59,543 screened; **33 hits** (21.2 CPU-min).
  - 29 of the 33 have L_pre ≥ 35; 25 of those have scorable pairs (target 20).
- **Enlarged RAND.**
  - 62 genomes with pairs; 35 at L_pre ≥ 30 (previously 10).
  - Median L_pre 38, against 39.5 for EVO_SD.
- **Checks.**
  - All hits re-confirmed.
  - The W2-13 worker-0 replay recovers exactly its 3 S_late-qualifying hits.

## Primary refit (EVO_SD vs RAND, X = L_pre)

| quantity | estimate | 95% CI | p / note |
|---|---|---|---|
| c_EVO | −0.45 pp | [−1.59, +0.70] | Freedman-Lane 0.66; stratified 0.41 |
| b (slope) | +0.12 pp per position | | |
| d (slope × EVO) | −0.003 | [−0.090, +0.077] | |
| GLM odds ratio, EVO | 0.93 | [0.72, 1.21] | |
| raw pooled gap | +0.15 pp | | EVO_SD 3.71% vs RAND 3.57% |
| length-matched | | | RAND 3.57% vs matched EVO 2.77% |

**Alternative fits (c_EVO, pp)**

| fit | c_EVO | 95% CI |
|---|---|---|
| L_exec | −0.32 | [−1.39, +0.77] |
| D_pre | −0.15 | [−1.38, +1.03] |
| frac_both_pre | −0.02 | [−1.24, +1.19] |
| all evolved vs RAND | −0.81 | [−1.74, +0.10] |
| common support | −0.87 | [−2.13, +0.43] |
| L_pre ≥ 30 | −0.62 | [−2.22, +0.95] |
| L_pre ≥ 35 | −0.67 | [−2.60, +1.07] |
| seed-12345 L_pre | −0.44 | [−1.61, +0.68] (not the pre-registered fit) |

Leave-one-out range for c_EVO: −0.59 to −0.26.

**Both-pre pair class**

| group | strict lethality |
|---|---|
| EVO_SD | 63/728 = 8.65% |
| enlarged RAND | 88/989 = 8.90% |
| old RAND | 22/366 = 6.0% |
| new hits | 66/623 = 10.6% |

- Difference: −0.24 pp [−3.9, +3.2].
- Mantel-Haenszel OR 0.91 [0.65, 1.27], p = 0.60.

**Binned by L_pre**

| L_pre | EVO_SD (n) | enlarged RAND (n) | new hits (n) |
|---|---|---|---|
| 30–45 | 3.3% (21) | 4.2% (17) | 4.1% (12) |
| 45+ | 5.5% (16) | 6.4% (18) | 8.1% (13) |

W2-13's 5 long hits sat at 3.2%. That drove its positive point estimate.

## Adversarial rounds
1. **Does the scheme import evolved structure?** No.
   - Evolved-enriched bigrams per genome: new 0.00, uniform 0.025, old RAND 0.056, EVO_SD 0.31, EVO_SF 3.5.
   - Nearest-evolved Hamming distance: median 62 (min 61), the same as uniform (62, min 60).
   - Shared 4-grams with evolved genomes: none.
   - Nibble distance to uniform: 0.047 (sampling noise is about 0.046).
2. **Does the scheme shift RAND at fixed length?** Possibly. New vs old RAND at matched L_pre differs by +1.16 pp [−0.37, +2.82]. **This is the strongest objection.**
3. **Hit rate.** 5.5e-4 vs W2-13's implied 2.5e-4 (p ≈ 0.04). The screen is deterministic, so this reads as sampling luck. 0 hits came from 16,326 screened rejects (2–3 expected).
4. **Bootstrap noise.** Covered by the 10-seed check above. The verdict is stable.

## Ledger entry (W2-20)
- **Result:** UNRESOLVED (upper bound 0.704 vs 0.7). T4(c′) not supported. An excess the size of the raw gap is excluded. W2-13's positive estimates came from short, sparse random hits.
- **Confidence:**
  - moderate-high that there is no evolved excess ≥ about 0.75 pp;
  - the 0.7 cut cannot be called either way.
- **Strongest objection:** the new-vs-old RAND offset at matched L_pre (+1.16 pp). Either the scheme or a non-linear slope could favour RAND.
- **Next:**
  - spline or binned L_pre fit, plus a pair-level random-effects model;
  - long hits drawn plain-uniform, to separate the scheme from the slope;
  - test early copy sites as backup routes.
