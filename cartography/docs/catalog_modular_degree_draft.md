# Catalog Entry Draft — P103 EC modular degree stratification

**Task:** `catalog_modular_degree`
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Reserved P-ID:** `P103` (pre-reserved in task payload; post-NAMESPACE_V2 counter).
**Status:** DRAFT — awaiting sessionA/B review before merging.
**Proposal:** insert under Section 4 (Stratifications) after P102 Artin Dim and before Section 5, once P102 merge lands.

---

## P103 — EC modular degree stratification

**Drafted by:** Harmonia_M2_sessionC, 2026-04-17 (task `catalog_modular_degree`).

> **DERIVABLE-NOT-STORED caveat (read before using):** The modular degree `deg(φ)` of an EC over Q — where `φ: X_0(N) → E` is the optimal modular parametrization — is NOT a column on our read-only `lmfdb.ec_curvedata` mirror. Sister columns (`num_int_pts`, `class_size`, `faltings_height`) are present but `modular_degree` itself is not. Any worker using P103 at scale must either (a) compute via Magma `ModularDegree` or Sage `EllipticCurve.modular_degree()` (rank-0 / rank-1 cases only for a provable version; otherwise heuristic via L-symbolic computation), (b) pull from LMFDB's public EC detail endpoint per curve (slow, rate-limited), or (c) wait for a Mnemosyne/Koios materialization. P103 is a PLACEHOLDER catalog entry pending materialization — its content is doctrinal scaffolding, not a ready-to-query axis.

**Code:** No `modular_degree` column exists in `lmfdb.ec_curvedata` at catalog-draft time (`information_schema` search 2026-04-17 returns zero hits). Derivation path: `modular_degree = deg(φ)` where `φ: X_0(N) → E` is the strong Weil parametrization. Computable per-curve via Magma / Sage / PARI at moderate cost for small conductor; expensive for N > 10^6.
**Type:** stratification (derived integer-valued axis; modular-parametrization geometry)

**What it resolves:**
- **Modular parametrization degree.** The minimal degree of a dominant morphism `φ: X_0(N) → E` when E has conductor N (equivalently: the degree of the optimal curve in the isogeny class). For the optimal curve, `deg(φ) = m_E` with `m_E ∈ Z_{≥1}` a canonical integer invariant.
- **Faltings-height relation (Edixhoven-Jong / Ullmo-Yafaev).** `log(modular_degree)` and `Faltings_height` are related via explicit theorems at proven levels (cf. Ullmo's bound); provides a BSD-adjacent calibration hook but with formula-lineage risk (Pattern 1).
- **Congruence-prime detection.** Primes dividing `modular_degree` control the congruences between `f_E` (the weight-2 newform attached to E) and other newforms of level N. This is the Ribet-Taylor-Wiles lifting regime — modular degree divisibility by `p` signals a non-trivial `p`-adic deformation space.
- **Quality indicator for the Birch-Swinnerton-Dyer period.** The Manin-constant and the modular degree jointly determine the real period `Ω_E` up to rational ambiguity; `modular_degree` is one-half of that constraint.
- **Isogeny-class invariance (up to Manin constant).** All curves in an isogeny class share the same `X_0(N)`, and the optimal curve has a distinguished `deg(φ)`. Non-optimal curves have `modular_degree` differing by an integer factor related to the isogeny degree. Joint with `P040 Isogeny class size` is the natural classification.

**What it collapses:**
- **Sign information, Manin constant, and period.** `modular_degree` is an integer magnitude; orientation and Manin-constant fine structure collapse.
- **Within-conductor variation.** Two different conductors can share the same `modular_degree`; the axis does NOT separate curves by `N`.
- **L-function content beyond the optimal-curve constraint.** Different isogenous curves with the same modular degree still have identical L-functions by definition.

**Tautology profile:**
- **P103 ↔ Faltings height (partial tautology via Edixhoven-Jong / Ullmo).** For rank-0 curves over Q, one has inequalities of the form `c_1 · log(m_E) + O(log N) ≤ h_F(E) ≤ c_2 · log(m_E) + O(log N)` with explicit constants. Joint `(P103, Faltings_height)` analyses must factor out this formula-lineage before claiming independent signal. **Pattern 1 family.**
- **P103 ↔ `num_int_pts` (partial).** Integral-point counts are bounded in terms of `modular_degree` via Vojta-type bounds. Joint usage has implicit formula-lineage through the arithmetic of the modular parametrization.
- **P103 ↔ P040 Isogeny class (near-identity on optimal-curve representative).** The optimal curve is the distinguished member whose `modular_degree` is the class-canonical value; non-optimal curves differ by explicit integer factors. P103 applied at isogeny-class level is `(P040, P103|optimal)` — use the pair, not P103 in isolation across class members.
- **P103 ↔ `sha_primes` via Ribet lifting.** Primes of congruence divide `modular_degree`; those same primes often appear in `sha_primes` for curves with non-trivial Ш. Joint use re-asserts Ribet-Taylor-Wiles ↔ BSD formal structure.
- **P103 ↔ conductor (conductor-exponent weak correlation).** `log(modular_degree)` grows on the order of `log(N)` with heavy conductor-windowed variation; pooled linear fits between the two look structural when they are mostly asymptotic scaling.

**Stratum-count summary (post-materialization prediction, not yet measured on our mirror):**
- Distribution is heavy-tailed and conductor-correlated. Expected regimes: `modular_degree = 1` (rank-0 with trivial Manin constant, narrow window), small `modular_degree ∈ {1, 2, 4, 8}` commonly, long tail into thousands and beyond for high-conductor curves.
- Small-n strata discipline: at any fixed `modular_degree = k` for `k > 10`, coverage drops fast; joint stratification with conductor window requires explicit `n ≥ 100` check.
- Expected ranges (from literature heuristics): 95%+ of curves have `modular_degree ≤ 1000`; rarer curves extend to 10^5+.

**Calibration anchors:**
- **Modularity theorem (Breuil-Conrad-Diamond-Taylor, 2001):** every EC over Q is modular, so `modular_degree` is well-defined and finite for every curve. Any attempt to compute on our mirror that returns undefined / infinite is a data-integrity violation.
- **Isogeny invariance of `deg(φ)·c_E`** where `c_E` is the Manin constant: the product is an isogeny-class invariant. Cross-check for any P103 implementation.
- **Edixhoven-Jong bound** (rank 0): explicit relation between `modular_degree` and Faltings height. Calibration spot-check on known rank-0 examples.
- **Modular-degree is a positive integer**: axis-level sanity check.

**Known failure modes:**
- **Using P103 without materialized data** — any worker drawing P103-based claims must document which of (Magma / Sage / public LMFDB endpoint / future `modular_degree` table) they used, and spot-check against a known value (e.g., the curve `11.a1` has `deg(φ) = 1`).
- **Treating `modular_degree` as orthogonal to Faltings height** — partial tautology via Edixhoven-Jong (Pattern 1 family).
- **Pooling across ranks without rank-conditioning** — heuristics for `modular_degree` vs `L(E,1)` / `L'(E,1)` differ by rank; pooled analysis mixes regimes.
- **Using non-optimal-curve `modular_degree`** — for non-optimal class members, the value is an integer multiple of the optimal; a "P103 analysis" over all curves without optimality filtering is a Pattern-20 mixture-of-strata risk.
- **Sparse high-value strata** — `modular_degree > 10^4` is rare; Pattern 9 coverage-cliff discipline applies.

**When to use:**
- **Ribet-Taylor-Wiles deformation / congruence-prime analyses** — `modular_degree` is the arithmetic-of-congruence axis.
- **BSD period-calibration work (rank 0, 1)** — combined with Manin constant and `Ω_E`, `modular_degree` closes the BSD leading-coefficient cycle for small conductor.
- **Joint with P040 Isogeny class size** to separate optimal-vs-non-optimal curves within each class.
- **Faltings-height calibration spot-checks** — when bounds are being verified empirically.
- **Small-conductor exploratory analyses** — where Magma / Sage `modular_degree` is computationally affordable.

**When NOT to use:**
- **Before materialization** — reporting "P103 distribution" over 3.8M curves is vacuous on our current mirror.
- **Alongside Faltings height as if orthogonal** (Pattern 1 via Edixhoven-Jong).
- **Across non-optimal curves without flagging** — Pattern 20 mixture risk.
- **For non-EC objects** — `modular_degree` is EC-specific.
- **As a substitute for `sha_primes` / Selmer in congruence detection** — these are related but orthogonal refinements.

**Related projections:**
- **P038 Sha:** via Ribet lifting (`p | modular_degree` implies non-trivial congruence at level Np; often present in `sha_primes`).
- **P040 Isogeny class size:** joint natural-classification axis; `modular_degree` is optimal-curve-canonical.
- **Faltings height (separate proposed entry):** partial tautology via Edixhoven-Jong (Pattern 1 family).
- **Conductor P020:** heuristic log-scaling `log(modular_degree) ~ log(N)` with heavy tails.
- **Manin constant** (not yet catalogued): `deg(φ)·c_E` is isogeny-invariant.
- **P035 Kodaira:** sibling DERIVABLE-NOT-STORED entry; similar materialization constraint.

**Follow-ups this entry motivates:**
1. **`materialize_modular_degree_per_curve`** — Mnemosyne/Koios infra task: run Magma `ModularDegree` or Sage on all 3.8M `ec_curvedata` rows, write to a new `ec_modular_degree(lmfdb_label, modular_degree, manin_constant, optimal)` table. Requires James input on runtime and storage (per P035 Kodaira precedent — not auto-seedable).
2. **`catalog_faltings_height`** — separate entry (sessionD EC harvest candidate); will need Edixhoven-Jong Pattern-1 cross-reference back to P103.
3. **`catalog_manin_constant`** — Manin-constant catalog entry; product `deg(φ)·c_E` is the isogeny-invariant companion.
4. **`audit_modular_degree_optimal_curve`** — once materialized, verify that every isogeny class has exactly one "optimal" curve and that `modular_degree` scales predictably among isogenous curves.
5. **`wsw_F005_P103_check`** — F005 High-Sha parity cohort (`sha ≥ 16`, 67K curves) vs `modular_degree` distribution. Heuristic: high-Sha curves often have large `modular_degree`. Pattern 1 check before claiming the correlation.

---

## Proposed tensor update

Add column `P103` to `landscape_tensor.npz` with initial invariance cells (pending materialization):

| Feature | P103 | Justification |
|---|---|---|
| F001 modularity | +1 | Modularity theorem makes P103 a well-defined axis; axis existence is a calibration anchor. |
| F003 BSD parity | 0 | Untested until materialized; expected +0 (not parity-dependent). |
| F005 High-Sha parity | 0 | Heuristic correlation expected; Pattern 1 risk via Ribet lifting. Untested. |
| F010 NF backbone | 0 | NF-side specimen (already demoted per sessionC wsw_F010_alternative_null); P103 is EC-specific. |

---

## Language-discipline check

- "Projection," "stratification," "DERIVABLE-NOT-STORED," "Pattern 1 family," "isogeny invariance," "Ribet lifting" used consistently.
- No "cross-domain" or "bridge" language.
- Modular parametrization described as *the morphism through which the projection is defined*, not as a cross-domain link.

---

*End of draft. Per worker protocol, catalog entry is NOT appended to
`harmonia/memory/coordinate_system_catalog.md` directly. Materialization
must be explicitly seeded with James's approval (per P035 Kodaira
precedent). SessionA/B to review draft and merge via
`merge_P103_modular_degree`.*
