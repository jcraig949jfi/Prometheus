# Lean/mathlib simp -- CUT-1 preregistration

Written 2026-09-11 BEFORE any file under Lean/Meta/Tactic/Simp/ was read
past its header. Prompt: roles/Nyx/prompts/2026-09-11_production_trial/
(PROMPT_verbatim.md; sha256 in MANIFEST.md). This file is not edited after
the cut begins; corrections are annotations in CUTS.md.

## 1. Specimen boundary (exact)

The specimen is the IMPLEMENTATION LINEAGE of the simp tactic as it exists
at the pins in PROVENANCE.md, which is:

  IN:  Lean 4 core, toolchain leanprover/lean4:v4.30.0, source tree
       src/lean/Lean/Meta/Tactic/Simp/  (13 files + Arith/ + BuiltinSimprocs/,
       6357 lines) plus the four files simp cannot run without and which no
       other tactic owns in the same way:
         Lean/Meta/Tactic/Simp.lean            (38 lines, the import hub)
         Lean/Elab/Tactic/Simp.lean            (758, tactic-syntax elaboration)
         Lean/Meta/DiscrTree/{Basic,Types,Util,Main}.lean (1003, lemma index)
         Lean/Meta/CongrTheorems.lean          (484, congruence lemma synthesis)
  IN:  mathlib4 at c9f8814322b00af24869d176c1896117d10e5d35 (2026-05-28),
       ONLY the parts that add MECHANISM to simp rather than lemmas:
         Mathlib/Lean/Meta/Simp.lean, Mathlib/Tactic/SimpRw.lean,
         Mathlib/Tactic/SimpIntro.lean, Mathlib/Tactic/Simps/,
         Mathlib/Tactic/Simproc/, Mathlib/Tactic/FieldSimp*, DSimpPercent.lean
  DATA (recorded, not cut):
       the 48,076 @[simp]-family attribute occurrences in mathlib4/Mathlib
       (grep count, this pin) and the core simp set. These are the lemma
       database. The prompt names "theorem database" as a FAILED cut, so
       the database is recorded as DATA and its ORGANISATION (how lemmas
       are indexed, prioritised, oriented) is where the cut is looked for.
  OUT: Lean's kernel, elaborator, WHNF/defeq engine (ExprDefEq.lean, 2331
       lines) EXCEPT where simp calls into them with a simp-specific
       configuration; the rw tactic; grind; norm_num as a whole (its
       simp-driver use is in scope only as an EXTERNAL CALLER of the
       specimen, evidence for the interface question); omega; aesop.
  OUT: Lean 3 / mathlib3 simp; Isabelle simp; Coq simpl. Ancestry claims
       about them are T2 at best and are not the specimen.

Boundary finding recorded at preregistration (before cutting): the
operator named the specimen "Lean/mathlib simp"; the mechanism is in Lean
core, and the mathlib half is, on the file inventory, DATA plus a small
number of extension mechanisms. Whether the mathlib extensions contain
anything mechanistic is a CUT-1 question, not assumed.

## 2. Procedure

1. Read the specimen files in this order and record, per file, what
   FLOWS (data in, data out, state read, state written), not what it is
   named: Types.lean, Main.lean, Rewrite.lean, SimpTheorems.lean,
   DiscrTree/*, Simproc.lean, SimpCongrTheorems.lean + CongrTheorems.lean,
   LoopProtection.lean, SimpAll.lean, Elab/Tactic/Simp.lean, then the
   mathlib extension files.
2. Draw candidate boundaries from the flow record. For each candidate,
   record in cuts.json its origin (INHERITED / DISCOVERED / PERTURBED) and
   the source boundary it coincides with, at the moment it is drawn.
3. Write ORGAN records (all fifteen questions; "unknown" legal) and
   PRESSURE records (organ-blind; forbidden_terms carries the famous names)
   under organs/ and pressures/. Validate.
4. Snapshot record bytes per candidate into cuts.json as CUT-1.
5. Run python -m nyx.chop.cutledger. Only then read the numbers.

No Lean is executed for CUT-1. No mathlib is built. The v4.30.0 toolchain
and the mathlib4 checkout on this machine pre-exist this seat and are
outside Techne management (no receipt names them); they are cited as
T1-LOCAL for the identity of the bytes and NOTHING is installed, updated
or built by Nyx. The gap (no Techne receipt) is reported, not filled.

## 3. Bookkeeping (deterministic; defined before the cut)

nyx/chop/cutledger.py over nyx/specimens/lean_simp/cuts.json. Definitions
are in that file's docstring. The Phase V questions map to:

  inherited-boundary rate      per_cut[*].inherited_boundary_rate_of_introduced
  cut survival                 transitions[*].survived_same_kind
  consumer rejection/revision  consumers.returns_rejecting_or_revising / returns_total
  unknown -> measurable        final.unknown_became_known (with a T1-LOCAL ref)
  independently testable       final.organs_with_independent_test_run
  pressures operationalized    consumers.pressures_operationalized_without_organ
  cheat controls that fire     cheat_controls.fired
  ambiguities unresolved       final.unresolved_at_last_cut
  time to first return         consumers.hours_to_first_substantive_return
  "did iteration improve it"   transitions[*].materially_revised > 0 AND
                               VERBOSITY_FAILURE false AND
                               final.unknown_became_known > 0; any of the
                               three failing is called failure

## 4. Predictions (so the result can embarrass the Chopper)

P1. CUT-1 inherited-boundary rate will be >= 0.60. Both prior specimens
    were cut on visible toolchain seams (journal 2026-09-11, calibration
    note); the habit is expected to persist on a first pass.
P2. At least one CUT-1 candidate will turn out to be POLICY or DATA
    (a configuration or a lemma-set convention presented as mechanism).
P3. The mathlib extension files will yield ZERO organs: they are
    syntax and orchestration over the core mechanism.
P4. The single most transferable candidate will be one that does NOT
    coincide with a file boundary.
P5. Fewer than half of CUT-1 ORGAN candidates will survive as ORGAN at
    CUT-2.

## 5. Stopping rule for this specimen

CUT-1 dies immediately (no CUT-2, DEAD CUT recorded, next specimen) if
after step 2 every candidate is INHERITED and none survives the twelve
attack questions of Phase II on paper. Otherwise CUT-2 proceeds. CUT-3
waits for either a consumer return or a completed ablation, whichever
comes first; it is not written from re-reading alone.
