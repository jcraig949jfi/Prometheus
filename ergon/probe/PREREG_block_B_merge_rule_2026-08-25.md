# Preregistration — replenishment block B and its merge rule

**Ergon (driver), 2026-08-25.** Executing P1 of `roles/Ergon/RESUME_ergon_2026-08-25.md` under
the REDESIGN ruling: *"Add a second independently pinned replenishment block, preregister its
merge rule, and report both block-wise and pooled results. The original pin then continues doing
the exact job for which it was created: preventing post-observation widening."*

**Committed BEFORE block B is generated or collected.** No number in this file exists yet.

---

## 1. Why a second block rather than extending the pin

The original manifest is pinned at `manifest_sha256` prefix **`e6b1e001`**, and `campaign.py`
**refuses to run on a mismatch**. That pin exists precisely so the population cannot be widened
after seeing results. Extending it would satisfy R13 by destroying the property the pin was
created to hold — and the driver asking for the extension is the party whose run it unblocks.

So: **`e6b1e001` is immutable and stays exactly as it is.** Block B is a sibling with its own
sha, its own ledgers, and its own independently verifiable identity.

## 2. Block B — parameters, fixed now

```
rung            M30                      (same rung; NOT a sweep — the rung is already ruled)
generator       task_gen_v3.generate     (same generator, same version, sha recorded at build)
n               220
seed            20260825                 (distinct from block A's 20260821)
uid prefix      nearmiss_mixB-M30-#####  (distinct namespace; no uid can collide with block A)
host pin        nvidia:deepseek-v4-flash (same host; no cross-host pooling, ever — R9)
second family   nvidia:nemotron-super-49b-v1 MUST also run block B in full, or the
                cross-family screen is UNDEFINED on block B and block B contributes nothing
                to a Tier B reading.
```

`n = 220`: at block A's measured cross-family screen removal (6/200 = 3.0%), 200 + 220 = 420 raw
yields ≈407 post-screen, comfortably above the R13 floor of 300 with margin for a worse removal
rate on B. Deliberately **not** tuned to land exactly at 300.

## 3. The merge rule — fixed before any block B row exists

1. **Both blocks are reported block-wise, always.** Any pooled figure appears beside its two
   constituents, never alone.
2. **Pooling is permitted only if all three hold:**
   - both blocks pass their own transport (≥0.95) and truncation (≤0.02) gates;
   - both blocks have a complete second-family leg on their own rows;
   - the two blocks' **cross-family post-screen point estimates** have overlapping 95%
     manifest-level intervals.
3. **If the intervals do not overlap, pooling is FORBIDDEN** and the disagreement is the
   finding: two same-rung, same-host, same-generator blocks that disagree mean the rung is not
   a stable property of the family, and the leveling does not transfer across draws. Report both,
   pool neither, and escalate.
4. **The primary analysis set is the pooled post-screen set** when pooling is permitted; each
   task carries a `block` label, and every reported statistic is reproducible restricted to
   either block alone.
5. **Block B cannot rescue block A.** If block A's own cross-family read had failed its band,
   adding B would not change that; B adds power, not admissibility.
6. **No third block.** If A+B still fails R13, that is a result about the design, not a licence
   to keep adding blocks until the floor is met. Adding blocks until a gate passes is
   sweep-until-in-band wearing different clothes.

## 4. What is NOT preregistered here, deliberately

The **decision gate** for the arms is not restated in this file. Under the REDESIGN ruling it is
no longer `Δ_carry ≥ X` but *"residue contributes beyond a shape-matched, saturated method
control"*, evaluated on the factorial. This document governs **the population only**.

## 5. Acceptance criteria for P1

- `e6b1e001` still matches after block B exists (asserted in code, not by inspection).
- Block B has its own committed manifest, meta, and sha; no uid collides with block A.
- The pooled post-screen n ≥ 300, or the reason it is not is recorded.
- A test exists that **fails** if block A's sha changes or if the two blocks' uid namespaces
  intersect — the constructed world where the thing I least want is detectable.

*— Ergon, M1, 2026-08-25. Written before the data, by the party the data would unblock.*
