# W2-29 PREREG: is the world's post-27 persistence background residue (FULL vs BANK), morph emergence, or neither?

Written 2026-10-01T02:28:12Z (`date -u`), before any production simulation in this folder.
(Only a 2-seed, 25-epoch timing pilot on seeds 5000/5001, outside the production range, was run: 3,200 FULL calls in 0.83 CPU-s.)

## Process
- W2-14 `ffield.py` + W2-22 `w22.run2` logic (both imported, unedited). BASE, 7ae3 arm-B cell (atlas_axis NONE, tier M),
  X-TICKET seeding (BASE seed = 9_998_000 + s), CTX CARRY, MUT ON, horizon T = 300.
- `w29.run3()` = a copy of `w22.run2` with (a) a passive recorder of the genome of every child counted in B
  (child genome read with `r._genome(victim)` after the world's `_pair_interact`; read-only), and (b) stop rule `xk163`:
  stop as soon as B_xk >= 163 (outcome decided; dynamics before the stop are unchanged). Other stops as W2-14/22
  (extinct; frozen = epoch >= 100 and no anc-0-parent birth for 100 epochs). No runaway/depth stop.
- **Equivalence gate:** before production, `run3(..., stop="orig", rec=False)` must equal `w22.run2(..., stop="orig")` on all
  output fields for >= 6 seeds per arm (FULL and BANK), and `run3` FULL must equal `ffield.run` FULL. If not, nothing runs.
- Arms (seed-matched, s = 1000..1599, same seeds as W2-22 FIELD BANK):
  - **FIELD FULL** (= the world; background-background interactions and residue kept).
  - **FIELD BANK** (W2-22's runs; background partners replaced by bank draws at contact). Conditioned BANK runs
    (B >= 27, 33 runs) are **replayed** with `run3` (BANK, stop xk163) only to record genomes; replay B/B_xk must match
    W2-22's records (for runs that did not reach B_xk >= 163) or the replay is flagged.
- Seed order: FULL runs are dispatched in seed order with an ORDERED map. If the budget stops FULL early, the analysed set is
  the **contiguous completed seed prefix** 1000..S, and BANK is restricted to the same prefix (prevents duration bias).

## Readouts
- B, B_xk exactly as W2-22 (B_xk = counted births whose victim was not a founder-label member before the interaction).
- Conditioning event E27: B >= 27 by epoch 300.
- **Primary:** P(B_xk >= 163 | E27), FULL vs FIELD BANK.
- **Morph (per conditioned run):** a recorded lineage genome g is a **side-0 morph** if, on a fixed 16-partner panel
  (W2-14 BASE bank, epochs 10-299, rng "W2-29", partner bank registers, donor ZERO context, copy errors off; W2-3
  `common.outcome`), conv_side0 >= 0.5 and conv_side1 < 0.5. **Genotype-confirmed** additionally requires the W2-24 mechanism:
  with g at side 0 (traced stock z8, W2-24 `tvm.pair_t`, partner = panel partner 0), the first LDIR executed by side 0's own
  context has destination DE = 0x0040 (64). Founder control must test negative; 44->AC and 49->5C must test positive.
- Per run: morph_present (any confirmed morph among recorded genomes up to the run's stop), first epoch, and B at first
  appearance; morph_by27 (first appearance at B <= 27).
- Births recorded: every child counted in B (causal-lineage). Classification is done afterwards, in a separate process.

## Eligibility (computed before running)
- FULL conditioned rate prior: world X-TICKET 4/128 = 0.031 (95% CP 0.009-0.078). FIELD BANK realized 33/600 = 0.055.
- Expected conditioned FULL runs at 600 seeds: 18.6 (p = 0.031); P(>= 10) = 0.99; at 400 seeds 12.4, P(>= 10) = 0.80.
  At the CP lower bound 0.009, 600 seeds give 5.2 -> INELIGIBLE likely.
- Cost projection: FULL BASE ~0.26 ms/call, 128 calls/epoch -> ~3.3 CPU-s per 100-epoch run; W2-22 FIELD BANK averaged 3.6
  CPU-s/seed, with conditioned horizon runs at ~90 CPU-s. FULL projected ~6-8 CPU-s/seed -> 600 seeds ~60-80 CPU-min.
  BANK replay of 33 conditioned runs <= 14 CPU-min (less with xk163). Classification ~2-5 CPU-min.
- **Budget rule:** FULL production hard-stops at cumulative 62 CPU-min. **ELIGIBLE iff the FULL prefix has >= 10 conditioned
  runs.** If < 10: INELIGIBLE; switch to the fallback (existing X-TICKET/X-RUNAWAY world runs + W2-22 FIELD BANK,
  morph-stratified) with the same rule below, labelled FALLBACK.

## Decision rule (pre-stated; one-sided Fisher exact, alpha 0.05; success = B_xk >= 163 among E27 runs)
- **RESIDUE supported** if, within the NO-MORPH stratum, FULL > BANK with p < 0.05.
- **MORPH supported** if, within EACH arm separately, morph-present > morph-absent with p < 0.05 (both arms).
- Both supported -> report BOTH. Neither -> **UNRESOLVED**. A stratum with 0 runs in a cell makes that test undefined
  (counts as not supported).
- Secondary (not rule-bearing): the same tests with morph_by27 instead of morph_present (guards against reverse causation:
  big runs make more births, hence more chances to switch); the unstratified FULL vs BANK primary; the B-based readout
  P(B >= 163 | E27); Mantel-Haenszel across strata.

## Budget
<= 90 CPU-min total, <= 6 processes (Pool(5) + parent), `python -B`. No git writes. No kills of processes I did not start.
