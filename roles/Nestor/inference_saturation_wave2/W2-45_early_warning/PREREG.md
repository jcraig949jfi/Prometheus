# W2-45 PREREG: out-of-sample early-warning test (W2-2 EW-1/1b/2) + one new observable (EW-N)

Written 2026-10-01T03:03:43Z (`date -u`), before any early-warning quantity was computed on W2-29 FULL, W2-22 or W2-37
data. Analysis of existing records only; no simulation.

## What I had seen before writing this (disclosure)
- W2-2 REPORT (rules fitted in-sample on X-TICKET, 4 runaways / 124 others).
- W2-29 REPORT: per-run outcome counts and the composition table of the 13 B_xk/B successes (which runs are side-0
  dominated, which have no side-0 genome, s1469 = 78% 43->C3). So EW-N below is NOT blind to which successes carry
  side-0/C3 genomes at all; it is blind only to WHEN they first appear and to the controls' early genotypes.
- W2-26 REPORT: "some side-0 converter appears before depth 20 in 12/12 runaways vs 4/11 controls" (W2-17 cells).
- Record schemas only (field names), not values, of runs_FULL.jsonl / genomes_FULL.jsonl / W2-22 / W2-37 runs.

## Data
- FULL: W2-29 `runs_FULL.jsonl` (600 seeds, s 1000-1599). **No per-epoch trajectory is stored.** Per run: B, Bxk, kin,
  epochs, stop, maxA, depth. For the 22 runs with B >= 27 only: `genomes_FULL.jsonl`, one row per distinct causal
  genome = [hex, first_epoch (0-based), B at its first birth (inclusive), count].
- BANK models: W2-22 `runs_FIELD.jsonl` (600, s 1000-1599) and `runs_FREE.jsonl` (1200); W2-37 `runs_FIELD.jsonl`
  (600, s 50000-50599, only if W2-37 FIELD has logged DONE) and `runs_FREE.jsonl` (1200). traj = (N, A, B, Bxk) per epoch,
  kept only when maxA >= 10.

## Outcomes (both reported; primary = B_xk >= 163, the W2-29/W2-22 runaway criterion)
- R_xk: Bxk >= 163. R_B: B >= 163 (W2-2's "lineage reaches >= 163 certified births").
- FREE cap256 runs with outcome < 163: censored -> C- (non-runaway) and C+ (runaway) both reported.

## Observables (epoch e is 1-based; traj[e-1] = end of epoch e; genome first_epoch f (0-based) = epoch f+1)
- EW-1: B(15) - B(10) >= 3.
- EW-1b: max over e in 11..20 of B(e) - B(e-1) >= 2.
- EW-2: B(5) >= 4.
- EW-4 (necessity check only): first founder-lineage birth by epoch 10.
- EW-3, EW-5, EW-6: not computable from these records (need D0 / law fit / post-takeover census); reported as such.

## Reconstruction where traj is absent (fixed before looking)
Each run gets alarm in {1, 0, ?}.
- Certain negatives: B < 3 (EW-1), B < 2 (EW-1b), B < 4 (EW-2); run ended (extinct) at epochs <= 10 (EW-1, EW-1b).
- Frozen-inferred negatives (tier 2, declared assumption): stop == "frozen" means no anc0-parent birth in the last 100
  epochs, so the last birth is at 0-based epoch epochs-101; if that is <= 9, no birth in epochs 11-20 -> EW-1, EW-1b = 0.
  Assumption: every causal birth is also an anc0-parent birth. Checked on traj-bearing BANK runs and FULL E27 genome rows.
- Genome bounds (FULL B >= 27 runs and BANKREP): B_end(e) >= max{B_first : f <= e-1}; B_end(e) <= min{B_first : f >= e} - 1
  (else final B). Window counts take lower/upper bounds from these; an alarm is 1 if the lower bound meets the threshold,
  0 if the upper bound fails it, else ?.
- Scoring with ?: hit and FA computed under both imputations (all ? -> 0, all ? -> 1). PASS rule (W2-2): hit >= 0.75 AND
  FA <= 0.03. Verdict PASS iff PASS under both imputations; FAIL iff FAIL under both; else UNRESOLVED (data-limited).
- CIs: Wilson 95% for hit, FA, PPV.

## Model processes (task 3)
Same observables, same rule, on FIELD BANK and FREE BANK. "Generic" claim requires PASS (or at least the same
hit/FA pattern within CIs) in the BANK arms; a FAIL there with PASS in FULL = world-specific.

## EW-N (new, pre-registered; scored on FULL only)
- **Definition.** Alarm iff the causal lineage has, among genomes first born in epochs 1-20 (first_epoch <= 19), at least
  one that is (a) a side-0 converter, W2-29 `c1_classes.json` field `side0` (c0 >= 0.5 and c1 < 0.5 on the fixed 16-
  partner panel), or (b) the 43->C3 keep variant (byte 43 == 0xC3; founder has 0xC1).
- **Population.** Genomes are recorded only for B >= 27 runs, so EW-N is scored on the FULL E27 stratum (B >= 27,
  n = 22) as a CONDITIONAL discriminator (eventual E27 runs only; not a deployable unconditional warning). Stated
  as a limitation up front.
- **Rule.** Same PASS rule within the stratum: hit >= 0.75 and FA <= 0.03 (i.e. zero false alarms) on R_xk; R_B also
  reported. Comparator: EW-1b within the same stratum.
- **Sensitivity (descriptive, not rule-bearing).** Windows epochs 1-15 and 1-30; side-0 alone; C3 alone; ring
  definition (side0 and (de & 127) == 64); EW-N AND EW-1b.
- **Pre-stated expectation.** From W2-29's "morph by B <= 27" table (FULL 4/9 vs 4/13) I expect EW-N to FAIL the FA
  bound; a PASS would be a surprise.

## Budget
<= 15 CPU-min, python -B, no simulation, no writes outside W2-45_early_warning/.
