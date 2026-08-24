# Cycle 053 — PRE-REGISTRATION: factoring in `_verify_mahler_mpmath`

**Committed BEFORE inspecting more than one of the 17 stored entries.**
Confidence on every prediction (H1a build-debt; ledger 17/27 = 0.630).

## The defect (cycle 052, measured)

`lehmer_brute_force._verify_mahler_mpmath` escalates precision three times — dps 15/30/60,
extraprec 50/100/200, maxsteps 300/600/1000 — and **never factors**. On `Lehmer x (x+1)^2`
(degree 12, double root at −1 **on the unit circle**) the ladder returns `nan` where squarefree
factoring returns `1.1762808182599176` exactly.

Its NaNs set `verification_failed=True` on 17 band entries, which drives the run's published
**INCONCLUSIVE** verdict, framed as *"without high-precision certification we cannot decide
H5 vs H2 cleanly."*

## Why this is more than one function

`verification_failed` is consumed by `_lehmer_brute_force_path_b`, `lehmer_brute_force_path_c`,
`lehmer_boundary_layer` (where `verification_failed_at_dps30: True` is **definitional** for the
17), `discovery_promotion` and `kill_vector`. **Paths A, B and C are three workarounds for one
defect**, and the 17 have hardened into a named category downstream.

## Scope, fixed in advance

Fix the verifier and test it against the **stored** 17. **Do NOT re-run the brute force** —
that alters a published record other work cites, and the retract-vs-re-run disposition is
HITL #311, James's call. This cycle ships the mechanism, not the verdict.

## Predictions, with confidence

1. **All 17 `verification_failed` entries carry a repeated root** (some factor multiplicity
   >= 2). Confidence: **high.** I have seen exactly one — multiplicities 2 and 6 — and am
   generalising from it, which is the error I have made seven times. Stated at high anyway
   because the mechanism predicts it; if it fails, the mechanism is wrong, which is the point
   of writing it down first.
2. **The fixed verifier returns a finite M for all 17.** Confidence: **high.**
3. **The fixed verifier agrees with Path B's independent symbolic factorization to 1e-9 on
   all 17.** Confidence: **moderate-to-high.** Path B reached its answer by a different route
   (sympy `factor_list` over Z[x], then a cyclotomic-aware product); agreement is a genuine
   cross-check rather than a restatement.
4. **The fix makes Path B's role confirmatory rather than load-bearing** — the verifier alone
   reproduces its classification for all 17. Confidence: **moderate.**
5. **At least one downstream module hard-codes "17"** as a count or a category rather than
   deriving it. Confidence: **low-to-moderate.** `lehmer_boundary_layer` calls
   `verification_failed_at_dps30` definitional, which reads that way, but I have not looked.

## Kill test

**If the fixed verifier disagrees with Path B on ANY of the 17, the fix does not ship.** Two
independent routes to the same quantity must agree; a disagreement means either my fix is wrong
or Path B's published `H5_CONFIRMED` is, and neither may be shipped past silently.

## Self-guards

- **Population.** Every claim about "the 17" is measured over all 17, enumerated. After the
  cycle-052 sampling-window error (first-40 of an ordered table, 100x unrepresentative), any
  sample here is the **whole set** — it is 17 items, there is no excuse for a window.
- **Limit language.** Per cycle 052's rule, any limit I write must state a **mechanism**, not
  an observation.
- **Two arms.** Any comparison names its arms and asserts they differ only in the fix.

*— Techne, cycle 053, before measuring.*
