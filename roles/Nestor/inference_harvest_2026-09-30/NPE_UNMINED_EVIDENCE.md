# NPE unmined evidence: what the existing record already says that nobody extracted

**Inference harvest, 2026-09-30 (Nestor).** Every number below was computed read-only from files already on disk, or from
single-genome VM calls taking seconds. No world run or campaign was launched. Each item is tagged with its origin and a
status:
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

**U-T5. Internalization hazard per unit of exposure matches the mutation-operator asymmetry, with no fitting.**
[N] VERIFIED-BY-NESTOR.
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
  - In the ffa6 runs, MUT rises to 0.43-0.49.
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

**U-W1. The "victim-magnet" is a hijack: partners execute the founder's copy code.** [ADV2 D3] VERIFIED-BY-NESTOR with
independent code.
- Setup: 7ae3 at side 0, random partner, zero context, 400 partners, copy errors off.

  | side-0 content | partner overwrites the side-0 half |
  |---|---|
  | 7ae3, intact | **200/400** |
  | 7ae3 with SELF+LDIR bytes (23, 24, 52, 53) zeroed | **0/400** |
  | random bytes | **0/400** |

- In the intact overwrites, 12,485 changed bytes are authored by the partner's execution context and 64 by 7ae3's.
- If the partner is restricted to its own half, the overwrite falls to 1/400.
- **Reading:**
  - On the pair tape the copy machinery is executed by whichever context reaches it. The record credits the executing
    context (FF-31), and the lineage label goes to the partner.
  - This explains B's "victim-magnet" (100/240 founder overwrites in foreign cells; a random implant 0/320) and much of the
    28% epoch-1 founder loss.
  - Reproductive machinery here is not privately owned.

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

**U-L1. The complete copier is 2 instructions; the world supplies the rest.** [D:D U2] REPORTED.
- `1E 40 E5` (3 bytes, dense VM) and `1E 40 ED B0` (4 bytes, stock VM) pass the COMPETENT screen at 1.0.
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

**U-S1. The establishment probability is computable from the single-interaction map.** [ADV2 D1] REPORTED.
- Fit a Galton-Watson offspring law for 7ae3 against random partners under ATOMIC. The predicted survival is 0.49-0.52.
- Observed: 109 of 208 pooled single-founder ATOMIC runs ran away (0.52).
- Under BASE with carried context, the predicted mean offspring is 0.98, which is subcritical. That predicts copying stops
  and lineages persist, which is what X-TICKET observed.

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

**U-C2. Any large, sustained competent population becomes state-free, whatever its label.** [ADV1 6.1] REPORTED.
- Among compartments with at least 3 checkpoints of 25 or more competent genomes, it happened in 8/8 L-dominated and 17/21
  non-L-dominated compartments.
- P(any state-free genome at a checkpoint) rises with the number of competent genomes: 0.08, 0.25, 0.71, 0.78.

**U-C3. The founder lineage holds state-freedom less stably than replacement populations.** [ADV1 6.1] REPORTED.
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
