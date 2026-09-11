# Lean/mathlib simp -- failure landscape, ablations, decoys

Currency: 2026-09-11 (CUT-1). Every ablation below is DESIGNED, NOT MEASURED.
No Lean was executed. The specimen exposes most of these as configuration,
so a consumer with the v4.30.0 toolchain can run them cheaply.

## F. Failure modes read from the source (each cites a line)

F1  memo staleness under parent-dependent procedures -- Types.lean 76-107
    documents the +arith case; the fix is a flag the procedure must remember
    to set (Result.cache := false). Contract by convention.
F2  index/lookup config skew -- keys computed at attribute time under
    simpGlobalConfig (SimpTheorems.lean 249), looked up under the tactic's
    indexConfig (Types.lean 71); DiscrTree/Types.lean 45-56 and issue 2669.
F3  bad keys -- a rule whose lhs reduces to star/other at the root; the
    specimen counts them (Types.lean 242, Rewrite.lean 262-270) but only
    when diagnostics are on.
F4  depth-capped discharge fails silently -- discharge?' returns
    .maxDepth and the rule does not fire; indistinguishable at the result
    from "condition false" (Rewrite.lean 42-43).
F5  perm detection is structural only -- isPerm (SimpTheorems.lean 261-273)
    catches variable permutations, not two-rule loops or non-permutation
    reorderings; those fall to maxSteps.
F6  maxSteps exhaustion is an error, not a partial result (Main.lean 682).
F7  simp_all is entry-order dependent -- SimpAll.lean loop 59-124 rewrites
    hypotheses in array order and replaces rules as it goes; no confluence
    guard.
F8  wellBehavedDischarge is a declaration -- a lying discharger yields
    wrong cached results (Types.lean 426-433); the tactic-supplied
    discharger is installed as NOT well behaved (Main.lean 770) so caching
    is pessimised whenever a user supplies one.
F9  literal folders are per-type hand code -- BuiltinSimprocs/ one file per
    type; no generic mechanism.
F10 instance-argument check relaxed for convenience -- Rewrite.lean 66-83
    records that the strict defeq check was abandoned; the compat flag
    tactic.skipAssignedInstances remains.
F11 conjunction splitting makes rule identity many-to-one; erasure is by
    Origin (SimpTheorems.lean 540-551).

## A. Ablations designed (cheap ones first; all NOT RUN)

A1  Simp.Config.index := false      (c02 off)      predict: same results, more candidates, slower
A2  Simp.Config.memoize := false    (c08 memo off) predict: same results, more steps
A3  Simp.Config.singlePass := true  (c08 loop off) predict: fewer rewrites; some goals stop closing
A4  perm := false on every rule     (c06 off)      predict: any store with add_comm hits maxSteps
A5  discharge? := fun _ => none     (c07 off)      predict: conditional rules never fire
A6  maxDischargeDepth 0 / 1 / 2     (c07 graded)   predict: monotone count of fired conditional rules
A7  decide/ground/arith := false    (c23 off)      predict: closed arithmetic needs lemmas or fails
A8  descent disabled (app atomic)   (c09 off)      predict: root-only rewriting; near-total failure
A9  preprocess := identity          (c01 off)      predict: all non-Eq lemmas silently dropped
A10 simp_all store frozen           (c13 partial)  predict: stale rules; some goals stop closing

A1-A3, A6, A7 are configuration at the tactic; A4, A5, A9 need a patched
build or a Meta-level harness; A8, A10 need source edits.

## D. Decoys (what would look like the organ and is not)

D1  a rule store with all-wildcard keys: "retrieval" that returns
    everything (c02 decoy)
D2  a discharger that returns a proof of the wrong type: caught only by
    the isDefEq assign check (Rewrite.lean 47-49); a decoy for c07
D3  a traversal that reports failIfUnchanged instead of exhausting the
    budget on a planted loop (c08 decoy: "no progress" hiding non-termination)
D4  field_simp at this pin: a NAME decoy for the whole specimen (c20)

## Cheap-control opportunities for Archaeon

- A4 is a one-flag ablation with a near-certain outcome; a positive
  control for any rewriting organism's termination discipline.
- D3 is a general decoy for any "normaliser" organism: plant a loop,
  require the counter to hit the cap.
- The specimen's own diagnostics (Diagnostics.usedThmCounter,
  triedThmCounter, thmsWithBadKeys) are a free instrument for "which
  rules earned their keep" on any corpus, if a Lean toolchain is run.
