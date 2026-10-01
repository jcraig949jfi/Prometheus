# W2-14: calibrating theory F (U3), and the c7c vs W2-2 600x disagreement

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Files (this folder):** `ffield.py` (the process), `v0_bitexact.py/.json`, `b0_banks.py/.json` (+ `banks.pkl`), `l1_ladder.py` + `ladder.jsonl`, `a1_summary.py/.json`, `a2_kin_signature.py/.json`.
> - **Run conditions:** about 45 CPU-min (40 budgeted). No git writes. No `Runner.run()`.

## Short answer
- **The c7c vs W2-2 ~600x disagreement is not a field effect.** It comes from three things: c7c's empty-register partners, its uncertified readout, and W2-2 comparing unlike readouts.
- **BASE:** with realistic partner registers, F-style processes stop over-predicting.
- **ATOMIC validation (≈ 0.52) did NOT pass** on causal readouts at 300 epochs.
- **A kin/density second regime is neither shown nor ruled out.**

## 0. The process and the bit-exact check

- **Cell and runners.** 7ae3's arm-B cell (atlas_axis NONE, tier M), on a runner that is constructed and never run. BASE uses `world.Runner`. ATOMIC uses `run_ds.runner_cls(world)`.
- **Field.** The runner's own 256 organisms, placed as `run()` places them.
- **Each epoch.** `_env_epoch()`, then shuffle-and-pair. Every pair that contains a founder-lineage member goes through the world's own `_pair_interact(i, a, b)`.
- **Switchable ingredients:**
  - **Structure:** FIELD (partners drawn from the current field, so kin pairing and density are present) or FREE (each member gets a private background partner; this is the c7c / h1 setup).
  - **Partner:**
    - FULL: background pairs also interact;
    - BANK: at contact, draw genome + registers from a founder-free field at that epoch;
    - POOL: a fresh random genome with post-interaction registers (h1);
    - FRESH0: a fresh random genome with empty registers (c7c).
  - **Context:** CARRY or ZERO.
  - **Mutation:** ON or OFF.
- **v0 bit-exact check.** FIELD+FULL on X-TICKET seeds reproduces X-TICKET's per-epoch trajectories exactly. 4/4 seeds over 40 epochs, including two runaways (s35, s59) and every P-11 causal flag. The first attempt diverged only because pair index 0 had been passed, and the P-11 assay seed includes that index.
- **Background alone.** A founder-free BASE field gives 1 birth in 300 epochs and depth 0. Under ATOMIC the background stays random.

## 1. The 600x, and the second regime

### 1a. BASE results (40 seeds per row, horizon 300)

| process | occupancy ≥ 40 | B ≥ 163 | depth ≥ 20 | B bins: 0 / 1-4 / 5-26 / 27-162 / ≥ 163 |
|---|---|---|---|---|
| FREE FRESH0 (c7c's model) | 0.225 | 0.125 | 0.075 | 14 / 12 / 4 / 5 / 5 |
| FREE POOL (h1's model) | 0.025 | 0 | 0 | 23 / 13 / 4 / 0 / 0 |
| FREE BANK | 0.050 | 0 | 0 | 31 / 5 / 3 / 1 / 0 |
| FIELD FRESH0 | 0.125 | 0.050 | 0.050 | 20 / 14 / 4 / 0 / 2 |
| FIELD POOL | 0.025 | 0 | 0 | 24 / 13 / 2 / 1 / 0 |
| FIELD BANK | 0.075 | 0.025 | 0.025 | 23 / 11 / 4 / 1 / 1 |
| FIELD BANK, ctx ZERO | 0.100 | 0.075 | 0.075 | 19 / 13 / 5 / 0 / 3 |
| FIELD BANK, mutation OFF | 0.100 | 0.075 | 0.075 | 18 / 11 / 8 / 0 / 3 |
| **World** (X-TICKET, 128 runs; depth read at 2000 epochs) | 0.031 | 0.031 | 0.031 | 69 / 37 / 18 / 0 / 4 |

**How the 600x decomposes:**
1. **Partner registers are the main cause.**
   - Going from FREE FRESH0 to FREE POOL: B ≥ 163 falls 5/40 → 0/40 (p = 0.027), and occupancy ≥ 40 falls 9/40 → 1/40 (p = 0.007).
   - This also explains c7's child conversion of 0.85: children inherit the leftover context of an empty-register victim.
2. **The readout adds about 3x.**
   - Within FREE FRESH0: occupancy 0.225, certified births 0.125, depth 0.075.
   - Outside the world, occupancy is contaminated by label floods with B ≈ 0 (FIELD FRESH0 s21, FIELD POOL s23, FIELD BANK s36, FREE POOL s25).
   - In the world, all three readouts coincide at 4/128.
3. **W2-2 compares unlike readouts.**
   - Its 0.0003 is the tail of an infinite-population law below replacement (m_c 0.77).
   - The world's B is counted in a finite field and includes kin re-conversions after saturation. In the three big runaways, B exceeds net label growth by 719-2284 births.
   - **On a readout both sides define the same way, P(the lineage ever reaches ≥ 27 certified births), the law gives about 0.025 and the world 4/128 = 0.031. They agree.**
   - The only difference is what happens *after* a big burst: the law says it dies out, the world says it fills the field.

### 1b. Is there a kin/density second regime?
**Not demonstrated, not refuted.**
- Realistic FREE partners give 0/80 runaways. That is consistent with both the law and the world (world vs FREE, p = 0.14).
- The FIELD BANK family gives 7/120, against 0/40 for FREE BANK (p = 0.13).
- **The empty 27-162 gap is weak evidence.**
  - Its edges sit on observed runs: s2 ends at B = 26 and s14 at B = 163.
  - The law expects about 3.1 runs inside the gap, so seeing none has P = 0.045, before correcting for the edges having been chosen from the data.
- **What the world trajectories show (a2).**
  - Runaways pass 27 members by real growth (B ≈ label count, 10-37).
  - Births per member do **not** rise afterwards: 0.07-0.31 before, 0.04-0.13 after.
  - The difference is on the loss side: s2 stalls at 28 (rate 0.247 → 0.011), and the runaways do not.
- **Two untested mechanisms:**
  - overwrite by kin is cost-free;
  - kin re-conversion repairs eroded, sterile members.

## 2. F calibration

**BASE.**
- With POOL or BANK partners, the process predicts 0-0.025 against 0.031 observed.
- What closes the over-prediction is the partner's register state.
- Kin pairing, density, context carry and mutation are inconsistent or not significant.
- **Caveat:** 0/40 cannot separate 0.0003 from 0.031 (95% upper bound 0.088). This shows "no longer over-predicting", not "calibrated".

**ATOMIC (the validation case): not passed.**

| source | depth ≥ 20 | B ≥ 163 | occupancy ≥ 40 |
|---|---|---|---|
| model, FIELD BANK, C-ATOMIC seeds 0-29, 300 epochs | 0.233 | 0.333 | 0.467 |
| world, same seeds (depth read at 2000 epochs) | 20/30 = 0.67 | | |
| world, C1 overall | 0.575 | | |
| world, X-ATOMIC | 36/64 | | |

- Per-seed agreement is weak: 9 both, 5 model-only, 11 world-only, 5 neither.
- It is open whether the gap is the horizon (300 vs 2000 epochs) or a real under-prediction.
- c7c's earlier 0.55 "fit" used empty-register partners, so it is not credited.

**BRIDGE C7: not run.** c8 also uses `p_state=(None,0,0)`, so its 0.44 is expected to shrink.

## 3. Where the map-built process stops testing F

**The rungs, from least to most world-like:**
1. FREE with FRESH0 partners.
2. POOL (realistic partner registers).
3. BANK (a realized founder-free background).
4. FIELD (kin pairing and density).
5. FULL, which is the world itself.

**What each rung can test:**
- **Rung 5** is the world, bit-exact, so agreement there is uninformative.
- **Rung 4** already contains a population term, so F's "no lineage term" fails in substance.
- **Rung 3** is mildly circular.
- **Rung 2** is the last rung where partners are purely external.

**Conclusion.** F is a genuine test only with founder-independent, non-kin, externally supplied partners (rungs 1-3).
- On that reading, BASE passes ("no over-prediction") and ATOMIC fails or is open.
- If kin and field-shaped partners count as part of F, F cannot be falsified for this cell: it says only that the world computes itself.

## Ledger entry (W2-14)
- **Result:**
  - c7c's over-prediction comes from empty-register partners (p = 0.027 and 0.007) plus an occupancy readout (about 3x).
  - With realistic partners the process predicts 0-0.025 vs 0.031.
  - W2-2's 0.0003 came from comparing unlike readouts. On P(reach ≥ 27 certified births), law 0.025 vs world 0.031 **agree**.
  - The second regime is not demonstrated. The only world signal is that large lineages persist; fertility does not rise.
  - The ATOMIC validation did not pass at 300 epochs.
- **Confidence:**
  - high: partner registers as the cause;
  - medium: the W2-2 readout reconciliation;
  - low: F calibrated for ATOMIC;
  - undecided: the second regime.
- **Strongest objection:**
  - The ATOMIC precondition failed or is horizon-censored.
  - The BASE result rests on 0-1 events per 40 runs.
  - The partner banks themselves come from world runs.
- **Next:**
  1. The world itself (FIELD+FULL) under ATOMIC, seeds 0-29, 300 epochs (about 10 CPU-min).
  2. A static repair test for eroded BASE members.
  3. c8 with carried partner registers.
  4. FREE vs FIELD BANK under BASE at about 300 seeds each, to decide the second regime.
  5. Preregister the gap edges before any "empty gap" claim.
