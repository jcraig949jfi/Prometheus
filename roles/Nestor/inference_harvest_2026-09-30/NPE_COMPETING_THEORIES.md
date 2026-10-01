# NPE competing theories: mechanistic accounts of what the pair-tape world is doing (revision 2)

Nestor's inference harvest, 2026-09-30.

**Inputs:**
- dossiers A–G;
- two independent adversaries: ADV1 (deflationary) and ADV2 (ontology);
- two static forensics: FOR (functional core) and S1 (map predicts outcomes);
- Nestor's checks, coded U-xx in NPE_UNMINED_EVIDENCE.md;
- a red-team review of revision 1 (RT), whose corrections are applied here.

Nestor's pre-adversary draft is frozen at `drafts/THEORIES_DRAFT_NESTOR.md`. §9 records what changed and why.

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
> | (a) home / kin advantage | **unsupported, not excluded**; this is the residual R | Founders behave as independent tickets: a common p1 fits 798 k = 1 + 336 dose runs [corrected 2026-10-01 per W2-48; was "416"] (p = 0.31), β = 1.13 [0.98, 1.29] (W2-12). The k = 4 excess that was R's only positive datum is a plug-in artifact plus one low k = 1 arm. β up to about 1.3 remains allowed. Static kin pairing is real (an exact-copy partner gives 0/400 half lost vs 54%), but it predicts β of only about 1.02–1.05. |
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


The seven theories are **mutually distinguishable**: each makes at least one prediction another contradicts. Some predict the
same headline outcome. They are kept separate because they disagree about mechanism, and the mechanism decides what the next
experiment should be. Where two theories predict the same thing, this document says so. It does not manufacture opposition.

**Notation.**
- **Φ:** the single-interaction pair map.
- **W:** the world's write-back rule (BASE or ATOMIC).
- **Family:** the contents descended by content ancestry.
- **Occupancy:** the share of sites held by a family.

---

## T1. Reachability: mutational supply × exposure (the search theory)

**Mechanism.** Each NPE transition is a first-passage event in genotype space. Its rate is the density of functional
genotypes within reach, times the number of trials (occupied sites × copy events × effective mutation supply). Selection
decides what persists, not what appears.

**Explains.**
- **Acquisition as a base rate.** Random dense genomes are competent at about 2e-4 (3 hits; CI 4e-5 to 6e-4). That is
  consistent in order of magnitude with dense acquisition: 5% vs 7.3% at the first checkpoint, 66% vs about 55% over a run
  (FOR, corrected).
  - PLANT (32/96) and SHAM (0/96) are the same arithmetic.
- **Internalization appears only after takeover (8/8).** Takeover is what supplies trials.
- **Detection rises with population size.** P(a state-free genome is seen at a checkpoint) rises with the number of
  competent genomes: 0.08, 0.25, 0.71, 0.67, 0.78 across the bins, so it is not monotone (U-C2).
- **Within-run drift toward state-freedom** (FOR Q5).
- **The ffa6/7ae3 difference is consistent with the supply difference.** The hazard ratio is about 8x against a supply ratio
  of about 7x, but the 95% CI on the ratio is about 1.1x–370x (n = 1 event in 7ae3) (U-T5).

**Struggles with.**
- **Why walks stop where they do.** The 16000006 walk (multi-step; single knock-ins 0/5) ended at `LD DE,3200`, and T1
  offers no reason.
- **ffa6 27000053.** It took over with 409k exposure and produced 0 events, which has P ≈ 0.055 under T1's own ffa6 hazard.
- **The 7ae3 event is 91% execution-computed (MKL) bytes and ≤ 6% mutation-made.** The OPERAND operator's count is therefore
  not obviously the supply for it (RT M1).

**Unique prediction.** The appearance hazard per copy event is invariant across payoff regimes. State-free variants appear even
when state-freedom earns nothing, which requires a true reset-every-interaction world. Payoff moves only the sweep.

**Decisive falsifier.** Measured by genealogy, not first detection, the appearance hazard per copy event is far lower in a
reset-every-interaction world than under VICTIM registers. That would mean appearance is driven by demand.

**Existing test.** None in NPE. BEE's ZERO arm (18/100 state-free events, transient) is suggestive, but it is a different
engine (D:F 5.2).

**Missing data.**
- a true no-payoff arm;
- copy-event counts per checkpoint;
- genealogy-based appearance events;
- a mutation-operator swap with an adequate event count (see E3's eligibility problem).

---

## T2. Scaffold tracking: the world defines reproduction (the ecological theory)

**Mechanism.** The world supplies most of what "reproduction" means:
- placement at offset 0;
- HL = 0 as the address;
- a long count;
- the 64/128 geometry;
- the pairing schedule;
- write-back;
- the newborn's registers, which are the victim site's leftovers (`world.py:812/877`, U-W7).

A family takes over those supplied functions that the world provides unreliably, and never those it provides reliably.

**Explains.**
- **Zero-specialization is HL = 0 geometry** (C-ZERO-SPECIFIC 26/48 vs 2/48). It tracks the world supplied (X-A3-FAIR).
- **Self-location is never internalized:**
  - 280/280 SELF-free copiers are tape-anchored;
  - only 2 of 332 are locators.
- **The address source is internalized.** State-free copiers take their address from constants, not entry registers (27% vs
  56% world-dependent; FOR Q2).
- **Self-poisoning is the copier's own pointer advance destroying the supplied address.** Carried E/L reproduces it on 32/44
  sides, and robust donors reload their pointers (S1).
- **The cell axis.** The single-interaction map cannot see it: observed CARRY is 0.16 (C7) vs 0.36 (CF). The ecological
  differences between cells (mutation, migration) matter (S1).
- **World rules decide outcomes:**
  - the energy "wall" is an asymmetry between birth paths (U-F4);
  - the splice matters;
  - so does the write-back rule.

**Struggles with.**
- **The wait.** Why internalization waits for takeover when the entry noise exists from epoch 0. T2 needs T1's supply term.
- **Transience.** Under steady demand T2 predicts persistence, yet 4/8 events are gone by epoch 2000.

**Unique prediction.** When only the demand is changed (the newborn-register rule), the *sweep* is ordered by how
uninformative the newborn's entry state is: RANDOM ≥ VICTIM > DONOR > per-interaction-reset ≈ no payoff. When placement is
made unreliable (tape rotation), either locators internalize, if they are reachable, or reproduction collapses.

T1 predicts the same sweep ordering. **T2 and T1 separate only on appearance**: T2 expects appearance to track demand, T1
expects it to track supply (RT B5).

**Decisive falsifier.** State-freedom sweeps as far under a per-interaction reset (no payoff) as under VICTIM registers.

**Existing test.** Indirect only. X-A3-WITHDRAW's CONTROL_ZERO keeps a standing 10–33% robust fraction that never sweeps,
while ABRUPT sweeps to 0.96 within 100 epochs (U-C5).

**Missing data.**
- the newborn-register factorial with a true reset arm;
- tape rotation (WP-7).

---

## T3. Compact copy setup: the representation does the work (the representation theory)

**Mechanism.** The instruction set supplies a half-duplicator. A competent genome is that instruction plus a short chain
computing its operands modulo 128.

**Evidence (FOR):**
- The knockout **collapse set has a median of 8 bytes** (IQR 6–10), about 5 beyond the last-setter motif, and the chain is
  mostly incidental.
- State-free genomes have the same collapse size, 8 vs 8. They differ in *where the address comes from* (constants) and in
  copying from side 0.
- 128/128 sampled genomes are copiers; 0 are painters.
- All BYTEWISE P-11 survivors are near-homopolymers (U-X5).

**Explains.**
- Copy_primitive's 5x effect on P-11.
- Dense encoding.
- Core composition.
- Function conserved while bytes regenerate: any chain yielding the right operands will do, and copy direction is neutral.
- **The phase arithmetic of self-poisoning.** It follows from LDIR semantics (count mod 128), so T3 predicts the same
  non-monotone budget pattern as T6 (RT M8).

**Struggles with.**
- **The 16000006 walk.** Single knock-ins do not confer robustness, and the adapted graft succeeds in only 1/12. Something
  in the background mattered.
- **Per-donor outcome differences need more than the setup.** The failure of the one-generation map and the success of the
  post-hoc two-generation map (S1) show that whether *the copies* can copy matters. That is a closure property, not a bare
  "compact instruction" property.

**Unique prediction.** Genomes matched on their full (two-generation) map perform the same in-world, whether evolved or
synthetic, and whether passengers are intact or scrambled with random bytes. Scrambling outside the *state-free* knockout
set costs nothing.

**Decisive falsifier.** Evolved genomes beat map-matched synthetic genomes or their own scrambles, in their home population,
by a frozen margin.

**Existing test.** The static half is done and supports T3 for single-site dependence. Single knockouts cannot see multi-site
dependence. The in-world half has never been run.

**Missing data.**
- the reconstitution test E1 (revision 2);
- a pairwise-knockout map;
- a register-free copy-op control (E8).

---

## T4. Reproductive organization: a self-maintaining lineage process (the program's former default)

**Mechanism.** The hereditary unit is a lineage process, not a byte string. It:
- regenerates its own material;
- keeps function while material turns over;
- maintains a core;
- reorganizes its reproductive setup by distributed, multi-site change when the scaffold becomes unreliable.

On this view, organization is carried and rebuilt by the family's own activity, and parts of it may be kin- or
population-context dependent.

**Explains.**
- The 16000006 walk (the strongest single residue; ADV1 R1–R2).
- Material turnover with function conserved.
- CVT-R transmission of organism-authored setup variation (83/100; 8/8).
- The primitive regenerated in foreign cells.

**Status: unsupported and untested. It is not contradicted (RT M3).**
- None of T4's distinctive predictions has been measured:
  - (a) kin- or home-context benefit;
  - (b) heritability of the *mechanism* across independent origins;
  - (c) multi-site epistasis beyond the single-knockout core.
- The grounds revision 1 gave for demoting T4 were mostly void:
  - the 1.009 enrichment ratio is near-automatic when L's share is bistable;
  - the Galton-Watson match was measured on the unevolved founder;
  - the 8-byte core comes from single knockouts;
  - "generic internalization" depends on unassayed founders (U-C2).
- **What does legitimately remove T4 as the *default*:**
  - burden symmetry (memory `verdict_mapping_burden_symmetry`): support needs a certificate, and T4 has none beyond one
    exploratory lineage;
  - everything else in the record is accounted for by T1/T2/T3/T6/T7 without it.

**Unique predictions.**
- (a) Evolved genomes outperform their map-matched synthetic twins and their own random-byte scrambles **in their home
  population**, but not in a naive one.
- (b) State-freedom from independent origins in different runs shares a mechanism that is transmitted as a unit (CVT-R /
  Jacobian), rather than converging on different constant-loading solutions.
- (c) Pairwise knockouts reveal dependence that single knockouts miss.

**Decisive falsifier.** Two findings together would falsify it:
- E1 (revision 2) finds no home-population advantage, with a ruler shown able to register one;
- pairwise knockouts find no epistasis beyond single-knockout predictions.

**Missing data.**
- a home-population reconstitution arm;
- a pairwise knockout map;
- a mechanism comparison across independent origins (E4 revision 2).

---

## T5. Executable machinery: reproduction partly performed by whoever reaches the code (the execution-field theory)

**Mechanism.** On the pair tape, code is data and data is code. pc crosses the half boundary, so a copy routine can be executed
by a context other than its owner.

**Verified case (U-W1).**
- 7ae3 is a SELF-using copier in a SELF-enabled cell. With 7ae3 at side 0, it is overwritten by the partner's content in
  200/400 random pairings.
- The overwrite happens in 0/400 once its SELF+LDIR bytes are zeroed.
- The partner's context authored 12,485 of 12,549 changed bytes.
- The overwrite falls to 1/400 when the partner is confined to its own half.
- Artemis previously reported the execution-order (side-1) hijack.

**Scope (RT M2, B1).** In the 24 corpus copiers tested (typical, SELF-free), partner-like overwrites of their half do occur,
and depend on their own copy byte. The changed bytes are mostly written by **the copier's own context**:
- 17,203 own vs 13,391 partner (state-free, side 1);
- 10,277 own vs 648 partner (not state-free, side 0).

For typical copiers the dominant mode is therefore **wrong-side self-import**, and partner execution is the minority. In the
foreign cells 9cba and e160 the SELF hijack cannot operate, because their ops masks exclude SELF: the single-interaction rate
is ≤ 1.5%. The foreign-cell victim magnet (100/240 vs 0/240) is **unexplained**.

**Explains.**
- Founder loss at side 0 in SELF-enabled cells: part of the 28% in X-TICKET.
- Why every copier is single-sided (U-W2).
- The attribution errors in the record: FF-31, AN8 candidates, founder-less runaways (candidates, untested).

**Struggles with.**
- **Frequency dependence.** No frequency dependence of erosion is visible up to 15 members (U-W5).
- **Internalization.** T5 says nothing about it.

**Unique prediction.** If pc may not cross into the partner's half (writes allowed):
- hijack births vanish;
- the founder's epoch-1 loss drops, in SELF-enabled cells;
- the winning genomes change beyond what a recomputed Φ predicts.

**Decisive falsifier.**
- An EXEC-motif audit of recorded births finds partner execution in < 5% of founder overwrites and births.
- Containment changes outcomes only by what the recomputed Φ predicts.

**Missing data.**
- the EXEC-motif audit (S2, static);
- an execution-containment world rule.

---

## T6. First principles: a stochastic rewrite field (stated without program vocabulary)

**Mechanism** (ADV2 §2).
- The system is a fixed set of 256 **sites**. Each holds a **content** (a 64-symbol string) and a **context** (a small state
  that stays with the site; only 7 bits of each pointer are observable on a 128-cell ring).
- Each step, a random matching pairs the sites.
- For each pair, a deterministic-plus-noise map Φ rewrites both contents and both contexts.
- A post-processing rule W then decides what each site keeps.
- A content spreads across sites to the degree that it:
  - (i) turns partner contents into copies of itself over a large share of partner contents and contexts (κ);
  - (ii) keeps its own site (ρ);
  - (iii) leaves copies that themselves do (i)–(ii) (the two-step closure the S1 repair found necessary);
  - (iv) restores, through its own action, a context in which it still works (context closure).
- The field has two kinds of stable configuration: a mixed configuration in which no content has growth rate above one, and
  single-content-class configurations.
- Changes of which class holds the field are rare transitions between them.

**Explains, in these terms.**
- **Which strings end up holding the field.** It is roughly predictable from pair statistics once (iii) is included:
  post-hoc ρ = 0.81–0.86. From one-step statistics alone the prediction is only coarse (S1).
- **Why outcomes are all-or-none.** There is no stable configuration between "absent" and "holding the field".
- **Why names attached to sites drift away from the strings they were first attached to.** A threshold rule moves the names,
  while Φ, residue and noise rewrite the strings (U-I6).
- **Why a string's usefulness decays across its own consecutive steps.** Its action moves its own context, and strings that
  rewrite their own context back persist (S1).
- **Why padding with a constant symbol inflates apparent copying.**

**Struggles with.**
- **Which class wins when several are present.**
- **Frequency dependence before a class holds the field.**
- **The cell differences Φ cannot see** (CARRY 0.16 vs 0.36).
- **Why a particular multi-step path was taken** (16000006).

**Unique prediction.** Holding-the-field outcomes are predicted by pair statistics computed string by string, including (iii),
with no history. Once (iii) is included, the prediction transfers to strings not used to build it.

**Decisive falsifier.** The two-step pair statistics fail on an independent string panel.

**Existing test (S1b, static, criterion frozen before computing): PASS, qualified.**
- The donor's own causal offspring law over a horizon predicts first-donor fate for 43 W1 first donors out of sample: AUC 0.89,
  ρ 0.71, permutation p 5e-5.
- The content is essentially "does it copy from its carried state". The simplest statistics do best, and W1's self-poisoning
  measurements do as well.
- So T6 holds at the first-donor stage. Post-takeover prediction is untested.

**Missing data.**
- a panel beyond W1;
- occupancy trajectories (E9);
- partner-conditioned statistics after takeover.

---

## T7. Demography: finite-population birth–death with a world-set offspring law (the deflationary quantitative theory)

**Mechanism.** The quantitative regularities are properties of a branching process in a finite population of 256, read at a
fixed horizon:
- the early fate;
- independent founders;
- the depth gap;
- the horizon effect;
- transient events.

**Explains.**
- X-DOSE-CURVE independence at the runaway endpoint (LRT p = 0.42; 0.70 pooled).
- Win given size: 7/9 at ≥ 8 members, 5/5 at ≥ 16.
- The horizon effect (U-T6).
- The depth gap, as extinction vs saturation.
- The splice as an offspring-mean reducer that cuts the tail only.

**Struggles with.**
- **The k = 4 excess at depth ≥ 5.** p = 0.0013 against pooled p1, although the joint LRT p = 0.108.
- **The BASE miss.** The map's zero-context BASE P_est is 0.26, against 0.03 observed: T7 needs content sterility (erosion)
  that a plain offspring law does not contain.

**Unique prediction.** The same demographic signatures appear with a register-free supplied copy op (E8):
- independent tickets;
- the depth gap;
- BASE ≪ ATOMIC;
- splice tail suppression.

**Decisive falsifier.** Those signatures change qualitatively with such an op, beyond its own offspring law.

**Missing data.** The SELFCOPY control world.

---

## 8. Collision table

Cells read "untested" where no test bears on the theory. Revision 1 marked some of these as contradictions (RT M3).

| observation | T1 reach | T2 scaffold | T3 setup | T4 organization | T5 execution | T6 field | T7 demography |
|---|---|---|---|---|---|---|---|
| dense acquisition ≈ base rate (order of magnitude) | predicts | neutral | predicts | neutral | neutral | predicts | neutral |
| state-freedom after takeover (8/8) | exposure | needs T1 | neutral | lineage process | neutral | context set becomes family-set | neutral |
| ffa6 > 7ae3 (≈ 8x, CI ≈ 1–370x) | consistent (supply ≈ 7x) | cell ecology | neutral | neutral | neutral | neutral | neutral |
| state-free in 25/29 large compartments; non-D0 founders unassayed | consistent | consistent | consistent | untested (acquired vs founding unknown) | neutral | consistent | neutral |
| collapse core ≈ 8 bytes; state-free no larger (single KO) | neutral | predicts | predicts | untested (multi-site) | neutral | predicts | neutral |
| 16000006 multi-step walk | allows | allows | strained | predicts | neutral | allows | neutral |
| one-step map: coarse pattern yes, within-ZERO no; two-step map ρ 0.81 (post hoc) | neutral | neutral | strained (closure matters) | untested (unevolved donors) | neutral | predicts (with iii) | consistent |
| side-0 hijack of 7ae3 (SELF cells) | neutral | neutral | neutral | neutral | predicts | predicts (Φ contains it) | absorbs |
| foreign-cell victim magnet (no SELF) | neutral | neutral | neutral | neutral | **not explained** | not explained | not explained |
| depth gap 22–161 | neutral | neutral | neutral | takeoff | neutral | extinction vs holding | predicts |
| transience (4/8) | appearance without payoff | strained | neutral | strained | neutral | weak closure advantage | drift balance |
| self-poisoning 12/12 vs 3/29; robust donors reload pointers | neutral | predicts (supplied address destroyed) | predicts (LDIR semantics) | neutral | neutral | predicts (context closure) | neutral |
| cell axis invisible to the map (0.16 vs 0.36) | predicts (mutation/migration) | predicts | neutral | neutral | neutral | fails | partly |

---

## 9. How the adversaries and the red-team changed Nestor's draft

1. **T4 was removed as the default on burden grounds, not on contradiction.** Revision 1 overstated the grounds (RT M3).
   Burden symmetry is the legitimate reason: T4 has one exploratory residue, and its distinctive predictions are untested.
2. **T5 is new and scoped.** It came from ADV2's hijack probe, which Nestor verified with independent code. The RT then
   narrowed it: typical SELF-free copiers mostly self-import, and the hijack cannot explain the foreign-cell magnet.
   Kin-pairing (Allee) is a secondary idea, and U-W5 shows no effect up to 15 members.
3. **T6 was sharpened** into ADV2's site/content/context ontology. S1 then added the two-step closure term (iii), which the
   one-step map lacked. The T6 statement is now written without program vocabulary (RT m13).
4. **T7 was split off from T1** (ADV1). It needs erosion (content sterility) to explain the BASE miss (RT B7).
5. **T2 gained the newborn-register mechanism** (U-W7). T1 and T2 separate only on appearance, not on sweep (RT B5).
6. **T3 was strengthened by FOR and corrected by FOR.** NOP-padded `1E 40 E5` passes partly by zero-painting. The honest
   minimal copiers are 6 exact 3-byte strings. Competent genomes are 50–70x more common than the reachable-motif prior. T3
   is also strained by S1: whether copies can copy matters.
7. **Where Nestor departs from ADV1:** the 1.009 enrichment ratio is uninformative. It is not evidence of label independence.
8. **Where Nestor departs from ADV2:** ATOMIC makes the *label* individuality valid by construction. Material regeneration
   under ATOMIC is still real, and it is expected under T6 as well.
