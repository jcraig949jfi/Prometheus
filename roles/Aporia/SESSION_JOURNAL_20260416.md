# Aporia Session Journal — 2026-04-16

## Session: Data Landscape Unblock + Deferred Test Execution

### Context
James pushed major infrastructure changes: permissions granted across all 3 Postgres databases, 6 new indexes built, nf_fields (22.1M rows) fully loaded, bsd_joined materialized view (2.48M rows) available.

### What I Executed

**BSD Parity at Scale (via bsd_joined)**
- Result: **2,481,157 / 2,481,157 PERFECT** (100.000000%)
- (-1)^rank = root_number for every curve
- Rank distribution: 953K rank-0, 1.24M rank-1, 275K rank-2, 6.7K rank-3, 1 rank-4
- 282,373 curves at rank >= 2 (BSD unproven) — all match
- 350x scale-up from yesterday's 7,171-curve sample
- Non-circular: root_number from functional equation, rank from algebraic computation

**MATH-0042 Lehmer Conjecture**
- Tested 27,000 NF polynomials (3,000 per degree 2-10, random sample)
- Then targeted 4,500 smallest-discriminant fields per degree
- **Result: SUPPORTED** — no non-cyclotomic violation
- Smallest non-cyclotomic Mahler measure: 1.2683 (degree 10, field 10.0.379908823.1)
- Gap above Lehmer's number: 1.2683 - 1.1763 = 0.092
- Two apparent violations at M=1.001 were CYCLOTOMIC polynomials (Phi_24 and Phi_30) — numerical integration artifact, not real violations. Confirmed via root analysis (all 8 roots on unit circle).
- Note: Harmonia independently ran 90K polynomial Lehmer scan on M2

### Data Landscape Survey

**New access confirmed:**
- lmfdb.nf_fields: 22,178,569 rows (degree, disc, class_number, regulator, coeffs, galois_label)
- lmfdb.bsd_joined: 2,481,157 rows (EC + lfunc join with leading_term, root_number, positive_zeros, z1-z3)
- prometheus_sci: 14 tables accessible (knots, OEIS 394K, QM9, groups, etc.)
- prometheus_fire: 40 tables accessible (zeros 121K, battery results, tensor features, noesis, etc.)

**New indexes (critical for performance):**
- idx_ec_iso on ec_curvedata(lmfdb_iso) — enables BSD parity joins
- idx_ec_conductor_numeric on ec_curvedata(conductor::bigint)
- idx_mf_weight_level on mf_newforms(weight::int, level::int) — enables Langlands matching
- idx_artin_dim_conductor on artin_reps(Dim::int, Conductor::numeric)
- Plus 6 existing lfunc indexes (origin, conductor, degree, etc.)

**Key finding from Agora review:**
- Ergon confirmed: lfunc_lfunctions has ZERO Artin L-functions in the origin field. The artin_reps -> lfunc linkage does NOT exist in our data dump. MATH-0260 (Artin entireness) cannot be tested through lfunc.
- Charon killed P1.1 (Mahler-EC L-value bridge): z=0.00 on permutation null.
- Harmonia already ran Lehmer scan (90K polys) and 6-pack exploration including BSD 2.48M.

### What This Unblocks (Not Yet Executed)

1. **BSD Phase 2 full formula**: bsd_joined has leading_term. Can compute Omega*Tamagawa = leading_term * torsion^2 / (sha * regulator) for rank 0-1 (non-circular).
2. **MATH-0145 Brumer-Stark blind trial**: nf_fields has class_number + class_group for 22M fields. Filter to totally real (r2=0), compute Brumer-Stark element.
3. **Pair correlation (MATH-0062)**: prometheus_fire.zeros has 121K object zeros accessible.
4. **OEIS bridge for fungrim**: prometheus_sci.analysis.oeis (394K) + analysis.fungrim accessible.

### Remaining Blocked

- **Artin entireness (MATH-0260)**: No Artin L-functions in lfunc dump. Would need separate Artin L-function table from LMFDB.
- **P1.1 Mahler-EC bridge**: Killed by Charon (permutation null z=0.00).
- **Knot silence**: Confirmed genuine. P1.3 re-encoding failed. H3 (genuine independence) is leading.

### Updated Batch 01 Scorecard

| # | Test | Result | Scale | Status |
|---|------|--------|-------|--------|
| 1 | Jones unknot (cal) | PASS | 249 knots | Done |
| 2 | Langlands GL(2) (cal) | PASS 100% | 10,880 reps | Done |
| 3 | abc distributional | SUPPORTED (stratified) | 3.8M EC | Done |
| 4 | BSD Phase 1 rank | PERFECT | 3,824,372 EC | Done |
| 4b | BSD Parity | PERFECT | 2,481,157 EC | **Done today** |
| 5 | Chowla | SUPPORTED | N=10^7 (Ergon: 10^8) | Done |
| 6 | Artin entireness | FRONTIER MAPPED | 359K open | Blocked (no Artin L-funcs) |
| 7 | Lehmer | SUPPORTED | 31,500 NF polys | **Done today** |
| 8 | Brumer-Stark | Ready to execute | 22M NF available | Unblocked |

---
*Aporia, 2026-04-16*
