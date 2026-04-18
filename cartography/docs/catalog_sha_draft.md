# Catalog Entry Draft — P038 Sha (Tate-Shafarevich order) stratification

**Task:** `catalog_sha`
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Reserved P-ID:** `P038` (pre-reserved in task payload).
**Status:** DRAFT — awaiting sessionA/B review before merging.
**Proposal:** insert under Section 4 (Stratifications) after P035 Kodaira and before Section 5, once intervening P036/P037 land.

---

## P038 — Sha (Tate-Shafarevich order) stratification

**Code:** `WHERE sha = s` or `WHERE CAST(sha AS bigint) IN (...)` on `lmfdb.ec_curvedata`. 100% coverage across all 3,824,372 EC rows. Values are always perfect squares (`sha ∈ {1, 4, 9, 16, 25, 36, ...}`) by the Cassels-Tate alternating pairing on the finite part of Ш.
**Type:** stratification (arithmetic / algebraic axis), with a **major provenance caveat** (see below).

> **RANK ≥ 2 CIRCULARITY CAVEAT (read before using):** For `rank ≥ 2`, LMFDB's `sha` column is computed **by assuming BSD** and solving for the Sha value that makes the formula balance. Using `sha` as an *independent* stratification for anything BSD-adjacent at rank ≥ 2 is a closed loop (Mnemosyne's audit, 2026-04-15, anchoring `signals.specimens` row for the BSD v1 kill). Restrict to `rank ≤ 1` when `sha` must be independent evidence. For rank ≥ 2 work, either (a) treat `sha` as a *dependent* variable of BSD (not an axis), (b) filter to rows where a non-BSD Sha computation exists (descent-proven or 2-isogeny-descended), or (c) explicitly document the circularity in the result.

**What it resolves:**
- **Perfect-square Sha distribution.** Empirical breakdown across 3.8M curves:
  - `sha = 1` (trivial Sha): 3,502,608 (91.58%)
  - `sha = 4`: 212,138 (5.55%)
  - `sha = 9`: 65,936 (1.72%)
  - `sha = 16`: 22,749 (0.59%)
  - `sha = 25`: 10,953 (0.29%)
  - `sha = 36`: 3,239 (0.08%)
  - `sha = 49`: 2,795 (0.07%)
  - `sha ≥ 64`: ~4,500 combined (~0.12%)
- **High-Sha subfamilies.** The `sha ≥ 16` tail (~37K curves) is the concentration of non-trivial Tate-Shafarevich structure in LMFDB — **F005 High-Sha parity** calibration anchor lives here.
- **Sha-parity coupling with rank.** At rank 0: sha > 1 implies specific ε-factor parity structure (selmer-group rank ≥ 2 over Q-rational torsion). At rank 1: sha > 1 is rarer and geometrically constrained.
- **Cohort for 2-descent / 2-isogeny arguments.** Curves with `sha_primes` enumerated and `sha` a power of small primes admit computable descent arguments.

**What it collapses:**
- **The Cassels-Tate pairing structure itself.** `sha` records only the ORDER; the bilinear-form structure, odd/even part decomposition, and p-primary component sizes are collapsed into a single integer square.
- **The distinction between proven-Sha and BSD-assumed-Sha** (see caveat). Pooled analysis of `sha` without filtering by rank mixes provenance classes.
- **Any feature orthogonal to the integer-square equivalence class** — two curves with `sha = 4` can have very different rank, conductor, and torsion; `P038` treats them as one stratum.

**Tautology profile:**
- **P038 ↔ P023 Rank (circular at rank ≥ 2).** The decisive tautology — `sha` at rank ≥ 2 is a BSD-derived quantity, so jointly stratifying by `sha` and `rank` at rank ≥ 2 re-asserts BSD as if it were signal. Restrict all rank ≥ 2 P038 work to `WHERE sha_computation_method != 'BSD_assumed'` or equivalent, and document which side of that filter the analysis used. This tautology was anchored in the review-polished P023 failure-modes entry as "**Rank ≥ 2 BSD-joined circularity**" (sessionC catalog_polish, 2026-04-17).
- **P038 ↔ F003 BSD parity (direct identity).** F003 is the calibration anchor that SAYS `rank = analytic_rank` holds over 2.48M rows. Sha enters via the BSD formula; any coupling between `sha` and `analytic_rank` at rank ≥ 2 factors through BSD. This is not a failure of P038 — it is BSD working — but it means `sha` cannot corroborate BSD at rank ≥ 2.
- **P038 ↔ F005 high-Sha parity (calibration anchor).** F005 sits at `sha ≥ 16` and verifies parity of analytic rank for the high-Sha subfamily. P038 is the stratification that defines this subfamily. The anchor holds at 100% across 67,035 rows (verify_restore); any P038 analysis that produces disagreement with F005 implies either data corruption or a specimen-level error.
- **P038 ↔ Regulator (BSD formula).** The BSD leading-coefficient formula: `L^(r)(E,1) / r! = (Ω · Reg · #Sha · ∏c_p) / (|E(Q)_tors|² · |E_Q̄|)`. Regulator · Sha product is determined by the L-value / torsion / Tamagawa. Independent-looking "Regulator stratification × Sha stratification" at rank ≥ 2 is a single BSD identity rearranged.
- **P038 ↔ `sha_primes`.** `sha_primes` enumerates which primes divide |Ш|. For `sha = p²` with one prime: `sha_primes = [p]`. Not independent; `sha_primes` is a derivative projection of the same underlying data.

**Stratum-count summary:**
- 91.58% of EC have `sha = 1` (the trivial stratum dominates any pooled analysis).
- Effective non-trivial Sha coverage (≥ 4): 321,764 curves (8.42%).
- High-Sha F005 anchor cohort (`sha ≥ 16`): 67,035 curves.

**Small-n strata discipline:**
- Joint `P038 × P023 rank` strata: rank ≥ 4 with `sha > 1` drops into single digits quickly. sessionB's Liouville lesson applies — enforce `n ≥ 100` per adequate stratum at entry time.
- Joint `P038 × P020 conductor window`: coarse bins (e.g., `log10 N ∈ [4,5)`) at `sha ≥ 16` may have adequate n (~10–30K); fine bins won't.
- At high `sha` values (`sha ≥ 100`), per-value strata are small (≤ 400 each); pool by ranges rather than exact value for most analyses.

**Calibration anchors:**
- **Cassels-Tate (proved):** the finite part of Ш over a number field, when finite, has order a perfect square. Any `sha` value that is not a perfect square is a data corruption — **strongest immediate-spot-check anchor**.
- **Mazur torsion + rank-0 BSD (F002/F003):** at rank 0, `sha` satisfies the rank-0 BSD formula `L(E,1) = (Ω · #Sha · ∏c_p) / |E(Q)_tors|²`. Rank-0 `sha` is therefore independently computable from `L(E,1)` — it is NOT BSD-assumed at rank 0 (the formula is proven at rank ≤ 1 for modular forms).
- **Kolyvagin / Gross-Zagier at rank 1:** the rank-1 BSD formula is also proven. `sha` at rank 1 is proven-independent.
- **F005 High-Sha parity:** 67,035 high-Sha rows. Anchor holds at 100% per current tensor. Any P038 analysis implicating F005 must preserve this.

**Known failure modes:**
- **Using rank ≥ 2 `sha` as independent evidence of BSD** (the circularity caveat). Every publication-grade rank ≥ 2 claim that uses `sha` must document its provenance.
- **Pooling across ranks without rank-conditioning.** 91.58% sha=1 dominates; any "sha effect" measured pooled is a rank-0 + rank-1 effect by weight.
- **Treating `sha_primes` as an independent axis** (it is a derivative of `sha`).
- **Assuming sha values are integers of arbitrary magnitude.** Values are always perfect squares; any analysis allowing non-square sha is reading corrupted data.
- **Small-n at `sha ≥ 64`.** Rare values (100, 121, 144, 169, ...) have dozens of curves each; any stratification at those values needs explicit coverage reporting.

**When to use:**
- **Rank 0 and rank 1 BSD-adjacent analyses** where proven `sha` computations exist.
- **F005 high-Sha parity investigations** — P038 is the natural entry filter (`WHERE sha ≥ 16`).
- **Stratifying by `sha ∈ {1, >1}` as a binary** to separate trivial from non-trivial Tate-Shafarevich structure — this is the safest coarse application.
- **Cassels-Tate spot-checks** — fast calibration of new EC data imports (non-square sha → halt and investigate).
- **Joint with P020 conductor conditioning** for BSD-adjacent residual analysis at rank ≤ 1.

**When NOT to use:**
- **At rank ≥ 2 for any BSD-corroboration claim** without an explicit non-BSD-assumed filter (circularity).
- **Jointly with Regulator as if orthogonal** — they share the BSD leading-coefficient factor.
- **Against `analytic_rank` at rank ≥ 2** — circularity via BSD parity.
- **As a primary classification axis** — `sha=1` dominates, so P038-alone is de facto "trivial vs non-trivial."
- **For non-EC objects.** `sha` is EC-specific; Artin / MF / NF objects have analogous but distinct Ш concepts (Selmer group analogues) that do NOT live in `ec_curvedata`.

**Related projections:**
- **P023 Rank stratification:** parent tautology at rank ≥ 2; P038 is the most-affected downstream axis.
- **P020 Conductor conditioning:** recommended joint axis for rank ≤ 1 BSD-adjacent work.
- **P024 Torsion stratification:** joint (P038, P024) for Mazur-plus-Sha classification — standard EC BSD decomposition.
- **P028 Katz-Sarnak:** SO_even/SO_odd parity of EC L-functions correlates with root number which enters the BSD formula that also determines `sha` at rank ≥ 2; tautology chain to be aware of.
- **P035 Kodaira (sessionD, merged by sessionC):** Tamagawa `c_p` enters BSD formula alongside `sha`; joint P035 × P038 analysis faces BSD-formula-lineage risk at rank ≥ 2.

**Follow-ups this entry motivates:**
1. **`audit_sha_provenance_flag`** — Mnemosyne/Koios infra: add a `sha_computation_method` column to `ec_curvedata` (or a companion table) distinguishing `BSD_assumed`, `descent_proven`, `2_isogeny_bounded`, `lfunc_evaluated`. Enables safe rank ≥ 2 filtering per the caveat.
2. **`wsw_F005_P038_refinement`** — re-examine F005 High-Sha parity within finer P038 strata (`sha ∈ {16, 25, 36, 49, 64}` separately). Does parity hold uniformly or does one sub-stratum dominate the 100%?
3. **`catalog_regulator_P_nnn`** — document Regulator stratification as a separate catalog entry, flagging P038 × Regulator BSD-formula tautology explicitly.
4. **`pattern_20_sha_sensitivity`** — under the catalog_polish promotion of P023 rank-tautology to a Known-failure-mode, Pattern 20 (pooled artifact) applies specifically to rank ≥ 2 Sha stratification: any pooled rank ≥ 2 Sha claim should be cross-checked by filtering to rank ≤ 1 first and confirming the effect reproduces.
5. **Cassels-Tate anchor formalization** — promote "sha values must be perfect squares" to F-level calibration anchor (F007 or similar). Catches data corruption on import.

---

## Proposed tensor update

Add column `P038` to `landscape_tensor.npz` with initial invariance cells:

| Feature | P038 | Justification |
|---|---|---|
| F003 BSD parity | 0 | Sha enters BSD at rank ≥ 2 circularly; at rank ≤ 1 Sha is independent but the BSD parity anchor itself is rank parity, not Sha. 0 = untested directly, flagged for circularity. |
| F005 High-Sha parity | +2 | By construction — F005 is the `sha ≥ 16` cohort and P038 is the direct stratification. Perfect alignment. |
| F010 NF backbone | 0 | NF-side, not EC; Sha does not apply directly. |
| F011 GUE deficit | 0 | Zero-statistics specimen; Sha is not expected to resolve density-regime features. Pattern 13 prediction: -1 if tested, but untested → 0. |

---

## Language-discipline check

- "Projection," "stratification," "tautology," "circularity caveat," "calibration anchor," "Pattern 1 family," "cross-projection" used consistently.
- No "cross-domain" or "bridge" language.
- BSD described as *identity visible through the stratification at rank ≥ 2*, not as a cross-domain validation.

---

*End of draft. Per worker protocol, catalog entry is NOT appended to
`harmonia/memory/coordinate_system_catalog.md` directly. SessionA/B to
review and merge via `merge_P038_sha` task.*
