# Dossier E: ARC3, the NPE frontier, and the ancestry replay (reader-historian, 2026-09-30)

- **Scope:** `roles/Nestor/campaigns/npe-arc3-2026-09-28/`, `npe-frontier-2026-09-30/`, `ancestry-replay-2026-09-28/`, and the
  two 09-28 directives in `roles/Nestor/prompts/`. Paths below are relative to `roles/Nestor/` in the `nestor-d2v13` worktree
  unless they are given in full.
- **Method:** read-only. Section 6 was computed by me from committed result JSONs, using scratch scripts outside the repo, in
  under a minute of CPU. No world was run and nothing was written to git. No holdout, D2 or secrets path was opened.
- **Convention:** each section keeps **DATA** (numbers read or computed) apart from **READING** (my interpretation, or the
  seat's). Where the seat's own conclusion is quoted, it is attributed to the seat.

---

## 1. Causal story (chronological)

### 1.0 Starting point (P2, accepted 09-28 by the ARC3 directive)
- **DATA.** The directive (`prompts/2026-09-28_arc3_endogenous_heredity_portfolio/DIRECTIVE_VERBATIM.md`, sha256 2b2aeca0) stated
  the P2 baseline:
  - "persistent state poisons donors" was withdrawn in favour of zero-register specialization. Donors use the zero registers
    as implicit self-location, and their own execution destroys that condition.
  - The competence screen certified donors from the zero state, and was flagged as circular.
  - Candidate 7ae3 seed 16000006 was "n = 1 ... a hypothesis, not a result. Treat it adversarially."
  - Register reset became an explicit world axis (CARRIED is the default; ZERO, CONST and RANDOM are conditions).
- **READING.** ARC3's central question: can a lineage endogenously take over machinery the environment currently supplies?

### 1.1 The mutation operator corrected (accessibility delegate)
- **DATA.** `delegates/accessibility/ACCESSIBILITY.md` s0 and `operator_check.json`. Both cells use the OPERAND operator with
  LOCAL locality and no indels.
  - In 7ae3 (Z8_64) opcode bytes **never mutate**: 0 of 2,000 mutated sites fell at opcode positions. A neutral lineage
    receives about **34** effective mutations in 2,000 epochs.
  - In ffa6 (Z8_SLOTTED) slot offsets 1-3 mutate, including opcodes, and the frame shifts. A neutral lineage receives about
    **239** effective mutations.
  - Nothing dies in these cells. The only selection is being overwritten by a copy.
  - No random genome, and none of its 1- or 2-step mutants, is competent: 0/3,200 genomes and 0/6,400 mutants.
- **READING.** This erratum on P2 (`FINDINGS.md` "CORRECTION (mutation operator)") is the root of the 7ae3/ffa6 asymmetry that
  recurs through everything below (T-STATE-3).

### 1.2 Reset specificity under a fair ruler (X-A3-FAIR, 03:07-05:06)
- **DATA.** `x_a3_fair/run_fair.py` docstring and `SUMMARY.json`.
  - **Design:** a treatment-blind ruler over entry states Z (zero), K (0x5A), R1 and R2. Both organisms enter the state. DONOR
    means competent from any of them. There are 3 worlds x 2 cells x 24 seeds = 144 runs.
  - **ZERO world:** 30 donor runs; 23/48 reach L4 (causal depth >= 20). Specialist-of-world share S_ZERO = 0.867.
  - **CONST:5A world:** 27 donor runs; 3/48 reach L4; S_5A = 0.111.
  - **Classification:** SIGNAL, label **ZERO_LITERAL**.
  - **CARRIED first-donor genomes:** Z_ONLY 26, K_ONLY 2, ROBUST 21. The late CONST:5A population is 346 K_ONLY against
    24 Z_ONLY.
- **READING (seat).**
  - Zero-specialization is not a ruler artefact, and specialization tracks whatever the world supplies, over time.
  - Literal zero is special for establishment because HL = 0 equals the organism's own start at offset 0. It supplies
    geometry-aligned self-location.

### 1.3 The 16000006 forensic (delegate): the ruler breaks, the single-change story dies, and the copier fixes its own destination
- **DATA.** `delegates/forensic_16000006/FORENSIC_16000006.md`.
  - **Replay:** exact. Depth 267 = 267; P-11 events 137,427 = 137,427.
  - **The ruler cycles:**
    - The D0 founders' carried state cycles with period 2-3. They copy after k = 0, 2, 5 own executions and fail after
      k = 1, 3, 4.
    - The first "robust" member under the old single-k rule (vid 320, epoch 352) is the same cycle shifted in phase. Byte 45
      changes (LD D,(HL) -> LD D,6F) in the post-copy loop.
    - That member fails from CONST and from RANDOM starts.
  - **Genuine full robustness (FR):**
    - First FR member: vid 1005, epoch 399, reached by 9 births and 1 mutation from D0 vid 211.
    - Its key bytes do not propagate: byte 0 is rewritten on every copy, and 0 of 158 descendants kept byte 0 = 01.
  - **Epoch-700 modal genomes (8):**
    - Distance from D0: 118-126 replications; they differ from every D0 genome at 49-54/64 bytes.
    - All 8 carry bytes 20..22 = `11 00 32` = **LD DE,3200** just before `LD (HL),B ; LDDR*`. This explicitly sets an
      aligned destination (0x3200 = 0 mod 128).
    - The triplet arose at vid 4887, epoch 463. The new byte at 20 came from neither parent.
    - CONST/RANDOM robustness flickers along 6 of the 8 paths.
  - **Causal tests (preregistered, `PREREG_CAUSAL.md`):**
    - knock-in into D0: 0/5 FR, although RANDOM rose from 0 to 0.32-0.34 in all 5;
    - revert: 0/8, because every revert destroyed copying;
    - literal cross-graft: 0/12, destroying copying in 12/12;
    - adapted graft, DE = HL + 0x40 (reported only): 1/12 FR.
  - **Post-hoc 20-position consensus knock-in:** not robust.
- **READING (delegate).** The candidate is KILLED as a single heritable change. Robustness did evolve **within D0's lineage by
  distributed change**, and it is not replacement: L_share = 1.0 and every path is rooted in D0. Its most visible ingredient is
  that the copier sets its own destination register.

### 1.4 State-free vs state-dependent donors (self-location delegate)
- **DATA.** `delegates/selflocation/SELFLOCATION.md`. 332 eligible copiers, 52 of them SELF-dependent:
  - **280/280 SELF-free copiers** fail when moved by 16 bytes or more;
  - 210/332 need the 128-byte wrap;
  - **182/332 are STATE_FREE**, meaning they still copy from random or constant registers;
  - STATE_FREE predicts state robustness: SELF_POISON in **3/179 vs 74/143**, Fisher p = 1.5e-28; at lineage level 1/28 vs
    28/46;
  - it does not predict SELF-dependence (27/182 vs 25/150);
  - only **2 true locators** exist (seed 16000026: SELF, LD D,L; LD E,D, LDIR, LDDR).
- **READING.** The environment supplies placement and geometry; the organism supplies, at most, register setup. This split
  defines the program's "internalizable vs never-replaced scaffold" dichotomy (SYNTHESIS s5-6).

### 1.5 Re-measuring with repaired rulers (X-A3-ENDOSTATE-R) and tracing lineage (X-A3-SFLINEAGE)
- **X-A3-ENDOSTATE-R.**
  - **DATA.** `x_a3_endostate_r/SUMMARY.json`, on the same 353 genomes as X-P2-ENDOSTATE:
    - STATE_FREE share 0.315 -> 0.647, rising in 5/13 measurable runs: WEAK_SIGNAL;
    - CYCLE_ROBUST 0.863 -> 0.882, rising in 2/13: CLEAN_NULL;
    - agreement of the old ruler with the cycle-aware ruler: 326/341.
  - **READING.** The P2 "no rise" reading holds for cycle-robustness. The less schedule-dependent ruler, state-freedom, rises.
- **X-A3-SFLINEAGE.**
  - **DATA.** `x_a3_sflineage/SUMMARY.json`: 5 replays with 0 mismatches; D0 was all not-free in 5/5.
    - The late state-free genomes are 100% in L in 3 runs: 7ae3 16000006, 7ae3 16000021 and ffa6 16000030.
    - They are 0% in L in 2: ffa6 16000003 and 16000005.
  - **Classification:** SIGNAL (within-lineage internalization).

### 1.6 Descendant competence (X-A3-AUTOPSY, 05:06-05:28)
- **DATA.** `x_a3_autopsy/SUMMARY.json`. The dominant loss between C1 and C6 is C3 (child material invalid): 0.514 in CARRIED
  (63 births) and 0.632 in ZERO (340).
  - Exact copies (C2): 4/63 and 38/340.
  - "Valid material, unusable start state": 5/63 in CARRIED.
  - Every child reached its next execution: C5 = C4 in both worlds.
- **READING.** The post-copy bottleneck is copy fidelity, not execution inheritance.

### 1.7 Endogenous internalization confirmed (C-A3-INTERNALIZE, frozen 86f929241, 05:28-07:31)
- **DATA.** `c_a3_internalize/VERDICT.json` and the `run_ci.py` docstring.
  - **Design:** 144 fresh runs (27,000,000+s, 72 per cell), random populations, dense VM, ATOMIC runner, CARRIED world.
  - **EVENT rule:** every D0 genome not state-free, AND at the **last checkpoint with any state-free genome**, >= 80% of the
    state-free genomes are in L and L_share >= 0.5. The bar is 4.
  - **Result:** **8 events** (7ae3 1, ffa6 7). 94 runs had a donor, 93 of them with D0 all not-free. 18 were replacement runs;
    34 were runaway.
  - **Verdict:** **CONFIRMED**.
  - **Controls:** the reset axis self-test, and the instrument reproducing the exploratory 16000006 EVENT.
- **READING (seat, `FINDINGS.md` E-A3-1).** "Endogenous internalization of register initialization", recurrent in fresh runs.

### 1.8 What "withdraw" tested (X-A3-WITHDRAW, 07:32-10:12)
- **DATA.** `x_a3_withdraw/run_wd.py` docstring and `SUMMARY.json`.
  - **Design:** the 16 C-ZERO-SPECIFIC zero-specialist donors, each implanted as a single founder in ffa6's cell. Every arm
    has the ZERO reset for epochs < 300. Then:
    - CONTROL_ZERO keeps p = 1;
    - ABRUPT drops to p = 0 (i.e. CARRIED);
    - GRADUAL ramps linearly to 0 at epoch 1300.
  - There are 96 runs.
  - **Ruler amendment A1** (pre-launch, 02:25): the single-k ruler was replaced by CYCLE-AWARE robustness because of the
    forensic.
  - **Question:** Bourrat 2022 predicts internalization only under gradual withdrawal.
  - **Results:**
    - established at 300: 12/32 per arm; 12/12 persist in every arm; PERSISTS(GRADUAL) - PERSISTS(ABRUPT) = 0.00, so
      **CLEAN_NULL**;
    - reported readout, cycle-robust share: ABRUPT 0.22 -> 0.94; GRADUAL 0.24 -> 0.93; CONTROL 0.15 -> 0.10.
- **READING (seat).** Withdrawal speed does not matter. Withdrawal is followed by a robustness rise "inside the lineage ... not
  sorting". Section 3 corrects the "not sorting" part.

### 1.9 External pressure: construction is not heredity
- **DATA.** Artemis #793 and Odysseus #803: P-11 certifies construction, so painters pass. Of the 57 S1-C "certified donors",
  2 self-copy and 17 paint.
  - Nestor's DOM screen of the W1/P2/ARC3 corpora: max 0.28.
  - CVT-R (Artemis #891, `FINDINGS.md` QUALIFICATION):
    - P2 donors: 23/32;
    - W1 q1: 83/100;
    - **16000006 epoch-700 modal genomes: 8/8**.
  - 19 P-11-certified genomes fail CVT-R, 11 of them at generation 2.
- **READING.** Every "competent donor" statement is a construction claim. The ARC3 central lineage itself passes the
  heredity ruler.

### 1.10 ARC3 closed; Nestor becomes the replay's instrument (post-ARC3 directive, ~11:50 ET 09-28)
- **DATA.** `prompts/2026-09-28_post_arc3_directive/DIRECTIVE_VERBATIM.md` (sha256 03d207b5):
  - ARC3 is closed, with no reinterpretation and no follow-on campaign;
  - Nestor is the independent NPE tracer and falsifier for Archaeon's ancestry replay;
  - D2 custody is kept separate;
  - "Do not let '34 births' become 'n=34'"; "Construction is not heredity"; "Be difficult to convince."

### 1.11 Ancestry replay (09-28 to 09-29): see section 5.

### 1.12 NPE frontier (09-30): the material audit and the task gate
- **X-MAT-INTERNALIZE.**
  - **DATA.** `npe-frontier-2026-09-30/x_mat_internalize/`:
    - frozen at c3e9eae9e, verdict commit ae38658fe;
    - dense taint self-test E1-E3 PASS (0 mismatches; non-vacuity 551/600);
    - replay gate 26/26 identical;
    - **all 8 EVENT runs ENDOGENOUS_MATERIAL**, median X = 0.020, max 0.107. Verdict **ENDOGENOUS**;
    - the REPLACEMENT runs' free_nonL has X of 0.90-1.00;
    - disclosures after Harmonia #1057: the pilot started before the freeze commit, and there is no planted-transplant
      control.
  - **READING.** The confirmed internalization is not a bookkeeping artefact of the pair-tape label.
- **X-TASK-GATE.**
  - **DATA.** `x_task_gate/PREREG.md`: frozen under Aporia #1150 for design only. **Not run**: syntax-checked, no pilot.
  - Stage 0 is a planted positive (EXTERNAL/TASK_GATED vs NONE). Stage 1 compares a TG gate against SHUF, a shuffled-gate
    null.
  - The preregistration declares that FLOOR or NO_REPLICATOR_REGIME is the likely outcome.

---

## 2. Table

| id | question | numbers | verdict | status |
|---|---|---|---|---|
| Accessibility delegate | Is usable copying mutationally accessible? What is the operator? | 0/3,200 random and 0/6,400 mutants competent; 72-80% of competent 1-mutants stay competent; copy-loss trap 0/144; neutral/soup ratio 1.75 (p = 0.20); carrier-exposure fit PLANT 28.6 vs 32 observed, DENSE 54.8 vs 49 | Operator CORRECTED (erratum on P2); carrier exposure SUGGESTIVE | Answered; WP-9 neutral baseline READY |
| X-A3-FAIR | Does zero-specialization survive a treatment-blind ruler? Does it track the world? | S_ZERO 0.867, S_5A 0.111; L4 23/48 ZERO vs 3/48 5A; CARRIED first donors 26 Z_ONLY / 21 ROBUST | SIGNAL, ZERO_LITERAL | Closed |
| X-A3-FORENSIC-16000006 | Is the fragile-to-robust transition one heritable change? | knock-in 0/5, revert 0/8, graft 0/12 (adapted 1/12); 118-126 replications, 49-54/64 bytes; LD DE,3200 | KILLED as single change; distributed within-lineage change | Closed; ruler defect recorded |
| Self-location delegate | Who supplies self-location and initialization? | 280/280 tape-anchored; 182/332 STATE_FREE; self-poison 3/179 vs 74/143 (p = 1.5e-28); 2 locators | Placement environmental; register setup organismal | Closed; WP-7 designed |
| X-A3-ENDOSTATE-R | With repaired rulers, does state robustness rise in runaway populations? | STATE_FREE 0.315 -> 0.647 (5/13 runs); CYCLE_ROBUST 0.863 -> 0.882; agreement 326/341 | WEAK_SIGNAL (STATE_FREE); CLEAN_NULL (cycle) | Closed |
| X-A3-SFLINEAGE | Do state-free genomes descend from non-free D0? | 3/5 runs with 100% of late free genomes in L; 2/5 with 0% | SIGNAL | Closed |
| X-A3-AUTOPSY | Where does reproduction fail after a copy? | C3 share 0.514 CARRIED / 0.632 ZERO; exact copies 4/63 and 38/340 | SIGNAL (C3 = material) | Closed; T-DC-5 opened |
| C-A3-INTERNALIZE | Does internalization recur in fresh runs? | 8/144 (bar 4; ffa6 7, 7ae3 1); 93/94 D0 all not-free; 18 replacement; 34 runaway | CONFIRMED | Closed; frozen 86f929241 |
| X-A3-WITHDRAW | Does gradual withdrawal of the zero reset help persistence? | persist 12/12 in every arm, difference 0.00; robust ABRUPT 0.22 -> 0.94, GRADUAL 0.24 -> 0.93, CONTROL 0.15 -> 0.10 | CLEAN_NULL (speed) | Closed; C-A3-WITHDRAW-ROBUST declared, not run |
| CVT-R (Artemis #891) | Are Nestor donors heredity carriers? | 23/32, 83/100, 8/8 | QUALIFICATION | Recorded |
| X-MAT-INTERNALIZE | Is the confirmed internalization made of L's own material? | 8/8 ENDOGENOUS_MATERIAL; median X 0.020, max 0.107; MUT 4.5-56%; replacement X 0.90-1.00 | ENDOGENOUS | Closed; no planted-transplant control |
| X-TASK-GATE | Does a task-competence gate produce task-coupled endogenous descent? | none | not run | Frozen, awaiting dispatch |
| Ancestry replay G1-G4 | Is the independent tracer valid? | fixtures 451/451, all mutants caught 3-22x; fresh set 2 raw 1.0 on every gated field (set 1 M failed: MUTATION label 0/225) | CLEAR | Closed |
| Production run 2 | Integrity | 9 simulations / 29 births; births byte-identical to run 1, 11/11; 2 reviews | HOLDS WITH NOTES | Standing |
| s4 v2.2 | Does the tracer's intervention coverage meet the floors? | flip coverage self 159/496 = 0.321, other 48/168 = 0.286, TIED 8/32 = 0.25 (floor 0.50); FAILED share 0; leak 0 | INCONCLUSIVE (flip floor unmet); 2/2 CONFORMS | E003 NPE leg INCONCLUSIVE @ 8fdad7f10 |
| 1% sample agreement | Does the tracer agree on production data? | 11 files / 28,055 records verified; addr/ctrl/exec/written 1.0; label 0.9984-1.0; 2,818 discrepant loci | PASS @ 8631128c3 | Closed |

---

## 3. Withdrawn or corrected interpretations

1. **P2 "frame-shift mutation" in 7ae3 was wrong.**
   - Evidence: `operator_check.json`. OPERAND never mutates 7ae3 opcodes, so the skeleton is frozen.
   - X-P2-BRIDGE's "mutation topology" reading is affected; its numbers are not (`FINDINGS.md` ARC3 CORRECTION).
2. **Single-k self-state ruler (rate_1 >= 0.25 rate_0) is a defect.**
   - Why: it reads one phase of cycling carried state.
   - Consequence: poisoned/robust labels in X-DD-SELFSTATE, X-P2-ENDOSTATE and X-P2-D0CHECK are unreliable.
   - Repair: WITHDRAW amendment A1 (cycle-aware, k = 1..6). ENDOSTATE-R shows the old conclusions largely survive
     (326/341 agree).
3. **16000006 as a single-mutation transition is KILLED** (0/5, 0/8, 0/12). "Byte 0 made it robust" is also wrong: byte 0 is
   rewritten on every copy.
4. **"Competent donor" = replicator is QUALIFIED to construction** (Artemis #793, Odysseus #803, CVT-R #891).
   - In the ancestry replay, L3/L4 ("child later a parent") are construction chains built from the P-11 parent pointer.
   - This is recorded as an erratum in `ancestry-replay-2026-09-28/GATES.json`. Heredity is L5 only, and NOT MEASURED
     (`CVTR_RECONCILIATION.md` s2-3).
5. **The Bourrat gradual-withdrawal premise did not hold for register initialization.**
   - T-SCAF-2 was downgraded (`BACKLOG_ARC3.md` change log).
6. **A1/A2 label canonicalization for G2 was withdrawn.**
   - It was replaced by C9 s5(a) clarifications, a re-freeze and a fresh agreement set (`GATES.json` post_exposure_rule_changes).
7. **s4 v2.1 did not conform: MARGINAL had replaced the gate decision (C4.4).**
   - v2.1's tallies are UNUSED. v2.2 restored "point estimate against floor", with MARGINAL as a mark only.
8. **Production run 1 was invalidated.**
   - Cause: `duplicate_of` marked every first record as its own duplicate, so the s4 per-class tallies were empty.
   - The restart condition (byte-identical exports) was later redefined for the sample gzip mtime (addendum 2). This was
     declared in GATES should_fix.
9. **X-PAIR-NORECOMB CLEAN_NULL was downgraded to INVALID** (R-11 verification).
   - Also an erratum: the 57 survivors were 53 tier L and 4 tier M, not all L (`FINDINGS.md`). This is adjacent context.
10. **X-MAT disclosures (Harmonia #1057).**
    - The pilot began before the freeze commit.
    - The claim that the replacement runs "validate" the XENO class was corrected to "agreement between two readouts, not a
      planted-transplant control".
    - WORK_STATE timestamps were wrong.
11. **Correction I propose (not yet recorded by the seat): X-A3-WITHDRAW's "not sorting".**
    - `FINDINGS.md` says the rise "is change within the lineage, not sorting".
    - The per-checkpoint data (section 6.3) show:
      - the cycle-robust share jumps from 0.22 to **0.96 in the first 100 epochs** after abrupt withdrawal, in 12/12 runs;
      - under CONTROL_ZERO a standing robust fraction of 0.10-0.33 is maintained throughout.
    - Single-founder design rules out sorting between lineages. It does **not** rule out selection on standing variation
      within the lineage, and the 100-epoch timescale favours it: ffa6 lineages receive about 0.12 effective mutations per
      lineage-epoch.
    - The ruler is also cycle-robustness, not STATE_FREE. So WITHDRAW is not directly the "counterpart" of C-A3-INTERNALIZE
      as SYNTHESIS s6 frames it.

---

## 4. Claimed mechanisms and evidence strength

| Mechanism | Evidence | Strength |
|---|---|---|
| **Carrier exposure** (frequency x persistence) controls acquisition | One-parameter hazard cross-predicts PLANT and DENSE (two informative arms); SHAM 0/96; planted copy decays 210 -> <21 per 256 | SUGGESTIVE: 2 arms, 1 parameter; the persistence-only discriminator (T-ACQ-9) is unrun |
| **Zero supplies geometry-aligned self-location** (HL = 0 = own start) | FAIR ZERO_LITERAL; 280/280 tape-anchored; L4 23/48 vs 3/48 | STRONG for "zero is special for establishment"; the HL = 0 mechanism rests on trace examples |
| **Copier fixes its own destination** (LD DE,xx00 before LDDR) | Present in 8/8 modal genomes; knock-in raises RANDOM from 0 to about 0.33 in 5/5; adapted graft 1/12 FR; revert destructive | MODERATE, n = 1 lineage: necessary for function in the late background, not sufficient |
| **Robustness by distributed within-lineage change** | 118-126 replications, 49-54 bytes, flicker on 6/8 paths, L_share 1.0 | STRONG for 16000006 (exact replay); generalization comes via C-A3 |
| **Internalization of register initialization recurs** | C-A3-INTERNALIZE 8/144 against bar 4; X-MAT ENDOGENOUS 8/8 | STRONG as recurrence and material origin. Mechanism per event is unexamined, except in 16000006 (not in the C-A3 sample) |
| **Mutation topology drives the ffa6 > 7ae3 rate** (T-STATE-3) | ffa6 7 vs 7ae3 1; operator facts; my section 6.1: conditional on D0 establishing with runaway, ffa6 7/8 vs 7ae3 1/3; 7ae3 lag 1,200 epochs vs ffa6 median 100 | HYPOTHESIS with consistent circumstantial support; confounded by cell (tape layout, slots) |
| **State-freedom predicts state robustness** | 3/179 vs 74/143, p = 1.5e-28 | STRONG (correlational, cross-sectional) |
| **Post-copy loss is copy fidelity (C3)** | 0.51 / 0.63 of losses | MODERATE: 16 donors in one cell |
| **Self-location is not internalized** | 2/332 locators; 0 in C-A3 corpora (implied) | STRONG as an observation. WP-7 (tape rotation) is the untested direct test |

---

## 5. What the ancestry replay certified

- **Specimen and unit.** T-003 specimen 4931614d912c52b2: 11 run records, i.e. 9 distinct simulations.
  - s9200006 C and s9200008 C duplicate their A arms under defect C9-D24; the lineage hashes are identical
    (`exports/*.summary.json` sim_id b36bf90c... and 7c895169...).
  - **29 distinct births** out of 34 recorded. G4 ruling C7.4: a run-clustered bootstrap over 9.
- **Tracer.**
  - An independent Z8 shadow tracer (`tracer/z8shadow.py`, `observe.py`), asserted value-identical to the frozen VM on every
    interaction: 256,000 per record.
  - Frozen at TRACER_FREEZE v4. v3 -> v4 changed only `run_production.py`.
- **G1, fixtures.**
  - 26 fixtures (12 Archaeon additions), **451/451 expectations** agree with the independent reference.
  - All deliberately broken tracers are caught, each 3-22 times.
  - 9 fixtures are inapplicable to NPE, e.g. K19 "no indels" and K10 "no LDIR under op mask".
- **G2, tracer agreement.**
  - Fresh set 1: set A PASS, but set M FAIL (MUTATION label 0/225, addr 209/225;
    `g2_fresh/NESTOR_COMPARISON.json`). This led to the C9 clarifications and a fresh set 2.
  - Fresh set 2 (`NESTOR_COMPARISON_SET2.json`): **every gated field 1.0 in every class**, MUTATION 212/212.
  - ctrl_slice is 0.94-0.96 and is not validated. pdom is also not validated. Both are excluded from production quantities.
- **G3, flip rule (C7.2).**
  - The prefix rule gates. Under the strict rule coverage is 0/64 on smoke births.
  - Under the prefix rule it is 31/32 on birth 257 and 0/32 on birth 256, because copied bytes execute before their final
    store.
- **Production run 2** (`REVIEW_PACKET_RUN2.md`). Births exports are byte-identical to run 1 in 11/11 records. Two independent
  reviews found **INTEGRITY HOLDS WITH NOTES**, and found that `s4_run.py` **DOES NOT CONFORM**.
- **s4 v2.2 conformance** (`review_s4v22/README.md`): 2/2 CONFORMS. Every K_R1 total was reproduced by hand.
  - **Flip coverage FAILS the 0.50 floor in every gated class:**
    - self 159/496 = 0.321;
    - other 48/168 = 0.286 (MARGINAL);
    - TIED 8/32 = 0.25.
  - FAILED share is 0. The per-byte completeness leak is 0 over applicable bytes.
  - The NPE leg is recorded **INCONCLUSIVE** by two frozen routes (E003_NPE_LEG_RESULT.md @ 8fdad7f10, Archaeon #948).
  - In the older frozen s4 (`exports/S4_SUMMARY.json`), flip coverage is self 0.447 and other 0.125.
- **Construction vs heredity** (`CVTR_RECONCILIATION.md`).
  - All 29 child genomes are DOM >= 0.75, and 27/29 are dominated by 0x36, the specimen's LD (HL),0x36 painting idiom.
  - Only 2 of the 29 later appear as a parent.
  - Heredity from the replay is **NOT MEASURED**.
  - My own recount: the `child_genomes_for_Q4` fields hold **14 distinct byte strings** (32-byte genomes). Their DOM is
    0.88-1.00, and 12 of the 14 are dominated by 0x36.
- **Class-agreement numbers on production data** (`g2_sample_check/rerun_8631128c3/AGREEMENT.txt`). Frozen reference vs owner,
  on 11 files and 28,055 records:

  | class | addr / ctrl / exec / written | label |
  |---|---|---|
  | unwritten | 1,693,918/1,693,918 | 1,691,234 (0.99842) |
  | written_other | 43,251 | 43,192 (0.99864) |
  | written_perf_none | 2,058 | 2,058 (1.0) |
  | written_self | 56,293 | 56,218 (0.99867) |

  - **2,818 discrepant loci, all in `label`.** The gate is raw >= 0.995 per class, so the result is **PASS**.
  - The route: the run-1 copy was verified by content identity (the gzip mtime differs), after the first attempt stopped at
    SCHEMA_UNDECLARED (exit 2) and was rerun as a single rerun.
- **The run-3 incident** (`INCIDENT_RUN3_2026-09-29.md`).
  - Two `/sc once 23:59` placeholder tasks, already started by hand with /run, fired again at 23:59.
  - They blocked in `wait-acquire cpu8` behind Ananke. When Ananke released the lease at 00:44:33, the production launcher
    started an **unauthorized run 3** at 00:45:03. Nestor found the unexpected lease and killed it at 00:49:25.
  - 10 of 11 git-ignored run-2 1% sample files were overwritten. Committed files were unaffected; the tracked births were
    restored.
  - Defects:
    - D-INC-1: a stale trigger plus wait-acquire amounts to a delayed unattended launch;
    - D-INC-2: the frozen launcher has no overwrite guard;
    - D-INC-3: hash-pinned evidence had no immutable second copy.
  - Resolution: the run-1 copies in `_scratch/` matched SAMPLE_MANIFEST_CONTENT, and the 8631128c3 verifier passed stage 1
    and stage 2 (`GATES.json` sample_1pct: VERIFIED).

---

## 6. UNMINED EVIDENCE (computed here)

Keys were checked against the files:
- the C-A3 and SFLINEAGE records hold `cell, seed, depth, d0_epoch, d0_free, checkpoints[{epoch, L_share, competent, free,
  free_in_L}]`;
- the X-MAT records hold `tags[{epoch, free_L, free_nonL, L, all}]`, each with
  `{ENDO, XENO, MUT, OTHER, D0, PRE, MKL, MKN, bytes, orgs}`;
- the WITHDRAW records hold `checkpoints[{epoch, anc0, events, competent_founder_genomes, sampled, robust}]`.

I applied `run_ci.event()` verbatim.

### 6.1 C-A3-INTERNALIZE: run anatomy (144 runs)
- **DATA: run categories.**

  | category | 7ae3 | ffa6 |
  |---|---|---|
  | no donor | 41 | 9 |
  | D0 already state-free | 1 (27000033) | 0 |
  | EVENT | 1 | 7 |
  | REPLACEMENT | 3 | 15 |
  | never any state-free genome | 26 | 41 |

  - The "OTHER_FAIL" category is empty: no run has L_share >= 0.5 and < 80% of the free genomes in L.
  - Event rate per donor run: 7ae3 1/31 (3%), ffa6 7/63 (11%).
- **DATA: complete segregation.**
  - In every EVENT run, state-free genomes **never appear outside L at any checkpoint** (first free_nonL: never).
  - In every REPLACEMENT run they **never appear inside L** (max free_in_L = 0).
  - No run of the 144 ever held state-free genomes in both compartments.
- **DATA: temporal ordering, where L takeover comes first.** In all 8 events the first state-free genome appears at or after
  the first checkpoint with L_share >= 0.5, never before.

  | run | D0 epoch | L >= 0.5 | first free | lag |
  |---|---|---|---|---|
  | 7ae3 27000023 | 80 | 400 | 1600 | 1,200 |
  | ffa6 27000012 | 880 | 1600 | 1600 | 0 |
  | ffa6 27000020 | 220 | 300 | 400 | 100 |
  | ffa6 27000024 | 1200 | 1300 | 1900 | 600 |
  | ffa6 27000046 | 460 | 600 | 700 | 100 |
  | ffa6 27000048 | 140 | 200 | 200 | 0 |
  | ffa6 27000051 | 760 | 1000 | 1100 | 100 |
  | ffa6 27000052 | 120 | 500 | 800 | 300 |

  - The ffa6 median lag is 100 epochs; the single 7ae3 event took 1,200.
  - SFLINEAGE's 3 within-lineage runs show the same order: 16000006 L 0.67 at 400, free at 500; 16000021 L 0.31 -> 0.93,
    free at the same checkpoint; 16000030 L 0.91 at 800, free at 900.
- **DATA: event and replacement differ before any divergence, at establishment.**
  - L_share at the second checkpoint after D0: EVENT median **0.62**, REPLACEMENT median **0.004** (max 0.16).
  - In X-MAT, **17 of 18 replacement runs never had more than 36 L organisms** out of 256. 12 had at most 1 at every checkpoint. D0's
    lineage was extinct (0 L organisms) in all 18 by the endpoint, and in 9 of them within 200 epochs of D0.
  - The only true "took over, then was replaced" run is ffa6 27000043: 170 L organisms at 500, 0 at 1400, free genomes from
    1400.
  - D0 epoch and depth do not separate the groups. Medians: D0 340 vs 300; depth 160 vs 158.
- **DATA: conditional rate.** Runs where D0's lineage ever reached L_share >= 0.5 with D0 not free: **15**.
  - Of these, 8 are EVENT, 6 never produced a free genome (7ae3 27000000, 008, 009, 061; ffa6 016, 053), and 1 is
    REPLACEMENT (043).
  - Restricted to runaway runs (depth >= 20): **8 of 11**.
  - By cell: ffa6 7/8 (the eighth is 043) and 7ae3 1/3. The 7ae3 non-events 27000008 and 27000061 are runaway lineages at
    L = 1.0 that never internalized.
- **DATA: near misses.**
  - Established, runaway, never state-free: 7ae3 27000008 (depth 86, L 1.0 from 700), 7ae3 27000061 (depth 110, L 1.0 at
    1900).
  - Established, non-runaway: ffa6 27000053 (depth 11, L 1.0).
  - Replaced after takeover: ffa6 27000043.
- **DATA: transience.** Only **4 of 8 events still hold any state-free genome at epoch 2000** (23, 20, 46, 48).
  - ffa6 27000012 rests on 1 organism at 1600. L then collapsed to 0.03.
  - ffa6 27000024 rests on 1 organism at 1900, with 0 at 2000.
  - ffa6 27000051 had 11 at 1200, then 0 from 1300, while competent genomes stayed at 65-190 and L = 1.0.
  - ffa6 27000052 peaked at 112 of 120 competent at 1200, then fell to 0 at 1700. **Competence itself went to 0** from 1700
    to 2000, with L still 1.0.
  - ffa6 27000020 flickers: 1 -> 0 -> 10 -> 0 -> 42 -> 0 -> 10 -> 0 -> 19.
- **READING.**
  - The rare-event framing (8/144) hides two factors:
    - most of the rarity is **first-donor lineages failing to establish**;
    - once D0's lineage takes over and runs away, internalization is the **majority outcome** (8/11).
  - "Replacement" (18) is mostly *D0 extinction followed by a later, non-D0 lineage*, not a contest between an internalizing
    lineage and a replacing one.
  - State-freedom appears in whichever lineage dominates, after it dominates. This fits carrier exposure: a large, persistent
    L supplies the mutational trials.
  - The event rule reads the *last checkpoint with free > 0*, not the endpoint. Persistence is therefore not part of the
    confirmed claim, and half the events are transient.

### 6.2 X-MAT-INTERNALIZE: tag trajectories (26 replays)
- **DATA: MUT accumulation.**
  - 7ae3 27000023: L's MUT share stays **1.6-6.1%** over 2000 epochs.
  - ffa6 EVENT runs rise roughly monotonically from 0-10% to **43-67%**, saturating after about 1000 epochs:
    - 27000012: 0.03 -> 0.67;
    - 27000052: 0.05 -> 0.67;
    - 27000020: 0.10 -> 0.48;
    - 27000046: 0.09 -> 0.48;
    - 27000048: 0.08 -> 0.43.
  - Replacement "all" populations: 7ae3 0.03-0.14, ffa6 0.19-0.62.
- **DATA: foreign material enters L during takeover and is then purged.**
  - Maximum XENO share in L: 7ae3 27000023 **0.193 at 500**, which fell to 0.000 by 1300, before the first free genome at
    1600.
  - ffa6 27000051: 0.161 at 1000, 0.099 at the first free genome (1100), and X = 0.061 at the endpoint.
  - Other events peak at 0.017-0.086.
  - Once L = 256/256 organisms, no MKN can be made and PRE is gone, so XENO decays only by overwriting.
- **DATA: composition of free_L at the endpoint.**
  - 7ae3: D0 0.047, **MKL 0.908**, MUT 0.045.
  - ffa6: D0 0.03-0.33, MKL 0.06-0.86, MUT 0.08-0.56.
  - Founder bytes (D0) are a minority everywhere except ffa6 27000012 (0.33).
- **DATA: replacement composition.** free_nonL is **MKN-dominated** (0.16-0.92, median about 0.67), with PRE 0.02-0.23.
- **READING.**
  1. The ENDOGENOUS verdict's power is concentrated in the takeover window.
     - After L = 1.0, X near 0 is almost guaranteed: there is no non-L source left.
     - The informative observation is that the pre-takeover foreign fraction, up to 19%, was purged before state-freedom
       appeared. It was not incorporated.
  2. "Made of founder material" should read "**made by the lineage**". What dominates is MKL (bytes computed by L members after
     D0) and MUT, not copied D0 bytes.
  3. The replacement lineages are equally "endogenous" to themselves (MKN-made).
     - Whether *their* founders were state-free is unmeasured, because the instrument tracks only the first-donor lineage.
     - The 18 replacement runs may therefore contain uncounted internalization events.
  4. The 7ae3/ffa6 MUT gap (≤6% vs ≤67%) directly shows, in the tagged material, the operator asymmetry from section 1.1. It is consistent
     with T-STATE-3: the 7ae3 lineage built its state-free genomes almost entirely from computed rather than mutated bytes.

### 6.3 X-A3-WITHDRAW: timing of the robustness rise (96 runs)
- **DATA: design identity.**
  - Up to epoch 300 the three arms are the **same world**: anc0, events and competent counts are identical in 32/32 donor-seed
    triples.
  - The same 12 (donor, seed) pairs establish in every arm.
  - The robust readout nonetheless differs before 300 in **12/32** triples, because the genome sampler is seeded per arm
    (`run_wd.py:85`).
  - The epoch-300 shares of 0.15, 0.22 and 0.24 are therefore one state read by three samples. That is a ruler-noise floor
    of about ±0.05.
- **DATA: pooled cycle-robust share among the established runs.**

  | arm | 300 | 400 | 500 | 600 | 1000 | 2000 |
  |---|---|---|---|---|---|---|
  | ABRUPT | 0.22 | **0.96** | 0.97 | 0.94 | 0.98 | 0.94 |
  | GRADUAL | 0.24 | 0.21 | **0.64** | 0.77 | 0.95 | 0.93 |
  | CONTROL | 0.15 | 0.25 | 0.28 | 0.15 | 0.24 | 0.10 |

  - In ABRUPT, every established run reaches a robust share >= 0.5 at epoch 400.
  - In GRADUAL, 11/12 do so by 700. At epoch 500 the reset probability is still 0.8, so **20% carried interactions suffice**.
  - Under CONTROL, 9 of 12 runs cross 0.5 at some checkpoint (e.g. seed 26000014 at 1000, with 6/6), yet the pooled share
    never exceeds 0.33.
- **READING.** Standing robust variation exists inside zero-reset lineages, persists at 10-33%, and is swept within 100 epochs
  once carried state matters. That is selection on standing variation within a single-founder lineage, not new acquisition.
  It does not contradict "within lineage", but it does contradict "not sorting" as `FINDINGS.md` words it.

### 6.4 X-A3-FAIR: class dynamics (144 runs)
- **DATA.**
  - CONST:5A world: first donors are Z_ONLY-dominated in 21/27 donor runs, and **16 of those runs later lose all donors**.
    K_ONLY dominates only later: the donor-genome share is 0.96 at epochs 800-1400.
  - CARRIED world: donor-genome shares are ROBUST 0.96 in epochs ≤ 700, falling to 0.54 late, while Z_ONLY rises to 0.44.
    First-to-last dominant class: Z_ONLY -> NONE 10, Z_ONLY -> Z_ONLY 6, Z_ONLY -> ROBUST 3, ROBUST -> Z_ONLY 2.
  - Median first-donor epoch: ZERO 700, CARRIED 850, 5A 900.
- **READING.**
  - Zero-competence is the *a priori* easiest form of donor to arise, even in a world that never supplies zeros. Those
    donors die out, and world-matched specialists replace them.
  - So "literal zero is special" holds for **discovery**. "Specialization tracks the world" holds for **establishment**.

---

## 7. Anomalies worth preserving

1. **Two "state-free" rulers disagree in scale.**
   - The transplant ruler finds 182/332 copiers state-free.
   - FAIR's CARRIED first donors include 21/49 ROBUST, i.e. competent from ANY random vector.
   - Yet C-A3's D0 sets were all not-free in 93/94 runs under STATE_FREE, which requires BOTH R1 and R2 at >= 0.5.
   - The "founders are not state-free" premise therefore partly depends on the both-vectors stringency and on the two fixed
     vectors chosen once. It was not tested across other random vectors.
2. **Complete compartment segregation** (6.1): no run ever had state-free genomes both inside and outside L. This is a
   striking regularity with no explanation yet.
3. **Transient events.** 4/8 confirmed events hold no state-free genome at 2000. ffa6 27000052's lineage lost all
   competence while holding L = 1.0.
4. **The 7ae3 event is built from computed bytes.** 91% of its state-free genomes' bytes are MKL. This may be real (a
   rewriting or painting-like copier) or a z8taint convention, e.g. register-routed moves tagged as "computed". MKL also
   collapses operand provenance: an L organism computing from a non-L partner's bytes still yields MKL. Neither caveat is in
   the X-MAT limits.
5. **The WITHDRAW sampler is not paired across arms** even though the worlds are identical before epoch 300.
6. **X-MAT has no planted-transplant positive control**, as Harmonia acknowledged. The REPLACEMENT X = 1.0 agreement is
   partly definitional: those populations contain no L organisms at all.
7. **The 1% production discrepancies are all label-field**, spread uniformly over locus positions 0-31 (68-99 per position).
   Duplicate simulations (s9200006 and s9200008 A+C) contribute twice: 505 and 766 of the 2,818. That is harmless for a
   per-locus rate, but it is the same double-counting the directive warns about.
8. **Self-location positive control C_ZERO_HL_IMM_E misfired.** It was expected TAPE_ANCHORED and came out STATE_ANCHORED.
   The D32 rescue over-fires on low-complexity (60/64-zero) genomes.
9. **The forensic knock-in helped RANDOM but never CONST** (5/5 vs 0/5). An aligned destination does not cover all non-zero
   states: BC and other registers still come from state.
10. **In the ancestry replay, P4-eligible halves vastly outnumber acceptances.** For example s9200004 B: 7,451 eligible, 2
    accepted P4, 6 births.
11. **The run-3 incident pattern** (a stale one-shot trigger plus a blocking lease wait) is a general hazard for every seat
    using the lease-wait convention.
12. **16000006 passes CVT-R 8/8,** but C-A3's 8 event lineages have **no CVT-R or heredity test**. The confirmed class is
    construction-competent state-freedom plus material endogeneity, with heredity unmeasured, except in the exploratory
    lineage.

---

## Summary

```
1. ARC3 (09-28) found register initialization is internalized; self-location is not (280/280 copiers tape-anchored; 2/332 locators).
2. C-A3-INTERNALIZE CONFIRMED 8/144 (ffa6 7, 7ae3 1); X-MAT-INTERNALIZE (09-30) ENDOGENOUS 8/8, median X 0.020.
3. The 16000006 single-change story was KILLED (0/5, 0/8, 0/12); robustness arose by distributed change, via LD DE,3200.
4. Ruler corrections: single-k self-state cycles; P-11 = construction, not heredity (CVT-R 8/8 only for 16000006).
5. NEW: the rarity is establishment. Given D0 takeover plus runaway, 8/11 internalize (ffa6 7/8, 7ae3 1/3); free follows takeover in 8/8.
6. NEW: "replacement" (18) = the D0 lineage went extinct early (17/18 never >36 orgs); no run has free genomes both in and out of L.
7. NEW: 4/8 events are transient (no free genome at 2000); the event rule reads the last free checkpoint, not persistence.
8. NEW: WITHDRAW's rise is 0.22 -> 0.96 within 100 epochs of withdrawal: a sweep of standing within-lineage variation, not de novo.
9. Ancestry replay: G1-G4 CLEAR; s4 v2.2 CONFORMS but flip floor unmet -> NPE leg INCONCLUSIVE; 1% sample agreement PASS (labels >=0.998).
10. Run-3 incident destroyed 10/11 sample files; recovered from run-1 copies by content identity; X-TASK-GATE frozen, not run.
```

Path: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/dossiers/E_arc3_frontier_ancestry.md`
