# D-8 PREREGISTRATION — Blind Serendipity Incubator

Status: FINALIZED BEFORE BINDING EVIDENCE. This file is hashed into
`frozen/MANIFEST.json`. Any edit after freeze invalidates the generation.

## 1. Question

Can accumulated executable experience cause a machine-native system to
construct or preserve a reusable computational object (z) that materially
changes what it can subsequently find under fixed resources, when z's form,
human category, relevance coordinates, and mechanism of benefit are not
specified in advance?

## 2. Substrate

SVM-8 (`svm.py`): deterministic, total, straight-line stack VM over 8-bit
wraparound integers; lossy stack-overflow, pop-on-empty-yields-0, scratch
register; max 12 tokens post-expansion; cost = tokens executed. Wraparound,
dead code, destructive stack moves, redundant ops, pathological arithmetic
are legal physics and are never sanitized.

## 3. Tasks and learner-visible interface

A task exposes to the learner ONLY: a uid and 6 revealed (x0,x1,x2)->y byte
pairs. Exact solve = matching all 6 revealed pairs AND all 24 hidden
verification pairs; the verifier answers a single boolean, is capped at 50
submissions per task per arm, and its cost is metered separately
(oracle-side). Family labels, generator structure, and hidden inputs never
reach the learner.

Families (mechanisms quarantined oracle-side; see `tasks.py`):
- F1 arithmetic op-soup (dev + eval), generator length 7–12.
- F2 motif-composed from a secret pool of 12 shared motifs "A" (dev + eval).
  This is deliberately planted reusable structure, hidden from the learner;
  the positive verdict must not rest on F2 alone (heterogeneity reported).
- F3 bit-logic op-soup (dev + eval), generator length 7–12.
- F4 HELD-OUT (eval only): compiled parametric affine/xor templates (6
  fixed shapes, 1–2 exact constants) — a materially different generative
  mechanism. Calibration showed F4 is findable in principle but heavily
  budget-limited (M0 near zero at the frozen budget); the transfer
  analysis carries a weak-baseline caveat, declared here in advance.
- F5 structureless control (eval only): SHA-derived outputs, no generator
  exists; history must not help; expected solve rate ~0 in all arms.
- F6 misleading control (eval only): F2-shaped but from disjoint motif pool
  "B"; history statistics should mislead (negative transfer preserved).

Batteries (uids are deterministic; seed blocks are disjoint by prefix):
- CAL* (calibration, non-binding), VAL*/VALF5/VAL8* (instrument validation,
  non-binding), DEV (binding development: F1/F2/F3 x 20 = 60 tasks),
  EV (binding evaluation: F1/F2/F3 x 20, F4 x 16, F5 x 8, F6 x 12 = 96).

Degeneracy filter: generators must yield >= 4 distinct outputs on the hidden
set (resampled up to 60x; resample counts logged). Triviality screen
(oracle-side): a generator is resampled if a fixed 250-candidate uniform
random probe, seeded from the uid and independent of every learner search
stream, reproduces all 6 revealed outputs.

## 4. Resources

Per (arm, task): BUDGET = 10000 candidate evaluations (one evaluation = one
execution of one candidate over the 6 revealed pairs). Search FITNESS is
bit-level agreement over the revealed pairs (0..48) — an independently
justified partial-credit signal declared before binding evidence; the SOLVE
predicate remains fully exact (6/6 revealed bytes + 24/24 hidden bytes). Retrieval executions
of stored artifacts count against the SAME budget (no free preprocessing at
solve time). Identical-bytes memoization within a task episode is legal and
identical across arms. Separately metered: vm_steps, verifier calls/steps,
history construction (hist_evals, hist_vm_steps), organization construction
(build_ops). All meters land in the ledgers.

## 5. M0 (history-free) suite

Frozen comparators, identical budget and verifier access:
- M0a uniform random program search;
- M0b restart hill-climber (stall 200);
- M0c generational GA (pop 40, tournament 3, 1-point crossover 0.6,
  point/indel mutation 0.15/0.08/0.08, elitism 2).
Point mutation of a literal token uses a local ±1..8 wraparound
perturbation half the time (identical in every arm).
Comparator-selection rule (frozen before binding): the PRIMARY M0 is the
variant with the highest pooled F1–F3 solve rate on the calibration
batteries run under the frozen configuration (CAL5 + CAL6, n=60);
recorded in frozen/MANIFEST.json (`m0_primary`). Outcome: M0b (0.40) over
M0c (0.30) and M0a (0.20). All variants are still reported. Note: M1 is
GA-based, so the primary comparison is against a *different, stronger*
history-free base — conservative by construction; M1F vs M0c (same base)
is reported as decomposition evidence.

## 6. M1 (history-conditioned)

Same GA physics, same budget/fitness/verifier. Differences are confined to
the proposal distribution, all derived from the hoard by frozen generic
procedures with no target decomposition:
- HOARD: executable records (program bytes, weight, behavior on 8 fixed
  probe inputs), admitted by the frozen machine predicate: verified
  solution (weight 6), or >= 5/6 revealed byte matches (weight 5), or
  bit-fitness >= 40/48 (weight 1); dedup by probe behavior (shortest
  kept); cap 3000 FIFO. Probe executions for storage are metered
  separately (hist_evals / hist_vm_steps).
- Constructed organization (rebuilt deterministically from the hoard):
  bigram token-class statistics + empirical length/literal distributions
  (used to propose fresh candidates); weighted contiguous-segment table
  (len 2–5, top 300) used by splice mutation; donor retrieval (sample 200
  records, execute on the task's revealed inputs AT BUDGET COST, seed the
  population with the top 10).
- PROMOTED OBJECTS (the z-candidate registry): contiguous segments
  (len 3–6) occurring in verified dev solutions of >= 2 distinct tasks; top
  8 by (#tasks desc, length desc, lexical). Promoted segments become single
  macro tokens available to mutation. Expanded length still obeys the
  12-token cap: macros restructure the search distribution, they do not
  extend expressiveness.
Development: M1 processes the 60 DEV tasks sequentially (arm "DEV"),
updating the hoard; promotion runs once at dev end; the result is frozen to
`frozen/machinery.json`.
Primary evaluation arm M1F uses the FROZEN machinery (no updates during
eval), so any benefit is a reusable-machinery benefit (H-FROZEN is built
in). M1L (live updates during eval) is a secondary, reported arm.

## 7. Controls and counterfactuals (all frozen)

- H-BAG: same stored records; organization destroyed (uniform proposal, no
  bigram, uniform bag segments, no macros); retrieval-by-execution retained
  (possession + generic reuse only).
- H-SHUFFLE: same information mass/marginals; stored relational wiring
  permuted (bigram class permutation, segment weights permuted, macro
  registry replaced by random equal-length record substrings).
- H-RANDOM: full machinery built from a size-matched hoard of random
  programs (independent of developmental relevance), mirror promotion.
- ABLMAC / ABLRET / ABLBIG: component ablations of the frozen machinery.
- ABLZi: per-promoted-object ablation (macro i disabled), run on EV
  F1–F4; basis of z admission criterion E.

## 8. z admission criteria (behavioral; frozen)

A promoted object z_i is ADMITTED iff ALL of:
- A ABSENT: not a primitive (structural; promoted segments have len >= 3).
- B CONSTRUCTED: provenance = frozen promotion predicate over dev
  executions (logged in dev_summary.json).
- C/E CONSEQUENTIAL+ABLATABLE: on EV F1–F3, ablation of z_i removes >= 30%
  of the (M1F − M0primary) solve-rate advantage, with exact McNemar
  p < 0.05 after Holm correction across ALL tested z (winner-selection
  correction; the number tested is reported).
- D REUSABLE: z_i appears (as macro token or as byte substring) in M1F's
  verified solutions of >= 2 distinct EV tasks.
- F NOT POSSESSION: global H-BAG retention < 0.7.
- G NOT INFORMATION MASS: global H-SHUFFLE retention < 0.7.
- H NOT MEMORIZATION: the >= 2 reuse tasks (criterion D) must have
  solutions NOT byte-identical to any stored dev solution.
- I RESOURCE HONEST: all construction/retrieval/verifier meters present in
  ledgers; any arm exceeding the declared budget invalidates the run.

Retention(arm) := (S_arm − S_M0)/(S_M1F − S_M0) on EV F1–F3.

## 9. Endpoints and statistics

Inference unit: task instance. Design: paired across arms on identical
tasks; per-(arm,task) search streams are independent (seeded by
sha256("search-v1", arm, uid)).
- PRIMARY: M1F vs M0primary solve indicator on the 60 EV F1–F3 tasks;
  exact two-sided McNemar on discordant pairs; significance alpha = 0.05;
  effect = solve-rate difference with bootstrap 95% CI (2000 resamples,
  seeded).
- SECONDARY (reported with CIs, no verdict weight unless stated): F4
  held-out transfer; F6 misleading (negative transfer allowed and
  preserved); F5 must stay ~0; first-solve cost medians on jointly solved
  tasks; per-family heterogeneity; M1L; component ablations.
- If any retention CI spans its 0.7 threshold, the result is flagged
  "inside noise" in RESULTS.json even if the point verdict passes.

## 10. Verdict ladder (frozen mapping)

- S0 NO_EFFECT: primary test fails (p >= 0.05 or delta <= 0).
- S1 HISTORY_CONTENT_EFFECT: primary passes, but organization not shown:
  any of H-BAG/H-SHUFFLE/H-RANDOM retention >= 0.7, or M1F vs H-BAG
  McNemar p >= 0.05.
- S2 RELATIONAL_ORGANIZATION_EFFECT: primary passes AND all three
  retentions < 0.7 AND M1F vs H-BAG p < 0.05.
- S3 NEW_REUSABLE_MACHINE_OBJECT: S2 gates pass AND >= 1 promoted z
  admitted under section 8.
- S4 ENDOGENOUS_MACHINE_COORDINATION: NOT ATTAINABLE by this design's
  ceiling unless an admitted z's benefit is demonstrated to depend on
  hoard-derived structure beyond the experimenter-designed
  splice/bigram/retrieval schema (e.g., emergent macro-of-macro
  composition that survives ablation of all designed channels). We
  preregister that we do not expect to award S4.
- S5 UNANTICIPATED_MECHANISM: awarded only if, post-freeze, a load-bearing
  mechanism is objectively demonstrated OUTSIDE the frozen positive
  ontology {fragment content reuse, learned token statistics, donor
  retrieval seeding}: concretely, admitted-z benefit must persist while all
  three ontology channels are ablated. We preregister this as very
  unlikely to be awarded.
Budget violations => INVALID. The verdict is computed by
`experiment.py stats` from frozen thresholds; no post-hoc adjustment.

## 11. Anti-tautology audit (performed before freeze)

Path trace (task -> representation -> retrieval -> prior -> generator ->
candidate -> verifier): the learner sees only revealed I/O pairs; hoard
admission uses only revealed-match counts (raw problem evidence); retrieval
ranks donors only by executing them on revealed inputs; promotion uses only
frequency across verified solutions; the verifier returns a boolean.
No learner-visible quantity encodes target coordinates, violated
invariants, mutation families chosen per-target, subgoals, or
oracle-derived bottlenecks.
DISCLOSED DESIGN BIASES (attainable-claim ceiling): (1) the constructor's
physics biases z toward contiguous code fragments and proposal-statistics
objects; other z forms are reachable only implicitly — hence the S4/S5
ceiling statements above. (2) F2 contains planted shared motifs; if the
effect concentrates in F2, that is disclosed as recovered planted
structure, not unanticipated mechanism (S5 excluded for such z; S1–S3
unaffected since the learner was never told).

## 12. Instrument validation (pre-freeze, fail-closed)

V1 artifact possession registers and is attributed to possession; V2
shuffled random history shows no large spurious gain; V3 generic diversity
shows no large gain; V4 endpoint memorization is flagged by the novelty
checker; V5 a useless complex object is not admissible; V6 an over-budget
arm is caught by the ledger validator; V7 the structureless world stays at
zero; V8 a genuinely useful planted object IS detected with ablation loss
(sensitivity). Validation runs at the binding budget (an earlier
generation run at budget 2000 failed V8 and is preserved:
ledgers/validation_1787897167.json). All validation generations
(including failures) are preserved under ledgers/validation_*.json. Binding may begin only after a
fully passing generation, with failures left in place.

## 13. Stop conditions

Per the D-8 charter section 20. If triggered, the generation is preserved
and reported as the result; no post-freeze repairs.

## 14. Calibration disclosure

Engineering calibration used CAL*/VAL* seed blocks only (disjoint from
DEV/EV by uid prefix), logged in ledgers/cal_*.jsonl and LOG.md.
Informativeness band (declared before calibration): primary M0 solve rate
on CAL F1–F3 must land in [0.15, 0.60]; outside the band, generator length
ranges / budget may be tuned BEFORE freeze with all runs logged.

## 15. What is fixed at freeze

sha256 of svm.py, tasks.py, engine.py, experiment.py, PREREG.md; CFG dump;
m0_primary choice; python version; timestamp. See frozen/MANIFEST.json.
