CRIUS DISPOSITION: CLOSED -- ACCESSIBILITY FRONTIER MAPPED

CRIUS -- CAMPAIGN 2 TERMINAL PACKET  2026-09-23T10:23:47Z  instance m2-8d43bbf9
Prereg crius/CRIUS_C2_TERMINAL_PREREG.md (cbf30a726, sha 9c8e0855c8d6a719),
written before any run. Review crius/CRIUS_C2_TERMINAL_REVIEW.md. Receipt
crius/runs/C2_TERMINAL_DISPOSITION_RECEIPT.json (every input fingerprinted;
scorer crius/c2_terminal.py reproduces the verdict from the run receipts).
Every number below was printed by a script from a receipt.
================================================================================

1. WHAT "UNPARKED" MEANS HERE -- what changed since the park, and what did not

  Changed: (a) the estimand of gate witnesses E/H vs F/G was separated by
  declaration (gate v2): E/H = facts about the world, witnessed by the
  block control PROCEDURE_REUSE_C1; F/G = facts about the typed channel,
  witnessed by the 64-instruction bytecode control P_REC_INV_PLAN; nine
  fixtures show each control tests its contrast (TABLE_MEMO fails E and
  H's transplant clause; decorative P_REC fails F). (b) One instrument
  defect repaired: the invocation log recorded R0 as the argument for
  every block; typed PINVOKE carries its argument in parg, so the 09-19 H
  count for the typed control was on a loop register (regression test:
  args 0..3 logged while R0 = 9). (c) The rung-C gate re-ran clean from
  c2c.json 416bbe8b9be34706: A-H PASS separately (E 61/50/63 pct of FRESH
  cost, floor 20; F 6/6/6 vs 1/1/0 solved at 147-154 vs 190-193 cost; G
  ablation == code-only; H rich blocks 2/3/4, floor 2). C-GATE TRUE.
  Not changed: the world, budgets, fitness, selection, iteration count,
  E/H floors, the PARTS, the forbidden-move list. The 09-19 E failure on
  stream 302 was NOT instrumentation: the typed control genuinely solves
  27/50 there (start-specific procedures, no witness rule).

2. ACCESSIBLE vs EXECUTABLE

  EXECUTABLE, at three levels of construction, on the rung's own opset
  and sealed streams: block control 46.1 vs 20.7 fitness (45.7 vs 20.3
  solved, 74.7 invocations, reuse_gain 7315); typed control transplant
  6/6/6 vs code-only 1/1/0; PARTS: planner from scratch -0.057 (0/10
  streams), with procedures pre-loaded +16.741; the complete part +15.974
  (10/10) at 47 edits from the base.
  NOT ACCESSIBLE to (8+24) mutation-and-selection with segment splice,
  300 iterations, paired streams + takeover check, from ENUMERATE_VM or
  random init, at any rung A-D: 36 runs (18 at A/B on 09-19, 18 at C/D
  today; 129,744 candidates today), 0 candidates with reproducible
  ACC > FRESH on the sealed streams (> 5 pct of FRESH cost, competence
  kept, 3/3), 0 complete mechanisms (18/18 "first complete mechanism:
  None"), 0 selectable partials above the neutral-edit null.

3. WAS PARTIAL MACHINERY SELECTABLE BEFORE COMPLETION?  No.

  Every recorder/invoker step in the ancestry of every qualified top was
  re-evaluated PAIRED, parent vs child, on sealed streams 201-203 (the
  search's own fitness is not paired across iterations; takeover ties
  count as takeover). 19 steps; 9 "selectable" by the literal rule, all at
  +0.0004..+0.0011 fitness with 0 solved on every stream. The same rule
  applied to 8 neutral edits per top1 ancestry also marks 0-3 of 8 as
  "selectable" (|delta| median <= 0.0007): the typed-op steps sit inside
  the neutral-edit distribution. Elite survival: typed ops persist as
  hitchhikers (planner 146 iterations, recorder 84, invoker 46 at most)
  with no fitness consequence. Foothold: children newly carrying a
  recorder improve on their parent LESS often than other edits in 12/12
  distinct runs; invoker in 10/12. Two qualified tops fill the block store
  (32 blocks) and invoke it 43/49 times per lifetime with fitness
  identical under ACCUMULATED/FRESH/RESET/SCRAMBLED: invocation without
  content.

4. DID R4 AND R5 SURVIVE?

  R4 ("seeded and recombination searches do NOT assemble PSIM planning
  within 300 iterations in 3/3 seeds"): SURVIVES -- 0 qualified rung-C
  candidates solve chains inside invoked blocks with content-bearing
  ACC > FRESH. R4 surviving is the null.
  R5 ("splice from PARTS donors produces >= 1 lineage with reproducible
  ACCUMULATED > FRESH and competence kept in >= 1 of 3 seeds"): LOST --
  rung D recombination s1/s2/s3: 1,771 children carry a PART fragment,
  63 won the takeover check, 5 fragments reached a final top's ancestry.
  Re-evaluated paired: P_INV[22:26] (4 instr, no typed op) +0.0005 /
  0 solved; P_INV[7:8] = CONST R6,4 (1 instr) +1.0/+1.0/+0.0008 fitness,
  +1/+1/0 solved; P_PLAN[42:47] = MUL,MUL,LT,BRZ,ACT (child executes
  PINVOKE) exactly 0; P_REC[9:16] = MOD,ACT,DIV.. digit loop (7 instr)
  -0.0026/+0.0008/+0.0001, 0 solved; P_PLAN[42:45] (3 instr)
  +2.03/-3.08/-0.99, net negative. Selection kept the parts' constants
  and digit loops and dropped or neutralised their typed links. Rung D's
  random/seeded arms byte-replicate rung C (same best ids per seed;
  configs differ only in parts_donors) -- the determinism check.

5. CAUSAL INTERVENTIONS

  On the controls: transplant of artifacts alone carries the advantage
  (F), ablation removes it (G), TABLE_MEMO gains nothing from a full
  transplant, NOCAL solves 0 chains in blocks (D). On the searched
  candidates: nothing reached the causal clause; the one row not exactly
  A = F (rung D rec s2 top2: fitA 22.116, fitF 22.115, fitR 21.782,
  reuse_gain 86.8, under the floor) was probed: TRANSPLANT = ARTIFACT_only
  = CODE_ONLY = ID_ONLY = RECORD_IDS_ONLY at 10/12/13 solved. It carries
  nothing; the reset itself costs it.

6. WHERE THE FRONTIER IS

  Value landscape by construction (PARTS, identical at C and D): recorder
  alone -0.001 (0/10), invoker alone -0.002 (0/10), recorder+invoker
  +1.138 (7/10, +1.1 tasks) at 26 edits, planner alone -0.057 (0/10) at
  41, everything +15.974 (10/10) at 47. A one-link valley at B, a cliff
  at C. What selection does with the links: recorder = neutral hitchhiker,
  invoker = deleterious on arrival, planner = neutral. What it does with
  donated parts: keeps scaffolding (a CONST paid +1 task), drops links.
  What it finds instead: compressed enumerators (A-D), record-id clocks
  and counters (E1-E4 at A/B; none at C/D), invocation without content
  (C/D). The world's reward for reuse is intact and re-verified (gate v2
  at C and D, all witnesses).

7. WHY CLOSURE, NOT CONTINUATION

  The rule written before the runs required (a) gate TRUE [met], (b) R4
  and R5 survive [R5 lost], (c) a selectable partial in >= 2 of 3 seeds
  of the winning arm [0 above the null; 1 seed per arm by the literal
  count], (d) reproducible ACC > FRESH on sealed streams [0 candidates],
  (e) transplant/ablation causal [not reached], (f) content test [not
  reached], (g) no > 8-instruction edit [moot]. Only the forbidden moves
  (lower E/H, E2/H2, more budget, parts INTO the population, C3) could
  move these, and the shape is identical at every rung and arm: partials
  neutral-to-deleterious, whole-mechanism value only at ~47 edits,
  scaffolding kept and links dropped. More search here would measure
  budget, not accessibility. The lane closes with the map, no resume
  pointer, STATUS.md = CLOSED.

8. WHAT THE OPPOSITE DISPOSITION WOULD HAVE REQUIRED

  In rung D's recombination arm: >= 1 lineage in >= 1 seed with
  ACC > FRESH on 201/202/203 by > 5 pct of FRESH cost and competence
  kept (observed 0; best under-floor row 86.8, carrying nothing);
  ARTIFACT transplant < 0.95 x CODE_ONLY and ablation removing it (never
  reached); synthetic-count stores NOT reproducing the transplant (never
  reached); a recorder/invoker step beating its parent on the sealed
  streams by more than neutral edits do, in >= 2 of 3 seeds (observed 9
  steps of +0.001 / 0 solved, inside the null); and no single edit > 8
  instructions accounting for the mechanism.

DELIVERABLES (all committed on crius/base-role-adopt-2026-09-18, pushed)
  crius/CRIUS_C2_TERMINAL_PREREG.md            cbf30a726 (before any run)
  crius/vm.py crius/artifacts.py crius/gate_c1.py  repair + gate v2 a3f6a4be0
  crius/tests/test_c2_terminal.py              11 tests; crius/tests 41/41
  crius/runs/gate_c2c_v2/ gate_c2d_v2/         A-H receipts, both ALL PASS
  crius/runs/search_c2c_* search_c2d_*         18 runs: REPORT LINEAGE PATH
                                               candidates.jsonl.gz, qualify
  crius/c2_path.py crius/c2_terminal.py        path evidence; scorer
  crius/runs/C2_TERMINAL_DISPOSITION.json/.md  mechanical verdict
  crius/runs/C2_TERMINAL_DISPOSITION_RECEIPT.json  fingerprints of inputs
  crius/runs/C2_SUMMARY.md                     rungs A-D
  crius/CRIUS_C2_TERMINAL_REVIEW.md            full review
  roles/Crius/STATUS.md (CLOSED)  roles/Crius/journal/2026-09-23.md
PROVENANCE: MEASURED throughout; I wrote world, controls, gate, tools; the
  control separation was directed by the operator and fixture-validated
  before the gate ran. Not my lane: Nyx manifest mismatch (comms #516).
================================================================================
