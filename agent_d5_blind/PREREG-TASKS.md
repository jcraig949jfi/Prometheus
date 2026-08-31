# PREREG-TASKS — Hard-Task Battery, Oracles, Reachability (Phase 1)

Status: FROZEN 2026-08-27. Preconditions met in order: (a) G0_PASS on the
evidence preflight (commit a516b2d2); (b) instrument validation ALL 7 CASES
PASS; (c) hardness calibration complete (depth sweep: full pool 80/40/20% by
depth 1/2/3 at 30k; per-primitive heterogeneity measured; CTRL case-mix
calibrated 2-case 50% / 3-case 11% / 4-case 0%). Final pre-freeze design
deltas, all calibration-driven and pre-evidence: F1 depth range 1-5 and F4
depth 1-4 (depth-1 on-ramp so development has a findable entry band);
CTRL-RAND case count in {2,3,4}; navigation objective = bitwise Hamming
(s6b). Battery composed from evidence seeds and frozen in
results/task_manifest.json (58 dev + 20 alien, EC = RC = 1.0).

## 1. Task model
A task is a total function f over a small finite input domain D, presented
machine-natively as the full input->output table (list of (input tuple, output
word) pairs). No natural-language content anywhere in learner-visible data.
Task identity fields (family, seed, stratum) are generator-side metadata and
are NEVER learner-visible (anti-cheat statically verifies this).

Exact oracle: candidate RM-D5 program g solves f iff run(g, x)[0] == f(x) for
EVERY x in D (exhaustive; D is 8–64 points). Deterministic partial credit for
diagnostics only: exact-match count over D. Behavior fingerprints are used for
search bookkeeping only, never for correctness.

## 2. Hidden structure library H (generator-side, frozen at battery freeze)
A pool of primitive word functions and predicates with frozen parameters,
e.g. affine maps x->(a*x+b) mod 2^16, bitwise masks/shifts, parity and
threshold predicates, small nonlinear steps (x->x*x+c). Developmental tasks
are compositions over H. H is never learner-visible; nothing in any
learner-visible observation names or indexes H. Transfer, if it appears, must
ride on machine-native regularities of the induced tables and the reusable
machinery that solves them.

## 3. Task families
- F1 AFFMOD: f = h_k o ... o h_1 (k = 2..5), h_i in H (unary). D = {0..63}.
- F2 PIECE: f(x) = branch on frozen predicate p in H: gA(x) if p else gB(x),
  gA/gB small H-compositions. D = {0..63}. Rewards conditional machinery.
- F3 ITER: f(x) = g^k(x), g a depth-1..2 H-composition, k = 2..6. D = {0..63}.
  Rewards loop machinery (JNZ).
- F4 BIT: f treats x as a 6-bit field; compositions of bit-reverse, interleave,
  masked shifts from H-bit primitives. D = {0..63}.
- CTRL-RAND (structureless control, section 27 of the constitution): f = an
  independently uniform-random lookup table on D = {0..7} (outputs in 0..255).
  No shared structure across tasks by construction. Used to test that any M1
  advantage is selective, not generic extra compute.
- NEGXFER (negative transfer): generated like F1/F2 but from a poisoned
  variant H' (one frozen constant altered per primitive) so surface-similar
  machinery from development is subtly wrong. Unlabeled; mixed into the
  developmental stream at frozen positions.
- ALIEN (held-out, seeds 6000+): two-input tasks f(x, y) on D = {0..7}^2,
  binary combiners (ADD/XOR/MAX-like) over the SAME H unary primitives.
  Surface-dissimilar (arity 2, different domain), structurally related only
  through H. Frozen before any M1 development; zero-shot transfer measured
  with M1's history frozen (constitution section 29).

## 4. Expressibility classification (E)
- Constructive compiler: each H primitive and combiner has a hand-written
  RM-D5 realization template; compiling the generating composition yields a
  witness program. If witness length <= 24: EXPRESSIBLE with stored witness.
- If the compiled witness exceeds 24 instructions: bounded semantic-pruned
  synthesis attempts a shorter witness within a frozen compute cap; success ->
  EXPRESSIBLE; exhaustion of a provable bound -> NOT_EXPRESSIBLE; cap without
  proof -> UNKNOWN.
- UNKNOWN tasks are excluded from findability denominators and reported.
- EC = EXPRESSIBLE / ALL reported with exact counts per family and stratum.

## 5. Reachability classification (R) — structural theorem for RM-D5
The frozen mutation physics includes INSERT and DELETE whose support contains
every specific single-instruction edit. Hence any expressible witness of
length L is reachable from the seed repertoire by an explicit constructed path
of <= L+2 mutation steps (insert witness instructions in order, delete the
seed instruction). Therefore in RM-D5: R == E, by construction, with recorded
witness paths. This is documented as a property of the generation, not
measured: reachability CANNOT be the failure mode here, and every failure on
an EXPRESSIBLE task is a FINDABILITY failure. The instrument's ability to
detect genuine unreachability is validated on synthetic ablated-physics cases
(section 8), where INSERT is removed and length classes disconnect.
Consequence: CFR denominator = EXPRESSIBLE (== REACHABLE) tasks; RC = 1.0 is
expected and carries no information in this generation.

## 6. Difficulty strata (oracle-side only; frozen at battery freeze)
Strata assigned from generator/oracle properties, never learner outcomes:
minimal known witness length W* (post compiler + bounded synthesis
minimization), omniscient synthesis cost, composition depth, and bounded
solution-multiplicity estimate. Provisional bands (calibrated on engineering
seeds before freeze): EASY W* <= 4; MEDIUM 5–8; HARD 9–14; VERY_HARD >= 15.
Battery rejects tasks trivial for frozen M0 calibration on engineering seeds
(constitution section 19) and families with surface shortcuts.

## 6b. Navigation objective (frozen meter component)
All arms (M0 suite and M1) navigate on the same deterministic score: bitwise
Hamming distance between candidate outputs and target outputs, summed over the
FULL task domain (constitution s23 deterministic partial credit). Score 0 is
equivalent to the exact oracle passing; every claimed solve is re-verified on
the reference VM. Rationale (engineering measurement 2026-08-27): the
pointwise exact-match count is a needle landscape on externally generated
tasks — witness 1-mutation neighborhoods jump from 0 to seed-level distance,
and M0 solved 0/48 tasks at 10k evaluations across all families. Bitwise
distance restores a usable gradient at shallow depth (depth-1: 4/5 solved in
<= 237 evaluations). The performance path is a Numba engine verified
bit-identical to the reference VM on 2,402-program orbits
(substrate/test_equivalence.py); the reference VM remains the authoritative
oracle.

## 7. Findability (F) and primary metric
CFR = learner-exact-solved / oracle-expressible(-reachable), by stratum and
family, at each rung of a frozen budget ladder (provisional: 1000 / 3000 /
10000 / 30000 verifier evaluations; final ladder frozen in PREREG-EVIDENCE
after hardness calibration). Identical ladders for all M0 and M1 arms.
Acquisition cost: first-solution evaluation index; censored statistics for
unsolved tasks; per-task distributions reported, never means-over-solved only.

## 8. Instrument validation battery (before freeze; constitution section 45)
Synthetic cases with known intended classification, all must classify
correctly before the evidence battery freezes:
1. expressible + reachable + easy (identity-adjacent compositions);
2. expressible + reachable + hard to find (deep compositions, verified
   nontrivial for frozen M0 at low budget on engineering seeds);
3. expressible + UNREACHABLE under ablated physics (INSERT removed;
   reachability oracle must report unreachable there);
4. unexpressible (witness provably > 24 or requiring >8 registers of state;
   constructed adversarially, e.g. high-entropy 64-point random tables whose
   bounded synthesis proof exhausts);
5. structure-shared sequence where history plausibly helps (shared H
   fragments) — instrumentation must track artifact reuse;
6. unrelated sequence (CTRL-RAND) — reuse tracking must show no shared
   structure;
7. negative-transfer sequence (H' poisoned) — oracle-side labels must place
   poisoned tasks correctly while learner-visible data stays clean.

## 9. M0 comparator freeze rule (constitution section 37)
The main M0 denominator navigator is chosen from {NAV-POP, NAV-HC, NAV-RX} by
reach rate on the EVIDENCE PREFLIGHT rows (substrate targets, disjoint from
the task battery) — frozen before any task-battery evidence run. All three
still run on the battery; the preregistered G-gates evaluate against the
frozen main comparator only.

## 10. Deliverables of Phase 1
task_generators/ (hidden_library.py, families), exact_oracle/oracle.py,
reachability_oracle/ (structural-path constructor + ablated-physics assay),
results/task_manifest.json, results/oracle_solutions.jsonl,
results/reachability_rows.jsonl, results/task_difficulty.json, and the
instrument-validation report results/instrument_validation.json. All frozen
files hashed into anti_cheat/frozen_hashes.json at battery freeze.
