# RETROACTIVE VALIDITY SCAR ON SLICE 2B

Recorded 2026-09-21 under the operator's slice-2C ruling. This is not a
"fixed forward" note. It changes how much evidentiary weight slice 2B
deserves, permanently, and it travels with the 2B artifacts.

## What slice 2B claimed

"discovery_yield = 0/16" with the structural criterion unmet, reported in
pivot/APHRODITE_ENGINE_REVIEW_3_2026-09-21.md and
SLICE2B_RESULTS_2026-09-21.json.

## Why its STRUCTURAL arm is impaired

Two implementation defects meant the structural search did not instantiate
the grammar slice 2B believed it was testing:

1. THE ENUMERATOR REPAIR WAS NEVER APPLIED TO THE STRUCTURAL PATH.
   `_structural_search` called the v1 frontier-asymmetric enumerator, which
   cannot construct op(terminal, deep). The 2B packet's own section 4
   diagnosed that asymmetry as the reason the numtheory witness was
   unreachable -- while the structural arm was still running on it.

2. AN UNDECLARED TRUNCATION EXCLUDED THE ONLY WITNESS.
   HELPER_CANDIDATE_CAP = 40 was an arbitrary implementation constant, not
   part of any declared grammar. The declared helper space contains 48
   distinct helpers on two development instances, and EUCLID IS RANK 44.
   The one structural witness for numtheory was outside the cap.

Together: slice 2B's structural arm tested a SMALLER space than the one it
reported on. Its "no structural discovery" result cannot be read as evidence
about the declared grammar.

## What remains VALID in slice 2B

These do not depend on the enumerator or the helper cap, and stand:

  - lineage independence: 16 launched, 14 distinct artifact hashes, against
    v1's 10 launched / 1 distinct
  - tribunal isolation: disjoint entropy domain, construction refused before
    the generation-8 freeze, no lineage ever handed a tribunal
  - tribunal discrimination: modexp 1.00 held-out / 1.00 counterexample /
    metamorphic PASS; numtheory 0.61 / 0.00 / FAIL
  - membrane: 16/16 clean crossings, hash-at-extraction == hash-at-load,
    crossed == {artifact_bytes}
  - the decorative-loop fossil (L-004), which is now a permanent regression
    fixture adjudicated by the surrogate battery

## Disposition

  slice 2B structural evidence        IMPAIRED -- do not cite as evidence
                                      that structural discovery did not occur
  slice 2B apparatus evidence         VALID (list above)
  slice 2B overall label              GRAMMAR_INCOMPLETE, and now also
                                      GRAMMAR_MISINSTANTIATED
  pooling                             2B is never pooled with 2C

Grammar v1 is retained in engine.py, unused by later slices, so the impaired
result can be reproduced exactly rather than taken on trust.
