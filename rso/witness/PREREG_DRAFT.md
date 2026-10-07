# Native retained-information witness -- PREREGISTRATION DRAFT (C-009-T015)

Palamedes[harry1-679179c6], 2026-10-07. DRAFT: freezes, unchanged except for items marked OPEN, as the first act
of the witness campaign (C-010) IF C-009 closes CC1-CC4 (operator directive 2026-10-07 s6). Nothing here is an
outcome. Sources: SELECTION.md, DESIGN_DRAFT.md (Cadmus), RULER.md (Argus, C-009-T014), Cadmus's T013 refinement
(comms #1742), rso/binding/CONTRACT.md (incl. s6 v1.0.1).

## 0. Exposure (recorded before any witness data)

The designers have read ares/ARES_CYCLE2_REPORT.md and seen the fossil name ares/fossils/W4_activation_memory_s3:
prior Ares work found W15-evolved lineages at the fitness cap (10/10) with plasticity often load-bearing, and
W4-evolved memory in activations. A W4-evolved subject is therefore expected by the designers to tend to NEGATIVE
across W15 interrupts and a W15-evolved subject to tend to POSITIVE. To keep the design from being chosen for its
expected outcome, BOTH are registered (decision 3 of SELECTION.md is reversed here, before preregistration), each
reported separately, never pooled. Those prior runs are background, not witness evidence; none of their genomes
or seeds is used.

## 1. Question and claim (relative; closure C2)

Q: Does a frozen Ares organism retain the regime bit r of world W15 across the world's activation-reset events and
use it -- and, if so, through its declared allowed channel (plastic W1)?
Claim form (rendered only with subject digest, world variant, seed set, n, bound, delta, alpha): "In W15, subject
S answers r after the last interrupt above the registered no-carry bound (P-RET POSITIVE), mediated by plastic W1
(P-CHAN PASS)." No class, mechanism-in-general, recursion or cross-physics wording.

## 2. Subjects (frozen before any witness episode)

  S4   primary.   ares.search.run("W4", "present", Config(), P=128, G=120, eps=4, seed=20261007) -> champion genome.
  S15  secondary. ares.search.run("W15", "present", Config(), P=128, G=120, eps=4, seed=20261008) -> champion.
Config() = substrate defaults (n_hidden 8, ticks 2, topology/keep/plasticity allowed). Selection is the GA's own
(its seeds, EVAL_SEEDS); no choice among subjects after any witness outcome. Each champion's genome bytes are
hashed and committed, with the run receipt, BEFORE any witness episode. A subject run that fails (exception) is
re-run once with the same seed; never with another seed.

## 3. Witness seeds

2048 episodes per arm, balanced (1024 r = 0, 1024 r = 1, RULER.md s2), drawn by the registered generator from
seeds >= 900000, excluding EVAL_SEEDS, balanced_seeds_for(...) ranges and every episode seed the two subject GA
runs drew (recorded by the driver); the excluded set and the final list are committed before the witness runs.

## 4. Arms (adapter wrappers, rso/witness/ares_client.py; no ares/ source edit)

  for each subject X in {S4, S15}:
    X        correct resets                                     P-RET (main), P-OBS, P-PRES
    X-NOPL   plasticity disabled                                P-CHAN
    X-LEAK   delayed-leak reset (v := 0, live W1 not restored)  P-ERASE broken member
  shared:
    POS      hand-wired PLAST carrier                           P-CAL (must be POSITIVE)
    RECUR    hand-wired activation self-loop                    channel control (reported, not gating)
    NULL     reset_each_step / random population                P-CAL (no carry)
    SHUF     W15 "shuffled" (cue decoupled from r), subject S4  P-CAL (no carry)

## 5. Predicates and gates

  P-CAL   GATE (RULER.md): NULL and SHUF each correct <= k_neg = 1073 of 2048, AND POS P-RET POSITIVE. FAIL makes
          every P-RET outcome of the campaign UNQUALIFIED.
  P-OBS   GATE: rollout record=True vs record=False give identical actions on every witness seed, per subject.
  P-ERASE GATE pair on B2, paired carry-over (Cadmus T013): the same probe episode run after two different
          preceding episodes (r = 0 vs r = 1); exact count of differing actions over the registered probe set.
          X: 0 differing actions expected (PASS); X-LEAK: > 0 expected (it is the fire case). If X-LEAK shows 0
          differences, the erase gate is DETECTION_UNQUALIFIED for X (the leak could not be exhibited).
  P-PRES  GATE: X after reset vs a fresh instance of the same genome: identical actions on a fixed seed set.
  P-RET   RULER (RULER.md s3-s4): n 2048, bound 1/2, delta 1/20, alpha 1/100, k_pos 1078, k_neg 1073;
          NOT_SHOWN / POSITIVE / NEGATIVE / INDETERMINATE by that precedence. Decided once per subject.
  P-CHAN  GATE, only if X is P-RET POSITIVE: X-NOPL P-RET is NEGATIVE or INDETERMINATE AND X correct - X-NOPL
          correct >= k_pos - 1024 (OPEN: Argus to confirm or replace this difference rule before freeze).

## 6. Outcome classes per subject (registered)

  POSITIVE               P-CAL, P-OBS, P-PRES PASS; P-ERASE pair separates; P-RET POSITIVE; P-CHAN PASS
  POSITIVE (channel unidentified)   as above but P-CHAN FAIL: "retention by an unidentified channel"
  NEGATIVE               instrument qualified (P-CAL, P-OBS, P-PRES PASS, P-ERASE separates) and P-RET NEGATIVE
  DETECTION_UNQUALIFIED  P-CAL / P-OBS / P-PRES FAIL, or P-ERASE does not separate, or P-RET INDETERMINATE or
                         NOT_SHOWN (NOT_SHOWN is reported as such inside this class)
The campaign result is the pair (S4 class, S15 class); S4 is primary. No pooling, no re-run to change a class.

## 7. Evidence and custody (rso.binding; CONTRACT.md s6)

Every predicate node is a canonical receipt with a node execution row (parent_run_id, receipt_sha256) under its
top-level launch; each bundle's manifest names its launch; manifests and inventories are registered with the
keeper (Aporia) before the first check. A witness claim is QUALIFIED only with its bundle's custody QUALIFIED.

## 8. Independent challenge and stop rules

One Pallas Q3 challenge on the frozen witness path (>= 1 sound, 2 broken, 2 edits; e.g. a counterfeit P-RET input,
a leak that passes P-ERASE), committed before outcomes; one repair round; then the result is final within the
72-hour window. Stop at the first exhausted cap; keep partial results; at 2026-10-10T00:25Z the s8 stop rule.

## 9. Budget (proposed caps for C-010)

top-level launches 10; CPU 60 minutes; artifacts 200 MB; GPU 0; $0; repair rounds 1; reviewer hours 1.5.

## OPEN before freeze
  1. P-CHAN difference rule (Argus).
  2. Exact probe set and count for P-ERASE (Cadmus), and the P-PRES seed set.
  3. Driver (C-009-T016, Eupalamus) must record the subject GA episode seeds for the exclusion in s3.
