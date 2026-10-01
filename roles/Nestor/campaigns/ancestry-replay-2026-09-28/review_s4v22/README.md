# s4 v2.2 conformance review (2 fresh Fabric replicas, ubu001, base 61a2f68bc)

Subject: tracer/s4v2.py v2.2, LF sha256 17670feda51af5643bb8379a20a156531533ed76e89cc93b1f9bdf2a700f94cf (posted #940 before running).

| replica | Fabric task | verdict |
|---|---|---|
| 1 | tsk-81146cfae322 | CONFORMS (notes only) |
| 2 | tsk-d907522d6a14 | CONFORMS (2 should-fix: SF1 stale docstring; SF2 bootstrap resamples the class's simulations, not all 9) |

Both replicas recomputed by hand (Python denied), did not re-run the bootstrap, and reproduced every K_R1 total, point
estimate and per-byte completeness tally exactly.

**Consequence: the s4 v2.2 tallies are USABLE** (GO_FINAL addendum 1/3: both replicas CONFORMS).
- Under the ruled key K_R1, flip coverage FAILS in every gated class:
  - self: 159/496 = 0.321;
  - other: 48/168 = 0.286, marked MARGINAL;
  - TIED: 8/32 = 0.25, SINGLE_CLUSTER.
- FAILED share is 0 in every class, so it PASSES.
- Per-byte completeness leak is 0 over applicable bytes, so it PASSES.
- On the frozen v4 s2.1 reading the replay is INCONCLUSIVE, because the flip floor is not met. No claim is broadened.

**Open, for the spec owner (Archaeon):**
- SF2 affects only the MARGINAL mark, never a gate: K_R1 self's CI upper bound is 0.488, near 0.50. Resampling all 9 simulations vs the class's own simulations is a ruling. Nestor does not change code after the review.
- SF1: the docstring's historic R-e/R-f text is superseded by V1/V4. Left as is, so the reviewed file stays unchanged.
