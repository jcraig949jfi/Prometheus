# incubation/v3 — Lens Genesis: learned representation change

## Hypothesis

A learner operating under an initially valid but computationally pathological
representation can use executable experience to construct a new typed
representation that changes the problem decomposition seen by downstream
computation, exposes structure inaccessible under the original representation,
improves held-out computation causally, transfers frozen to a surface-dissimilar
world, is bounded/revised from executable evidence in a hostile world, and becomes
reusable material that makes acquiring a later representation dramatically cheaper.

## Design

One independent variable vs v2: learned artifacts change WHAT THE SOLVER
REPRESENTS THE PROBLEM AS. The downstream machinery is held fixed — it is exactly
the R2 control (the granted v2 bidirectional operator on the unchanged v2 engine),
so every R3 gain is attributable to the lens alone.

**The lens family** (`representations/lens.py`): a lens is a partition of a subset
of the primitive alphabet into 1–3 groups; the rest is EXCLUDED (recorded as the
discarded information). Applying a lens re-presents one reachability task as a
sequence of per-group subtasks — reach the target on that group's DISCOVERED
support (metered execution; supports are never supplied) — each solved by the
unchanged downstream engine, concatenated, and verified by replay on the true
domain. Aliasing is zero by construction; soundness rests entirely on replay. The
family contains qualitatively different transforms: full factorizations, coarse
partial factorizations, alphabet prunings (single-group), under-powered groups,
illegal exclusions.

**Classifier** (preregistered, `representations/classify_v3.py`): MACRO / OPERATOR
/ ACTION_RESTRICTION (single-group lens — same joint problem, does NOT qualify) /
REPRESENTATIONAL (>= 2 groups, and at least two subtasks must actually run).

**Worlds** (`worlds/families_v3.py`): one shared abstract alphabet, roles scrambled
non-contiguously across pid names. vA pressure (registers Z_997^8, two hidden
blocks, two cross-block decoys, deep tasks), vB reinforcement (Z_1013^9, permuted
slot layout, string surface), vC alien transfer (pairs of permutations of 9,
interleaved letter string), vD trap (heavy decoys: one primitive = a long baked
composition — one joint action, near-diameter displacement per block), vE recursion
(three blocks, three new primitives + a new decoy; lens space 2,798,250), vW0
no-pathology control.

**Learner** (`learner/lens_learner.py`): trigger = experienced pathology (>= 30%
budget failures over >= 10 tasks; never fires on vW0). Construction = exhaustive
metered evaluation of the frozen 11,050-lens space (sha `be25ed731e597b5e`, pinned
from the census into the preregistration) on the learner's own failed tasks.
Revision = a try-cap route whose learned content is a cost cap from the learner's
own clean-experience statistics. Recursion = extension order (prior groups kept,
prior exclusions kept excluded, only genuinely-new primitives assigned) vs the
frozen canonical order. The AST boundary test denies this module the world families
and every omniscient constant.

**Controls**: R0 baseline; R1 mined-macro (v1-style); R2 granted operator; F1 the
critical derived-feature control — the slot-match value as a best-first ordering
feature, state identity and decomposition unchanged; R4 omniscient ceiling
(harness-side only, never a gate).

## Census lineage (all recorded in results/)

lens_v0 REJECTED: the trap could not create solve-failure — block groups mod a
prime are essentially transitive, so decoy displacement leaves sub-targets
reachable; and vC at block depth 6 let the joint operator through. lens_v1
REJECTED: LIGHT decoys displace block targets only ~16 steps, absorbed by
block-bidirectional at R2's own cost (ratio 1.006 — not a trap); the F1 zero-luck
band was also wrong in kind (the control lucked into 1/5 permutation tasks;
"captures the gain" is a cost claim). lens_v2 PASSED: heavy decoys (ratio ~10x
with solve-loss), comparative F1 band, vC depth 7. Key census numbers: the
probe-solving lens class is a SINGLETON — 1 of 11,050 (0.009%), canonical rank
2,957 — among 28 behavioral classes; vE's known solver class has minimum canonical
rank 523,378 of 2,798,250 with 0/40 spot-sampled earlier lenses solving.

## Results observed (5 seeds, 2,030 task rows, results/lens_genesis_v1.json)

All 21 preregistered gates passed; anti-cheat battery passed. **VERDICT:
RECURSIVE_REPRESENTATION_EFFECT.**

- Trigger: fired 5/5 on vA+vB (65% budget failures), 0/5 on vW0.
- Construction: every seed evaluated all 11,050 lenses (326 support-valid) and
  found exactly ONE admissible — `LENS[u00.u03.u06|u01.u04.u07]`, the true
  factorization — identical in all five seeds (`p0001_consistent: true`).
  Classifier: REPRESENTATIONAL 5/5.
- Admission (held-out vA/vB, n=150): R3 solve 1.0 vs R2 0.30; median ops ratio
  R3/R2 = **0.0008** (~1,250x), identical per-seed; capture vs the omniscient
  ceiling = 1.000 in every seed. Ablation restores R2 result-identically.
- Controls: macros do nothing here (R1 = R2 = 0.30 — mined digrams from meet
  solutions, no recurring composition exists to mine); the derived-feature control
  solves 5% held / 10% vC at 400k-budget costs (R3/F1 = 0.0008) — the gain is not
  a feature, it is the decomposition.
- Transfer (vC, frozen hash): R3 solve 1.0 vs R2 0.325; R3/R2 = 0.0009; capture
  1.000. The lens — a partition of ACTION identities — crossed from register
  vectors to permutation pairs untouched.
- Trap (vD blind): solve rate fell to 0.53 and cost ratio 9.37 [9.34, 9.56] vs
  R2. Detection: 60/60 blind runs anomalous against the learned clean threshold,
  zero anomalies across 290 clean-world R3 runs. Revision: cap = 3,160 (10x clean
  median) learned identically in every seed; on fresh vD, p0002 routes 100% to
  fallback (solve 1.0, ratio vs R2 = 1.0747 — harm reduced to the 7.5% failed-
  attempt overhead); on fresh vA it routes 100% to the lens at overhead exactly
  1.0.
- Recursion (vE): the naive learner burned all 1,500 candidates (~22M ops) in
  every seed without finding a via-solving lens (the solver class starts at
  canonical rank 523,378); the experienced learner found an admissible extension
  at candidate 68 in every seed (>= 22x acquisition-cost separation; the census
  puts the naive-rank separation at >8,000x). The found lens extends p0001 (both
  prior groups preserved; prior exclusions never re-admitted), solves 50/50 held
  vE tasks, and is REPRESENTATIONAL.

## Honest notes and scope

1. The E winner is the COARSE extension (blocks 1+3 merged) because E selection is
   preregistered first-admissible, not min-cost; it extends p0001, qualifies under
   the classifier, and solves everything — the cheaper 3-split exists later in the
   order. Recorded, not hidden.
2. vD residual: p0002's 1.0747 vs R2 is repaired computational efficiency with a
   bounded residual (the failed lens attempt); repaired validity (solve 1.0) and
   residual overhead are reported separately per spec.
3. All cost claims are relative to the declared machinery: the fixed downstream
   engine and the frozen lens family. v3 demonstrates representation SELECTION AND
   CONSTRUCTION within a typed family (action-partitions) that the experimenters
   designed — not invention of the family itself. The census quantifies that the
   answer is not spelled inside the family (singleton class, 0.009%, rank 2,957);
   who wrote the ontology remains the open question above this experiment, exactly
   as preregistered in the program's scope.
4. The trap's lesson generalizes v2's: traps must attack the artifact's
   DEGRADATION mode (here: transitivity absorbs displacement; the working lever
   was making one joint action equal a near-diameter block displacement).

## Ledger

`ledger/p0001.json`: constructed from experience (trigger evidence recorded),
admitted, bounded (heavy-cross-transform worlds), revision → p0002; information
discarded = the excluded primitives; induced equivalence = none (aliasing 0).
`ledger/p0002.json`: try-cap routing successor, admitted. Append-only histories.

Per the spec: this experiment stops here. The next question — given symbolic,
algorithmic, and representational plasticity simultaneously, can failure route
plasticity to the right layer? — is explicitly NOT tested here.
