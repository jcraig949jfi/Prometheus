# CRIUS C2 TERMINAL PREREGISTRATION -- resolution round for the Accessibility Frontier

Currency: 2026-09-23, instance m2-8d43bbf9, written BEFORE the instrument
repair is run and BEFORE any rung-C gate or C/D search of this round.
Operator directive: this round ends in exactly one disposition, UNPARK ->
CONTINUE or CLOSED -- ACCESSIBILITY FRONTIER MAPPED; PARKED only for an
external infrastructure failure that makes the experiment uninterpretable.
Park receipt f2238721b; resumed at a39bc1647 (origin/main merged).

## I. The claim, reconstructed from the committed record

### What the rungs were meant to change (DESIGN_C2 s4; links L1-L6)
L1 acquisition (action id -> primitive), L2 representation (a procedure
relative to an argument), L3 retention, L4 addressing (which procedure and
argument), L5 invocation with an argument, L6 composition (chains: planning
in the head).
  C2-A  C1b substrate; no link is a single instruction. (Run: 9 searches.)
  C2-B  L1+L2+L3+L5 single instructions: typed PROCEDURE objects
        (PREC_BEGIN / PREC_END record the revealed primitives of the
        actions between them relative to the first step's position;
        PINVOKE h, a executes with an absolute argument through a
        substrate-maintained calibration artifact that is itself a block,
        so FRESH/RESET/SCRAMBLE/ABLATION/TRANSPLANT act on it). L4 and L6
        stay the program's job. (Run: 9 searches.)
  C2-C  C2-B + L6 local: PSIM r, h, a (mental application) and PMATCH.
        (Gate FAILED 2026-09-19; not searched.)
  C2-D  C2-C substrate + recombination donors = population + frozen PARTS
        (P_REC, P_INV, P_PLAN); PARTS never enter the population. (Not run.)

### Gates A-H, exact frozen definitions (DESIGN_C1 s7, carried by DESIGN_C2 s7; code crius/gate_c1.py)
  A  C1_FITNESS(QUIT_C1) < C1_FITNESS(ENUMERATE_C1) on every gate stream.
  B  every unsolved ENUMERATE_C1 task is charged its full interaction budget.
  C  integrity fixtures: store failures never act; out-of-range values are
     invalid actions; the C0 clock fossil keeps its signature.
  D  TABLE_MEMO_C1 replays 0 chain tasks (explicit counter, cell 255) and
     PROCEDURE_NOCAL_C1 solves inside invoked blocks <= 10 percent of what
     the calibrated control does (success_in_block).
  E  positive control: ACCUMULATED solves >= FRESH AND reuse_gain over
     stages C-E > 20 percent of FRESH charged cost, on 3/3 gate streams.
  F  ARTIFACT_TRANSPLANT remainder (from the stage-D snapshot) solves MORE
     tasks than CODE_ONLY AND at mean charged cost < 0.95 x CODE_ONLY,
     3/3 streams, code identical.
  G  ARTIFACT_ABLATION_ALL remainder mean cost within 5 percent of
     CODE_ONLY and solves <= CODE_ONLY, 3/3 streams.
  H  transplanted blocks unchanged (instruction hashes) AND >= 2 template
     blocks AND >= 2 of them invoked with >= 3 distinct arguments producing
     >= 3 distinct action sequences on the remainder AND TABLE_MEMO_C1's
     FULL transplant solves <= its CODE_ONLY.
  Rule (DESIGN_C2 s7): a rung whose gate fails is not searched.

### Predictions R1-R6, verbatim from DESIGN_C2 s9 (frozen; not restated in other words)
  R1 Rung A under paired streams + takeover: no gradient (replicates C1b);
     <= 1 of 9 runs ends below the seed on sealed streams.
  R2 PARTS at rung B: P-REC has negative selective value (re-execution
     cost, no benefit); P-INV from scratch ~ 0, positive with transplant
     on single tasks only; P-REC-INV positive on single tasks only (delta
     solved 0, delta fitness between +0.05 and +0.3), sign reproducible on
     >= 8/10 streams.
  R3 Rung B search: persistent-state creation frequency rises (PREC is one
     edit) to > 20 percent of candidates; useful invocations appear (> 0
     in > 5 percent of candidates); still no reproducible ACCUMULATED >
     FRESH with competence kept, because L4 (addressing) and physical
     trial cannot solve chains within 50.
  R4 Rung C: P-PLAN with transplant and P-REC-INV-PLAN have large positive
     value (+20 tasks); seeded and recombination searches do NOT assemble
     PSIM planning within 300 iterations in 3/3 seeds each (the pair loop
     is ~10 coordinated edits with no reward until complete).
  R5 Rung D: splice from PARTS donors produces at least one lineage with
     reproducible ACCUMULATED > FRESH and competence kept in >= 1 of 3
     seeds. This is the frontier prediction: the boundary lies between
     "each link is one instruction" (C) and "parts exist as donors" (D).
     Losing R5 means even donor-level parts do not compose under splice
     -- a linkage result, and the most informative failure available.
  R6 Structural distance from the seed to P-REC-INV falls from >= 40 edits
     (rung A) to <= 12 (rung B) and to P-REC-INV-PLAN <= 25 (rung C).
  Already scored (packet C2): R1 held@A, lost@B (2/9); R2 held in
  structure, lost in magnitude; R3 half; R6 lost; R4/R5 untested.

### Meanings
  FRESH: a new empty workspace and empty block store for EVERY task.
  ACCUMULATED: one workspace and block store persist over the lifetime.
  PARTS: frozen hand-written partial mechanisms (P_BASE the compact
    enumerator; P_CAL; P_REC recorder-only; P_INV invoker-only; P_REC_INV;
    P_PLAN planner-only; P_REC_INV_PLAN the complete rung-C mechanism);
    controls and (at D) splice donors, never population members.
  typed artifact / argument: a procedure object = PSTEP (kind, offset)
    steps; its argument is the ABSOLUTE position of its first step;
    PINVOKE h, a emits, for each step, the action id that performs
    primitive (kind, (a + offset) mod 4) via the calibration object.
  recorder / invoker: PREC_BEGIN/END create the object; PINVOKE uses it.
  The two controls of CRIUS-33: PROCEDURE_REUSE_C1 (Python, "block
    control": artifacts are ExecutableBlocks of ACTI instructions built and
    planned over in Python with depth-3 planning, witness-validated
    templates, argument passed in R0) and P_REC_INV_PLAN (bytecode, "typed
    control": 64 instructions, typed procedures, depth-2 planning over the
    first 8 store objects, argument passed through parg).
  Causal claim protected by F/G: an ARTIFACT-ONLY transplant into a fresh
    copy of the SAME code confers competence/cost advantage over the code
    alone, and removing the artifacts removes it -- the advantage is in
    the artifacts, not in code, ids, compute or storage.
  Accessibility/economic claim measured by E/H: on this world a positive
    control that ACCUMULATES gains substantially (E: > 20 percent of FRESH
    cost, with competence kept) and the object it carries is PROCEDURAL
    (H: the same unchanged object, applied to >= 3 distinct arguments,
    yields >= 3 distinct behaviours; a table gains nothing).

### The rung-C failure, verbatim (crius/runs/gate_c2c/GATE.md, 2026-09-19)
  E FAIL: 1/3 streams below the floor (302: reuse_gain C-E 708.8 = 12
    percent of FRESH cost 5748.6 vs the frozen 20 percent; 301: 45
    percent; 303: 43 percent). H FAIL: 1/0/1 blocks with >= 3 distinct
    args vs floor 2. F PASS (ART 6/6/6 vs CODE 1/1/0; cost 147-154 vs
    191-193). G PASS. A-D PASS. Window-10 retry: same (gate_c2c_window10).
  C/D were not searched after that failure. Rung-C search receipts that
  had run under the failed gate were deleted and are not evidence.

### Prior frontier evidence, preserved
  C1/RELAY: useful procedural reuse exists independently (gate F/G/H PASS,
  +25 tasks for the control). C1/C1b: no evolutionary gradient assembled
  the chain (18 runs, two budget regimes). C2 A/B: no gradient (18 runs
  under paired streams + takeover). PARTS: one-link valley at B (recorder
  -0.001, invoker -0.002, pair +1.138 at 26 edits) and a cliff at C
  (planner-only -0.057; +16.74 with procedures; complete +15.97, 10/10).

## II. CRIUS-33 resolved by a declared control separation (gate version 2)

Adopted (operator directive), unless inspection finds a concrete
implementation error that invalidates it:
  ACCESSIBILITY control for E and H: PROCEDURE_REUSE_C1 (the block control).
  CAUSAL control for F and G: P_REC_INV_PLAN (the typed control).
  A-D unchanged (QUIT/ENUMERATE, integrity fixtures, TABLE_MEMO/NOCAL).
Mechanistic justification: E and H are statements about the WORLD under
the rung's substrate -- that an accumulating positive control with a
procedural object exists and benefits. The block channel is a subset of
rung C's substrate (nothing about blocks changed at B or C), so the block
control's E/H numbers are the same facts they were at A and B, measured
again on rung C's exact config hash. F and G are statements about the
NEW channel -- that typed procedures carry advantage causally -- and
must be measured with the typed control. The previous single-control
gate conflated "the typed control is strong" with "the typed channel is
causal"; the typed control's E/H failure was a fact about a 64-
instruction depth-2 planner (27/50 on one stream), not about the channel.
This is a correction of the instrument's estimand, versioned as
GATE_VERSION 2 in crius/gate_c1.py; the receipt records both control
names, the gate version and the code commit. The E/H floors (20 percent;
>= 2 blocks with >= 3 arguments) and F/G definitions are unchanged.
Reported alongside, non-gating: the typed control's own E and H under the
repaired instrument (section III), so nothing is hidden.
Validity condition (checked by fixtures before the gate): E/H must FAIL
for a table/scalar control (TABLE_MEMO_C1) and F must FAIL for a control
whose artifacts are decorative (P_REC: records, never invokes) -- i.e.
each control tests its intended contrast on rung C's substrate. If either
fixture cannot be made to hold, the separation is invalid and the
stronger typed control is built instead.

## III. Instrument audit (before any search); repairs are the one allowed repair

Found on inspection (2026-09-23): the invocation log records entry
registers R0..R3 as the "argument". Correct for the block control (it
passes the argument in R0); WRONG for typed PINVOKE, whose argument is
the VM slot parg. The 2026-09-19 H count for the typed control (1/0/1
blocks with >= 3 distinct arguments) was therefore computed on a loop
register, not on the argument: an instrumentation defect. Repair: the
log records the effective argument ("arg": parg for PINVOKE/PSTEP
blocks, R0 otherwise); H reads it. Regression test added.
The grounding suite (crius/tests, extended this round) must show:
candidate/artifact accounting; mutation/duplication/splice validity;
typed argument flow (parg) and its logging; artifact identity and non-
aliasing (ids vs handles vs procedures); persistence/reset semantics;
invocation accounting (success_in_block, counts); recorder/invoker PARTS
accounting; full-budget failure charging (B); held-out procedural tests
(sealed namespaces); transplant/ablation behaviour; the accumulated
positive control; deterministic replay from a receipt on the typed
substrate; paired-stream seed alignment (every candidate of an iteration
carries the same stream seeds); no reward for merely allocating or
storing (allocation lowers fitness, all else equal); no scalar/table
shortcut satisfies H (TABLE_MEMO fails H) and a count-only store does not
count as content-bearing (synthetic-count probe).
Could the previous E/H failure have been instrumentation? H: yes, partly
(the argument defect). E: no evidence of instrumentation -- E's 12
percent on stream 302 comes from the typed control solving 27/50 there
(its recorded procedures on a swap-heavy library are start-specific;
the block control's witness rule avoids this). No world or pressure is
tuned.

## IV. Rung-C gate, clean re-run
Config crius/configs/c2c.json, hash 416bbe8b9be34706 (unchanged). Gate
version 2, output crius/runs/gate_c2c_v2/. Every witness A-H reported
separately. Outcomes: C-GATE TRUE -> run C and D; C-GATE FALSE -> no
threshold tuning, no D, diagnostics then CLOSE; INSTRUMENT INVALID ->
repair, regression test, rerun (a scientifically unfavourable result is
not an instrument failure).

## V. If admitted: the decisive C/D campaign (frozen)
Configs c2c.json / c2d.json as committed (hashes in RUN_META); 3 arms x
3 seeds x 300 iterations, mu 8 lambda 24, paired streams + takeover
check, sealed qualification (201-203), full battery A-J, lineage
readouts, exploit probes on every candidate flagged reproducible.
Additional readouts (declared now): time-to-first complete mechanism
(first candidate per run with PREC_END + PINVOKE-into-own-object +
success_in_block on a chain task); survival of partial structures
(iterations a lineage carrying >= 1 typed op stays in the elite);
recombination events producing functional descendants (splices whose
child's fitness exceeds both parents'); intermediate PARTS frequencies
(candidates executing PREC_END, PINVOKE, PSIM). Content-bearing test:
any candidate satisfying "reproducible ACCUMULATED > FRESH with
competence kept on 3/3 streams" is probed; it counts for R5 only if the
synthetic-count arms (empty blocks; empty records) do NOT reproduce the
transplant and ARTIFACT_only does. This is stricter than R5's text and
is declared here before the runs.

## VI. Disposition rule (operator's, restated in checkable form)
UNPARK -> CONTINUE requires ALL of: gate C v2 TRUE; R4 and R5 survive
their frozen tests; partial recorder/invoker components show selectable
value BEFORE complete reuse in the lineages (a positive fitness step
attributable to a partial, by ancestry, in >= 2 of 3 seeds of the
winning arm); the effect on paired sealed streams, not one lineage;
ablation removes it; ARTIFACT transplant beats code-only; held-out
procedural tests (sealed streams) hold; lineage shows incremental
acquisition (no single edit of > 8 instructions accounts for the
mechanism). Anything less -> CLOSED -- ACCESSIBILITY FRONTIER MAPPED,
with the measured frontier preserved and no resume pointer.

## VII. What is forbidden this round
No lowering of E/H floors; no E2/H2; no budget increases; no seeding of
parts into the population (donors at D only, as preregistered); no
task-specific primitives; no redefinition of procedure; no change of
selection pressure; no C3.
