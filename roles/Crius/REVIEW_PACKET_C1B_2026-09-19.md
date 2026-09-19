CRIUS -- CAMPAIGN 1b REVIEW PACKET -- D1 ISOLATION (CHAIN BUDGETS ONLY)
2026-09-19  instance m2-8d43bbf9  branch crius/base-role-adopt-2026-09-18
GO verbatim: roles/Crius/prompts/2026-09-19_c1b_go/ (a78569dad).
Calibration BEFORE search: crius/calibrate_c1b.py + crius/runs/calibration_c1b/
(be339ac0f). Config c1b.json hash bbf684cd638167f2 (= c1.json with chain
budgets 800/1200/1600 -> 50/50/50; nothing else changed). Gate A-H on
c1b: crius/runs/gate_c1b/GATE.md, ALL PASS (553ccff52).
================================================================================

0. VERDICT

The walker gradient is gone and nothing took its place that keeps state.
With chain budgets that give a random walk < 5 percent of chains, nine
runs (random / seeded / recombination x 3 seeds, 300 iterations, 64,872
candidates) produced no qualified lineage with a reproducible
ACCUMULATED > FRESH effect, none that created a block, none whose
invocations reached a store with a block in it, and no ancestral
gradient toward keeping or using state. The final-population tops are
cheaper counter enumerators (19-21/50 on sealed streams, the seed's
19.3, at 7-12k interactions against the seed's 11.2k); two of nine runs
drifted BELOW the seed (15.7, 6.7) under single-stream selection noise;
one exploit appeared and is preserved: monotonically growing record ids
that turn a program's actions invalid as they accumulate (a negative
acquired-state effect, the C0 clock's cousin). Decision per the GO: the
frozen C1 family is CLOSED. Recorded as evidence that, on this
instruction-level substrate with these operators, the independently
valuable procedure channel (the control gains +25 tasks through it) is
evolutionarily inaccessible. Next: CRIUS-25 / D2, a substrate/operator
campaign, preregistered in its own pass.

1. WHAT WAS FROZEN AND WHAT CHANGED

  Unchanged from C1 (97af44f88): world, generator, sealed namespaces,
  rotating streams, fitness ordering, FAIL/strict-ACT integrity,
  telemetry, mutation and splice operators, controls, procedure
  mechanism, VM, block-id semantics (CRIUS-28 untouched).
  Changed: interactions_by_depth {"1": 2000, "2": 50, "3": 50, "4": 50}.
  Calibration rule (recorded before search, controls only): budget(d) =
  smallest grid b (step 50) with RANDOM_C1 solve-within-b rate < 0.05
  and b >= 2 x P95 of PROCEDURE_REUSE_C1's interactions on solved
  depth-d chains. Streams: gate 301-310 (160 depth-2, 140 depth-3
  tasks); qual 201-210 for depth 4 only (40 tasks; no candidate touches
  them). Results: d2 RANDOM 2.5 pct at 50, P95 18, max 266 (the control's
  own enumeration fallbacks); d3 1.4 pct, P95 21, max 984; d4 5.0 pct
  exactly (2/40) at the grid floor, flagged, not blocking (depth 4 never
  occurs in search streams). Pass 1 (12 depth-4 tasks, one lucky walk =
  8.3 pct) is kept on file. Stated consequence: 50 admits the
  demonstrated route (plan in the head, invoke ~6-20 actions) and
  excludes physical trial of stored procedures on chains (144 pairs x
  ~6 actions). Unsolved work still pays its full budget (witness B).

2. GATE ON c1b (streams 301-303; PASS x8)
  A QUIT 20.5/17.4/20.5 < ENUMERATE 21.5/19.4/22.5 (walkers' upside on
    chains is now 1-2 tasks)     B unsolved 29/31/28, all charged
  C tests                        D TABLE_MEMO replays 0; NOCAL 0 chains
  E PROCEDURE ACC 50/49/50 vs FRESH 21/18/22; reuse_gain C-E 892/744/~800
    of FRESH cost 1466/1477/~1450
  F ART_TRANSPLANT 18/18/18 vs CODE_ONLY 1/1/0 (cost 21/28/~30 vs 48/50/50)
  G ABLATION_ALL == CODE_ONLY     H unchanged blocks; 2/3/3 rich blocks

3. SEALED-STREAM QUALIFICATION (qual 201-203, means; fit = C1_FITNESS)

  player               fitA   fitF  sucA sucF interA  chains  s13 (x3 seeds)
  PROCEDURE_REUSE_C1  46.13  20.74  45.7 20.3   3816   77/90  3 3 3 2 3 2 2 2
  TABLE_MEMO_C1       20.74  20.74  20.3 20.3  10902    3/90  3 0 0 0 0 0 0 0
  ENUMERATE_VM_C1     19.74  19.74  19.3 19.3  11178    4/90  3 0 0 0 0 0 0 0
  QUIT_C1             19.74  19.74  19.3 19.3   9448    0/90  3 0 0 0 0 0 0 0
  RANDOM_C1            7.22   7.22   7.0  7.0  34042    3/90  3 0 0 0 0 0 0 0
  searched, final-population top per run (and best-ever on its stream):
  random   s1/s2/s3   0.16 / 0.16 / 0.16  (0/50; best-evers 0-0.3)
  seeded   s1/s2/s3  20.06 / 20.77 / 16.04  fitA == fitF; blk 0; invk 0
  recomb   s1/s2/s3  21.41 / 19.75 /  6.87  s3: fitA 6.87 < fitF 9.24
  chains solved by searched tops: 3-6 of 90 (luck floor: RANDOM 3/90)
  s13 for every searched candidate (tops, best-evers, ancestors,
  contemporaries; 90 qualified): 3 0 0 0 0 0 0 0, except recomb_s3 top
  0 0 0 0 0 0 0 0 (competence falls under accumulation).
  Comparison set C1 (frozen budgets): seeded/recomb tops 27.6-32.0,
  ENUMERATE 25.3, chains by luck 5-16 per stream.

4. PRINCIPAL READOUT (the GO's three questions)

  Q-a reproducible ACCUMULATED > FRESH in any qualified lineage: NO.
      270 qualified rows (90 searched candidates x 3 sealed streams):
      246 with reuse_gain exactly 0.0 (ACC == FRESH on every task), 17
      negative, 7 positive. All 24 non-zero rows belong to ONE family,
      the recomb_s3 record-id clock (S2 below), whose sign flips with
      the stream: seed 201 -5524 (8 vs 11 solved), seed 202 +139 with
      FEWER tasks solved (12 vs 13), one contemporary +507 on seed 203
      (23 vs 20). Not reproducible across streams; competence not kept.
  Q-b creates / invokes reusable executable blocks: NO. Blocks created
      in 6 of 270 rows, all by two random-arm contemporaries that spam
      32 empty BLK_NEW per lifetime and solve 0/50. Invocations that
      reached a block: 0 in 270 rows (every BLK_INVOKE executed during
      search addressed an empty store: seeded_s1 top runs 50 invokes per
      lifetime on 0 blocks).
  Q-c ancestral gradient toward those behaviours: NO. Along the nine
      final-population lineages (LINEAGE.md per run), first-half ->
      second-half means: blocks created 0.0 -> 0.0 in 9/9; kept bytes
      0-2 -> 0-29 (a WS_WRITE per task in seeded_s1, never read);
      invokes rise in 2 lineages (0 -> 13, 3 -> 446) on empty stores.
      Census: candidates that invoked a block 0-31 per run; of those in
      their iteration's top 8: 0-5, never the top 1. State-keeping
      candidates (kept bytes or invoked) had a HIGHER mean fitness than
      their contemporaries in 41 of 65 sampled iterations with both
      present -- keeping state is not selected against; it is simply
      never load-bearing (Q-a).

5. WHAT REPLACED THE WALKERS (OBSERVATION; lineages preserved)

  S1  CHEAPER COUNTER ENUMERATORS (seeded s1-s2, recomb s1-s2). Example
      seeded_s2 d19ba9831f137eca: a single counter loop (lines 37-45:
      DIV/MOD digit extraction, ACT, ACT num_ops = RESET) covering the
      depth-1..3 order in one pass with a reordered digit schedule; 20.3
      /50 sealed at 7840 interactions vs the seed's 19.3 at 11178. The
      only live gradient under c1b is the 0.5-weight cost term, so
      selection compresses the enumerator. Store ops present (WS_REC_NEW
      50, BLK_APPEND 50 per lifetime) are executed once per task and
      change nothing (ACC == FRESH).
  S2  RECORD-ID CLOCK, NEGATIVE (recomb_s3 05932a87aec14f1b, it 300).
      WS_REC_NEW x3 per task creates EMPTY records (zero bytes: they
      evade the capacity bound; only cost bounds them). Record ids grow
      across the lifetime; ACT R0 on an id > 12 is an invalid action.
      ACCUMULATED: 989-1000 invalid actions per task from task 2 on,
      8/50 solved; FRESH: ids restart, 11/50. reuse_gain -5524. Same
      value channel as the C0 block-id clock (CRIUS-28); preserved, not
      patched: no preregistered integrity condition is violated (ids are
      values, capacity is bytes). Noted for CRIUS-28: empty records are
      free.
  S3  DRIFT BELOW THE SEED (seeded_s3 15.7, recomb_s3 6.7). With one
      rotating stream per iteration and parents re-evaluated on it, a
      stream on which the seed's enumeration order is unlucky lets
      cheaper-but-weaker children replace it, and the loss is not
      recovered (LINEAGE: successes 17.7 -> 16 across the lineage). A
      property of single-stream common-random-number selection, not of
      the substrate; recorded for the D2 design (evaluate on >= 2
      streams per iteration).
  S4  RANDOM ARM: nothing at all (0/50 on sealed streams, 3/9 runs);
      under c1b a random program cannot even collect walk luck.

6. PREDICTIONS (DESIGN_C1 s8 applied to C1b, scored)
  Q2 HELD (random < 20/50).  Q3 HELD in both clauses now (seeded 15.7-
  20.3, no state effect).  Q4 HELD (recombination flat).  Q5 HELD (3-6
  chains per 90 = the luck floor).  The isolation question is answered
  NO: the budgets did not mask a reachable gradient toward acquired
  state.

7. INTERPRETATION

  - D1 is closed as a confound: removing walk luck removed the walkers
    and exposed no reuse gradient beneath them.
  - The reuse route is worth +25.4 tasks (45.7 vs 20.3) to a Player that
    has it, and no lineage moved toward it in 18 runs (C1 + C1b) under
    three operators. The parts (calibrate, record-as-procedure, plan,
    invoke-with-argument) are individually costly and individually
    useless; the store is used only for side effects and free integers.
    Store use is not penalised by selection (41/65 census rows above),
    so the absence is not parsimony pressure: no partial version of the
    route pays.
  - Selection found every cheap gradient that exists: budget management
    (C0), walk luck (C1), enumeration compression and id side effects
    (C1b). This is the pattern the operator's ruling predicted for an
    instruction-level substrate; it is now measured three times.

8. DECISION (per the GO's decision rule)

  Reusable acquired state did NOT appear. The frozen C1 family (c1.json
  32dfb243be9fdec9 and c1b.json bbf684cd638167f2, with world
  7c53db874324b532 and generator 624728b00fdd3f2f) is CLOSED. Evidence
  statement: on the current instruction-level VM with point mutation,
  duplication and segment splice, the independently valuable procedure
  channel of RELAY (gate F/G/H PASS; +25 tasks for the control) is
  evolutionarily inaccessible within 300 x 32 evaluations per run, nine
  runs per budget regime, two budget regimes.
  Next: CRIUS-25 / D2 -- a substrate/operator campaign aimed at
  evolvable compositional structure, preregistered in crius/DESIGN_C2.md
  before code. Constraints carried forward from the GO: no seeding of
  the completed hand-written mechanism into the main population;
  hand-authored PARTS only as explicit diagnostic treatments to measure
  recombinability and missing bridges; CRIUS-28 stays separate.
  D2 design questions I will put in the preregistration (not decided
  here): (i) typed blocks whose input port and invocation are single
  instructions, so "keep and apply with an argument" is a 1-2 edit
  change; (ii) two streams per iteration to remove S3 drift; (iii) a
  PARTS-recombinability treatment arm (calibrator-only, recorder-only,
  invoker-only lineages as separate diagnostic populations, never merged
  into the main arm) to measure which bridge is missing.

9. CONFLICTS OF INTEREST AND PROVENANCE
  - I wrote the calibration rule; pass 1 and pass 2 are both on file
    (only the depth-4 sample and its search-relevance clause changed,
    before search). No search-time change of anything.
  - qualify.py ranks within the final population under rotation (fix
    dated in the C1 packet); the C1 comparison set was re-qualified the
    same way.
  - Grades: MEASURED s1-s6; INFERRED s7-s8.
  - Wall time: searches 111-462 s each (drive log); calibration, gate
    and qualification each under 10 min; M2, 8 workers per run.

10. RECEIPTS
  crius/runs/calibration_c1b/   CALIBRATION.md/json (+ pass1)
  crius/runs/gate_c1b/          GATE.md/json + control batteries
  crius/runs/baselines_c1b/     7 controls x gate streams
  crius/runs/search_c1b_<arm>_s<k>/  RUN_META, candidates.jsonl.gz,
      iterations.jsonl, best.json, qualify_qual/ (gz), REPORT.md,
      LINEAGE.md
  crius/runs/search_c1_*/LINEAGE.md   comparison set readouts
  crius/runs/CAMPAIGN_SUMMARY.md
================================================================================
