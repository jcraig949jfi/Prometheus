# W2-49: EW-1 and EW-1b FAIL out of sample (W2-45 unknowns resolved)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Written:** 2026-10-01T03:15:36Z.
> - **Compute:** 16.9 CPU-min.
> - **Files:** `w49.py`, `p1_replay.py`, `p2_tier2_audit.py`, `a1_rescore.py`, `unknown_sets.json`, `runs_replay.jsonl`, `runs_tier2_audit.jsonl`, `a1_rescore.json`, logs.

## Answer
All 72 unknown seeds were replayed, every one bit-exact (19/19 summary fields). Under W2-45's frozen rule (hit ≥ 0.75 AND false alarm ≤ 0.03), **EW-1, EW-1b and EW-2 all FAIL.**

**Results (B_xk target):**
- **EW-1:** hit 8/8; false alarm 28/592 = **0.047** [0.033, 0.068]. FAIL.
- **EW-1b:** hit 8/8; false alarm 23/592 = **0.039** [0.026, 0.058]. FAIL.
- **EW-2:** FAIL under both imputations. 68 EW-2-only unknowns were not replayed.
- **B target:** gives the same picture (EW-1 FA 0.046, EW-1b FA 0.037).

**Why they fail:**
- W2-45's condition for a PASS was that ≤ 4 of the 66 small unknowns fire. **14 fired.**
- The false alarms are split roughly evenly: 14/14 intermediates, plus 14 (EW-1) or 9 (EW-1b) small lineages with B between 11 and 26.
- Neither group alone breaks the bound; together they do.
- Seed 1303 fires, but only just: B10 = 20, B15 = 24, B20 = 26.

## Checks on the replays
- **Code changes are passive.** The only edits are a TRAJ append and the import path.
- **Trajectories are self-consistent** across all 97 runs.
- **Seeds 1303 and 1355 match at genome level.**
- **Tier-2 audit.** 25 frozen-inferred negatives with B ≥ 7: all bit-exact, 0 alarms.

## Table (FULL, n = 600, B_xk target)

| EW | TP / FN | FP / TN | hit | FA [Wilson] | PPV | verdict |
|---|---|---|---|---|---|---|
| EW-1 | 8/0 | 28/564 | 1.00 [.68, 1] | 0.047 [.033, .068] | 0.22 | **FAIL** |
| EW-1b | 8/0 | 23/569 | 1.00 [.68, 1] | 0.039 [.026, .058] | 0.26 | **FAIL** |
| EW-2 | 4–7/8 | 55–120 | 0.50–0.88 | 0.093–0.203 | ≤ 0.07 | **FAIL** |

The PASS line is 17 false alarms. The 14 intermediates alone use 14 of them.

## Adversarial points
1. **The FAIL rests partly on counting intermediates as false alarms.**
   - A "lineage reaches 27" target would give EW-1 a false-alarm rate of 0.024 and pass.
   - That target is post hoc and would need a new prereg.
2. **Tier-2 negatives can only add false alarms**, so the FAIL is robust.
3. **The replay is the same world:** 19 fields match across 97 runs.
4. **EW-1b sits near the line:** its CI lower bound is 0.026. PPV ≤ 0.26 for both.
5. **The 8/8 hit rate is n = 8,** and 1303 is marginal.
6. **The scorer was executed from W2-45's own source.**

## Ledger entry (W2-49)
- **Inference:**
  - W2-2's EW-1 and EW-1b do not survive out of sample.
  - They pick up fast early growth, catching every runaway, every intermediate and about 2.4% of small lineages.
- **Confidence:**
  - high: EW-1 FAIL;
  - medium-high: EW-1b FAIL;
  - high: intermediates fire 14/14.
- **Strongest objection:** the target definition (see adversarial point 1).
- **Next:**
  1. A pre-registered runaway-vs-intermediate discriminator on a ≥ 2,000-seed trajectory batch.
  2. A pre-registered "reaches 27" target.
  3. Test whether runaways split into fast and slow classes.
