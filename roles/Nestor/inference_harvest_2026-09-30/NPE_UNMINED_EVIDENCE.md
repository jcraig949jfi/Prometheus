# NPE unmined evidence: what the existing record already says that nobody extracted

**Inference harvest, 2026-09-30 (Nestor). Revision 2**, after the red-team review
(`adversaries/REDTEAM_SYNTHESIS_REVIEW.md`, cited as RT). Its corrections are applied in place and marked **[RT-corrected]**.

**Where the numbers come from:**
- read-only computation over files already on disk;
- single-genome or single-interaction VM calls;
- one exception: ADV2's toy population process (256 sites, 300 epochs, 3 seeds × 2 genomes, built from single-interaction
  calls; not `world.Runner`). It is cited only as illustrative (U-I6, U-N2).

No world campaign was launched.

Each item is tagged with its origin and a status:
- **[D:A]…[D:G]**: the reader dossiers in `dossiers/`;
- **[ADV1] / [ADV2]**: the adversary reports in `adversaries/`;
- **[FOR]**: `forensics/FORENSIC_FUNCTIONAL_CORE.md`;
- **[N]**: Nestor's own checks in this session. Scripts are in the session scratchpad; the key ones are reproduced in
  `forensics/`.
- Status is **VERIFIED-BY-NESTOR** where I re-derived the number independently, or **REPORTED** otherwise.

It is organized by the directive's forensic questions.

---

## 1. Temporal ordering before establishment

**U-T1. Establishment is decided in the first 3-10 epochs.** [D:D U5] REPORTED.
- In C-ZERO-SPECIFIC, every one of the 26 established ZERO runs made its first founder copy at epoch 0-3.
- In failed CONST and RANDOM runs the first copy came at a median of epoch 325 and 104.
- A late first copy essentially never establishes.

**U-T2. Runaways and short bursts are indistinguishable until epoch ~10, and diverge between epochs 10 and 20.**
[D:A 6.2] REPORTED.
- Source: X-TICKET trajectories.
- Cumulative causal births of at least 4 by epoch 5 captures all 10 wins and all 4 runaways among 21 runs.
- No experiment sampled genomes inside the epoch 10-20 window.

**U-T3. The founder is overwritten at epoch 1, before it copies, in 36 of 128 X-TICKET runs (28%).** [D:A 6.2] REPORTED.
- Adversary 2 predicts this from the single-interaction map: side-0 hijack gives 0.18-0.30 [ADV2 D2].
- See U-W1 for the mechanism.

**U-T4. In C-A3, state-free genomes appear at or after the lineage's takeover in 8 of 8 events, never before.**
[D:E 6.1] REPORTED.
- Median lag is 100 epochs in ffa6. The single 7ae3 event lagged 1,200 epochs.

**U-T5. Internalization hazard per unit of exposure is consistent with the mutation-operator asymmetry, but the test cannot
discriminate.** [N] VERIFIED-BY-NESTOR (the arithmetic). [RT-corrected] per RT M1:
- Conditional on 8 events, the 95% CI on the ffa6/7ae3 hazard ratio is about 1.1x to 370x.
- The single 7ae3 event's state-free bytes are 91% MKL (execution-computed) and ≤ 6% mutation-made. The OPERAND count
  therefore is not obviously its supply.
- Dossier E rated the operator account a cell-confounded hypothesis.
- The one-sided p for equal hazards is about 0.02.
- **Wave-2 N4 (code).** Copy errors flip any copied byte, opcodes included, at rate 0.002 per byte, about 0.3-0.6 flips per
  execution. The flipped bytes are tagged MKL. In runaway populations copy errors dominate the mutational supply in both
  cells. The 34-vs-239 world-mutation count is not the relevant supply, so the 8x ≈ 7x agreement is **likely
  coincidental**. The ffa6 > 7ae3 difference is unexplained.
- Source: C-A3 checkpoints, cumulative L organism-epochs before the first state-free genome, over the 15 runs where a
  founder lineage that was not state-free reached L ≥ 0.5.
- ffa6: 7 events over about 975k lineage organism-epochs, roughly 1 per 140k.
- 7ae3: 1 event over about 1,150k.
- The hazard ratio of about 8x matches the ratio of effective mutations per neutral lineage in 2000 epochs, 239 vs 34, or
  about 7x (ARC3 accessibility delegate).
- Caveats:
  - The unit is organism-epochs, not copy events.
  - The 7ae3 figure rests on one event.
  - ffa6 27000053 took over with L = 1.0 and exposure of 409k, yet stayed at depth 11 and never became state-free. That
    points to copy turnover, not presence, as the relevant supply.

**U-T6. Horizon effect: donors that appear earlier establish more.** [D:D U12] REPORTED.
- Donors whose first competent genome appeared by epoch 500 established in 12/18 runs; later ones in 11/31.
- Part of W1's "establishment rate" is time-to-horizon.

---

## 2. Information flow across generations; conserved versus regenerated structure

**U-I1. Founder material turns over almost completely, while function persists.** [N] VERIFIED-BY-NESTOR.
- Source: X-MAT per-checkpoint tags.
- In L's genomes, D0 (founder) bytes fall as follows:
  - 7ae3 27000023: from 0.94 to 0.04;
  - ffa6 27000046: from 0.86 to 0.03;
  - ffa6 27000048: from 0.68 to 0.09;
  - ffa6 27000020: from 0.75 to 0.19.
- The byte classes that replace them:
  - MKL, values computed by L organisms, rises to 0.3-0.9.
  - MUT rises to 0.43-0.49 in the three ffa6 runs shown, and to 43-67% across all ffa6 event lineages (dossier E §6.2).
- Foreign-computed bytes (MKN) peak at 0.19 during takeover and decay to 0 over about 500 epochs.
- A z8taint check shows no laundering bias: register loads keep the source tag, and a copy flip changes the value. So MKL
  bytes really are new values made during the lineage's own execution.

**U-I2. The founder's share of the state-free genomes is 3-33% (median about 0.11).** [D:F 5.1] REPORTED.
- X-MAT's ENDOGENOUS verdict therefore rules out import from a coexisting population. It shows founder descent only for a
  minority of bytes.

**U-I3. Founder byte share falls with world depth.** [D:B U4] REPORTED.
- Spearman is -0.63 overall and -0.82 in foreign cells.
- Certified founder depth does not predict it (-0.31).
- The highest founder content observed (0.50) sits in a run with founder depth 0.

**U-I4. Early and late competent genomes of the same "lineage" share about 5/64 aligned bytes.** [D:D U9] REPORTED.

**U-I5. Function is conserved while bytes are regenerated.** [D:B U5] REPORTED.
- In cell e160 the copy direction flipped from LDIR to LDDR (one bit) and was fixed at the founder's position.
- In 9cba, LDIR was re-created at bytes 55-56 instead of 52.
- Neither cell keeps C-CORE's byte pattern.

**U-I6. Label and content split from the map alone.** [ADV2 D6] REPORTED.
- In a toy process built only on the pair map, founder-label occupancy reaches 256/256 while sites that are 0.9
  founder-like fall to 0 by epoch 100.
- X-CONTENT's 13-25% founder material is therefore the expected consequence of a 0.9 threshold plus residue plus mutation.
  It is not a special property of NPE lineages.

---

## 3. Parent/offspring asymmetry and write authority

**U-W1. Partners can execute a SELF-using founder's copy code (7ae3, SELF-enabled cells). This is not the foreign-cell magnet.** [ADV2 D3] VERIFIED-BY-NESTOR with
independent code.
- Setup: 7ae3 at side 0, random partner, zero context, 400 partners, copy errors off.

  | side-0 content | partner overwrites the side-0 half |
  |---|---|
  | 7ae3, intact | **200/400** |
  | 7ae3 with SELF+LDIR bytes (23, 24, 52, 53) zeroed | **0/400** |
  | random bytes | **0/400** |

- In the intact overwrites, 12,485 changed bytes are authored by the partner's execution context and 64 by 7ae3's.
- If the partner is restricted to its own half, the overwrite falls to 1/400.
- **Reading** [RT-corrected per RT B1/M2]:
  - For a **SELF-using** copier in a **SELF-enabled** cell (7ae3, ffa6: ops mask 0x2a), partners can execute its copy
    routine and copy themselves over it. The record credits the executing context (FF-31), and the lineage label goes to the
    partner.
  - Artemis first reported the execution-order hijack (side 1).
  - **This does NOT explain the foreign-cell "victim magnet".** In 9cba (mask 0x2c) and e160 (0x28), SELF is disabled. The
    same probe gives 1/400 (zero context) and 6/400 (random context) there [RT R2]. The magnet in those cells, founders
    overwritten in 100/240 runs vs 0/240 for random implants in the same experiment, is **unexplained** (§7).
  - How much of X-TICKET's 28% founder loss at epoch 1 it explains (7ae3's own cell, SELF-enabled) has not been computed.
    ADV2's estimate is 0.18-0.30.

**U-W1b. For typical SELF-free copiers, the loss of their own half is mostly their own wrong-side copying.**
[RT R3] REPORTED.
- Setup: 24 FOR corpus copiers, 100 random partners each.
- Partner-like overwrites of the copier's half occur, and they depend on the copier's own E5/E7 byte:
  - state-free copiers at side 1: 489/1,200 intact vs 3/1,200 knocked out;
  - non-free copiers at side 0: 174/1,200 vs 20/1,200.
- The changed bytes are mostly authored by the copier's own context:
  - 17,203 own vs 13,391 partner;
  - 10,277 own vs 648 partner.
- 7ae3's pattern (12,485 partner vs 64 own) is atypical.

**U-W2. Every NPE copier copies from exactly one side.** [D:B U3; D:D anomaly 9] REPORTED.
- 7ae3, cb7f and 4931 copy from side 1 only; c2a8 from side 0 only.
- The corpus holds 0 two-sided copiers among 1,050.
- A single-sided copier can reproduce in at most about half of its pairings. No rate model has used this.

**U-W3. Loser lineages stop writing.** [D:A 6.3] REPORTED.
- They make 13 copy writes in 11,181 member interactions, a rate of 0.0012, against 0.56 in winners.
- "Stalled" means zero write activity, not failed copies.

**U-W4. Erosion is symmetric in authorship.** [D:A 6.6] REPORTED.
- Self 3,507 vs partner 3,241 (plus both 8,024).
- A copier is part of its own erosion. [ADV2 §1.8] names the mechanism: a tape-anchored copier at the wrong side imports its
  partner.

**U-W5. Erosion does not scale with lineage size at small sizes.** [N] VERIFIED-BY-NESTOR.
- Source: X-STALL-F0.
- Spearman(n_members, share of member interactions that change the genome) = 0.02 (p = 0.84) over lineages of 0-15
  members.
- No early kin-protection (Allee) effect is visible. A threshold above about 6% frequency remains untested.

**U-W6. Under ATOMIC, the founder label spreads without certified copies.** [D:B U1, A2] REPORTED.
- In 9cba, 0 of 120 runs have any P-11-certified founder edge, yet the founder label reaches 0.98-1.0 of the population.
- ATOMIC keeps predecessor-accepted, non-causal overwrites.

**U-W7. Newborns inherit the victim body's registers.** [ADV1 §1.10] VERIFIED-BY-NESTOR (code).
- `org.regs` is written back after execution (`world.py:812`) and never reset when the body is renamed
  (`world.py:877`).
- Every "birth" therefore runs the donor's content in the victim's leftover register context, which is noise from the new
  genome's point of view.

---

## 4. Latent reproductive subassemblies

**U-L1. Minimal copiers.** [D:D U2; FOR Q3] REPORTED. [RT-corrected]
- Rates:
  - `1E 40 E5` (dense) and `1E 40 ED B0` (stock) pass the COMPETENT screen at 1.0 **with NOP padding**. Part of that pass is
    zero-painting.
  - With random padding, FOR finds exactly 6 real 3-byte copiers (`LD E/L,0x40|0xC0 ; E5/E7`).
  - No 1- or 2-byte program passes (all 65,536 two-byte programs were tested).
  - Random 64-byte genomes are competent at about 2e-4: 3 hits in 14,024, CI 4e-5 to 6e-4. That is about 50-70x the
    reachable-motif prior of (3-4)e-6.
- **Acquisition consistency** [RT B2]: 5% of runs predicted at the first checkpoint vs 7.3% observed, and 66% vs about 55% by
  the end. This is an order-of-magnitude agreement only (band about 1-14% and 20-95%).
- `E5` alone reaches fidelity 0.97 without authorship.
- [ADV2 D8] adds that padding inflates the result. With NOP padding the 3-byte copier "converts" 0.60 of partners from
  random contexts; with random passenger bytes it converts 0.00.

**U-L2. Donor genomes are mostly executed-but-inert passenger bytes.** [D:D U10] REPORTED.
- About 7-14 bytes are functional (last-setter instructions plus the copy op).
- The median copy sits at byte 48, followed by a never-executed tail of 15-23 bytes.
- See [FOR] for the knockout-measured necessary sets.

**U-L3. The extended-core candidates are register setup for the LDIR.** [D:A 6.7] REPORTED.
- Position 48 (LD E,A) is conserved in 13/27 C-CORE runaways, followed by 42 (LD (BC),A) and 33 (LD H,C).
- [ADV2 D7]: the zero-context knockout map predicts retention only partly (Spearman 0.29). Essentiality measured against the
  realized family field is the untested refinement.

**U-L4. Heredity without a zero-state-competent genome.** [D:D U8] REPORTED.
- Certified chains of depth 2-18 occur with no COMPETENT genome in about a third of dense runs.
- The spontaneous stock-VM lineage survived a 200-epoch window with 0 competent genomes.
- The COMPETENT screen misses real copiers. [ADV2 §1.4] gives an example: c2a8 converts 0.81 of partners from random
  contexts and 0.00 from zero.

---

## 5. Reproductive failure modes

**U-F1. Self-poisoning predicts whether the first donor copies at all, almost perfectly.** [D:D U1] REPORTED.

| | copied in-world | never copied |
|---|---|---|
| self-OK | 12 | 0 |
| poisoned | 3 | 26 |

- p = 5.8e-8.
- 8 of W1's 23 "ESTABLISHED" first donors never copied. Their runs were rescued by a second acquisition.
- The Block C puzzle ("half of successful donors self-poison") is mostly a run-level label artefact.

**U-F2. Self-poisoning can be pure phase arithmetic.** [ADV2 D4] REPORTED on synthetic genomes only.
- A block copier whose copy count is 0 mod 128 returns its pointer to its own start after every execution. In carried
  context it converts in 16/16 interactions; neighbouring counts convert on the first interaction only.
- Copy count is set by the slice budget minus the pre-copy instruction count. The slice budget is therefore hidden
  heritable geometry.
- Real donors are untested: `q3_reset.json` carried_states and bridge `founder_ages` would test this with no new runs.

**U-F3. The splice blocks takeoff, not initiation.** [D:A 6.8, §4] REPORTED.
- Runs that make any copy: 81 with the splice vs 77 without.
- Pooled runaways: 0/222 with the splice vs 22/630 without (p = 0.0012).

**U-F4. The energy "wall" may be culling of starving newborns.** [D:B A3] REPORTED.
- Energy-economy cells reap the lowest-energy organism first, so a zero-energy newborn dies first whenever the world is
  full.
- The EXTERNAL birth path already grants a newborn half the parent's energy.
- C-ENERGY did not separate "cannot afford the copy" from "culled first".

**U-F5. Field scramblers.** [ADV2 D9] REPORTED.
- Nine panel "non-copiers" keep their own half intact in zero context (0.56-0.94) but fire a block op on random pointers in
  carried context, which rewrites up to 300 bytes of the 128-byte tape.
- They act as a field-level mutation source. The heredity ontology counts this only as "erosion".

---

## 6. Signatures preceding successful establishment

**U-S1. Establishment from the single-interaction map: partly predictable, and not yet "computable".**
[ADV2 D1; S1] REPORTED. [RT-corrected per RT B7.]

**7ae3 (ADV2).**
- Under ATOMIC, the Galton-Watson survival from 7ae3's offspring law against random partners is 0.49-0.52. S1 gives 0.57
  (ZERO context) and 0.63 (CARRY).
- The observed value, 109/208 = 0.52, counts **depth ≥ 20 runaways**. That ruler is under suspicion (E9).
- Under BASE the map gives:
  - ZERO context: m 1.11, P_est **0.26**, against about **0.03** observed (4/144). That is about an 8x miss.
  - RANDOM context: m 0.98 (subcritical), P_est 0.
- The losers' collapse in write rate (0.0012 vs 0.56) is content sterility from erosion. A near-critical offspring mean does
  not explain it.

**Panel test (S1, `forensics/FORENSIC_MAP_PREDICTS_OUTCOMES.md`). Verdict PARTIAL.**
- The specified one-step map predicts the policy ordering and the anti-zero donor. Pooled ρ is 0.53-0.56, significant under
  within-policy permutation.
- It fails within ZERO (ρ 0.08, p 0.38).
- It overpredicts every arm by 0.12-0.42, with Brier worse than a constant.
- It cannot see the cell axis: CARRY 0.16 in C7 vs 0.36 in CF.
- **A post-hoc two-step repair** adds whether the donor's copies themselves convert, plus a 500-epoch horizon. It gives ρ
  0.81 within ZERO and 0.86 pooled, with Brier 0.052 vs 0.076.
  - It recovers exactly the four donors carrying all CONST/RANDOM successes {0, 4, 14, 15}.
  - Four donors predicted high made **sterile copies**: their children convert at 0.00-0.03, and in a spot check every child
    differed at byte 0.
- The out-of-sample test of the repair on W1's first donors, with its criterion frozen before computing, is
  `forensics/FORENSIC_MAP_OUT_OF_SAMPLE.md`.

**U-S3. Robust real donors reload their pointers; phase arithmetic is rare.** [S1] REPORTED.
- Carrying only the E/L pointer bytes reproduces poisoning on 32/44 poisoning sides. Clearing them rescues 26.
- Copy counts in real donors are 164-295, set by the leftover slice budget, so Δ ≡ 0 mod 128 almost never occurs.
- The Δ-or-reload rule is right on 28/32 predicted-poison sides and 27/44 predicted-OK sides.
- Agreement with the W1 SELFSTATE labels: Fisher p = 9e-4.
- The direct `q3_reset.json` check is not significant (p = 0.16).

**U-S2. Size threshold.** [D:A 21] REPORTED.
- Win probability given the lineage reached at least 8 members: 7/9. Given at least 16: 5/5.

---

## 7. Lineages that nearly crossed a threshold but failed

**U-N1. C-A3 near-misses.** [D:E 6.1] REPORTED.
- Established and runaway, but never state-free: 7ae3 27000008 (depth 86) and 27000061 (depth 110).
- Established but not runaway: ffa6 27000053 (L = 1.0, depth 11).
- Replaced after takeover: ffa6 27000043.

**U-N2. cb7f: copying in every run, depth capped at 6.** [D:B U6; ADV2 D5] REPORTED.
- cb7f copies in 8/8 ATOMIC runs (163-1,053 P-11 events) but never exceeds depth 6.
- The map predicts takeover in the toy (3/3), so the cap may be a turnover or certification artefact of the depth ruler.
- One occupancy-logged replay would decide it.

**U-N3. C-CORE non-runaways at depths 6, 10 and 16, with founder material about 0 at the end.** [D:A 6.16] REPORTED.

**U-N4. Depth is bistable.** [D:A 6.1] REPORTED.
- None of 630 single-founder runs ends between depth 22 and 161.
- Both adversaries read this as extinction vs saturation plus turnover. It is not a hidden threshold.

---

**U-N5. The foreign-cell victim magnet is unexplained.** [D:B U1; RT R2]
- In 9cba and e160, the 7ae3 founder is overwritten in 100/240 runs, against 0/240 for a random implant.
- The SELF hijack cannot operate in these cells: the single-interaction rate is ≤ 1.5%.
- Candidates: side asymmetry combined with foreign-cell code paths, or label transfer through uncertified overwrites.

## 8. Apparently irrelevant mutations that change future evolvability

**U-E1. The operator asymmetry.** [D:E 1.1] REPORTED.
- In 7ae3, opcode bytes never mutate: about 34 effective mutations per neutral lineage in 2000 epochs, against 239 in ffa6.
- This one world setting predicts the ffa6 ≫ 7ae3 internalization rate (U-T5).
- It also explains the MUT share of state-free genomes: ≤ 6% in 7ae3 vs 43-67% in ffa6.

**U-E2. The copy direction is neutral.** [D:D U14] REPORTED.
- In the spontaneous lineage, LDIR and LDDR alternate by one bit, at a fixed byte 50, over 1,600 epochs.
- The corpus split is 498 LDIR vs 552 LDDR.

**U-E3. Reset-on-change halves 7ae3 acquisition.** [D:D U11] REPORTED.
- 25 → 13 runs (p = 0.02).
- Carried state may help first donors assemble.

---

## 9. Generic facts about state-freedom (C-A3), from the committed rows

**U-C1. State-freedom is not enriched in the founder lineage beyond its population share.** [ADV1 6.1] VERIFIED-BY-NESTOR.
- 5,342 state-free genomes observed in L, against 5,296 expected (ratio 1.009).
- The test has little power: only 5 of 236 checkpoints with a state-free genome have mixed L occupancy.

**U-C2. State-free genomes are present in most large, sustained competent compartments. Whether non-founder compartments
acquired the trait or were founded with it is unknown.** [ADV1 6.1; RT R4] REPORTED. [RT-corrected per RT B3/m4]
- Compartment counts (compartments with ≥ 3 checkpoints of ≥ 25 competent genomes):
  - L_share ≥ 0.95: 8/8;
  - L_share ≤ 0.05: 17/21;
  - total 25/29.
- With L_share ≥ 0.5 the L count is **8/11**. The 3 misses are U-N1's near-misses.
- C-A3's instrument assays only D0 for state-freedom. **In 4 of the 17 non-L compartments, state-freedom is already the
  majority at the compartment's first competent checkpoint:**
  - 7ae3 27000037: 147/148;
  - ffa6 27000002: 177/187;
  - ffa6 27000003: 157/182;
  - ffa6 27000035: 89/117.
- At the first checkpoint with ≥ 25 competent genomes the count is 7 of 17 (adding 27000070, 27000063 and 27000033).
- "Becomes" is therefore not shown. E4 is designed to resolve it.
- P(any state-free genome at a checkpoint) by competent-count bin: 0.08, 0.25, 0.71, 0.67 (75-124), 0.78. The series is not
  monotone.

**U-C3. Persistence: the founder lineage 4/8 vs replacements 16/18. The comparison is unmatched.** [ADV1 6.1] REPORTED.
[RT-corrected per RT B3]
- It sets *internalized* state-freedom against state-freedom that may be *ancestral* (U-C2).
- It is not evidence about T4 unless it is re-run on compartments that start with < 0.2 state-free.
- Still present at epoch 2000: 4 of 8 events vs 16 of 18 replacements.
- The per-genome state-free rate is lower in L-dominated checkpoints: 0.24 vs 0.43 (7ae3) and 0.45 vs 0.66 (ffa6). These
  counts are clustered by run.

**U-C4. Compartment segregation is a corollary of bistable occupancy.** [ADV1; ADV2] REPORTED.
- Only 94 of 1,296 checkpoints have 0.05 < L < 0.95.
- Segregation is therefore not a lineage-level regularity.

**U-C5. X-A3-WITHDRAW's rise is a sweep of standing variation, and one state was read three times at epoch 300.**
[D:E 6.3] REPORTED.
- Cycle-robust share goes 0.22 → 0.96 within 100 epochs of abrupt withdrawal, in 12/12 runs.
- The three arms are the same world up to epoch 300 but use per-arm samplers.
- FINDINGS' phrase "not sorting" should read "selection on standing variation within the lineage".

---

## 10. Instrument facts found along the way

**U-X1. The H1 competence ruler scores each genome once, on one cached 6-episode draw.** [D:B A1] REPORTED.
- This contradicts `tasks.py:33`.
- Ungated "competence" in the H1 line may be cache luck. The gated-with-VM zero is robust.

**U-X2. ATOMIC is a composite treatment.** [D:B A2] REPORTED.
- Its keep-rule is the predecessor criterion, not P-11.
- It also discards organisms' writes to their own half.

**U-X3. The index could not see causation but did show non-propagation.** [D:C 5.3] REPORTED.
- `dom_share_final` ≤ 2/384 in all 57 P-11 survivors.

**U-X4. Scheduler feedback built the 1,031.** [D:C 5.1] REPORTED.
- 979 of the 1,031 are tier L.
- The unbiased tier-M rate is 7.1% flagged and 0.55% P-11, with 0 of 102 on RECOMBINATION.

**U-X5. copy_primitive has no effect on the flag but a 5x effect on P-11 (p = 8.8e-7).** [D:C 5.2] REPORTED.
- Every BYTEWISE survivor is a near-homopolymer.

**U-X6. "Founder-less" C-ATOMIC runaways.** [D:A 6.11] REPORTED.
- Seeds 12,000,031 and 12,000,076 ran away with 0 certified founder births.
- Candidate mechanism: the hijack in U-W1.

---

## 11. Highest-value sources still unread

| source | question it answers | cost |
|---|---|---|
| `p2/delegates/corpus/corpus.json` (51,007 competent genomes) | map atlas: conversion over the full 128×128 phase grid, offspring law, closure, and Jacobian. Do they predict per-donor outcomes (D U4) and SELF_POISON labels? | static, minutes |
| `q3_reset.json` carried_states; bridge `founder_ages` | whether poisoning is phase arithmetic in real donors (U-F2) | static |
| X-CERT-BREAK births; Archaeon's 34 replay births | classify births by EXEC motif (copy, paint, hijack, residue) | static |
| One cb7f ATOMIC replay with occupancy logging | U-N2: takeover without depth? | about 0.3 core-h |
| C-A3 per-organism genealogy of state-free genomes | monophyletic sweep vs recurrent origin (the transience in U-C3) | replay, about 3 core-h |
| Bellerophon's sealed REPL-01 runs, re-read with an aligned material ruler | resolves BEE descent at replay cost [D:F 5.7] | replay |
