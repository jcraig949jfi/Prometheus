# Crius Campaign 1 -- preregistration (revised under the operator ruling of 2026-09-19)

Currency: 2026-09-19. Written BEFORE any C1 code; committed first. Ruling:
roles/Crius/prompts/2026-09-19_c1_ruling/ (MANIFEST). Campaign 0 is
CLOSED; its three failure families are fixtures (crius/fixtures/), not
detectors. The hidden-scale world proposed in the C0 packet is withdrawn:
a three-valued latent is a datum.

Scientific target (operator's words): does selection discover any
persistent computational machinery whose accumulated products reduce the
cost of solving future novel tasks without sacrificing competence?

## 1. The world: RELAY (crius/world_c1.py, crius/tasks_c1.py)

Objects: tuples of L=4 integers in Z_8.
Primitive actions (the fixed mechanics; 12 of them plus RESET=12):
    INC(p)  x[p] += 1 mod 8        p in 0..3
    DEC(p)  x[p] -= 1 mod 8
    SWAP(p) exchange x[p], x[p+1 mod 4]
A Player emits an ACTION ID in 0..11. Each STREAM carries a hidden
permutation pi of the 12 ids (semantics-preserving relabeling, ruling 4):
id k performs primitive pi(k). Nothing about pi is observable except
through acting.

Hidden per-stream PROCEDURE LIBRARY: K=3 templates. A template is a list
of m in {2,3} steps (kind, offset), offset in 0..3. Applying template T
with ARGUMENT a to x performs, in order, primitive (kind, (a+offset) mod 4).
Templates are drawn per stream from a frozen generator; the qualification
streams draw their own libraries and permutations in a sealed namespace.

Task = (start, target, interaction_budget, step_budget), where target =
chain of d templates with per-task arguments a_1..a_d applied to start
(resampled if target == start). The Player sees start, target, budgets,
the number of actions, and its own status channel; never templates,
arguments, pi, stage or family.

Why this is a PROCEDURE and not a datum (ruling 2): the reusable object is
"template T applied to argument a", a function from argument to action
sequence. Two tasks built from the same template with different arguments
share no action sequence and no (start, target) pair; a table of solved
pairs transfers nothing (D-witness), a scalar cannot hold a template, and
a fixed action script is broken by both the arguments and pi. Chains are
compositions of procedures with fresh arguments.

Lifetime = 50 tasks: A 10 (single templates, each >= 3 times), B 10
(single templates, new arguments), C 12 (chains of 2 distinct templates),
D 10 (chains of 3 distinct templates), E 8 (search streams: chains of 2-3
with a REPEATED template, e.g. T1 T1 T2; qualification streams add chains
of length 4). Order within a stage varies by stream seed.

Budgets (interactions): d=1: 2000 (brute force over sequences of length
<= 3 is at most 12 + 144 + 1728 = 1884 applies, so every single-template
task is brute-forceable and expensive); d=2: 800; d=3: 1200; d=4: 1600
(brute force impossible: 12^6 sequences). Step budget 40000 per task.
Reuse route: 3 templates x 4 arguments = 12 options; chains of 2 = 144
mental candidates, of 3 = 1728; planning in the head costs ~15k steps.

## 2. Streams (ruling 4)

A stream is (namespace, seed) -> (pi, library, task sequence). Search
streams: namespace "search", seed 1000 + iteration: every iteration of a
search run evaluates its whole population (parents re-evaluated) on ONE
new stream -- common random numbers within the comparison, rotation
across comparisons. Qualification: namespace "qual", seeds 201, 202,
203, never used by search (the namespace is part of the generator key,
so no search seed can collide with a qualification stream). Task order
and pi vary per stream.

## 3. Fitness (ruling 1): competence first, then cost

Per task: solved_t in {0,1}; charged_t = interactions_t if solved_t else
interaction_budget_t; compute_t = (vm_steps_t + store_units_t) / 100.
    C1_FITNESS = solved_count + 0.5 * (1 - sum_t (charged_t + compute_t)
                                          / sum_t (budget_t + step_budget_t/100))
The secondary term lies in [0, 0.5], so one additional solved task
dominates any possible cost advantage (lexicographic in effect;
witness A). Unsolved work pays its full budget (witness B). Every
component is in every receipt; reuse_gain_t = cost_t(FRESH) -
cost_t(ACCUMULATED) is still measured per task (charged cost).

## 4. Sandbox integrity (ruling 5)

- ACT accepts only 0..num_actions (12 = RESET). Any other value, and any
  non-numeric value, is an INVALID ACTION: no interaction, no reset,
  status code 2. Nothing can alias RESET by arithmetic accident.
- Every store failure (block store full, allocation failure, copy or
  compose of a missing block, record creation over capacity) writes the
  tagged sentinel FAIL into the destination register and sets status 1.
  FAIL poisons arithmetic (any op with FAIL yields FAIL), compares equal
  to nothing but FAIL, is not zero for branches, cannot be written to
  the workspace, and cannot be acted on. INPUT status returns the last
  status code (0 ok, 1 store failure, 2 invalid action) so an organism
  may branch on it deliberately; it can never act on it by accident.
- Permanent regression tests: the C0 empty-block clock program
  (cdc90b7185eeeeed) is a fixture; under the new semantics its store
  failures produce zero RESET actions (witness C), and a micro-test
  fills the store and asserts ACT on the failed result performs nothing.

## 5. Variation operators (ruling 6; Apollo checked)

Apollo's 2026-08 record (roles/Apollo/STARTUP.md): single-step mutation
could not co-locate a parser and its guarded scorer; a body+guard UNION
crossover (dispatch_merge) did, replicating the 2026-06-16 recombination
finding. The generic analogue for bytecode is SEGMENT SPLICE: copy a
contiguous segment (1-8 instructions) from a second parent into a random
position of the child, with branch targets shifted as for insertion.
Arms: random (mutation only), seeded (ENUMERATE_VM_C1 + mutation),
recombination (seeded + splice on 30 percent of children). No operator
knows what a store op is; none encodes store -> lookup -> replay.

## 6. Players and controls (crius/baselines_c1.py; controls only)

  RANDOM_C1        uniform valid action each step
  ENUMERATE_C1     iterative deepening over action sequences (Python)
  ENUMERATE_VM_C1  the same in bytecode (search seed)
  QUIT_C1          ENUMERATE on depth-1-looking tasks, halt otherwise
                   (the abstention shape, as a fitness witness)
  TABLE_MEMO_C1    memorises exact (start, target) -> sequence in the
                   workspace and replays on exact match; enumerates
                   otherwise (the answer-table shape; D and H witness)
  PROCEDURE_REUSE_C1  the positive control. Keeps EVERYTHING in the
                   block store: (i) a calibration block whose state maps
                   action id -> primitive (12 probes, once); (ii) one
                   block per discovered template, whose INSTRUCTIONS take
                   the argument in R0 and emit the template's actions
                   through the calibration map; (iii) plans in the head
                   over (block, argument) chains of depth <= 3 using the
                   primitive semantics, then executes by BLK_INVOKE with
                   R0 = argument; (iv) falls back to enumeration and
                   records the found sequence as a new template block
                   relative to the first step's position. It never
                   writes a workspace cell, so FULL_TRANSPLANT ==
                   ARTIFACT_TRANSPLANT for it by construction.

## 7. Pre-search gate (ruling 7): witnesses, each a number in a receipt

  A  C1_FITNESS(QUIT_C1) < C1_FITNESS(ENUMERATE_C1) on every search
     stream tried, and max secondary term (0.5) < 1 by construction.
  B  For ENUMERATE_C1 the charged cost of every unsolved task equals its
     interaction budget (receipt field charged_t).
  C  Fixture test: the empty-block clock emits 0 RESET actions from
     store failures; micro-test: 33 x BLK_NEW then ACT R0 performs no
     action and sets status 1 then 2.
  D  TABLE_MEMO_C1 on a sealed stream solves no chain task by replay
     (replays_hit = 0 in stage C-E) and PROCEDURE_REUSE_C1 with
     calibration disabled (identity pi assumed) solves fewer than half of
     what the calibrated control solves on permuted streams.
  E  PROCEDURE_REUSE_C1 ACCUMULATED solves >= FRESH and reuse_gain over
     stages C-E > 20 percent of FRESH charged cost, on 3/3 qualification
     streams.
  F  ARTIFACT_TRANSPLANT remainder (from the stage-D snapshot) solves
     more tasks than CODE_ONLY and at lower mean charged cost, 3/3
     streams, code identical (candidate_hash equal).
  G  ARTIFACT_ABLATION_ALL remainder is within 5 percent of CODE_ONLY
     (the advantage is removed), 3/3 streams.
  H  The transplanted blocks are unchanged (instruction hashes equal
     before and after the remainder) and each template block is invoked
     with >= 3 distinct arguments producing >= 3 distinct action
     sequences on the remainder; TABLE_MEMO_C1 (the datum control)
     shows no transplant advantage on the same tasks.
If any witness fails, the world is redesigned and no search runs.

## 8. Predictions (written before the gate runs; falsifiable)

  Q1 The gate passes A-H on the first world instance above (if it does
     not, the most likely failure is F/G at depth 1: brute force within
     budget makes transplant unnecessary there; the witness is scored
     on stages C-E where brute force is impossible).
  Q2 Random arm: no candidate solves >= 20/50 on any stream by iteration
     200 (C0's random arm never exceeded 17/50 even on a fixed table).
  Q3 Seeded arm (mutation only): best solves 20-24/50 (the depth-1
     tasks) with no acquired-state effect: reuse_gain on C-E within
     +-5 percent of FRESH cost; ARTIFACT_TRANSPLANT == CODE_ONLY.
  Q4 Recombination arm: also no acquired-state effect within 200
     iterations. This is the prediction the campaign wants to lose. If
     it is lost, the winning lineage's mechanism is recovered from the
     receipts (store op trace, block events, invocation arguments)
     before any narrative is written.
  Q5 No searched candidate solves any chain task on a sealed stream
     except by luck (<= 2 of 30 chain tasks per stream).

## 9. What is frozen at the freeze commit

configs/c1.json (hash in every receipt), world_c1.py (fingerprint),
generator (tasks_c1.py; fingerprints of a reference stream), fitness,
qualification protocol (suite "qual", seeds 201-203, battery A-J),
variation operators, and this file's predictions.
