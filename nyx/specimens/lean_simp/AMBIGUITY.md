# Lean/mathlib simp -- alternative cuts, preserved not merged

Currency: 2026-09-11 (CUT-1). Charter VII: Nyx's decomposition is a hypothesis.
Each alternative is stated so a second Chopper or a consumer can pick it up.

## Cut A (Nyx, CUT-1): eight organs around a rule store

c01 canonicalization, c02 key abstraction, c06 ordered-rewriting guard,
c07 recursive discharge, c08 traversal fixpoint, c09 congruence descent,
c13 mutual saturation, c23 closed-term evaluation; the store itself DATA.

## Cut B: one organ, "rule application", and everything else is policy on it

c05 (unify lhs, synthesize args, reject no-op) is the only thing that
turns a rule and a term into a new term with a proof. c04 (ordering),
c06 (perm guard), c07 (discharge) are policies deciding WHEN c05 may
fire; c08 decides WHERE; c02/c03 decide WHICH rules to offer it. Under
this cut the specimen has one MECHANISM and a large POLICY surface, and
the transferable thing is the policy surface's SHAPE, not any organ.
Nyx did not take this cut at CUT-1 because c05 as written is unification
plus bookkeeping and unification is Meta's, not simp's. The cut is live.

## Cut C: the specimen boundary is wrong; simp is a THIN client of Meta

Congruence (c09), reduction (c10), unification (inside c05), type-class
synthesis (inside c07), the trie (c03), whnf: all live outside the Simp
directory and are shared with other tactics. What the Simp directory
contributes is: the rule store's organisation (c17), canonicalization
(c01), the perm guard (c06), the pre/post/loop/memo schedule (c08, c11,
c14), and the discharge recursion (c07). Under this cut the honest
statement is "simp is a scheduling policy over Meta's rewriting
primitives plus a curated store", and the organs are c01, c06, c07, c08
only; c02 and c09 belong to a different specimen (Lean Meta). A second
Chopper who owns the Meta specimen would make this cut.

## Cut D: the capability is in the DATA and the pressure, not the machinery

The 48,076 attribute sites plus the orientation convention plus the
community review process are where "simp works" comes from; the
machinery is what any competent rewriting-engine implementation would
have (T2: the source comments themselves say "Lean 3 style" for the
unindexed path and "good enough for Mathlib 3" for extra-args handling).
Under this cut the deliverable to Vivarium (pressure orientation_is_a_choice)
is the main product and the organ cards are secondary. Nyx holds this
cut as the leading alternative and wrote the pressure accordingly.

## Combinations noticed (recorded, NOT built -- anti-reassembly law)

- c01 + c06 + c08 together are what a "self-maintaining rule store" would
  need; this is an observation about the specimen's internal coupling,
  not a proposal.
- c02's forgetting table and c09's argument-kind classifier both read
  binder information from the same ParamInfo; a shared human prior
  (binder discipline = relevance) sits under both. Observation only.

## Added at CUT-3

Cut C gained evidence: c30 (literal arithmetic inside unification) is a
Meta mechanism that the specimen merely reaches through a reflexive rule.
The specimen boundary preregistered in PREREG s1 excluded ExprDefEq.lean
"except where simp calls into it with a simp-specific configuration";
the ablation shows the call is load-bearing for a whole class of goals.
A second Chopper who draws the boundary around Meta would own c30 and c09
and leave this specimen with c01 c02 c06 c07 and a schedule.
