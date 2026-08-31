# AGENT D-5 — VERDICT

Date: 2026-08-27. All analysis from the pre-committed hashed script
(results/compute_gates.py, hashed before any M1 row was read). Rows committed
beside every claim. Machine verdict: results/gates_verdict.json.

## VERDICT: HISTORY_FINDABILITY_ADVANTAGE

Accumulated executable history increased the findability of exact solutions to
independently defined, oracle-reachable tasks under fixed metered budgets:
M1 − M0 = **+10.95pp CFR** (p = 0.0007 one-sided paired permutation, task-level
n = 42, effect 3.2 SE above zero). Margin over the preregistered 10pp floor is
0.95pp against SE 3.4pp — the EXISTENCE of the advantage is decisive, the
floor clearance is knife-edge (disclosed; also comparator-robust: vs the
marginally stronger-on-battery M0b-POP the delta is +10.0pp, p = 0.013).

BUT the causal decomposition (G9) shows what the advantage is and is not:
- M1-shuffled-history (same artifacts accumulated in permuted task order)
  retains **100%** of the advantage (77 vs 80 solves; 94/290 rows differ, so
  the arms genuinely diverged and re-converged in aggregate).
- M1-random-library (size-matched random-walk genotypes) retains **39%**.

The advantage is therefore a **library-content effect** — possessing
ecology-adapted executable artifacts, in any order — not a developmental-
correspondence effect. Consistent with that: no developmental trend (G6,
late-vs-early ≈ 0) and no significant frozen alien transfer (G7, +5pp,
p = 0.26). This is constitution s43's "M1 improves by carrying a library"
outcome, measured cleanly rather than assumed away.

## Claim ladder
- P0 PASS: 78/78 tasks have exact solving artifacts (constructive witnesses).
- P1 PASS (structural): R == E theorem — INSERT-complete physics makes every
  expressible witness reachable by an explicit edge-checked path (<= 26
  steps). Reachability carries no information in this generation; every
  failure on an expressible task is a findability failure. DISCLOSED.
- P2 PASS: strongest frozen history-free navigator solves 22.4% (mean
  per-task solve fraction, 42 non-control tasks, 30k evaluations; F3 40%,
  F4 27%, F1 18%, F2 0%).
- P3 PASS: G4 above.
- P4 NOT ESTABLISHED: HACR = 2.13 (M1 twice as fast on jointly-solved tasks)
  but 90% CI [0.93, 3.70] touches 1.0 at n = 13 — underpowered as frozen;
  preserved, not rescued.
- P5 NOT ESTABLISHED: alien zero-shot +5pp, p = 0.26.
- P6 NOT ESTABLISHED: G9 failed by design of the gate — the advantage is not
  attributable to correspondent developmental structure (shuffled retains
  it fully).
- P7 NOT ESTABLISHED: no acceleration over developmental time.

## Gate table (thresholds frozen before evidence)
- G0 PASS (substrate preflight, 5/5 gates; G0e weakly informative, disclosed)
- G1 PASS (58 dev + 20 alien, EC = 1.0) · G2 uninformative by R==E theorem
- G3 PASS (0.224 in [0.08, 0.70])
- G4 PASS (+0.1095, p 0.0007; floor clearance < 1 SE, disclosed)
- G5 FAIL (underpowered; HACR 2.13, CI90 [0.93, 3.70])
- G6 FAIL (−0.001, p 0.49)
- G7 FAIL (+0.05, p 0.26)
- G8 PASS (CTRL delta +0.06 <= 0.15 — advantage selective, though nonzero on
  the structureless control)
- G9 FAIL (shuffled retention 1.0, random retention 0.39)

## What this generation established beyond the gates
1. **Needle-landscape discovery**: externally defined tasks on a
   preflight-valid substrate were 0/48 findable under the pointwise
   exact-match objective; substrate-EMITTED targets were 57% reachable. The
   gap between emitted-phenotype accessibility and external-task findability
   is the central obstacle D-4-style geometry assays cannot see. Deterministic
   bitwise partial credit (s23) restored a soft findability gradient
   (depth-1 ~80%, depth-2 ~40-60%, depth-3 ~20% at 30k).
2. **R == E structural theorem** for INSERT-complete mutation physics: in such
   substrates reachability can never be the failure mode; a successor wanting
   a live reachability axis needs physics without universal single-edit
   insertion (validated here only on ablated-physics synthetic cases).
3. **Findability is per-primitive heterogeneous** even at depth 1 (SHRC 8/8
   vs MULC3 0/8 at 8000 evals): task-level replication is mandatory; single
   attempts measure seed luck.
4. The three-way failure split held: every dev/alien failure is a
   FINDABILITY failure by construction, with expressibility witnesses and
   reachability paths committed for all 78 tasks.

## What a successor generation inherits
- If the question is developmental SEQUENCING (P6/P7), design task ecologies
  where library content cannot saturate: non-stationary families, artifacts
  that require composition chains (so late tasks need machinery buildable
  only from earlier solutions), and physics without INSERT-completeness so
  reachability bites.
- G5 needs more jointly-solved tasks: either larger batteries or a
  cost-focused design where both arms solve most tasks.
- The +6pp CTRL delta (within gate) hints at a generic diversity-injection
  component; the 39% random-library retention measures it directly. A
  successor should meter diversity injection as an explicit baseline arm.

Forbidden-word check: this verdict makes no claim of intelligence, cognition,
understanding, or AGI. It claims one thing: under fixed metered search
budgets, an admissible library of previously executed, ecology-adapted
artifacts causally raised the probability of finding exact solutions —
regardless of the order in which that library was acquired.
