# W2-28 draft: WAVE-2 CORRECTIONS block for NPE_COMPETING_THEORIES.md

**Drafted:** 2026-10-01T02:31:27Z (`date -u`), by the W2-28 worker.
**Status:** this is a draft for Nestor to append. NPE_COMPETING_THEORIES.md has **not** been edited.
**Sources:**
- INFERENCE_LEDGER.md from the W2-6 entry onward;
- REPORTs W2-2, 3, 6, 7, 12, 13, 14, 17, 20, 22, 23, 24;
- W2-25 REDTEAM;
- this folder's TRACE_CHECKS.md.

**New numbers in this draft** (all from existing JSON, under 1 CPU-min):
- the K1 readout from `W2-22_second_regime/runs_{FIELD,FREE}.jsonl`;
- the label-flood counts in those same runs.

Each is marked **[W2-28]**.

**Paste position.** Directly under the "Nestor's pre-adversary draft is frozen…" paragraph (current line 12), before the first `---`. This mirrors the synthesis's block.

---

> **WAVE-2 CORRECTIONS (2026-10-01; ledger `roles/Nestor/inference_saturation_wave2/INFERENCE_LEDGER.md`; drafted by
> W2-28).** These supersede the corresponding text below. Line numbers refer to revision 2 as committed.
>
> **(A) Six theories collapse into one framework, F (W2-6).**
> - **F, the supplied rewrite field,** is the claim that a content's fate is computable from the *iterated* single-interaction
>   map (Φ under W, with the world's mutation kernel) against the realized partner distribution, with **no lineage-level term**.
> - **Its levels:**
>   - content: T3;
>   - rules: T2 + T5;
>   - dynamics: T7 as the branching limit and T1 as the mutation kernel, inside an iterated T6.
> - **The nesting results:**
>   - T1 and T2 differ on appearance only by counting unit (C5b). Per copy event, state-free variants are 6x more common
>     under noisy registers (p = 6e-4); per interaction attempt they are not.
>   - Erosion under BASE is the iterated map (C7b: conversion decays 0.46 → 0.01 over 9 interactions).
>   - The cell axis is at the noise floor (C9).
> - The seven theories below are kept as **levels and rivals inside F**. They are no longer independent accounts.
>
> **(B) T4 is eliminated as a theory (W2-6).** It loses every contest the existing data decide. Its parts now stand as follows.
>
> | part | status | grounds |
> |---|---|---|
> | (a) home / kin advantage | **unsupported, not excluded**; this is the residual R | Founders behave as independent tickets: a common p1 fits 798 k = 1 + 416 dose runs (p = 0.31), β = 1.13 [0.98, 1.29] (W2-12). The k = 4 excess that was R's only positive datum is a plug-in artifact plus one low k = 1 arm. β up to about 1.3 remains allowed. Static kin pairing is real (an exact-copy partner gives 0/400 half lost vs 54%), but it predicts β of only about 1.02–1.05. |
> | (b) a shared mechanism across independent origins | **against, provisionally** | 15 address-source classes in 26 runs; P(two runs share a class) = 0.05 (W2-6 C4). The panel is W1/FOR, not C-A3 origins; E4 Q2 decides. |
> | (c) multi-site epistasis beyond the single-knockout core | **dead as specified** | S3 frozen; stratum-matched SF = SD, ratio 1.01 [0.68, 1.50] (W2-6 C1). |
> | (c′) generic evolved epistasis | **not supported, on a corruption readout** | Length-matched c_EVO = +0.27 pp [−0.90, +1.46] (W2-13). With the long random-hit stratum: −0.45 pp [−1.59, +0.704] (W2-20). The pre-registered rule returns UNRESOLVED (upper bound 0.704 vs 0.70), but an excess the size of the raw gap (+1.39 pp) is excluded. The lethality screen uses random-value knockouts, which W2-4 shows are a **corruption** screen. The deletion (NOP-pair) readout is untested (W2-25 F15). |
>
> **(C) F is unfalsifiable as currently practised (W2-14 §3; W2-25 §3).**
> - **The rungs.** The map-built process runs from rung 1 (FREE, empty-register partners) to rung 5 (FIELD + FULL, which is
>   the world bit-for-bit).
>   - Rung 5 agreement is uninformative.
>   - Rung 4 (FIELD: kin + density) already contains a population term.
>   - **F can fail only at rungs 1–3,** with exogenous, non-kin partners.
> - **The tests run there:**
>   - BASE "no over-prediction" rests on 0/40, which cannot separate 0.0003 from 0.031.
>   - ATOMIC was first compared across unlike readouts. On matched readouts (W2-22, n = 30, none significant):
>     - the model trails the world by 0.13–0.23 on four readouts;
>     - it leads on depth_f by 0.07.
>
>     That comparison is rung 4, not 1–3. (The ledger's "trails by 0.07–0.23" misreads the sign on depth_f.)
> - **Absorption.** Every anomaly has been absorbed rather than predicted: the hijack (T5), erosion (T7), the partner-register
>   lever (W2-14), the side-0 morph (through the mutation kernel).
> - **No frozen quantitative prediction has been passed at a falsifiable rung.**
> - **Standing:** an ordinal, descriptive framework. It is not a tested theory. "F explains X" must not be written for
>   rung-4/5 agreement.
>
> **(D) F\*, a falsifiable restatement.** This builds on W2-25 §3; the amendments are marked †.
>
> **Scope.**
> - Stock Z8 physics (128-byte ring, 7-bit wrap, block op, slice 300).
> - One founder genotype g implanted in cell c.
> - Write-back W ∈ {BASE, ATOMIC}.
> - Splice off; horizon 300 epochs.
>
> **Reference process M\*(g, c, W) †.** The operational definition is W2-14's `ffield.py` with struct FREE, partner BANK,
> context CARRY and mutation ON, exactly as run in W2-22.
> - Each lineage member interacts through the world's own `_pair_interact` with a private partner. The partner (genome +
>   registers) is drawn from the founder-free background bank at that epoch.
> - There is no kin pairing and no density term.
> - Variants, side-0 morphs included, arise only through the world's mutation and copy-error kernel.
> - A static multitype reduction (W2-25's form) may stand in for M\* only after it is shown to equal M\* on R1–R3 within
>   the tolerances below.
>
> **Readouts.** All are named, and all are taken at the matched 300-epoch horizon.
> - **R1** = P(B_xk ≥ 27 by epoch 300).
> - **R2 †** = P(maxA ≥ 40 **and** B ≥ 27).
>   - The bare occupancy readout is contaminated by label floods: 26/49 FIELD BANK and 33/78 FREE BANK runs with
>     maxA ≥ 40 have B < 27 **[W2-28]**.
> - **R3** = P(B_xk ≥ 163 | B_xk ≥ 27).
>   - B_xk excludes kin-on-kin re-conversions (W2-22).
>   - It is reported under both cap-censoring treatments, C+ and C−.
>   - A verdict must hold under the treatment least favourable to it.
>
> **Claim.** For every in-scope (g, c, W), the world matches M\* within these tolerances:
> - |Δ| ≤ 0.05 on R1 and R2;
> - |Δ| ≤ 0.20 on R3.
>
> **Kinship clause, restated †.** W2-25 wrote "offspring laws do not depend on partner kinship". That is **false per call**:
> an exact-copy partner gives 0/400 half lost vs 54% for a random partner (W2-12 §4); see also W2-6 C5c. F\* therefore does
> **not** assume that Φ is kin-independent. It asserts that kin encounters are **negligible at the population readouts**.
> That assertion is what K1 and K3 test.
>
> **Decision rule for each kill criterion.**
> - **KILLED** if the 95% CI of the stated difference lies wholly outside ±tolerance.
> - **PASSED** if it lies wholly inside.
> - **UNRESOLVED** otherwise.
> - Tolerances are frozen at this block's commit. Any test whose data predate that commit can be scored only as
>   "consistent" or "inconsistent", never as "passed".
>
> **Kill criteria.**
> - **K1 (density + kin, population level).** FIELD BANK − FREE BANK on R2; tolerance 0.05.
> - **K2 (morph founders).** Implanted 44→ac and 37→81 founders (optionally 43→C3 and C3+AC) under `world.Runner` with
>   X-TICKET physics.
>   - Killed if R1 or R3 falls outside the 95% prediction band of M\* run on the same implanted genotype.
>   - The founder arm must reproduce 0.031 as a positive control.
>   - This is W2-25 Experiment 1.
> - **K3 (kin-swap ablation).** Within FIELD BANK, replace each kin partner by a bank partner with matched register state.
>   Killed if R3 moves by more than 0.20.
> - **K4 † (rung 5 vs rung 3, background residue).** World (FIELD + FULL, bit-exact) vs FIELD BANK on seed-matched runs.
>   Killed if R3 (on B_xk) differs by more than 0.20.
> - **K5 † (confinement beyond Φ).** HARV_WRAP in-world vs M\* rebuilt on the HARV_WRAP VM. Killed if R1 or R3 falls
>   outside M\*'s band. This is T5's "beyond Φ" clause in testable form.
>
> **(E) Status of each kill criterion after W2-22 and W2-23.**
>
> | criterion | status | evidence |
> |---|---|---|
> | K1 | **CONSISTENT, post hoc; not a frozen pass** **[W2-28]** | See note K1 below. |
> | K2 | **UNTESTED** | See note K2 below. |
> | K3 | **UNTESTED** | See note K3 below. |
> | K4 | **OPEN: a provisional strike against F\*** | See note K4 below. |
> | K5 | **UNTESTED in-world** | See note K5 below. |
>
> **K1 notes.**
> - On W2-22's own runs (fresh seeds 1000+, BASE, X-TICKET cell), on the maxA ≥ 40 readout: FIELD 49/600 = 0.082 vs FREE
>   78/1200 = 0.065. Δ = +0.017, 95% CI [−0.009, +0.043], which is inside ±0.05.
> - On R2 (B ≥ 27): 23/600 = 0.038 vs 45/1200 = 0.0375.
> - **Not frozen.** The 0.05 tolerance was proposed at 02:01Z while W2-22 was running, and W2-22's pre-registration froze a
>   different rule (ratio < 3 on conditional persistence).
> - **Ledger correction.** The ledger's "−0.38 under C+, +0.06 under C−, ambiguous" uses R3 (conditional persistence on B,
>   9/33 vs 31/48 or 10/48). That is not K1's readout.
>
> **K2 notes.**
> - It needs Experiment 1, which is in-world and not authorized.
> - W2-23 is static and does not bear on it.
> - The inputs are fixed:
>   - per call against bank partners, morphs 1.24–1.25 vs founder 1.17 (N17e);
>   - C3+AC 1.47 (W2-24).
> - M\*'s prediction band for an implanted morph is computable now, without `world.Runner`. FREE costs about 0.2 CPU-s per
>   seed.
>
> **K3 notes.**
> - W2-22's mechanism arms were not run, because they were conditional on SUPPORTED.
> - M1 (kin births turned into losses) is a different ablation from K3. Its one-seed smoke (s1579: maxA 227 → 99, still a
>   runaway) is an anecdote.
> - M2's "eroded" class is mis-specified.
>
> **K4 notes.**
> - World 4/4 vs FIELD BANK 9/33 = 0.27 (Fisher p = 0.011, W2-22). Against FREE BANK: 0.21 under C− (P(4/4) ≈ 0.002) and
>   0.65 under C+ (≈ 0.18).
> - The point difference exceeds 0.20. But:
>   - n = 4 world events;
>   - the world's readout is B, not B_xk;
>   - the seeds are unmatched (X-TICKET seeds vs 1000+).
> - It is not called a kill.
>
> **K5 notes.**
> - W2-23 shows confinement changes the per-call law causally:
>   - N2 hijack 0.224 → 0/750;
>   - K3 relabel 0.60/0.43 → 0.025/0.125;
>   - side-1 good copies 0.62 → 0.88.
> - So M\* rebuilt on HARV predicts a different world, and the prediction can be computed statically before any in-world
>   run.
>
> - **ATOMIC.** W2-22's matched-readout check (the world at 300 epochs vs the FIELD BANK model, seeds 0–29) found no
>   significant difference on any readout: depth_world 20/30 vs 14/30, p = 0.19; B ≥ 163 14/30 vs 10/30, p = 0.43. W2-14's
>   "ATOMIC validation did not pass" is withdrawn. This is rung 4, so it is not an F\* test.
> - **Net.** F\* has **no kill and no frozen pass**. The live threat to it is K4, the realized-background residue.
>
> **(F) Stale lines, with replacement wording.** These are the red-team's four (W2-25 F14) plus the other lines Wave-2
> evidence has overtaken.
> - **:41–42 (T1 explains).** Replace with:
>   > "**The ffa6/7ae3 difference is confounded, not supply-matched.** The hazard ratio is about 8x per takeover (95% CI
>   > about 1.1x–370x; n = 1 event in 7ae3) and about 13x per competent-genome exposure (W2-1 C12). World-mutation supply
>   > differs about 7x between the cells, and the operators also differ in kind: SLOTTED ignores the operator and puts 87%
>   > of ffa6 edits on opcodes, while 7ae3's OPERAND operator skips instruction starts (W2-8 D4; N14). Every 7ae3-vs-ffa6
>   > contrast confounds supply size with operator kind. The difference persists without payoff (FAIR ZERO: ffa6 3/3 vs
>   > 7ae3 0/5). Status: undecidable on existing data."
> - **:47 (T1 struggles).** Replace "P ≈ 0.055 under T1's own ffa6 hazard" with:
>   > "P(0 events) ≈ 0.20 with competent-genome exposure (W2-1 C12); not a strain on T1."
> - **:57–58 (T1 existing test).** Replace with:
>   > "**Existing test.** X-A3-FAIR's ZERO world resets both organisms' registers before every interaction, so it is an
>   > existing no-payoff arm (W2-1 C11 iii). State-free genomes appear there de novo (2/23 runs; one sweeps to 185/187), so
>   > appearance does not require payoff. The end-of-run robust share is 0.11 under reset vs 0.70 with carried registers.
>   > Whether that difference lies in appearance (T2) or in sweep (T1) depends on the counting unit: per copy event,
>   > state-free variants are 6x more common under noisy registers (p = 6e-4); per interaction attempt they are not
>   > (W2-6 C5b). Genealogy-based appearance counted per attempt is still missing."
> - **:110–111 (T2 existing test).** Replace with:
>   > "**Existing test: FAIR ZERO tests the decisive falsifier directly.** State-freedom does not sweep as far under
>   > per-interaction reset (robust share 0.11 vs 0.70), so T2 survives its falsifier. Sweeps without payoff do occur
>   > (2/23), however, so payoff is not required for a sweep (W2-1)."
> - **:181 (T4 status).** Replace "Status: unsupported and untested. It is not contradicted (RT M3)." with:
>   > "**Status (Wave 2): eliminated as a theory (W2-6). By part:**
>   > - (a) home/kin advantage: unsupported, not excluded (W2-12: β = 1.13 [0.98, 1.29]; the k = 4 excess is a plug-in
>   >   artifact);
>   > - (b) shared mechanism: against, provisionally (W2-6 C4, W1/FOR panel);
>   > - (c) multi-site epistasis: dead as specified (S3; W2-6 C1);
>   > - (c′) generic evolved epistasis: not supported on a corruption readout (W2-13; W2-20: −0.45 pp [−1.59, +0.70]);
>   >   the deletion readout is untested.
>   >
>   > Only (a) survives, as the residual R. Burden symmetry still applies: R needs a certificate (for example a frozen
>   > β > 1 in a same-batch k = 1 vs k = 4 test) before it can be called supported."
> - **:233–234 (T5 scope).** Replace "The foreign-cell victim magnet (100/240 vs 0/240) is **unexplained**." with:
>   > "The foreign-cell victim magnet (100/240 vs 0/240) is plausibly a partner hijack of the founder's **LDIR**, with no
>   > SELF needed, accumulated as a per-site hazard.
>   > - Per-call relabel is 0.0013–0.0073, and 0 with bytes 52–53 knocked out.
>   > - Single-site 2,000-epoch chains give 24/40 and 17/40, vs 0/30 for the knockout (W2-3 K3; N1).
>   > - Harvard confinement cuts the chains to 1/40 and 5/40 (W2-23 P2). About half the residual is copy-back by
>   >   converted partners.
>   >
>   > Static harness only; not demonstrated in-world."
> - **:298–303 (T6 existing test).** Append:
>   > "Wave 2 (W2-14): the field process is a genuine test only at rungs 1–3 (exogenous, non-kin partners). Agreement at
>   > rungs 4–5 is the world computing itself. See (C)–(E) for F\*."
> - **:330 (T7 struggles, k = 4 excess).** Replace with:
>   > "**Resolved (W2-12).** p = 0.0013 is a plug-in artifact, because it treats p1 as exact. A common p1 fits (p = 0.31),
>   > with no batch heterogeneity (p = 0.64); β = 1.13 [0.98, 1.29]; leave-one-experiment-out prefers independence. The
>   > residual tension is C-CRITICAL-MASS's low k = 1 arm (5/80)."
> - **:331–332 (T7 struggles, the BASE miss).** Replace with:
>   > "**Resolved (W2-14).** The over-prediction came from empty-register partners (FREE FRESH0 → POOL: B ≥ 163 falls 5/40
>   > → 0/40, p = 0.027) plus an uncertified occupancy readout. On P(reach ≥ 27 certified births) the law gives 0.025 and
>   > the world 0.031. What remains is post-27 persistence (SYN correction (l))."
> - **:354 (collision row).** Replace with:
>   > "| ffa6 > 7ae3 (≈ 8x per takeover, ≈ 13x per competent exposure; CI ≈ 1–370x) | confounded: supply size × operator
>   > kind (D4, N14) | cell ecology | neutral | neutral | neutral | neutral | neutral |"
> - **:359 (collision row, side-0 hijack).** Change the T5 cell to:
>   > "predicts; causal in the static harness (W2-23 P3: 0.224 → 0/750 under confinement)"
> - **:360 (collision row, foreign magnet).** Change the T5 cell to "explained statically: partner LDIR (N1, W2-3 K3,
>   W2-23 P2)", the T6 cell to "contained in Φ", and the T7 cell to "absorbs".
> - **:361 (collision row, "depth gap 22–161").** Prefix it with:
>   > "premise broken (SYN (d)); the f = 1 gap is P ≈ 0.045–0.056 with data-chosen edges (W2-28 TRACE_CHECKS)".

---

## Notes for Nestor (not part of the block)

- **K1 is the only new computation here.** Its 95% CI is a Wald interval on two independent proportions. A Newcombe interval
  would be marginally wider and would not change the inside-±0.05 reading.
- **maxA vs occupancy at 300.** maxA is the maximum over the run, not occupancy at epoch 300. W2-22 runs stop early
  (frozen, runaway_decided, free_cap256), so end-of-horizon occupancy is not recorded. maxA is the quantity W2-14 called
  "occupancy ≥ 40".
- **Optional.** If W2-25's original wording of K1 (bare occupancy) is preferred over R2, the K1 status is the same:
  Δ = +0.017.
- **Two amendments go beyond W2-25 §3. Both are open to attack.**
  - **K4** is added because W2-22's world-vs-FIELD-BANK gap is the one observation already pointing against F\*. Without
    K4, F\* could pass K1–K3 while the background residue goes untested.
  - **The kinship clause is restated** because the per-call kin dependence (W2-12) would otherwise falsify W2-25's
    wording trivially.
