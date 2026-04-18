# Block-Shuffle Null Protocol

**Status:** Standard discipline as of 2026-04-17.
**Discovered:** F010 kill trajectory, sessionC wsw_F010_alternative_null.
**Authority:** Pattern 20 diagnostic bullet 4 + Pattern 21 (null-model selection).

---

## When to run it

Before promoting ANY specimen from `live_specimen` to anything stronger,
AND before entering a new P028-class stratified finding in the tensor.

Specifically run it when:
1. A finding uses a plain permutation / label-shuffle null and crosses z≥3.
2. The data has an obvious stratum structure (degree, rank, conductor,
   bad-prime count, symmetry class) that the plain null did not preserve.
3. A sample-size replication (Pattern 20 bullet 4) is ambiguous.

If all three hold, block-shuffle is mandatory.

---

## How to run it

Block-shuffle-within-stratum preserves the per-stratum marginal distribution
and shuffles only within. Choice of stratum matters — it should be the
axis whose marginal could carry the signal spuriously.

1. **Pick the stratification axis.** Common choices (by specimen class):
   - NF/Artin couplings → within `deg` (number-field degree)
   - EC/MF couplings → within `conductor` decile or `num_bad_primes`
   - Spacing/rank features → within `rank` cell or `(rank, symmetry_class)` joint
   - Szpiro-class features → within `k` (bad-prime count) stratum

2. **Shuffle within each stratum, recompute the test statistic, repeat.**
   200–1000 permutations typical. Keep the stratum marginal EXACTLY preserved
   (shuffle only the paired label, not the stratum key).

3. **Compute z = (observed - null_mean) / null_std.**
   Also report `null_p99` so the table can be re-inspected later.

4. **Threshold.** Standard: z ≥ 3 (positive) OR z ≤ -3 (negative) per stratum
   AND pooled. Borderline (|z| ∈ [2, 3]) = flag, do not promote.

5. **Interpret.**
   - |z_block| < 3: signal was between-stratum marginal (not a real coupling).
   - |z_block| ≥ 3 everywhere: durable. Record both `observed` and `null_p99`.
   - |z_block| ≥ 3 in some strata but not all: partial; report per-stratum.

---

## Anchor cases (calibration)

**Killed:**
- **F010 NF backbone** (sessionC 2026-04-17). Plain permute z=2.38 (borderline);
  block-shuffle-within-`deg`: observed ρ=0.173 vs null mean 0.205, z=-0.86.
  The 0.27 decontaminated ρ was degree-mediated between-strata leakage.
  Plain null over-rejected because it destroyed the per-degree marginal.

**Survived:**
- **F011 GUE first-gap deficit** (sessionB 2026-04-17). Block-shuffle-within-
  conductor-decile: observed spread 7.63% vs null p99 0.27%, z_block=111.78.
  Session's strongest durable finding.
- **F013 zero-spacing rigidity** (sessionB 2026-04-17). Block-shuffle-within-
  conductor-decile: slope_diff_z=13.68 vs null p99=1.47, z_block=15.31.
- **F015 Szpiro sign-uniform-negative** (sessionC 2026-04-17). Block-shuffle-
  within-`k`: every k-stratum passes at z ∈ [-24.03, -3.48]. Magnitude
  non-monotonicity is Pattern 20 territory, but SIGN is durable.

The F010/F015 pair is the instrument calibration: same protocol kills
the artifact, confirms the real. Trust the protocol.

---

## Common failure modes

1. **Picking the wrong stratum.** If you shuffle within a stratum that
   doesn't carry the spurious signal, the protocol reduces to plain permute.
   Always ask: "what marginal could produce this signal if the coupling
   weren't real?" That's the axis to shuffle within.

2. **Running it on too-small n.** F010 block-shuffle ran at n=51. Borderline
   for block-null stability. Aim for n ≥ 100 per stratum or flag
   the small-n cell explicitly.

3. **Conflating plain-null z with block-null z.** They measure different
   things. Always report both when you have them — the gap IS the Pattern 20
   diagnostic.

4. **Skipping when n is "obviously large enough."** sessionB argued F011's
   per-rank n=773K made block-shuffle unnecessary. It turned out to still
   matter (z_block=111.78 was consistent with plain z=7.63, but the audit
   was needed to confirm). Always run the audit — never reason it away.

---

## Implementation reference

See `harmonia/wsw_F010_alternative_null.py` (sessionB draft, sessionC
patched `DISC_CAP=10**12` per factoring-bottleneck fix) for a reference
block-shuffle-within-degree implementation. See
`harmonia/audit_P028_block_shuffle.py` (sessionB) for within-conductor-
decile implementation on F011/F013.

Result schemas (both runs) recorded in `cartography/docs/wsw_F010_alternative_null_results.json`
and `cartography/docs/audit_P028_findings_block_shuffle_results.json`.

---

## One-line summary

**Before promotion, shuffle within the obvious marginal; if z ≥ 3
survives, the signal is within-stratum real. Otherwise it was the marginal.**
