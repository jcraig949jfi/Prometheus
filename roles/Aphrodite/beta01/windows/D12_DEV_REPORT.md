# DEV-12 REPORT (C-006 Beta-01, cycle 12)

Opened 2026-10-05 about 14:07Z, after TEST-11 closed. Closed about 14:16Z with T12 frozen.

## 1. Starting point
T11 was MEASURED and not positive under the frozen sign tests:
- primary 123 vs 99, p 0.0625, which is the attainable minimum;
- cumulative 123 vs 93, p 0.14.

The mechanism is confirmed at selection level on EXPOSED seeds.

## 2. The first broken rung
**Evidential, not mechanistic.** The improver package (g10 + O10 + g11) has a large, uniform-direction effect on the
seeds that were used to build it, but:
- it has no unexposed replication;
- every frozen test so far was underpowered for the number of seeds the change can affect.

Another rule change would stack a fourth exposed modification. Doctrine (fix the earliest failed rung) points to
replication.

## 3. Design
**T12: a fresh-seed replication on W8 LIN 16-23**, which are committed but never used.
- It reuses the T51 pipeline unchanged.
- The primary test is an exact sign-flip permutation (it uses magnitudes; a T11 lesson).
- The attainable minimum p is reported.
- The power limit is stated before data: about 7-8 seeds. More would need W8 regeneration.

Not chosen:
- an endpoint-aligned selection score (T11 attack question 3): it is a new rule, and it would be exposed;
- seed 1's validation-to-transfer mismatch: a single seed;
- the sham re-test (the midpoint-2 placeholder): the strongest Beta-01 effect is now the improver package, and the
  NULL arm plus the fresh seeds already test it against junk and overfitting.

## 4. Pre-freeze controls
- **K1:** g11 reproduces T11 seed 3. PASS.
- **K2:** g10 after g11 in the same worker reproduces T10 seed 13, which proves the selector reset. PASS. This control
  caught a real design hazard before freeze: the first draft patched the selector per worker.
- **Sign-flip p on T11's exposed diffs:** 0.051, which matches a hand computation.

## 5. Frozen
beta01/windows/T12_REPL_SPEC.md. Runner t12_replicate.py, sha256 ceed378d....
