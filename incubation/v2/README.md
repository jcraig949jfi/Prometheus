# incubation/v2 — Operator Genesis

## Hypothesis

Repeated failure/cost structure can cause a learner to construct a new executable
algorithmic operator that changes its search architecture — the topology and control
policy of computation, not the contents of a composition slot — and that operator can
transfer frozen to an unseen world, be bounded by failure-driven revision, and alter
subsequent learning.

## Design

One independent variable versus v1: learned artifacts may reorganize computation.
Everything else keeps the v1 microscope.

**Meta-runtime** (`runtime.py`): search programs declare processes (root ×
{successors, predecessors}), a scheduling policy over runtime observables, and a halt
condition; optional two-stage sequencing for via-tasks. Every generator call and
verification replay is metered; budgets are strict (no goal credit past the meter);
candidate solutions are only constructible from orientation-compatible histories and
are always verified by replay.

**DSL** (`dsl.py`): 634 one-stage programs, canonical enumeration frozen by sha
`c44f6a4f09094537` before any run. No BIDIRECTIONAL token: "expand the smaller
frontier" must be constructed from FSIZE comparisons; a meet organization requires
jointly choosing both process specs, a workable schedule, and a MEET-capable halt.
The census measured 78 behaviorally distinct organizations; the meet class is 2.52%
of the space, first member at canonical rank 49.

**Domains** (`domains.py`): dA pressure (registers Z_997^6, deep tasks, forward
search exhausts the 400k meter), dB reinforcement (Z_1013^7, five primitives,
independent generator), dC alien transfer family (permutations of 12 under
free-growing generators), dD trap (Z_257^6, shallow tasks, predecessors unreliable:
85% of true preimages dropped, 24 spurious candidates per call), dE recursion probe
(via-tasks with deep halves), dW0 no-pathology control.

**Conditions**: A0 fixed forward baseline; A1 = A0 + one mined v1-style macro per
domain (a real control — it mines the planted composition and lifts solve rate from
0.30 to 0.62); A2 the architecture-construction learner; A3 the omniscient
meet-in-the-middle ceiling, harness-side only, never learner-visible, never a gate.

**Learner** (`learner.py`): starts as A0. A preregistered pathology trigger (>=30%
budget failures over >=10 tasks) licenses construction: exhaustive metered evaluation
of the frozen program space on the learner's own failed tasks; cheapest probe-solver
wins. The preregistered classifier (`dsl.classify`, structural AND behavioral) must
rule the artifact ARCHITECTURAL. Revision is failure-driven: anomalous runs trigger a
backward-edge audit (replaying claimed predecessor edges); a routing predicate is
fitted as the cheapest executable feature exactly separating bad from good evidence.
The recursion probe (dE) compares acquisition cost: a naive learner walks the frozen
canonical enumeration; an experienced learner walks its library neighborhood first.

## Preregistration

The `PREREG` dict in `experiments/operator_genesis_v1.py` (committed before the run)
fixes budgets, cells, twenty gates, the classifier, the enumeration sha, and the
five-tier conservative verdict enum: NO_ARCHITECTURAL_LEARNING →
ARCHITECTURAL_ADAPTATION_ONLY → TRANSFERABLE_ARCHITECTURAL_OPERATOR →
TRANSFERABLE_OPERATOR_WITH_REVISION → RECURSIVE_LEARNING_EFFECT.

## Census lineage (all recorded in results/)

meta_v0 REJECTED: budget-enforcement leak; dC generators relation-bound (2.4^d);
dD trap not a trap (meet-search still won, 0.896). meta_v1 REJECTED: register growth
is 3.55^d, so two depth-9 forward halves fit one budget in dE. meta_v2 PASSED; then
the FIRST FULL RUN failed D_HARM (1.42 vs 1.5) and D_DETECT (28.6% anomaly in two
seeds) — dD was marginal because the backward root is always meetable, so a dead
backward tree degrades meet-search to forward-plus-waste. meta_v3 REJECTED the 85/8
repair (1.405); a recorded sweep showed spurious VOLUME is the lever; meta_v4 PASSED
at 85/24.

## Results observed (5 seeds, 1,640 task rows, results/operator_genesis_v1.json)

All twenty gates passed; anti-cheat battery passed. **VERDICT:
RECURSIVE_LEARNING_EFFECT.**

- Trigger fired in 5/5 seeds on dA+dB experience (65% budget failures) and never on
  dW0. Construction was exhaustive-metered (634 candidates, ~62M ops); winners:
  `STAGE[AS+ZP|IF:FSIZE:LE:FSIZE|ANY]` in four seeds, `STAGE[AS+ZP|ALT|ANY]` in one
  — the learner reinvented meet-in-the-middle, in the balancing variant, from cost
  pressure alone. Classifier: ARCHITECTURAL in 5/5.
- Admission (held-out dA/dB, n=150): A2 solve 1.0 vs A0 0.30; median ops ratio
  A2/A0 = 0.0115 [0.0114, 0.0125] (~87x); A2/A1 = 0.0126; capture vs the omniscient
  ceiling = 1.000 in every seed. Ablation restores A0 result-identically.
- Transfer (dC, frozen hash): A2 solve 1.0 vs A0 0.31; A2/A0 = 0.0171; the macro
  control does not transfer (A1 0.325 ≈ A0); capture 1.000.
- Trap (dD blind): pooled harm 2.26 [2.12, 4.86]; the seed whose operator used ALT
  scheduling paid 33x — the trap distinguished operator variants that admission
  could not, which is exactly what World D exists to do. Blind solve rate fell to
  0.91. Detection: 9-14/14 runs anomalous per seed; the backward-edge audit flagged
  100% of anomalous runs and 0 clean runs.
- Revision: router = AUDIT_T > 0 (one predecessor-consistency probe at the target)
  in 5/5 seeds; on fresh dD it routes 100% to fallback (solve 1.0, ratio vs A0
  1.0085 — harm erased to +0.9% probe overhead); on fresh dA it routes 100% to the
  operator (overhead 1.0028).
- Recursion (dE): the naive learner burned its full 1,200-candidate budget (~72M
  ops) without finding a via-solving program in all 5 seeds; the experienced learner
  found `SEQ(o0001, o0001)` at candidate #2 in all 5 seeds (>=600x acquisition-cost
  separation); the found program solves 50/50 held via-tasks and is ARCHITECTURAL.
  Bidirectional search itself is not the dE answer — one of its ingredients is.
- Honest notes: (i) o0001 is not syntactically identical across seeds
  (`o0001_consistent: false`) — construction selects among behaviorally equivalent
  meet organizations; both admitted variants tie the ceiling in clean worlds and
  differ enormously under the trap. (ii) dD solve-loss under blind A2 means the trap
  costs solve rate as well as ops; the routed o0002 restores 100%. (iii) The
  MEET_VERIFY_CAP (200) bounds verification storms by construction; without it the
  trap would be strictly worse for blind operators.

## Ledger

`ledger/o0001.json`: constructed from experience, admitted, bounded (unreliable-
predecessor worlds), revision → o0002. `ledger/o0002.json`: routing successor,
admitted. Append-only histories.
