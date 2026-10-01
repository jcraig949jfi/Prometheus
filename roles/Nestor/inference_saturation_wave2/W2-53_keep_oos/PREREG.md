# W2-53 PREREG: out-of-sample test of W2-42's static side-0 keep association on W2-37's fresh seeds

Written **2026-10-01T03:15:49Z** (`date -u`), before any replay or assay in this folder.

## What has been looked at before this file
- W2-42 REPORT and scripts (r1_replay.py, a2_assay.py, a4_panel.py, a5_summarize.py); W2-29 w29.py; W2-22 w22.py;
  W2-37 PREREG.md and p1_run.py.
- W2-37 run records, **scalar outcome fields only** (B, B_xk, stop, cpu_s): to size the conditioned set and budget.
  Seen: FIELD 600 runs, 27 with B >= 27 (6 with B_xk >= 163); FREE 1200 runs, 50 with B >= 27 (10 with
  B_xk >= 163, all stop = free_cap256; 25 cap-stopped with B < 163; 15 frozen). No genome, keep or jump data of any
  W2-37 run has been seen (none exist yet).
- Classifier calibration on **W2-42's in-sample panel only** (a4_panel.json): the jump flag below reproduces W2-42's
  "351/351 STRONG carry the jump; 27/1069 non-STRONG copiers do" exactly; F has no flag.

## Hypothesis H-KEEP
Among W2-37 runs with B >= 27, the births-weighted static side-0 keep of the founder-family causal lineage is higher in
successes (B_xk >= 163) than in failures.

**Per-run statistic (primary), k0:** W2-42 a5's `k0` = mean static side-0 keep (`keepF0`, W2-30 t2 scorer via W2-42
`a2_assay.work`, unchanged) over a births-weighted sample of the run's causal-lineage child genomes. W2-42's in-sample
"median 0.894 vs 0.598" is the group median of this per-run quantity. Sensitivity: per-run *median* keepF0 of the
same sample.

## Sampling (same as W2-42 a4)
- Births pool = multiset of recorded causal-lineage child genomes (genome repeated by its birth count), in genome
  first-birth order (W2-29's `G` insertion order).
- **Window (primary):** births up to the end of the epoch in which B_xk first reaches 163 - this is exactly W2-29's
  `xk163` stop, which defined W2-42's pool. For runs that never reach 163, all births to the W2-37 stop.
  Sensitivity: all births to the W2-37 stop for every run.
- Up to **50 births per run**, `random.Random("W2-42a4|%s|%d" % (arm, s)).sample(pool, 50)` with arm in
  {FIELD, FREE}; whole pool if <= 50.

## Classes and censoring
- Conditioned set: W2-37 runs with B >= 27 (FIELD BANK s = 50000..50599; FREE BANK s = 50000..51199).
- Success: B_xk >= 163 (final record). Failure: B_xk < 163.
- **FREE cap censoring (primary):** a run stopped at `free_cap256` with B < 163 and B_xk < 163 is censored (the cap cut
  it off before B_xk could reach 163) and is **excluded from the failure class**. Cap runs with B_xk >= 163 are
  successes. FIELD has no cap; FIELD `horizon` failures are the defined outcome at T = 300 and stay failures.
- **Sensitivity (reported, not decision-bearing):** censored FREE runs counted as failures.
- Expected primary sizes: FIELD 6 S / 21 F; FREE 10 S / 15 F (sensitivity 10 S / 40 F).

## Tests (primary sample)
1. **Per arm:** one-sided Mann-Whitney U (scipy `mannwhitneyu`, alternative = "greater", default method), k0 of
   successes > failures, alpha = 0.05, separately for FIELD and FREE.
2. **Pooled stratified (decision-bearing):** van Elteren stratified Wilcoxon, strata = {FIELD, FREE}, weights
   1/(N_s + 1), tie-corrected variance, normal approximation, one-sided (successes greater). A stratified permutation
   p (labels permuted within stratum, 20,000 draws, rng seed "W2-53|perm") is reported as a check.
3. **Secondary prediction:** per-run STRONG share (fraction of sampled births in W2-42's STRONG band: not MORPH
   [convF0 >= 0.5], not NONCOPIER [max(convF0, convF1) < 0.5], keepF0 >= 0.85) predicts success with
   **AUC > 0.7**. Decision-bearing AUC = pooled AUC over both arms' primary runs (Mann-Whitney U / (n_S n_F), ties
   0.5). Per-arm AUCs reported.

## Decision rule (primary sample)
- **SUPPORTED** if pooled van Elteren p < 0.05 **and** pooled STRONG-share AUC > 0.7.
- **REFUTED** if pooled van Elteren p > 0.5.
- **UNRESOLVED** otherwise.
- The sensitivity verdict (censored FREE runs as failures) is computed by the same rule and reported; if it differs from
  the primary verdict this is stated as a fragility, the primary verdict stands.

## Bit-exactness gate (before any scoring)
- Replay = W2-22 `w22.run2` body copied verbatim (mech branches inert, mech = None) + W2-29/W2-42 passive recorder
  (genome of each causal-lineage child read with `r._genome(vic)` after the interaction; no rng use, no world writes),
  called exactly as W2-37 p1_run.py: BASE, seed 9_998_000 + s, struct, BANK, CARRY, MUT ON, T 300, BASE bank + POOL,
  traj on, stop "xk".
- Every conditioned run must match its W2-37 record on all output fields (epochs, stop, B, Ball, maxA, A_end, N_end,
  depth_f, depth_world, calls, Bxk, kin, n_mech) and on `traj` where the record kept it.
- A mismatching run is excluded and listed. If more than 2 runs mismatch, the test is **NOT_VERIFIED** (no verdict).

## Descriptive readouts (not decision-bearing)
- Per run: k0, median keep, STRONG/PARTIAL/F-LEVEL/LOW/MORPH/NONCOPIER shares, mean class m, and **jump-class
  presence**: share of sampled births whose genome carries a JP-type opcode (C3, C2, CA, D2, DA) at p in 0..51 with
  7-bit target (g[p+1] & 0x7F) >= 64 (W2-42's absolute upper-half jump; calibrated above), and the first epoch at
  which a jump-carrying birth occurs.
- Class m success vs failure (one-sided MW), as in W2-42.

## Budget
<= 30 CPU-min total, <= 5 processes, `python -B`. Estimated: replay ~17 (FIELD) + ~2.4 (FREE) CPU-min from W2-37
cpu_s, plus recorder overhead; assay ~5 CPU-min. FREE replays first, then FIELD. If cumulative CPU passes 28 min the
remaining work stops and the completed set is reported with the shortfall stated.
