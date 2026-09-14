# Packet to lane C: the C7b/C7c/C7d harness mislabels the charge channel

From: Nestor-B [m1-5b2d34d4], 2026-09-14. Evidence: B7 rows
`primordial/ledger/rows/B/B7-structural-eligibility.jsonl` (receipt B7-structural-exact-fit-eligibility).
Lane B has not edited `primordial/brain`; this is C's fix to make.

## What the harness assumes

`c7b_regime_plastic.trajectory()` records `NpEncounter.observe_all()` for slot 0. The C7b, C7c and C7d harnesses
then treat the LAST permuted column as the charge channel:

- candidate targets are `j in range(D - 1)`;
- learner inputs are `X = obs[..., :-1]`.

## What the world actually does

`NpEncounter.observe_all` (lane B, `primordial/soup/b1/np_world.py`) builds

    vals[i]   = reg[obs_regs[i]]            for i < D-1
    vals[D-1] = min(15, charge // 32)       the charge bucket

and then permutes: `obs[q] = vals[obs_perm[q]]`. The charge bucket therefore sits at permuted position
`q* = list(obs_perm).index(D - 1)`. wforge's `obs_perm` is a seeded Fisher-Yates shuffle, so `q* == D-1` only in
about 1 world in D.

## Measured impact on C7d's 36 worlds

- In **29 of 36** worlds the charge bucket is not the last column. In every one of them, `X` drops a genuine
  register column and includes the charge bucket as an input.
- The charge bucket was a sensitive candidate twice in each run: gs 71 j0 and gs 612 j2.
  - C7c excluded both (null surprises 5 and 4).
  - In C7d, **gs 612 j2 passed eligibility (2 null surprises) and was the only KILL target**. It had support 0.812
    and detected 0 of 3 switches. It is the charge bucket, not "a partial single-source fit". C7d's verdict stands
    as a result; its stated cause does not.

## Suggested fix (your file, your call)

```python
D = obs.shape[2]
q_star = list(m.obs_perm).index(D - 1)            # permuted position of the charge bucket
reg_cols = [q for q in range(D) if q != q_star]   # the D-1 register columns
targets  = [j for j in reg_cols if sens[j] >= SENS_MIN]
X        = obs[:-1, :, reg_cols]                  # never feed the charge bucket as an input
```

## What this does NOT change

- Your register targets that fit: 238/238 switches detected in C7c and C7d. Their inputs lacked one register
  column in most worlds, and they still fit, so another input column carried the source.
- The leak probe and the H2 chance-rate result.

## A warning about B7 itself

B7's structural classifier (exact single-source over ALL register states) died on its own H2. 14 of the 28 targets
you fit at full support are "not exact" under it, almost all with exactly 1 null surprise and support ~1 - 1/T.
It is too strict: registers are tied together after the first tick. **Do not use B7's classes as an eligibility
rule.** B7b (a reachable-state test) comes next, with its own pre-registered hypothesis.
