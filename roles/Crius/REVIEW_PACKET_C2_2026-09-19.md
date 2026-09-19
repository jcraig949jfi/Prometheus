CRIUS -- CAMPAIGN 2 REVIEW PACKET -- ACCESSIBILITY FRONTIER (D2), RUNGS A-B
2026-09-19  instance m2-8d43bbf9  branch crius/base-role-adopt-2026-09-18
Ruling: roles/Crius/prompts/2026-09-19_c2_ruling/ (26658551e). Prereg:
crius/DESIGN_C2.md (565135bd0, before code). Build b971c3a8f + fixes
(713b2773f telemetry caps, 9c5caf812 calibration-object robustness).
Configs: c2a 401915ec4da9443a, c2b c9c87cec99eb063f, c2c 416bbe8b9be34706.
World 7c53db874324b532, generator 624728b00fdd3f2f (unchanged since C1).
================================================================================

0. VERDICT

The frontier was measured, and it is not where the ladder was built to find
it. On the PARTS diagnostic the reuse chain has a one-link valley followed
by a cliff: at rung B, recorder-only and invoker-only are worth nothing
(-0.001 and -0.002 fitness, 0/10 streams), recorder + invoker together are
worth +1.14 (7/10 streams, +1.1 tasks, cost -4616) at 26 edits from the
seed; at rung C, planner-only is worth -0.057 from scratch and +16.7 with
procedures transplanted, and the complete recorder + invoker + planner
mechanism is worth +15.97 over planner-only (10/10 streams, +15.9 tasks).
Search under paired streams with a takeover check found no gradient
toward that chain at rung A (9 runs) or rung B (9 runs): no lineage
created a procedure and invoked it usefully; the only reproducible
ACCUMULATED > FRESH effect (E4, rung B recombination_s1) is a record-id
clock used to shift the enumeration order, reproduced exactly by twenty
empty records made by nobody. Rung C's gate failed on witnesses E and H
against the strongest bytecode control I could write (F and G, the
ruling's retained causal requirement, pass), so rungs C and D were not
searched under the preregistered rule. Predictions: R1 held at A, lost at
B (2/9 runs below the seed); R2 held in structure, lost in magnitude; R3
half; R6 lost (distances 26 and 47, not <= 12 and <= 25); R4/R5 untested.
A decision is needed on rung C (section 9).

1. WHAT WAS FROZEN, WHAT MOVED (DESIGN_C2 s1-s4, s11)

  Frozen: RELAY, generator, sealed namespaces, C1b budgets, C1_FITNESS,
  FAIL/strict ACT, controls, gates A-H, qualification (final-population
  rank, 3 sealed streams). Block ids remain values.
  Moved, uniformly: paired common-random streams (2 per iteration, parents
  re-evaluated) + takeover check on an independent third stream (every
  displacement decision logged); metadata charge of 2 bytes per record/
  block/procedure (CRIUS-28/31 fossils keep their signatures under it,
  fixtures F1/F4); post-success actions are ignored no-ops (a recording
  can close after an early success); program length 96.
  Rung A: C1b substrate. Rung B: typed PROCEDURE objects (PREC_BEGIN/END
  record the revealed primitives of the actions between them, relative to
  the first step's position; PINVOKE h, a executes with an absolute
  argument through a substrate-maintained calibration artifact, itself a
  block: FRESH/RESET/SCRAMBLE/ABLATION/TRANSPLANT act on it; an organism
  may tamper with it and it re-initialises). Rung C: + PSIM (mental
  application) and PMATCH. Rung D: + PARTS as splice donors (not run).

2. PARTS DIAGNOSTIC (gate streams 301-310; controls only; s5)

part        len dist   fit  solv  cost |  dFit   sign dSolv dCost | tpFit tpDFit
  ENUMERATE_VM   39   - 21.720 21.3  9843 |    -     -     -     -  |
  P_BASE         19   0 21.924 21.5  9378 |    -     -     -     -  |
  P_CAL          35  18 21.924 21.5  9390 | -0.000 0/10   0.0   +13 |   (rung A)
P_REC          25   7 21.923 21.5  9485 | -0.001 0/10   0.0  +108 | 21.92 -0.001
P_INV          37  20 21.922 21.5  9592 | -0.002 0/10   0.0  +214 | 23.16 +1.238
P_REC_INV      43  26 23.060 22.6  4976 | +1.138 7/10  +1.1 -4616 | 23.07 -0.094
P_PLAN         58  41 21.867 21.5 16376 | -0.057 0/10   0.0 +6998 | 38.67 +16.74
P_REC_INV_PLAN 64 47 37.841 37.4  7277 | +15.97 10/10 +15.9 -9098 | 38.66 -0.000
  (tp columns from rung C, typed donor P_REC_INV_PLAN)
  dist = edit distance from P_BASE; dFit = part minus its immediate ancestor
  (P_REC_INV vs P_INV; P_REC_INV_PLAN vs P_PLAN) on the same paired streams;
  tp = store pre-loaded from the rung's positive control (rung B's donor is
  the block control, so its tp column is uninformative; rung C's is typed).
  Reading: the first link (record OR invoke) has no value; the pair has a
  small value that is competence (+1.1 tasks: physical trial of a stored
  procedure solves one chain per lifetime) as much as cost; the planner is
  worthless without procedures and worth +16 with them. Category (s5):
  parts individually non-beneficial -> coordination / valley, one link deep
  at B; then a cliff at C whose height (+14.8) is only visible once the
  pair exists. Fitness granularity is NOT the limiting factor at B: the
  pair's +1.14 is a competence gain, well above the stream noise.

3. GATES

  A: PASS x8 (PROCEDURE_REUSE_C1).  B: PASS x8 (block channel unchanged;
  PROCEDURE_REUSE_C1).  C: FAIL -- E on 1/3 streams (302: reuse_gain C-E
  = 12 percent of FRESH cost, floor 20 percent; the bytecode control solves
  27/50 there vs 38/38 on 301/303), H on 3/3 (1/0/1 blocks reached >= 3
  distinct arguments, floor 2); A-D and F, G PASS (ARTIFACT_TRANSPLANT
  6/6/6 vs CODE_ONLY 1/1/0 solved, cost 147-154 vs 191-193; ablation ==
  CODE_ONLY). A widened planning window (10 objects) did not change E or
  H (crius/runs/gate_c2c_window10) and was reverted. D: not gated
  (same substrate as C).

4. SEARCH READOUT (crius/runs/C2_SUMMARY.md; per-run REPORT.md, LINEAGE.md)

  rung A (9 runs)  fitA (fitF if different)   sucA          blk invk
  random  s1/s2/s3   7.2 (6.2) / 9.2 (8.6) / 3.5   7.0/9.0/3.3  32/54/0  849/0/0
   seeded  s1/s2/s3  22.8 / 22.1 / 21.8            22.3/21.7/21.3  0     0
   recomb  s1/s2/s3  21.8 / 20.1 / 20.1            21.3/19.7/19.7  0     0
  rung B (9 runs)
   random  s1/s2/s3   6.6 (3.9) / 2.8 / 2.5          6.3/2.7/2.3  39/3/1   0
   seeded  s1/s2/s3  19.4 / 21.8 / 22.8            19.0/21.3/22.3  1     0
   recomb  s1/s2/s3  19.1 / 20.8 / 22.8            18.7/20.3/22.3  1     0
  (seed ENUMERATE_VM: 19.3 solved on the sealed streams; "blk 1" at B is
  the substrate's calibration object.)
  Frequencies (of 7208 candidates per run): organism-made objects A
  449-3435, B 268-2832 (4-39 percent; PREC_END is one edit at B and is
  used: 107-2287 candidates executed a typed op); invoked a block A 0-2800,
  B 29-518; invoked with own-made objects A 0-2800 (all in random_s1, the
  E2 replay lineage), B 2-126 (< 2 percent); ancestral gradients (LINEAGE,
  first half -> second half of the top lineage): object creation rose in
  7/18 lineages (all three random arms at A and B, plus B recomb_s2 and B
  seeded_s1, all to 8-58 empty or junk objects per lifetime), invocations
  rose in 3/18 (A seeded_s2 0 -> 36 on an empty store; B random_s1 0 ->
  378 and random_s2 0 -> 13, both E3-type walkers); no lineage's rise in
  either quantity coincided with a rise in solved tasks.
  Reproducible ACC > FRESH (5 percent floor, competence kept, 3/3 streams):
  0 candidates in 17 runs; 6 members of ONE lineage in rung B recomb_s1
  (E4). Takeover check: 431-1066 takeovers and 201-714 blocked
  displacements per run; drift below the seed: A 0/9, B 2/9 (19.0, 18.7 vs
  19.3, within a task of the seed).

5. EXPLOIT LINEAGES (preserved; probes in crius/runs/*/probe_*.json)

  E1 rung A seeded_s2 f312bc39: ACC 15/16/17 vs FRESH 0/0/0. Stage-B
     transplant 7/419 == synthetic empty blocks 7/419; restart from empty
     at task 10 does better (8/318). A block-id clock that gates a fixed
     enumerator; FRESH's per-task restart starves it. Not reuse.
  E2 rung A random_s1 933ec695: BLK_REC_BEGIN/END records the program's
     own ACTI script into blocks (15/30/45 steps: nested recordings) and
     BLK_INVOKE replays it ~800 times per lifetime. Content is load-
     bearing (synthetic empty blocks 1/505 vs recorded 2/458) but the
     advantage over CODE_ONLY is +0/+1/+1 tasks: a replayed random walk.
     The one lineage in 18 runs whose artifact content mattered.
  E3 rung B random_s1 e342bfe7: workspace data (4096 bytes of appended
     stream and links) conditions the walk; full transplant 5/337 vs
     everything else 1/512 on one stream, nothing on the other two.
  E4 rung B recomb_s1 026d7a5a (6 qualified members): WS_REC_NEW twice per
     task; the returned record id seeds the enumeration counter, which
     counts DOWN from it; the order therefore shifts with the accumulated
     record count. Sealed streams: +0/+1/+2 tasks, cost -988/-5446/-743,
     3/3 positive. RECORD_IDS_ONLY (twenty empty records, made by nobody)
     reproduces the transplant exactly (8/297.7, 11/66.6, 14/115.2 on all
     three streams). Selected across ~300 rotating streams with the
     takeover check, so it is not stream luck; it is a systematic
     advantage of not starting every enumeration at the same index,
     carried by a ~5-bit datum. It satisfies the letter of "reproducible
     ACCUMULATED > FRESH with competence kept" and none of its substance.
  Instrument note: the substrate's calibration object made "created an
  object" trivially true and gave every acting program reuse_gain +7 at
  rung B (its re-creation cost under FRESH); the census now counts only
  organism-made objects and the reproducibility flag uses the 5 percent
  floor (c2_summary.py, dated).

6. PREDICTIONS (DESIGN_C2 s9)

  R1 rung A: no gradient, 0/9 runs below the seed -> HELD. Rung B: 2/9
     below the seed (by < 1 task) -> LOST narrowly; the takeover check
     did remove the C1b collapse (15.7, 6.7) shape.
  R2 P_REC negative HELD (-0.001, 0/10); P_INV ~0 from scratch HELD,
     +1.24 with typed transplant HELD; P_REC_INV: sign 7/10 (predicted
     >= 8/10) LOST narrowly; delta solved +1.1 (predicted 0) LOST; delta
     fitness +1.14 (predicted +0.05..+0.3) LOST upward. Category: valley,
     not fitness granularity.
  R3 creation > 20 percent of candidates: 4/9 runs (5-39 percent) HALF;
     useful invocations > 5 percent: 0/9 LOST; no reproducible ACC >
     FRESH with competence kept except by a clock: HELD in substance, and
     the criterion needs the content test (section 5 E4).
  R4, R5 NOT TESTED (rung C gate).  R6 LOST: 26 and 47 edits, not <= 12
     and <= 25; typed instructions shorten the mechanism by a factor of
     about two, not four.

7. INTERPRETATION

  - The frontier is not a single rung; it is a shape: one valley link
    (record or invoke alone) then a cliff (planning). Selection saw
    neither edge: no lineage at A or B reached the pair, whose value is
    real (+1.1 tasks) but 26 edits away with two zero-value links first.
  - Every reproducible effect selection did find is a counter: block ids
    (E1), record ids (E4), or replayed scripts (E2). Under rotating
    streams with a takeover check, E4 is genuinely selected, which says
    the search works and the chain is simply not on any gradient it can
    see.
  - The literal criterion "reproducible ACCUMULATED > FRESH with
    competence kept" is satisfiable by a ~5-bit datum; the probe's
    synthetic-count arms (blocks, records) are the discriminator and
    should be part of the criterion.

8. THE BOUNDARY, STATED

  On this VM family, with point mutation, duplication and segment splice,
  under competence-first fitness on RELAY, no evolutionary gradient
  toward the acquisition -> representation -> retention -> invocation
  chain exists at rung A or at rung B (where acquisition, representation,
  retention and invocation are each single instructions), in 18 runs of
  7208 candidates each. The chain's first useful stepping stone (record +
  invoke) is 26 edits from the seed and worth +1.14; the next (planning)
  is 21 more edits and worth +14.8. Whether rung C's single-instruction
  mental simulation, or rung D's donor parts, make the chain selectable
  is untested because the rung-C gate could not be passed by a bytecode
  control (section 3).

9. DECISION REQUESTED (rung C gate)

  (i) Accept a DECLARED deviation: at rungs C and D measure witnesses E
      and H with the block-channel control (the block channel is
      unchanged and its gate passes at B) and keep F and G -- the ruling's
      retained causal requirement, which the typed control passes -- with
      the typed control; then run C and D (R4, R5). My recommendation:
      R4/R5 are the campaign's decisive predictions and the PARTS cliff
      already shows the typed channel's value at C.
  (ii) Build a stronger typed control first (depth-3 planning or a
      duplicate-free recorder need more than 96 instructions or a Python-
      side typed control): about a day.
  (iii) Stop the ladder at C with the PARTS shape as the frontier result.

10. PROCESS ERRORS (ledger rows)
  - My driver treated an existing gate receipt as a pass; rung C's
    searches ran ~20 min under a failed gate before I stopped them; their
    receipts were deleted, nothing from them is cited.
  - Two launch bugs (takeover log opened before its directory; donor
    pool name shadowing the worker pool) and two runtime failures
    (organism tampering with the calibration table; unbounded telemetry
    lists exhausting worker memory) cost about two hours; each is a
    dated commit and the C2 tests cover the substrate cases.

11. PROVENANCE
  MEASURED: sections 2-6 (receipts: crius/runs/parts_c2*/, gate_c2*/,
  search_c2[ab]_*/ with candidates.jsonl.gz, takeovers.jsonl, qualify_qual/
  (gz), REPORT.md, LINEAGE.md, probe_*.json; C2_SUMMARY.md). INFERRED:
  sections 7-9. Wall time: searches 13-28 min each at A/B (paired streams
  + check triple the C1b cost). Receipts gzipped 815 MB -> 58 MB.
================================================================================
