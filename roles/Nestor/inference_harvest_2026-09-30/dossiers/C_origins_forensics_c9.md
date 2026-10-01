# Dossier C: origins, forensics and the Cycle-9 verification machinery

Reader-historian dossier, 2026-09-30. Read-only. No world runs and no git writes. Every number in this dossier
falls into one of three classes:

- **[record]**: a number written in a frozen file. The file is cited.
- **[author]**: a conclusion or interpretation the Nestor seat, or another seat, wrote down. The file is cited.
- **[computed here]**: a number this dossier recomputed read-only from the frozen record, in under 2 minutes of CPU.
  The scripts are in the session scratchpad and are not committed.

All paths are relative to `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/` unless marked otherwise.
Abbreviations:
- **Z80A** = `campaigns/z80atlas-2026-09-19/` (the 72-hour campaign).
- **FOR** = `campaigns/z80atlas-forensics-2026-09-23/` (the forensic replays).
- **VER** = `campaigns/z80atlas-verify-2026-09-22/` (Cycle 9, "C9").

---

## 1. The causal story, in chronological order

### 1.1 Before launch (2026-09-19): the first false replicator was caught in rehearsal

The 72-hour campaign crossed 16 factors: reproductive physics, representation, ecology, pressure, and accessibility
manipulations inherited from CW01 cycle 8. The grammar hash was frozen at `570c8037...` (Z80A/PREREGISTRATION.md).
Four substrate faults had to be fixed before the calibration gate would pass
(memory `project_nestor_z80atlas_campaign.md`):

1. Slot indices were treated as byte offsets, so every genome read back as zeros.
2. Pending ALLOCs leaked. That produced a false reading that "endogenous reproduction does not invade".
3. Operand mutation was uniform, which erased the ATOMIC/INCREMENTAL constant distinction.
4. Tier sat inside the grammar, so no family ever accumulated evidence across tiers.

In rehearsal, the PAIR_TAPE world called one half "a copy of the other" whenever the two halves were 90% byte-identical.
- [record] It fired 5 times in 3 minutes.
- [record] It raised the campaign's top flag, `SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES`.
- [record] The inspected specimen had `copy_bytes` 0, seven stray writes, and no copy loop.
- Source: memory `feedback_similarity_is_not_copying.md`.

[author] Diagnosis: a converged population resembles itself, so a similarity test "reports replication continuously
and reports it loudest exactly where nothing is happening". The in-code comment is preserved at VER/world.py around
line 823.

The fixes were:
- **Private-slot physics:** births now need donor writes, snapshotted at ALLOC and differenced at BIRTH. The world
  also keeps a `births_similar_no_write` counter.
- **Pair tape:** the fix was different and weaker. Declared limitation 4 in the preregistration says pair-tape heredity
  is "detected by byte similarity ... 0.90 fidelity threshold ... a heuristic ... not a proof of causation".
- The criterion that shipped was:
  - `fid_other >= 0.90`;
  - `fid_self < 0.90`;
  - the donor's `writes_other >= n/4`.
- Fidelity is read **after** `_mutate` (VER/world.py lines 826-840, the `p11.predecessor_accepts` call).

This asymmetry between the two detectors is the seed of everything that follows.

### 1.2 During the run (09-19 to 09-22): flags fire, and the defects are recorded rather than patched

At 11.9 h the seat logged three special-flag defects and deliberately did not patch them in flight (Z80A/DEFECTS.md).

- **Z80A-D01.** `REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION` fired on a *historical* crossing but quoted
  *final-state* held scores. [record] Margins at 11.9 h ranged from +0.833 to -0.750, and 4 of 13 were negative.
- **Z80A-D02.** `RESERVOIR_CROSSED_A_MOAT` never checked that the reservoir contributed. [record] 22 of 24 flags came
  from seeded instruments.
- **Z80A-D03.** The index whitelist omitted `replication_events` and `births_similar_no_write`. The first adjudicator
  read them from the index, found nothing, and declared all 36 spontaneity flags then present INADMISSIBLE.
  - That verdict was wrong in the other direction.
  - Read from the per-run records, each flag had `replication_events >= 1`.
  - [record] The inspected run showed 1 evidence-backed event against 26 resemblance events.

DEFECTS.md then asserted: "The replication detector: it was corrected BEFORE launch ... and it is holding." That
statement was later refuted (section 3, W-17).

### 1.3 The packet (09-22): 1,031 "spontaneous replicators"

[record] Z80A/observatory/PACKET.md:

| quantity | value |
|---|---|
| runs | 23,471 (0 voided) |
| replicated runs | 5,309 |
| spontaneous replication runs | 1,031 |
| specials | 1,221 |

[record] ADJUDICATION.md:

| flag | ADMISSIBLE | WEAK | INADMISSIBLE |
|---|---|---|---|
| SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES | 1,031 | 0 | 0 |
| REACHED_ONLY_UNDER_ENDOGENOUS_REPRODUCTION | 1 | 50 | 14 |
| RESERVOIR_CROSSED_A_MOAT | 0 | 0 | 124 |

- The one admissible endogenous-only instance was `64dea50f417efb02-s1203-tL-a0` (A-4): final held 1.0 against a
  "matched" external control at 0.0.
- The first report (REPORT.html rev 1) had four integrity defects, R-01 to R-04 (FINDINGS section B):
  - a sign inversion;
  - a WEAK run named as the sole admissible instance;
  - categorical claims the record could not support;
  - 24 of 28 axes shown.
- The root cause, in the author's words, was that "a human-readable summary was sourced from another human-readable
  summary."
- Rev 2 plus `report_audit.py` (40 checks) repaired these.

### 1.4 Reading the record (09-22 to 09-23): the headline narrows twice

These narrowings are in FINDINGS A-1 and VER/REVIEW_PACKET.md section 9.

- **Events are not lineages.** [record] Reconstructed ancestry reached maximum depth 1 in 911 of 1,031 runs, depth 2 in
  111 and depth 3 in 9.
- **C9-D01.** [record] All 1,031 are `PAIR_EXECUTION`. Zero came from ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL, CONSTRUCTIVE
  or OVERWRITE. The spontaneity result therefore rests entirely on the weaker pair-tape detector from 1.1.
- [author] Restated finding: "in the one physics where two organisms share a tape, one half overwrites the other at high
  fidelity, and it rarely propagates."

The Cycle-9 repair pass (rev B) found six substrate defects by reading the code (FINDINGS C-1):

| repair | predecessor defect |
|---|---|
| P-1 | The lineage kept only a 400-event tail, and migrations were never logged |
| P-2 | Every birth counted as a lineage edge |
| P-3 | Historical and final-state outcomes were conflated |
| P-8 | The whole initial population was placed in niche 0 |
| P-9 | `COEVO_ENV` silently bypassed the reservoir's easy niche. The sole A-4 instance sits in a `COEVO_ENV` cell |
| P-10 | `ENV_MIG` was semantically inert: `env_difficulty` returns 1.0 outside RESERVOIR, so its gate never fires |

- Rev A's H1 framing, "cycle 8 showed forced read wins", was withdrawn (A-3).
- `FORCED_READ` turned out to change the target and the input construction, not only the read order.

### 1.5 The forensic stage (S1, 09-23/24): the funnel, the H4 autopsy, and P-11

The operator's post-reset directive ordered three forensic products before any freeze (VER/STRATEGY_POST_RESET.md).

**S1-A, the replication funnel** (FOR/S1A_FUNNEL.md). [record]

- The 907 random-start FREE-policy runs (the private-slot physics) produced **zero births**. This substrate mutates only
  at birth, so those populations never varied: "no search at all".
- 256 of 256 replays matched their frozen summaries.
- Across 192 FREE replays there were 114,485 BIRTH/SPLIT calls, and every one had no pending allocation. Organisms that
  allocate never declare a birth, and organisms that declare never allocated.
- OVERWRITE produced 656 replayed births, none at fidelity >= 0.90.
- By contrast, `PAIR_EXECUTION` mutates every paired organism every epoch.

[author] Conclusion: "Comparing replication rates across the two families compares a search against no search." The
zero outside the pair tape is therefore a statement about zero variation, not about detector asymmetry.

**S1-B, the H4 autopsy** (FOR/H4_AUTOPSY.md). [record] The A-4 source run had:
- 0 ALLOC calls, 0 births, 0 deaths and 0 mutations in 4,000 epochs;
- 384 seeded readers, unchanged throughout;
- a first crossing at epoch 636 with no genome changed. `COEVO_ENV` moved the task under a frozen population.

The exact matched control was re-run at seed 1203, tier L. It **crossed at epoch 48**, before the endogenous run, and
then lost the crossing to undirected mutation.

- The 4x runtime gap came from execution (11 vs 294 ops per organism per epoch) and a validation cache on unchanged
  genomes. It was not extinction.
- **Z80A-D04:** the scheduler stored `control_summary` per family, so 64 of 65 endogenous-reach flags were adjudicated
  against a sibling's control.
- A-4 was **withdrawn**.
- **C9-D07:** the H4 design cannot test accessibility at all, because its endogenous arm cannot reproduce.

**S2/S1-C, P-11 and the reassay** (VER/P11_SPEC.md, FOR/S1C_P11_REASSAY.md). [record]

- P-11 was specified, tested (T-P11, 14 checks) and committed (`f28e5fd72`) before any of the 1,031 was inspected.
- 1,031 of 1,031 replays matched.

| reading | runs | events |
|---|---|---|
| predecessor criterion | 1,031 | 7,919 |
| P-11 primary (causal_value_authorship) | **57** | 69 |
| literal last-write authorship | 48 | 54 |

- Maximum P-11 depth is **2**: 55 runs at depth 1, 2 at depth 2, and **0 at depth 3**.
- **Z80A-D05:** under `atlas_axis = RECOMBINATION`, `_mutate` splices the victim with a random living organism, often
  the donor. [record] In 6,287 of 6,547 RECOMBINATION events the interaction itself moved fewer than 10% of the
  victim's bytes toward the donor.
- That is why 910 of the 1,031 sit on one axis.
- Worked example `ec37c8167691fb2c-s7979-tM-a0`: 3.1% donor-like after the interaction, 95.3% after the splice.
- This example is one of the ten `SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES` exemplars printed in PACKET.md.

[author] The third narrowing: "57 of 1,031 random-start pair-tape runs contain at least one interaction in which one
organism can rebuild a randomized partner to >= 0.90 fidelity by its own writes; none of those lineages reaches
depth 3."

### 1.6 Preregistering Cycle 9 (09-24): the stop, the tournament, the freeze

Rev D of VER/PREREGISTRATION.md carries the amendment log A-1 to A-28:

- **H4 withheld** (A-22).
- **H2:** a 16-specimen panel rebuilt from the P-11 survivors, 16 seeds, rule B >= 8/16 and C <= 2/16, and a panel
  positive requires >= 2 strata (A-17, A-18).
- **H3:** two RESERVOIR cells repicked from the P-11 record, 32 seeds (A-20).
- **P-11 authorship** primary = causal value authorship, with literal authorship a mandatory sensitivity (A-16, A-28).

**C9-D12** (S4_CANDIDATE.md) warned that H2's depth >= 5 bar had no precedent, since the maximum P-11 depth over
1,031 runs was 2.

Then **C9-D14** stopped the freeze (VER/PREFREEZE_STOP_2026-09-24.md). On the pair tape an organism keeps its id while
its bytes are replaced. [record] D14_PROBE.json, both H3 cells, 600 epochs:
- 128 of 128 organisms were never the child of any lineage edge;
- median identity to their own birth genome was 0.000;
- the share below 0.10 was 1.000.

An oid-walked certificate therefore certifies that an *identity* moved, not that *material* did. The repair was a
bounded ruler tournament on 9 adversarial fixtures (VER/H3_RULER_TOURNAMENT.json), recorded as A-24:

| ruler | fixtures correct |
|---|---|
| **R3 material** | **9/9** |
| R1 founder fidelity | 7 |
| R0 id | 4 |
| R2 causal edge + window | 4 |

- A runner, the H1/H2/H3 adjudicators and an independent audit were built (T-INFRA).
- C9 was **frozen** at 2026-09-24 07:05:54: protocol `5819bc6d...`, 1,200 runs, 380 bundles (VER/FREEZE.json).
- It launched at 07:06.

### 1.7 C9 outcome (09-24, 07:06 to 13:51) and mining afterwards

[record] VER/observatory/REPORT_C9.md and C9_OUTCOME_AND_ADDENDUM.md: 1,200 of 1,200 runs, audit 21/21 PASS.

| | frozen verdict | after mining |
|---|---|---|
| H1 cue gating | NO_DETECTED_EFFECT (M = I = 0.0) | **INVALID, C9-D16.** `world.Runner` never passed `output_gate`/`cue_cost` into any TaskSpec. All four arms were identical at 0.325 |
| H2 propagation | REPLICATION_EVENTS_WITHOUT_PROPAGATION | **WEAK_SIGNAL**: `7ae3f9c1437c8000` reached B depth >= 5 in 4/16, with C 0/16 |
| H3 reservoir (R3) | NOT_DEMONSTRATED: certificates 1/1/0 of 64 | **CLEAN_NULL.** The legacy id certificate would have counted 10/10/0 |

- **C9-H1R** (repaired rerun, fresh seeds, same rule) came out **COST_INTERACTION_ONLY**: I = +0.20, M = -0.10.
  - Gate plus a VM-cost cue gave competence 0.000, against 0.200 ungated.
  - With a free cue, the gate was harmless.
  - The effect transplanted to all 4 other transforms (EXPERIMENT_GRAPH `C9-H1R`, `X-H1-TRANSPLANT`).
- **X-H2-7AE3** re-ran 7ae3 with one founder on fresh seeds: 0/16 at depth >= 5 (C9 had 4/16). With k = 4 founders:
  3/16. [author] "lineages stall at depth 1-4 regardless of dose."
- The seat's later confirmatory chain (C-RUNAWAY, C-ATOMIC, C-CORE) belongs to another dossier. In summary:
  - the RECOMBINATION splice that manufactured the artifacts also *prevents* runaway heredity;
  - tape-write erosion stops pair-tape heredity in 7ae3's cell (FINDINGS E-10).
- **C9-D17/C9-D24** (FINDINGS "DEFECT C9-D24"): the H2 arm C (random bytes) is bit-identical to arm A (in situ). Arm B's
  RNG stream is shifted. "Random 0/16, in situ 0/16" is therefore **one** null, not two. [author] T-DEF-D24 audit:
  no verdict changes.

### 1.8 Downstream qualification (09-28): P-11 certifies construction, not heredity

Artemis #793 and Odysseus #803 recertified the 57 first P-11 donors (`roles/Odysseus/expedition/recert/RESULT.md`
section 5). [record]

| class | n |
|---|---|
| real informative copiers | 3 (2 OK: `7ae3`, `e141105526c59efe`; 1 context-dependent: `cb7f...s60768`) |
| painters (BWEM: write a fixed pattern that matches themselves; 14 near-homopolymers, mostly 0x36 = `LD (HL),n`) | 17 |
| STRUCTURE_WITHOUT_BEHAVIOUR (a bare LDIR/LDDR fed by register state borrowed from the host body) | 28 |
| PROV: do nothing from any state tried | 9 |

FINDINGS (ARC3 section) qualifies every "57 surviving replicators" statement to "P-11-certified construction events".

---

## 2. Table of hypotheses and experiments

| question | numbers | verdict | status / source |
|---|---|---|---|
| Spontaneous replicator from random bytes (flag) | 1,031 ADMISSIBLE / 1,031 | ADMISSIBLE under the predecessor criterion | Frozen, unchanged; NARROWED 3x (FINDINGS A-1, E-3) |
| Events are lineages? | depth 1: 911, 2: 111, 3: 9 | NARROWED | FINDINGS A-1 |
| Reproduction diversity of spontaneity | 1,031 PAIR_EXECUTION, 0 other | NARROWED (C9-D01) | REVIEW_PACKET s9 |
| Pair events survive causal assay (P-11) | 57 runs / 69 events (literal 48/54); max depth 2 | 57 survive | FOR/S1C_P11_REASSAY.md |
| Are the 57 genomes copiers? | 3 copiers, 17 painters, 28 SWB, 9 PROV | QUALIFIED to construction events | Odysseus recert RESULT s5; FINDINGS ARC3 |
| Endogenous-only accessibility (A-4) | 1 ADMISSIBLE, 50 WEAK, 14 INADM.; source run 0 births; exact control crossed at epoch 48 | WITHDRAWN | FOR/H4_AUTOPSY.md; FINDINGS E-4 |
| Reservoir crossed a moat | 0 / 0 / 124 (117 seeded, 7 exogenous) | WITHDRAWN as unanswerable | FINDINGS A-5 |
| First-replication timing implies no cliff | range 0-3,946 across tiers | WITHDRAWN | FINDINGS A-6 |
| Matched-pair map | 10,741 pairs, all Hamming-1; pressure +0.304 | HOLDS; pressure row scoped to EXTERNAL only (2026-09-29) | FINDINGS A-2 |
| Cycle-8 forced-read advantage | both read-order rows favour ANSWER_BEFORE_READ | OPEN; "cycle 8 established it" WITHDRAWN | FINDINGS A-3 |
| Non-pair physics: where the chain breaks | 907 FREE runs, 0 births; OVERWRITE 0/656 births >= 0.90 | HOLDS: no search; the protocol (FREE) or fidelity (OVERWRITE) is the barrier | FOR/S1A_FUNNEL.md; FINDINGS E-1 |
| C9 H1 cue gating | 0.325 in all 4 arms | INVALID (C9-D16) | C9_OUTCOME |
| C9-H1R | I = +0.20, M = -0.10 | COST_INTERACTION_ONLY (CONFIRM) | EXPERIMENT_GRAPH C9-H1R |
| C9 H2 propagation | 15/16 specimens never reach depth 2; 7ae3 B 4/16, C 0/16 | REPLICATION_EVENTS_WITHOUT_PROPAGATION (frozen); WEAK_SIGNAL (mined) | REPORT_C9.md |
| 7ae3 replication on fresh seeds | k=1: 0/16; k=4: 3/16 | Establishment-lottery prediction FALSIFIED | EXPERIMENT_GRAPH X-H2-7AE3 |
| C9 H3 easy-niche reservoir | R3 certificates 1/1/0 of 64; cell 4931: 0 crossings; cell a621: crossed_ever 24/29/25 of 32 | NOT_DEMONSTRATED / CLEAN_NULL | C9_OUTCOME; C9-H3-NULL (easy niche NOT_COMPETENT, held 0.000) |
| C9 H4 | none | WITHHELD (A-22) | PREREGISTRATION |

---

## 3. All withdrawn interpretations, with reasons and evidence

Each entry gives the claim, the reason it was withdrawn, and the evidence.

**W-1. Pair-tape similarity = replication** (rehearsal, 09-19).
- Why withdrawn: a converged population is 90% self-similar. The flagged specimen had `copy_bytes` 0 and no copy loop.
- Evidence: memory `feedback_similarity_is_not_copying.md`; VER/world.py comment near line 823.

**W-2. "All 36 spontaneity flags INADMISSIBLE"** (first adjudicator).
- Why withdrawn: it read fields the index did not carry (Z80A-D03). The same runs have `replication_events >= 1` in their
  per-run records.
- Evidence: Z80A/DEFECTS.md D03.

**W-3. REPORT rev 1 claims.**
- Why withdrawn:
  - R-01: sign inversion of two effects;
  - R-02: named a WEAK run as the sole admissible instance, taken from SPECIALS, which carries no verdict;
  - R-03: reservoir answerability and an "accessibility cliff";
  - R-04: 24 of 28 axes shown.
- Evidence: FINDINGS section B.

**W-4. "The replication detector ... is holding"** and "matched-pair effects are not affected".
- Why withdrawn:
  - The pair detector was later shown to credit the splice (Z80A-D05) and to fail P-11 on 974 of 1,031 runs.
  - The matched-pair pressure row was scoped to EXTERNAL-only on 09-29.
- Evidence: Z80A/DEFECTS.md "What is NOT affected"; FOR/S1C; FINDINGS A-2 scope note.

**W-5. 1,031 "spontaneous replicators" as replicators.**
- Why withdrawn: narrowed four times.
  1. Depth 1 in 911.
  2. All pair-tape (C9-D01).
  3. 57 under P-11.
  4. Only 3 of the 57 donors copy their own genome.
- Evidence: FINDINGS A-1, E-3, ARC3 "QUALIFICATION OF CYCLE-9-ERA COUNTS"; Odysseus recert.

**W-6. A-4 endogenous-only accessibility.**
- Why withdrawn:
  - the control was a sibling's M-tier seed-1816 run (Z80A-D04);
  - the endogenous population never reproduced;
  - held moved with `COEVO_ENV` drift;
  - the exact control crossed first (epoch 48).
- Evidence: FOR/H4_AUTOPSY.md; FINDINGS E-4.

**W-7. The "4x runtime = early extinction" hypothesis** (REVIEW_PACKET open question 3; FINDINGS A-4 "suspicion").
- Why withdrawn: 0 deaths. The gap is execution plus the validation cache.
- Evidence: FOR/H4_AUTOPSY.md cost decomposition.

**W-8. A-5 reservoir stepping stones**, and D02's claim that the question "is answerable after the campaign" from lineage
records.
- Why withdrawn:
  - lineage is a 400-event tail, thinned to 50 under disk pressure;
  - only the parent's niche is stored;
  - migrations are not logged;
  - all 124 flags are seeded or exogenous.
- Evidence: FINDINGS A-5; Z80A/DEFECTS.md D02.

**W-9. A-6: first-replication timing implies no sharp accessibility cliff.**
- Why withdrawn: the range 0-3,946 spans two tiers with different budgets and 35 physics/structure/representation combinations.
- Evidence: FINDINGS A-6.

**W-10. "Cycle 8 showed forced read wins"** (prereg rev A).
- Why withdrawn:
  - Cycle 8 established the obstruction.
  - Forced read was a proposal, never a result.
  - `FORCED_READ` also changes the target and the inputs.
- Evidence: VER/PREREGISTRATION.md A-3, A-4; FINDINGS A-3.

**W-11. Rev A H1 explanation E3** (the derived moat tag was to blame).
- Why withdrawn: all 10,741 pairs are Hamming-1 on the declared axis, and a label cannot alter dynamics.
- Evidence: PREREGISTRATION A-6.

**W-12. The rev-A/rev-B P-1 certificates.** Rev A's was "easy-niche ancestry"; rev B's walked organism ids.
- Why withdrawn:
  - Rev A's certificate could be satisfied without the lineage ever leaving the niche.
  - Rev B's id walk certifies identity, not material (C9-D14). Zero-edge certificates were possible (`lineage_len 1`).
- Evidence: PREREGISTRATION A-1, A-19, A-24; PREFREEZE_STOP; D14_PROBE.json.

**W-13. "H3 arm B has identical migration".**
- Why withdrawn: NICHES_HIGH_MIG migrates at 0.08 against the reservoir's 0.02 (C9-D13).
- Evidence: PREREGISTRATION A-21.

**W-14. Rev-B H2 panel** (16 specimens drawn from the 1,031).
- Why withdrawn: only 2 of the 16 survive P-11, and none is retained.
- Evidence: VER/S4_CANDIDATE.md s2.

**W-15. The rev-B proposed protocol hash.**
- Why withdrawn: no derivation existed anywhere in the repo (C9-D08).
- Evidence: FINDINGS E-5.

**W-16. C9 H1 "NO_DETECTED_EFFECT" read as "no effect".**
- Why withdrawn: the intervention never reached the task (C9-D16), so the arms were identical to the decimal.
- Evidence: C9_OUTCOME_AND_ADDENDUM.md.

**W-17. "H2 arms B and C share the background; only the bytes differ"**, and "random 0/16 + in situ 0/16" read as two
nulls.
- Why withdrawn: RANDOM_MATCHED equals in situ, and B's RNG stream is shifted by L draws (C9-D17, C9-D24).
- Evidence: FINDINGS "DEFECT C9-D24", wording errata.

**W-18. The erratum "the 57 P-11 survivors arose at tier L".**
- Why withdrawn: the correct split is 53 at L and 4 at M. [computed here] Confirmed: 53 L, 4 M.
- Evidence: FINDINGS R-11 verification.

**W-19. The X-PAIR-NORECOMB CLEAN_NULL.**
- Why withdrawn: downgraded to INVALID because it had no positive arm and both arms sat at P-11 events 0/0.
- Evidence: FINDINGS R-11.

**W-20. Treating a P-11 event as a property of the genome.** This covers the H2 arm-B "donor genome" implant and the phrase
"57 replicators".
- Why withdrawn: P-11 re-executes the recorded register file. 54 of 57 genomes do not copy from any state they can
  reach on their own.
- Evidence: Odysseus recert RESULT s7.1; FINDINGS ARC3.

**W-21. "7ae3 propagation is an establishment lottery"** (from C9's 4/16).
- Why withdrawn: fresh-seed replication at k=1 gave 0/16. The prediction of about 0.68 at k=4 was falsified (3/16).
- Evidence: EXPERIMENT_GRAPH X-H2-7AE3.

**W-22. SI framing of the downstream C-CORE chain.** Out of arc; noted for completeness.
- Why withdrawn: withdrawn by operator directive on 09-26.
- Evidence: FINDINGS E-10 last paragraph.

Superseded, not withdrawn: **PREFREEZE_STOP_2026-09-24.md** says "Nothing is frozen". The freeze happened later the same
day. The file was never annotated (section 6, A-9).

---

## 4. Rulers and detectors that were built

| ruler | certifies | known blind spots (source) |
|---|---|---|
| **Pre-launch similarity detector** (>= 0.90 byte identity) | resemblance | convergence reads as replication (W-1) |
| **Private-slot evidence gate** (ALLOC snapshot, BIRTH differencing, donor writes >= half the child; separate `births_similar_no_write`) | the organism placed the child's bytes | Sound for what it measures. It fired 0 times from random starts because FREE physics never varied (S1-A) |
| **Predecessor pair criterion** (fid_other >= 0.90 read *after* `_mutate`; fid_self < 0.90; donor writes_other >= n/4) | "the victim half now resembles the donor, and the donor wrote something into it" | The splice (Z80A-D05); pre-existing similarity plus partial overwrite; writes to padding; writes the victim later overwrites (P11_SPEC s1 fixtures) |
| **P-11** (VER/p11.py, P11_SPEC.md): predecessor prefilter AND a randomized-victim assay, 3 draws, majority 2 | the recorded interaction, re-run from its exact state, rebuilds a random victim by the donor's own writes | See the list below this table |
| **Causal replication depth** (P-2; on the pair tape, P-11 edges only; the predecessor depth is kept beside it) | the longest chain of causal edges | See the list below this table |
| **P-1 ancestry certificate** (born easy -> migrated -> resident hard -> crossed hard) | an organism-id path | On the pair tape, id is not heredity (C9-D14). Retained as `id_certificate_legacy`; it counted 10/10/0 where R3 counted 1/1/0 |
| **R0-R3 tournament** (H3_RULER_TOURNAMENT.json) | the choice of H3 ruler | 9 synthetic fixtures, built by the same seat that chose the winner. R2's window k = 50 was fixed before the tournament |
| **R3 material certificate** (z8taint: every byte carries the niche where its value was made, through the VM and through alignment under mutation; a crossing outside the easy niche by a genome with >= 0.50 easy-niche material) | material provenance at the crossing | See the list below this table |
| **P-3 / P-4 / P-5 / P-7** | P-3: separate ever/final outcomes. P-4: reservoir flag only on a complete certificate, seeded runs excluded. P-5: the INDEX suffices for adjudication. P-7: immutable bundles, identical results under reordering or kill/resume | Each ships with an injected-defect negative control (REVIEW_PACKET s3). P-7 did not catch that bundle *arms* share RNG draws (C9-D24) |
| **Anticheat** | runner births, sandbox, leakage and similar | `SANDBOX_ESCAPE` counts *blocked attempts*, not escapes, yet it is listed as an exploit on 11,531 runs (PACKET.md) |
| **adjudicate.py** (CROSS 0.90, MARGIN 0.25) | post-hoc flag admissibility | Reads final-state numbers only. D04 inherited controls went undetected until S1-B |
| **report_audit / report_audit_c9** | every published number is recomputed from the record | C9-D03: the receipt was once written against a deleted temp file |
| Downstream: **CVT-R** (Artemis), **Odysseus recert**, **DOM screen** | heredity across generations; genome-level copying; painter screen | Outside this arc; they bound what P-11 can mean |

**P-11 criteria.**
- C2: rebuild >= 0.90.
- C4: donor authorship >= 0.90 of the directed changes. Primary = last value change (`prov`); literal = last write
  (`prov_lit`).
- C5: donor-disabled control < 0.90.

**P-11 blind spots.**
1. **Painters.** A near-homopolymer donor that fills the victim with its dominant byte passes. [record] 17 of 57 per the
   Odysseus recert; 24 of 57 have dominant-byte share >= 0.8 (section 5.7).
2. **Body state versus genome.** The re-execution uses the recorded registers, so a bare LDIR on borrowed HL/DE/BC passes
   (28 SWB).
3. **C5 is nearly vacuous.** It was decisive in 2 of 7,919 events (P11_SPEC s4 predicted this).
4. **The literal authorship reading** kills genuine block copiers (P11_SPEC s3.1).
5. **Only predecessor-accepted events are assayed.** A real copy that fails the post-splice fidelity clause is never seen.
6. **Thin margins.** 26 of 57 survivors rest on one event passing exactly 2 of 3 draws (R-05, verified TRUE). Per-draw
   files are gitignored.
7. **Construction is not heredity.** CVT-R: 19 P-11-certified genomes fail generation 2.

**Causal replication depth, blind spots.**
- It is world-level, not founder-rooted (FINDINGS E-10 scope note).
- An unbroken certified chain is capped at about 1/p generations by a per-edge P-11 break rate of about 5-16%
  (X-CERT-BREAK).
- Pair "births" rename a body in place.
- The ">= 5" bar had no precedent (C9-D12).

**R3 material certificate, blind spots.**
- **Material is not function.** A crossing made of easy-niche bytes need not be a crossing *caused* by them.
- **Pair writes move material in every arm**, including C (A-25).
- **Tags depend on the alignment heuristic** under indels.
- **The H3 easy niche was itself not competent** (held 0.000, C9-H3-NULL). The ruler could only return near-zero.

---

## 5. Unmined evidence, with numbers computed here

The **universe** here is `pool`: the random-start `PAIR_EXECUTION` runs with `derived.spontaneity_test = True`.
[computed here] It holds 1,934 runs. By world:

| world | runs | flagged |
|---|---|---|
| PAIR_TAPE | 1,635 | 1,031 |
| GRID | 199 | 0 |
| GRAPH | 100 | 0 |

`PAIR_EXECUTION` in GRID and GRAPH worlds never flags, even though it is the same physics label.

### 5.1 The scheduler manufactured the 1,031; the unbiased rate is small

[computed here]
- 979 of the 1,031 flags sit at tier L.
- The tier-L pool is 1,195 runs:
  - 696 INTERVENTION and 194 VERIFY;
  - 965 of them in the LATE stage;
  - reason strings such as "late verification of X (best interest 0.95) : intervention on read_order";
  - 96 distinct targets;
  - 911 of 1,195 on the RECOMBINATION axis.
- The tier-M pool (731 runs) is 100% `exploration_floor`, spread roughly uniformly over the 8 atlas axes.

The splice artifact generated interest: the replicated signal carries weight 0.30. Interest steered LATE allocation back
into RECOMBINATION cells, and those produced more artifacts. **1,031 is a count shaped by a feedback loop, not a rate.**

In the unbiased exploration-floor sample (tier M):

| | flag rate | P-11 survivors |
|---|---|---|
| all M-pool runs | 52/731 (7.1%) | 4/731 (0.55%) |
| RECOMBINATION | 40/102 | **0/102** |
| other axes | 12/629 (1.9%) | 4/629 |

### 5.2 The axes that matter for the flag are not the axes that matter for causation

[computed here] Per pool run, the P-11 survival rate is:

| | P-11 survivors | flag rate |
|---|---|---|
| RECOMBINATION | 35/1,014 (3.5%) | 90% |
| other axes | 22/920 (2.4%) | 13% |

The P-11 difference is Fisher p = 0.18. Among flagged runs, however, non-RECOMBINATION flags survive at 22/121 against
35/910 (p = 5.9e-8).
- **The atlas axis drives the flag and barely touches the causal rate.**

At tier L, P-11 survivors per pool run by factor (flag rate in parentheses):

| factor | level | P-11 per pool run | flag rate |
|---|---|---|---|
| **copy_primitive** | BLOCK | 45/612 (7.4%) | 0.548 overall |
| | BYTEWISE | 8/583 (1.4%) | 0.518 overall |
| mutation_rate | LOW | 50/735 | |
| | MID | 3/265 | |
| | HIGH | **0/195** | |
| mutation_operator | BOTH | 1/208 | |
| | OPCODE | 16/209 | |
| | OPERAND | 36/778 | |
| pressure | PREDATION | 1/148 | 108/148 flagged |
| | EXEC_TIME_COST | 4/209 | 192/209 flagged |
| structure | RESERVOIR | 1/122 | |

- **copy_primitive** has no effect on the flag rate but a 5x effect on P-11. Among flagged runs, 47/531 against 10/500,
  Fisher p = 8.8e-7.
- PREDATION and EXEC_TIME_COST flag often but almost never survive.
- Only one tier-L P-11 survivor is in RESERVOIR, yet RESERVOIR was the structure H3 then tested.
- Of the 10 BYTEWISE survivors, all 10 are near-homopolymers (Odysseus table: BYTEWISE near-homopolymer n = 10). **No
  high-information P-11 event exists under BYTEWISE copying.**

### 5.3 The index cannot see causation, but it could see non-propagation

[computed here] Survivors against flagged non-survivors:

| field | 57 survivors | 974 flagged non-survivors |
|---|---|---|
| `fid_mean_final` | 0.940 | 0.939 |
| `span_mean_final` median | 64 | 64 |

The index fidelity key is blind to causality.

- `dom_share_final` sits at 1/384 (0.0026) in all 57 survivors, with a maximum of 2/384. **At run end no genome occurs
  more than twice** in any P-11-surviving population.
- That is index-level evidence of non-propagation, available since 09-22 and never cited.
- `invader_share_final` is null in every pool run: the field was never populated for random pair runs.
- `births_endogenous > 0` if and only if the run is flagged. All 903 unflagged pool runs have 0 births and replication_rate
  0, so the index holds **no visible near misses**. Near misses would have to be mined from per-run telemetry, which is
  not in this worktree.

### 5.4 The splice confound was visible in the frozen adjudication two days before P-11

[computed here from Z80A/observatory/ADJUDICATION.json]

- `births_similar_no_write` exceeds 10 in 906 of 910 RECOMBINATION flags and in **0 of 121** other flags. It is a
  perfect marker of Z80A-D05.
- D03 put this ratio "in front of the reader" on 09-22.
- P-11 survival by that counter:
  - <= 10: 22/125 (17.6%);
  - > 10: 35/906 (3.9%);
  - by bin: 0: 6/46; 1-10: 16/79; 11-40: 0/153; > 40: 35/753.
- Totals: 7,919 replication events against 48,418 resemblance-without-write events. The frozen `replication_events`
  equals the reassay's `n_pred_events` in 1,031 of 1,031 runs.

### 5.5 What precedes a replication signal

[computed here]
- The first predecessor event falls at a median of 15.6% of the run for survivors and 14.1% for non-survivors.
- No survivor flagged within the first 10 epochs; 27 non-survivors did.
- The first P-11 event coincides with the first predecessor event in only **8 of 57** survivors; 49 are later.
- The first-replicator genome preserved in SPECIALS equals the first P-11 donor in only 8 of 57.
  **The genomes PACKET.md prints as exemplars are mostly not the causal donors.**
- Survival rises weakly with the predecessor event count: 1 event 4/79; 2-3 events 6/177; 4-7 events 7/322;
  8-15 events 30/389; 16-31 events 7/54; 32+ events 3/10.
- Donor writes: the upper quartile is 168 for survivors against 42 for non-survivors.

### 5.6 Replication does not associate with task crossing

[computed here] At tier L, `crossed` is:

| group | crossed | held >= 0.90 at final |
|---|---|---|
| survivors | 33/53 | 0 |
| flagged non-survivors | 500/926 | 4 |
| unflagged | 113/216 | 0 |

Crossing runs at 52-62% in every group. The serendipity tag `task_repro_overlap` equals the `crossed` count exactly in
every group, so it is `crossed` under another name.

### 5.7 Joining the Odysseus recert to Cycle 9 (never done in the record)

[computed here; the labels come from `roles/Odysseus/expedition/recert/L2_rows.json`]

**H2 panel.**

| label | specimens |
|---|---|
| LABEL_OK | 1 (`7ae3`) |
| LABEL_CONTEXT_DEPENDENT | 1 (`cb7f`) |
| STRUCTURE_WITHOUT_BEHAVIOUR | 11 |
| LABEL_PROVENANCE_ONLY | 3 (`4931614d`, `48c75e14`, `a6211683`) |

The only H2 signal came from the only certified copier on the panel. Given the later recert, the H2 null for the other
15 was nearly predetermined.

**H3 cells.** Both are LABEL_PROVENANCE_ONLY near-homopolymers:
- `4931614d...s1190`: donor 0x36 at share 0.94. Its same-cell survivor `s9368` is a BWEM painter.
- `a62116831...s7926`: donor 0xfc at share 0.95.

So H3 asked whether an easy niche seeds crossings in two cells chosen because a non-copier once passed P-11. Combined
with the easy niche's own incompetence (C9-H3-NULL), **H3 measured little about reservoirs with heredity.**

The dominant-byte share of the 57 first P-11 donors is >= 0.8 in 24 and >= 0.5 in 27. That reproduces the Odysseus
split of 14 BLOCK plus 10 BYTEWISE near-homopolymers.

### 5.8 Matched pairs

[computed here]
- 12 of the 57 survivors have a matched partner in the index.
- In the 7 partners that are themselves random pair runs, the partner was **flagged but not P-11** in every case.
  Examples: BLOCK to BYTEWISE 2 of 2; PRIMITIVE to NONE; ADD1 to XOR5A.
- self_location NONE to PRIMITIVE, 17 pairs: flag-concordant in 17 of 17. The flag is insensitive to self-location.
- The pairs are small, but they are the only same-seed causal comparisons for P-11 that exist in the frozen record.

### 5.9 Seeded replicators on the pair tape

[computed here] Seeded replicators replicate in:

| physics | replicated |
|---|---|
| ENDOGENOUS_COPY | 1,170 / 1,198 |
| OVERWRITE | 709 / 726 |
| CONSTRUCTIVE | 695 / 722 |
| ENDOGENOUS_PARTIAL | 675 / 705 |
| **PAIR_EXECUTION** | **842 / 1,853 (45%)**; 448 with >= 50 births |

The one physics that produced every "spontaneous" flag is the one most hostile to a known replicator. This anticipated
the later tape-write-erosion result (C-ATOMIC) by two days.

### 5.10 Questions the record can answer and nobody asked

1. Re-estimate the spontaneous P-11 rate on the exploration-floor sample only, by axis, with confidence intervals (5.1).
2. Per-run telemetry could test whether `births_similar_no_write` bursts precede P-11 events, and so serve as a leading
   indicator. It lives in the graphworld worktree, `Z80A_FROZEN_OBS`.
3. Cross the copy_primitive effect with the Odysseus classes: is BLOCK's 5x advantage entirely the 3 copiers plus the
   SWB class?
4. `dom_share_final` over time in the 57: did any genome ever exceed 1% share mid-run?
5. The two flagged runs with `dom_share_final` 1.0 and pop_final 1 (`14530181c07dba74-s87860-tL-a0`,
   `cb350944c642b1c6-s13386-tL-a0`, both PREDATION with HIGH mutation) are near-extinctions carrying the flag. What
   killed them?

---

## 6. Anomalies worth preserving

1. **The all-zero replicator.** `5e20dc8a5cf24970-s4912-tL-a0`:
   - its first predecessor replicator genome is 64 zero bytes;
   - its first P-11 donor is 95% 0x00 and passed 3 of 3 draws;
   - the recert labels it PROV.
   A random victim "rebuilt" to near zeros. This is the purest painter/erasure case.
2. **The convergent 0x36 motif.** `LD (HL),0x36`, whose operand equals its opcode, dominates the first P-11 donors of 12 runs in
   11 unrelated families (4931, 0e6c, 473d, 4c22, 4e3b, 164f, 2448 twice, 2cb5, 12ad, 2a6c, dab2). It also dominates 27
   of 29 child genomes in the ancestry replay (`campaigns/ancestry-replay-2026-09-28/CVTR_RECONCILIATION.md`). It is the
   substrate's cheapest self-matching construction.
3. **The adjudicator failed in both directions on the same flag.** v1 called all 36 INADMISSIBLE for a false reason. v2
   called all 1,031 ADMISSIBLE with no causal check (Z80A-D03 against D05).
4. **H1's four arms were identical to three decimals** (0.325, 0.20, 0.05). Identical arms are a defect signature, not a
   null. The report audit passed 21/21 over them.
5. **PREREGISTRATION.md contradicts itself.** Its header reads "rev D ... NOT FROZEN. NOT LAUNCHED." and its gate row 6
   reads "not done", while the freeze block reads "FROZEN 2026-09-24T07:05:54". PREFREEZE_STOP says "Nothing is frozen."
   All of these sit in the frozen directory. The constants hash moved `ade1f755` -> `b1c8a904` -> `c0e488de`
   (frozen). P11_SPEC says the P-11 values were unchanged.
6. **The H4 source run crossed with a frozen genome pool.** Its held score reached 1.0 purely through `COEVO_ENV` drift.
   The exact control crossed at epoch 48 and then lost it to mutation. Environmental drift alone can produce a
   "crossing"; any accessibility claim under `COEVO_ENV` needs a no-reproduction null.
7. **`ENV_MIG` was inert, P-8 placed everyone in niche 0, and P-9 had COEVO bypass the reservoir.** Three structural
   factors in the 72-hour grammar did not do what their names say, and 177 of the 1,031 sit in ENV_MIG cells (C9-D02).
8. **`SANDBOX_ESCAPE` fired on 11,531 runs, about half the campaign.** Its evidence note says "blocked attempts, not
   successful escapes". It is a measure of write-outside-own-span behaviour, which is exactly the donor-write behaviour
   that pair-tape heredity needs.
9. **The frozen 7ae3 signal (4/16) did not reproduce at k = 1 on fresh seeds (0/16).** The later confirmations (C-RUNAWAY,
   C-ATOMIC) changed the world (splice off, atomic write-back) rather than replicating the C9 condition.
10. **P-11 survivor `cb7f5ca16e697938-s60768-tL-a0` has donor-authored share 0.0** on its ordinary event, yet it passes
    P-11 on the randomized victim (FOR/P11_REASSAY.jsonl, `first_p11_event`). The assay and the observed event can
    disagree about authorship.
11. **Arm C of H2 was the same simulation as arm A** (C9-D17/D24). "Random-bytes null" and "in situ" were one experiment.
    The seat had already written the defect-signature lesson for H1, and the same signature went unrecognized in H2.

---

## Summary

1. The first "spontaneous replicator" (09-19 rehearsal) was 90% similarity with no copying. The private-slot detector was
   fixed to require donor writes; the pair-tape detector kept a similarity-plus-write-count heuristic.
2. That pair detector produced all 1,031 ADMISSIBLE spontaneity flags. 910 of them came from one axis, where the world's
   own RECOMBINATION splice made the match (Z80A-D05).
3. The 1,031 is a scheduler-shaped count: 979 come from LATE tier-L intervention runs. Unbiased sampling gives a 7.1% flag
   rate and a 0.55% P-11 rate, with 0 of 102 on the RECOMBINATION axis.
4. P-11 (a randomized-victim assay, prospectively specified) keeps 57 runs (48 literal) with maximum depth 2. A later
   recert finds only 3 of those 57 donors copy their own genome; 17 paint.
5. Non-pair physics never searched (0 births means 0 mutation). A-4 was withdrawn: its control was unmatched and its
   population never reproduced.
6. C9 froze at protocol 5819bc6d after C9-D14 forced the R3 material ruler. H1 was INVALID (C9-D16), and the rerun gives
   COST_INTERACTION_ONLY. H2 is no propagation except 7ae3 (4/16), which did not reproduce at k = 1. H3 is a clean null.
7. The index could not see causation (fid_mean_final 0.940 against 0.939). It did show non-propagation:
   dom_share_final <= 2/384 in every survivor.
8. `births_similar_no_write` > 10 perfectly marked the splice artifact (906/910 against 0/121), available on 09-22.
9. copy_primitive has no effect on the flag but a 5x effect on P-11 (p = 8.8e-7), and every BYTEWISE survivor is a
   near-homopolymer. The H2 panel held 1 copier, and both H3 cells were painter or provenance-only cells.
10. 22 withdrawn or superseded interpretations are listed with evidence. Path:
    `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/dossiers/C_origins_forensics_c9.md`
