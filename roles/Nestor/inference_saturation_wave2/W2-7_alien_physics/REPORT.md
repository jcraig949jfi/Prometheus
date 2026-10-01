# W2-7: alien reproductive physics (directive item G)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Scope:** static only. No world or evolution run, no campaign edits, no git writes. About 27 CPU-min, `python -B`.
> - **Files in this folder:**
>   - `alien_vm.py`: VM variants built by source injection on the read-only campaign `z8.py`;
>   - `alien_pair.py`: P-11 and the `run_de` COMPETENT screen, with layout hooks;
>   - `variants.py`, `selftest.py` (→ SELFTEST.json), `probes.py` (→ PROBE_*.json), `extras.py` (→ PROBE_extras.json);
>   - `DIFFS.md`: world-level injection sketches.

## Summary
1. **What was built.** 10 variant families (15 arms), all by source injection.
   - All four self-tests pass, including bit-identity with the stock VM wherever a modification does not fire.
   - Every positive control passes 4/4 random paddings and every negative control fails 0/4. SIDERAND is the one exception: it has no genome-level negative.
2. **Physics alone moves the random-genome copier rate by more than 3 orders of magnitude.**
   - RING192: 90/12,000, against stock's 2/12,000 (about 40x). Its minimal copier is 2 bytes (`14 E5`).
   - SELFCOPY: 23% of random genomes are competent (702/3,000).
   - NOWRAP, NOBLOCK, ROTATE and REGRAND: 0/12,000 each.
   - **So the 2e-4 base rate is a property of the encoding and geometry, not of reproduction in general.**
3. **Evolved copiers depend on the physics.**
   - Absolute placement: 0/128 survive ROTATE.
   - 7-bit wrap: 7/128 survive NOWRAP.
   - Block op: 0/128 survive NOBLOCK.
   - They do **not** need partner execution: 128/128 survive Harvard confinement.
4. **Three supplied pathways that the Wave-1 list missed:**
   - **S8, the long count is also the terminator.** The count ends the donor's run in 113/128 genomes.
   - **S9, the slice length carries load.** Only 66/128 survive a 5x slice.
   - **S10, running first protects the donor.**
5. **Independent check.** REGRAND's survivors are exactly the 48 state-free genomes plus 3, which confirms the Wave-1 state-free classifier with independent code.

## Self-tests (all pass)

| test | what was compared | result |
|---|---|---|
| T1 | dense VM vs `run_dc.dense_z8()` | 6,000/6,000 identical |
| T2 | 8 VM variants vs dense, where the modification did not fire | 100% identical (≥ 501 cases each); every modification is live, changing state in 575–967 of 583–999 firing cases |
| T3 | `alien_pair.assay` vs `p11.assay` | 160/160 identical |
| T4 | `alien_pair.competent` vs `run_de.competent` | 0 mismatches over 319 genomes |

## Supplied pathways, revised

**S8: the long count is also the terminator.**
- `LD HL,0; LD DE,64; LD BC,64; LDIR` is competent on 0/4 paddings on stock. Adding a HALT makes it 4/4.
- Without the HALT, the donor keeps executing and re-runs the victim's copy. The victim's context then authors the final bytes, so the C4 check fails: donor share 0.017 at fidelity 0.94.
- In 113/128 evolved genomes the slice ends the copy, so nothing executes after it.

**S9: the slice length carries load.**
- At slice 1500, 62/128 evolved genomes lose competence.
- Of the failing draws, 120/186 fail on C2 (fidelity) and 4 on C4 (authorship): code running after the copy wrecks it.
- Real copy counts (164–295) are tuned to a 300-step world.

**S10: running first protects the donor.**
- When the random partner runs first, the stock motif misses fidelity 0.9 in 16/200 draws, against 0/200 when the donor runs first.
- So FOR Q5's side-0 switch may partly be a run-first advantage.

**Partner execution** is not needed for competence (Harvard: 128/128).

## Results

Columns:
- **positive / negative:** controls competent out of 4 random paddings.
- **panel (SF):** survivors among the 128 competent dense genomes, with state-free survivors out of 48 in brackets.
- **random hits:** paired random genomes, the same genomes in every arm. Stock pooled with FOR is 5/26,024 ≈ 1.9e-4. A result of 0/12k only bounds the rate below 2.5e-4.
- **minimal copier:** t = instructions, B = bytes.

| arm | positive | negative | panel (SF) | random hits | minimal copier |
|---|---|---|---|---|---|
| STOCK | `1E40E5` 4 | NULL 0 | 128 (48) | 2/12k | 2t/3B (19 copiers) |
| STOCK_B1500 | 4 (rate 0.5–0.85) | 0 | 66 (24) | 0/3k | – |
| A_NOBLOCK | LOOP 4 | `1E40E5` 0 | 0 | 0/12k | none ≤ 2t; LOOP is 8B |
| A5_NOBLOCK_B1500 | LOOP 4 | 0 | 0 | 0/3k | – |
| B_EXPLEN | EXPL_H 4 | 0 | 100 (44) | 1/12k | 3t/4B (`1E40 43 E5`) |
| C_NOWRAP | `1E40E5` 4 | `1EC0E5` 0 | 7 (2) | 0/12k | 2t/3B (10 copiers) |
| **C2_RING192** | 4 | `1EC0E5` 0 | 34 (11) | **90/12k** | **2t/2B** (`14E5`, `14E7`, `24E7`) |
| C3_RING192_RGAP | 4 | 0 | 26 (8) | 77/12k | – |
| D_HARV_HALT | 4 | XJUMP 0 (stock 4) | 128 (48) | 4/12k | 2t/3B |
| D2_HARV_WRAP | 4 | XJUMP 0 | 127 (48) | 5/12k | – |
| E_REGRAND | STATEFREE_H 4 | `1E40E5` 0 | 51 (48) | 0/12k | 3t/5B (`1E40 ED32 E5`) |
| F_ROTATE | SELFLOC_H 4 | `1E40E5` 0 | 0 | 0/12k | none ≤ 3t; a hand-built SELF locator is 7B |
| G_BLOCK_OWN | LOOP 4 | 0 | 0 | 0/12k | none ≤ 2t |
| H_RELADDR | `1E40E5` 4 | `2E40E5` 0 | 105 (48) | 1/12k | 2t/3B |
| I_SIDERAND | 4 (rate 0.55–0.8) | none | 118 (47) | 3/12k | 2t/3B |
| J_SELFCOPY | `E5` 4 | NULL 0 | 125 (48) | 702/3k | 1t/1B |

**Mechanism checks:**
- **RING192.** 256 ≡ 64 (mod 192), so a change of 1 in the high byte (D or H), irrelevant on the 128-byte ring, now produces the copying offset.
- **ROTATE.** The victim's fidelity equals (64 − r)/64 exactly.
- **RELADDR.** The stock side-0 motif becomes a side-1 donor in 49/80 cases (0/80 on stock).
- **HARV.** It gains side-1 copiers because the halt at the half edge acts as a terminator.

## Theory predictions per variant

Theories T1–T7 are as in NPE_COMPETING_THEORIES.md.

| variant | predictions |
|---|---|
| NOBLOCK / BLOCK_OWN | Acquisition collapses; downstream dynamics need seeding. |
| EXPLEN | Adds a new organism-side function: halting after the copy. |
| NOWRAP / RING192 | The rate follows the address arithmetic, and the core composition shifts from E/L setters to D/H. |
| HARV | **The unique test of T5:** hijack births should drop beyond a Φ recomputed under HARV. |
| REGRAND / VE-RAND / VE-RESET | Separates T1 from T2. |
| ROTATE | Collapse predicted. |
| RELADDR / SIDERAND | Is the side-0 switch geometry, or run-first advantage? |
| SELFCOPY | Reverse control for T7. |

Layout variants must patch both `world._pair_interact` and `p11.interact`. Otherwise the ruler certifies events under stock physics.

## Attack loop (summary)

| variant | confound | resolution |
|---|---|---|
| NOBLOCK | budget | B1500 arm (which is itself confounded by S9) |
| EXPLEN | first control flawed | switching to HALT-terminated controls exposed S8 |
| RING192 | inert gap | random-gap arm: 77 vs 90, so the modulus dominates |
| HARV | adds a terminator | compare against Φ recomputed under HARV |
| REGRAND | randomizes both contexts | use the newborn-only arms |
| ROTATE | equivalence | verified analytically |
| RELADDR | – | labelled an alteration, not a removal |
| SIDERAND | no negative control | liveness shown mechanically |

Rarity claims rest only on minimal-copier length and the panel, never on a 0/12k count.

## Ranking by information per cost

1. **C2_RING192** (a one-line world edit).
   - Acquisition stays endogenous and rises about 40x, while 94/128 evolved solutions die.
   - Frozen predictions:
     - T1: about 85% of runs have a competent genome by epoch 100 (stock about 7%).
     - T3: D/H setters appear in the core, with a different self-poisoning modulus.
2. HARV_HALT: the clean test of T5.
3. VE-RESET / VE-RAND: T1 vs T2.
4. SIDERAND.
5. EXPLEN.
6. RELADDR.
7. SELFCOPY.
8. NOWRAP.
9. NOBLOCK / BLOCK_OWN.
10. ROTATE.

## Ledger entry (W2-7)
- **Result:**
  - Physics moves the base rate by 3+ orders of magnitude. The minimal copier ranges from 1B (SELFCOPY) to 8B (NOBLOCK).
  - Evolved copiers rely on absolute placement, the 7-bit wrap, the block op, slice 300 and zero registers (except the state-free 48). They do not rely on partner execution.
  - New supplied pathways: S8 terminator, S9 slice, S10 run-first.
  - REGRAND reproduces the state-free classification (48/48).
- **Confidence:**
  - static facts: high;
  - RING192 ratio: moderate, but the order of magnitude is secure;
  - in-world predictions: none.
- **Strongest objection:** these are static, fresh-state, single-interaction measurements. Establishment and the dynamics after takeover need in-world tests. Several arms change two things at once.
- **Next:**
  1. Freeze RING192 predictions, then run a bounded 48+48 RING192 vs STOCK test. This needs authorization.
  2. Run HARV_HALT in a SELF-enabled cell.
  3. Re-audit Wave-1 claims that assume slice 300 or that side 0 runs first.
  4. Add a terminator audit to the competence certificate.
