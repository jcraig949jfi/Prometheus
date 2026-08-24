# Cycle 052 — PRE-REGISTRATION: the scalar/batch divergence in `mahler_measure`

**Committed BEFORE measuring the divergence rate or writing the fix.**
Confidence stated on every prediction (H1a build-debt; ledger at 13/18 = 0.722).

## The defect

Cycle 051 fixed the scalar path via exact squarefree decomposition. The batch path was not
touched, so one module's two APIs now disagree:

```
mahler_measure([1,2,-1,-4,-1,2,1])        = 1.0            (exact, correct)
mahler_measure_batch([[1,2,-1,-4,-1,2,1]]) = 1.000146...   (the old defect)
```

`mahler_measure_batch(method='individual')` calls the scalar function and is therefore already
correct; `method='companion_batch'` builds a companion-matrix stack and is not. `'auto'` picks
between them on a **degree-spread heuristic**, so **which answer a caller gets depends on the
shape of the batch around their polynomial**, not on their polynomial. `mahler_measure_padded`
is the same stack exposed directly (Charon's Lehmer scan calls it).

## The fix under test

Screen each entry with the **exact** gate `deg gcd(f, f') > 0` (measured cycle 051 at 0.13
ms/entry over 8,625 catalog rows). Non-squarefree entries route to the scalar path; everything
else stays in the companion stack. The stack exists for throughput, so the design constraint is
that the squarefree majority keeps it.

## Predictions, with confidence

1. **The known counterexample resolves through every method** — `'auto'`, `'companion_batch'`,
   `'individual'` and `mahler_measure_padded` all return 1.0 to 1e-12. Confidence: **high.**
2. **Batch and scalar agree to 1e-12 across a randomised sweep** including deliberately
   non-squarefree entries. Confidence: **moderate-to-high.** This is the property the module
   should always have had.
3. **The gate costs less than 10% throughput** on all-squarefree batches (the common case).
   Confidence: **moderate.** 0.13 ms/entry was measured on catalog-degree polynomials against a
   ~17 ms/call scalar path, but the batch path is far faster per entry, so the *ratio* is what
   is untested — and the ratio is what matters here.
4. **At least one existing caller in the repo passes non-squarefree input.** Confidence:
   **low.** Zero of 8,625 catalog entries were non-squarefree, and generator-constructed
   polynomials are the untested population. Stated so the consumer question is answered by
   measurement rather than assumed either way.
5. **`mahler_measure_padded` is affected too, and fixing `mahler_measure_batch` alone leaves it
   broken.** Confidence: **high** — it is the same stack, exposed as its own public entry point.

## Kill test

**If prediction 3 fails badly — the gate costs more than 2x on squarefree batches — the fix
does not ship as written.** The batch path's entire purpose is throughput; a correctness fix
that destroys it has to be redesigned (screen once per batch, cache by coefficient hash, or
gate only when a cheap necessary condition fires), not merged and apologised for.

## Self-guard — applying cycle 051's lesson to this cycle's script

Twice now a measurement script has answered a different question than its kill test posed
(cycle 049's stale output file, cycle 051's stored-literals-vs-old-path). **So the comparison
script for prediction 3 must name its two arms explicitly — `gate ON` vs `gate OFF`, same
inputs, same process, differing only in the change under test — and assert that they differ in
nothing else.** No comparison against a stored constant, and no comparison against a number
from a previous cycle.

*— Techne, cycle 052, before measuring.*
