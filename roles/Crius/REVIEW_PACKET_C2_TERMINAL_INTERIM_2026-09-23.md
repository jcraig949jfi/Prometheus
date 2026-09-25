CRIUS -- C2 TERMINAL ROUND, INTERIM REVIEW PACKET (rung C admitted; C/D running)
2026-09-23T08:37Z  instance m2-8d43bbf9  HEAD f16d49322 (branch
crius/base-role-adopt-2026-09-18, base a39bc1647 = origin/main at boot)
Prereg for this round: crius/CRIUS_C2_TERMINAL_PREREG.md (cbf30a726,
written and committed before the repair ran). Operator directive: one
disposition at the end of the round, UNPARK -> CONTINUE or CLOSED --
ACCESSIBILITY FRONTIER MAPPED; PARKED only for infrastructure failure.
================================================================================

0. WHERE THINGS STAND (one paragraph)

The claim was reconstructed verbatim from the committed record; CRIUS-33
was resolved by a declared two-control gate written before any run; the
instrument audit found one concrete defect (the invocation log recorded
register R0 as the "argument", which is right for the Python block control
and wrong for typed PINVOKE, whose argument travels in the VM slot parg --
so the 2026-09-19 rung-C H count was computed on a loop register);
the repair plus nine contrast fixtures are committed and green (39 tests);
the clean rung-C gate v2 PASSES every witness A-H separately; the
decisive C/D searches are running from a clean state (rung C random arm
done, seeded arm at iterations 39-64 of 300; rung D queued behind its own
gate v2). No world, budget, pressure or floor was changed. The
disposition is not yet made; sections 6-7 state exactly what decides it.

1. THE CLAIM, RECONSTRUCTED (CRIUS_C2_TERMINAL_PREREG.md s I)

  Chain links: L1 acquisition (id -> primitive), L2 representation
  (procedure relative to an argument), L3 retention, L4 addressing, L5
  invocation with an argument, L6 composition (planning in the head).
  C2-A  C1b substrate, no link local.                  (9 runs, done)
  C2-B  L1+L2+L3+L5 single instructions: PREC_BEGIN/END, PINVOKE h,a,
        substrate-maintained calibration artifact.       (9 runs, done)
  C2-C  + L6 local: PSIM (mental application), PMATCH. (gate v2 PASS;
        9 runs in progress)
  C2-D  C2-C + recombination donors = population + frozen PARTS
        (P_REC, P_INV, P_PLAN); PARTS never enter the population.
                                                         (queued)
  Gates A-H (frozen, DESIGN_C1 s7 / DESIGN_C2 s7; code gate_c1.py):
   A QUIT < ENUMERATE fitness on every gate stream
   B every unsolved task charged its full budget
   C integrity fixtures (failures never act; out-of-range invalid; clock)
   D TABLE_MEMO replays 0 chains; NOCAL solves <= 10 pct of control's
     chains inside invoked blocks
   E positive control: ACC solved >= FRESH AND reuse_gain(C-E) > 20 pct
     of FRESH charged cost, 3/3 streams
   F ARTIFACT_TRANSPLANT remainder solves MORE than CODE_ONLY AND mean
     cost < 0.95 x CODE_ONLY, 3/3, code identical
   G ABLATION_ALL within 5 pct of CODE_ONLY and solves <= CODE_ONLY, 3/3
   H blocks unchanged; >= 2 template blocks; >= 2 with >= 3 distinct
     arguments giving >= 3 distinct sequences; TABLE_MEMO FULL <= CODE
  Predictions R1-R6 are quoted verbatim in the prereg; the two that decide
  this round:
   R4 Rung C: P-PLAN with transplant and P-REC-INV-PLAN have large
      positive value (+20 tasks); seeded and recombination searches do
      NOT assemble PSIM planning within 300 iterations in 3/3 seeds each.
   R5 Rung D: splice from PARTS donors produces at least one lineage with
      reproducible ACCUMULATED > FRESH and competence kept in >= 1 of 3
      seeds. Losing R5 means even donor-level parts do not compose under
      splice -- a linkage result.
  Rung-C failure of 2026-09-19, verbatim: E FAIL 1/3 (302: 708.8 = 12 pct
  of 5748.6 vs 20 pct); H FAIL (1/0/1 blocks with >= 3 args vs 2); F/G
  PASS; A-D PASS; C/D not searched; rung-C receipts under that gate were
  deleted and are not evidence.
  Prior frontier evidence preserved: reuse exists (C1 F/G/H; +25 tasks
  for the control); no gradient assembled it in C1/C1b (18 runs) or C2
  A/B (18 runs); PARTS: one-link valley at B (recorder -0.001, invoker
  -0.002, pair +1.138 at 26 edits, 7/10) and a cliff at C (planner-only
  -0.057; +16.74 with procedures; complete +15.97, 10/10, at 47 edits).

2. CRIUS-33 RESOLVED: THE DECLARED TWO-CONTROL GATE (gate version 2)

  ACCESSIBILITY control for E and H: PROCEDURE_REUSE_C1 (Python block
  control: block artifacts of ACTI instructions, depth-3 planning,
  witness-validated templates, argument in R0).
  CAUSAL control for F and G: P_REC_INV_PLAN (64-instruction bytecode:
  typed procedures, depth-2 planning over 8 store objects, argument via
  parg).
  Why this is a correction of the estimand and not a relaxation: E and H
  state facts about the WORLD under the rung's substrate (an accumulating
  positive control with a procedural object exists and benefits); the
  block channel is a strict subset of rung C's substrate, so those facts
  are re-measured, on rung C's exact config hash, with the control that
  demonstrates them. F and G state facts about the NEW channel (typed
  procedures carry advantage causally) and are measured with the typed
  control. The single-control gate had conflated "the typed control is
  strong" with "the typed channel is causal". No floor changed. The
  typed control's own E/H are reported as non-gating diagnostics so
  nothing is hidden. Versioned GATE_VERSION 2; both control names, the
  version and the code commit are in the receipt.
  Validity fixtures (crius/tests/test_c2_terminal.py, all green):
   - E PASSES for the block control and FAILS for TABLE_MEMO_C1 (a table)
   - F PASSES for the typed control and FAILS for P_REC (records, never
     invokes: decorative artifacts)
   - H counts the effective argument: PINVOKE with args 0..3 while R0 is
     held at 9 logs [0,1,2,3]; the block control's argument (R0) still
     counts and yields >= 2 rich blocks
   - allocation is not rewarded (WS_REC_NEW + BLK_NEW per task lowers
     fitness, same solved count)
   - TABLE_MEMO fails H's transplant clause (FULL <= CODE_ONLY)
   - paired streams: every candidate of an iteration carries the same two
     stream seeds; takeovers.jsonl written
   - a typed-substrate receipt replays to its replay_hash
   - PARTS accounting: P_REC creates >= 3 procedures and invokes 0;
     P_INV creates only the calibration object

3. INSTRUMENT AUDIT (prereg s III) -- result

  Defect found: invocation-log "argument" = R0 for every block. For typed
  procedures the argument is parg. Repair: the log records the effective
  argument (parg when the invoked block is a procedure, R0 otherwise);
  H reads it. Regression test added. Consequence, measured: on stream
  302 the typed control now shows 2 rich blocks where the defective count
  showed 0 (its H "would pass" there); 301/303 still 1.
  Could the 2026-09-19 E/H failure have been instrumentation? H: partly,
  yes (above). E: no -- the typed control genuinely solves 27/50 on
  stream 302 (swap-heavy library; its recorded procedures are start-
  specific, and it has no witness rule), so its reuse_gain there is 12
  pct. That is a property of a 64-instruction control, not of the world.
  Also verified in the suite: candidate/artifact accounting; mutation/
  duplication/splice validity; typed argument flow; artifact identity
  (ids vs handles vs procedures; the calibration object survives
  tampering); persistence/reset semantics; invocation accounting
  (success_in_block); full-budget charging (B); sealed procedural
  streams (search/qual/gate namespaces disjoint); transplant/ablation
  behaviour; the accumulated positive control; deterministic replay;
  paired-stream alignment; no reward for allocation; no table shortcut
  through H. Nothing about the world, budgets or selection was touched.

4. RUNG-C GATE v2, CLEAN RE-RUN (crius/runs/gate_c2c_v2/GATE.md, 7661050d9)

  config 416bbe8b9be34706, world 7c53db874324b532, generator
  624728b00fdd3f2f, code a3f6a4be0, gate streams 301/302/303
  A PASS  QUIT 20.47/17.41/20.48 < ENUMERATE 21.47/19.41/22.48
  B PASS  unsolved 29/31/28, every one charged its budget
  C PASS  integrity fixtures (tests)
  D PASS  TABLE_MEMO replays 0/0/0; control 29/29/29 chains in blocks;
          NOCAL 0/0/0
  E PASS  (block control) ACC 50/49/50 vs FRESH 21/18/22; reuse_gain C-E
          891.7 / 744.0 / 897.4 of FRESH cost 1466.2 / 1477.3 / 1427.9
          = 61 / 50 / 63 pct (floor 20)
  F PASS  (typed control) ARTIFACT_TRANSPLANT 6/6/6 solved vs CODE_ONLY
          1/1/0; mean cost 147.5 / 153.7 / 152.3 vs 190.5 / 191.6 / 193.0
  G PASS  (typed control) ABLATION_ALL == CODE_ONLY: 190.5 / 191.6 / 193.0
  H PASS  (block control) blocks unchanged; template blocks 3/5/4; rich
          (>= 3 args and >= 3 sequences) 2/3/3 (floor 2); TABLE_MEMO
          FULL 1/1/? <= CODE 1/1/?
  Diagnostics, non-gating, typed control's own E/H after the repair:
   301 E would pass (38 vs 21; 2589 of 5742) | H would NOT (3 blocks, 1 rich)
   302 E would NOT (27 vs 22; 709 of 5749)   | H would pass (4 blocks, 2 rich)
   303 E would pass (38 vs 22; 2466 of 5725) | H would NOT (3 blocks, 1 rich)
  C-GATE TRUE. Rung C is admissible. C and D searches launched from a
  clean state (the driver now keys on the receipt's verdict, not on the
  receipt's existence -- the 09-19 process error).

5. WHAT IS RUNNING AND WHAT EXISTS ALREADY

  Running (drive_c2cd.py): rung C, arms random/seeded/recombination x
  seeds 1-3, 300 iterations, mu 8 lambda 24, paired streams + takeover
  check, then qualification on sealed streams 201-203 with the full A-J
  battery, REPORT.md, LINEAGE.md; then rung D after its own gate v2 and
  PARTS diagnostic. At 08:37Z: rung C random s1/s2 done (best on their
  streams 0.16/0.16 -- nothing), s3 at 233; seeded s1/s2 at 64/39
  (bests 23.5/22.9 on their streams; the seed is ~21.5).
  Path-evidence readout (crius/c2_path.py, new): per 50-iteration window,
  candidates executing PREC_END / PINVOKE / PSIM and the conjunctions;
  survival of each typed op in the elite (iterations present, longest
  consecutive run); child-minus-parent fitness for children newly
  carrying each op vs other edits; first candidate with recorder +
  invoker + own invocation + solved > 22 (proxy for a complete
  mechanism; the strict test reads success_in_block on chains from the
  qualification receipts); splice children exceeding both parent and
  donor. Baseline on rung B (9 runs, committed as PATH.md): first
  complete-mechanism proxy = None in 9/9; recorder in the elite for up to
  103 consecutive iterations as a neutral hitchhiker; invoker never more
  than 2; children newly carrying a recorder improved on their parent
  4.8 pct of the time vs 26 pct for other edits (invoker 10.2 pct) --
  carrying a part is, if anything, deleterious at B.

6. WHAT DECIDES THE DISPOSITION (prereg s V-VI, checkable)

  UNPARK -> CONTINUE requires ALL of:
   a. gate C v2 TRUE                                          (met)
   b. R4 and R5 survive their frozen tests
   c. partial recorder/invoker components show selectable value BEFORE
      complete reuse: a positive fitness step attributable to a partial,
      by ancestry, in >= 2 of 3 seeds of the winning arm
   d. the effect on paired sealed streams (201-203), not one lineage
   e. ablation removes it; ARTIFACT transplant beats code-only
   f. sealed procedural streams hold (no table/scalar memorisation) and
      the content test holds: synthetic-count stores (empty blocks;
      empty records) do NOT reproduce the transplant, ARTIFACT_only does
   g. lineage shows incremental acquisition: no single edit of > 8
      instructions accounts for the mechanism
  Anything less -> CLOSED -- ACCESSIBILITY FRONTIER MAPPED, with the
  measured frontier preserved and NO resume pointer.
  Explicitly insufficient (operator s VI): a hand-written or seeded
  control working; a complete mechanism appearing without selectable
  precursors; a rare multi-edit jump; accumulated > fresh from unrelated
  retained state (the E1/E4 counters); invocation useful only after the
  representation is supplied by hand.

7. HOW R4 AND R5 WILL BE SCORED (frozen text, operational reading)

  R4 "seeded and recombination searches do NOT assemble PSIM planning
     within 300 iterations in 3/3 seeds each": SURVIVES if no qualified
     candidate of rung C's seeded or recombination arm solves chain tasks
     inside invoked blocks (success_in_block on depth >= 2) with a
     reproducible content-bearing ACC > FRESH; LOST if one does. Note
     the asymmetry: R4 surviving is the null; only R5 can earn CONTINUE.
  R5 "splice from PARTS donors produces at least one lineage with
     reproducible ACCUMULATED > FRESH and competence kept in >= 1 of 3
     seeds": SURVIVES only if such a lineage exists in rung D's
     recombination arm AND passes the content test (f) -- an E4-type
     counter does not count, declared before the runs.

8. WHAT WOULD HAVE TO BE TRUE FOR EACH DISPOSITION

  CONTINUE: in rung D, at least one lineage in >= 1 seed (and the
  foothold in >= 2 seeds) whose ancestry shows a splice bringing a PART
  (or an equivalent evolved fragment) that raised fitness BEFORE the
  full mechanism existed, whose transplant carries the advantage through
  artifacts alone, whose ablation removes it, and whose sealed-stream
  competence is kept.
  CLOSED: rung C searches assemble nothing (R4 survives) and rung D's
  donor splices either never produce a functional descendant, or produce
  complete mechanisms only by single large jumps with neutral/deleterious
  precursors, or produce counters (E1/E4 shapes) that the content test
  rejects.

9. PROVENANCE
  MEASURED: sections 2-5 (receipts: crius/runs/gate_c2c_v2/, crius/tests/
  test_c2_terminal.py, crius/runs/search_c2[ab]_*/PATH.md). Commits this
  round: cbf30a726 prereg; a3f6a4be0 repair + fixtures; 7661050d9 gate v2
  receipt; f16d49322 path tool + baselines. Conflicts: I wrote the world,
  controls, gate and tools; the control separation was directed by the
  operator and validated by fixtures written before the gate ran.
  Nothing in this packet depends on the C/D runs; the terminal review
  will supersede it and carry the disposition line.
================================================================================
