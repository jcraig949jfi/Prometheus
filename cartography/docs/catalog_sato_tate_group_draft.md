# Catalog Entry Draft — P037 Sato-Tate group stratification

**Task:** `catalog_sato_tate_group`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 15)
**Reserved P-ID:** `P037` (via `agora.work_queue.reserve_p_id()` at claim-time).
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications) after P036 Root number and before Section 5.
**Reference:** `cartography/docs/ec_harvest_triage.md` (sessionD), harvest row "Sato-Tate distribution — 1960s — equidistribution of normalized a_p".

---

## P037 — Sato-Tate group stratification

**Code:** `WHERE st_group = <group_label>` on `lmfdb.g2c_curves` (66,158 rows, column `st_group`) and on `lmfdb.lfunc_lfunctions` (column `st_group`, indexed via join strategies rather than full scan). Also `st_label` and `st_label_components` carry the finer rational classification. **Note:** `bsd_joined` has a `symmetry_type` column but it is all NULL at 2026-04-17; `st_group` lives on the genus-2 and lfunc tables, not directly on the EC curve row. For EC `a_p` analyses, join to `lfunc_lfunctions` via `origin = 'EllipticCurve/Q/...'`.
**Type:** stratification (algebraic / Lie-group equidistribution axis for normalized Frobenius traces)

**What it resolves:**
- **The compact Lie group on which normalized Frobenius eigenvalues equidistribute.** For an elliptic curve over Q: `SU(2)` in the generic (non-CM) case per the Sato-Tate conjecture (proved for weight-2 newforms by Taylor et al. 2011); `N(U(1))` (normalizer of the maximal torus in SU(2)) for CM curves. For a genus-2 curve: one of 34 possible Sato-Tate groups classified by Fité-Kedlaya-Rotger-Sutherland (2012); the 28 types actually achieved form the stratification here.
- **CM vs non-CM distinction at the L-function level.** Equivalent information to `P025 cm` for EC, but expressed in Lie-group-theoretic vocabulary. For g2c, Sato-Tate type carries strictly more information than a single CM flag since genus-2 Jacobians can have partial CM / RM / QM structures that decompose into different Lie groups.
- **Moment predictions for normalized a_p.** The Sato-Tate group determines moments `⟨(a_p/2√p)^k⟩` exactly via the character table of the group's irreducible representations. Any deviation at finite conductor is a measurement of finite-N vs asymptotic universality.
- **Cross-projection calibration for Katz-Sarnak.** P028 Katz-Sarnak is the *zero-side* symmetry classification; `P037` is the *a_p-side* companion. The two should agree on family assignments up to the classical correspondences (SU(2) generic EC → SO family, N(U(1)) CM EC → also SO but with forced central zero via ε, etc.). Disagreements are data-quality signals.

**What it collapses:**
- **Within-group structural distinctions.** All 63,107 `USp(4)` genus-2 Jacobians in LMFDB map to the same stratum regardless of conductor, automorphism group, rank, etc. Use `P037` as a coarse equidistribution filter; stratify further by `P022` aut_grp, conductor, rank, etc., when the question is finer than "which Sato-Tate class."
- **Non-a_p structure.** Features independent of the Frobenius-trace equidistribution — e.g., explicit ideal-class-group invariants, regulator values, Tamagawa numbers — are invariant under `P037` and collapse.
- **Finer rational classification (`st_label`).** `st_group` is the Lie group; `st_label` sub-divides by the rational component-group structure (e.g., different finite extensions of the same identity component). Using only `P037` collapses the rational refinement that `st_label` would expose.

**Tautology profile:**
- **P037 ↔ P025 (CM flag) on EC.** For elliptic curves over Q, `st_group = SU(2) ⇔ cm = 0`; `st_group = N(U(1)) ⇔ cm ≠ 0`. Full aliasing on the EC slice. Applying `P037` and `P025` independently on EC-only data is double-counting. On the genus-2 side or for higher-dimensional families, `P037` carries strictly more information than any single CM-flag, so the aliasing is a pure-EC concern.
- **P037 ↔ P028 Katz-Sarnak (cross-side correspondence).** Sato-Tate classifies by `a_p` moments; Katz-Sarnak classifies by low-lying zero statistics. For EC: SU(2) generic → SO_even or SO_odd by rank parity (another nested tautology with `P036` root number / `P023` rank). For g2c: USp(4) → Sp family predicted. The cross-side correspondence is a proved theorem stack (Taylor et al. + Katz-Sarnak); treating `P037` and `P028` as independent on the same family risks double-counting the same classical predictions.
- **P037 ↔ P031 Frobenius-Schur on Artin-origin L-functions.** For 2-dimensional Artin L-functions, Sato-Tate group is determined by the image of the Galois representation (SU(2) for "large image" cases; finite Lie groups for small-image cases). `P037 × P031` on the Artin slice is a proved-identity pair via known theorems, not an independent cross-axis.
- **P037 ↔ moments of `a_p`.** Reporting a deviation from the expected `⟨(a_p/2√p)^k⟩` moment under a specific Sato-Tate class, while using `P037` as the stratifier, is formula-level lineage (Pattern 1). The moment IS the prediction the class makes; use a null model (permutation of curve labels within class) to separate structural deviation from class-definition recovery.

**Stratum-count summary (live queries, 2026-04-17):**

For **genus-2 curves** (`g2c_curves`, top 20 of 28 observed classes out of 34 possible):
- `USp(4)`: 63,107 (95.4%) — generic g2c (no CM / no RM / full-image Galois)
- `SU(2)×SU(2)`: 2,440 (3.7%) — split Jacobian into two non-isogenous EC
- `N(U(1)×SU(2))`: 303
- `N(SU(2)×SU(2))`: 144
- `E_6`: 51
- `J(E_1..6)`: small counts
- `F_{ac}`, `D_{2,1}`, `D_{3,2}`, `D_{6,2}`, `J(C_2)`, `J(C_4)`: single- or double-digit counts
- Total: 66,158 g2c rows

For **elliptic curves** (via `lfunc_lfunctions` with `origin LIKE 'EllipticCurve/Q/%'`): query timed out at 30 s on unindexed prefix scan; per classical theory the distribution is ~99.8% `SU(2)` and ~0.2% `N(U(1))` (CM curves are rare, `cm != 0` in ~4,100 out of 2.48M bsd_joined rows per earlier session data).

**Small-n strata discipline:**
- For g2c, any `P037` stratum outside `USp(4)` and `SU(2)×SU(2)` drops below `n = 100` immediately. Applying sessionB's Liouville-lesson `n ≥ 100` discipline at the stratum level means only two g2c strata are adequate for per-stratum `|z|` reporting; the remaining 26+ exotic classes must be pooled or reported with explicit `n` caveats.
- For EC, both strata (`SU(2)` and `N(U(1))`) have `n ≥ 100` by a wide margin. No small-n concern at the marginal level.
- Joint `P037 × P020 conductor` at narrow conductor windows rapidly produces small strata for g2c exotic classes. Apply Pattern 9 (delinquent frontier) discipline — absence of signal in exotic Sato-Tate classes is usually absence of measurement.

**Calibration anchors:**
- **Sato-Tate conjecture for elliptic curves over Q** (weight-2 newforms): proved by Taylor, Barnet-Lamb, Geraghty, Harris, Shepherd-Barron (2006–2011). Any implementation that gives `SU(2)` for a known-CM curve, or `N(U(1))` for a known-non-CM curve, is broken (Pattern 7 — stop all work).
- **Fité-Kedlaya-Rotger-Sutherland classification** for g2c Sato-Tate groups (2012): proved complete list of 34 possible groups; `st_group` values in LMFDB are required to lie in this set. Any new value is a data-quality violation.
- **SU(2) moment universality** for non-CM EC: `⟨(a_p / 2√p)^k⟩` → `(1/π) ∫ sin²θ cos^k θ dθ` as p → ∞. Finite-conductor deviations are the finite-N structure relevant to F011's GUE story on the `a_p` side rather than the zero side.
- **ec.cm ↔ st_group = N(U(1)) identity** on EC: by the Sato-Tate conjecture classification, `cm != 0 ⇔ st_group = N(U(1))`. Any row violating this is a data-quality issue — candidate calibration-anchor F-slot pending verification.

**Known failure modes:**
- **Applying `P037` to families where Sato-Tate is not yet proved.** For higher-genus families, higher-dimensional Artin reps, or non-modular-form L-functions, the Sato-Tate conjecture is open. `st_group` values in those families are conjectural, and LMFDB flags / documentation should be consulted before treating them as ground truth.
- **Confusing `st_group` with `st_label`.** `st_group` is the Lie group; `st_label` is the finer rational classification (different `st_label` values within the same `st_group` encode different component-group structures). Using one when the analysis needs the other silently loses information.
- **Small-n exotic-class extrapolation.** Genus-2 exotic classes (E_1..E_6, J(C_n), D_{n,k}) have counts in single digits to low tens. Any claim about exotic-class-specific behavior requires explicit `n` reporting; otherwise it is Pattern 4 / F012-Liouville noise inflation.
- **Treating `P037` and `P028` as independent cross-axes on the same family.** They are different sides of the same proved-theorem correspondence; joint independence is double-counting.

**When to use:**
- **Any genus-2 analysis** — `P037` is the primary non-conductor, non-rank axis available, and the 95.4% `USp(4)` / 3.7% split-Jacobian imbalance means pooled g2c is effectively a `USp(4)` analysis with noise.
- **CM vs non-CM EC questions** — preferred over raw `P025` only when the Lie-group framing is natural; otherwise `P025` is the cheaper boolean.
- **Cross-side calibration against Katz-Sarnak `P028`** — `P037` (a_p side) and `P028` (zero side) should agree on family-type assignments up to classical correspondences.
- **Moment-deviation probes** — any `⟨(a_p/2√p)^k⟩` measurement at finite conductor is testing Sato-Tate finite-N structure; stratify by `P037` at the start.

**When NOT to use:**
- **Jointly with `P025` CM on EC-only data** (full aliasing).
- **Jointly with `P028` on the same family as if orthogonal** (nested via classical theorem).
- **For non-EC, non-g2c, non-MF families without verifying Sato-Tate is proved** there.
- **As a claim-driver for exotic g2c classes with n < 100** — pre-commit to sessionB's Liouville discipline.

**Related projections:**
- **P022 aut_grp stratification (g2c-specific):** orthogonal in principle; joint `P037 × P022` is the natural g2c family-structure coordinate pair. F012 (H85 killed) was at `P022`; could re-examine within `USp(4)` vs split-Jacobian strata.
- **P025 CM:** aliased on EC; strictly refined by `P037` on higher-genus families.
- **P028 Katz-Sarnak:** cross-side correspondence via proved classical theorems.
- **P031 Frobenius-Schur Indicator:** on Artin-origin L-functions, jointly determines Sato-Tate group.
- **P036 Root number:** via rank parity and SO_even/SO_odd, forms a chain `P037 → P028 → P036 → P023`.

**Follow-ups this entry motivates:**
1. `build_idx_lfunc_st_group` — a functional index on `lfunc_lfunctions.st_group` (Mnemosyne) would unblock EC Sato-Tate queries; currently the full scan with origin prefix is 30s+.
2. `calibrate_F_ec_cm_stgroup_identity` — verify `cm != 0 ⇔ st_group = N(U(1))` across all 2.48M EC. Candidate calibration anchor (F008 or whichever is free).
3. `wsw_F012_restricted_USp4` — re-run F012 Möbius × aut_grp audit restricted to `USp(4)` g2c (excluding split Jacobians and exotic classes). The killed signal may have had structure hidden inside the 95.4% `USp(4)` cohort that the pooled-across-st_group aut_grp stratification missed.
4. `wsw_F011_stratified_stgroup` — test whether F011's GUE deficit also shows structure across `P037` classes (for EC, this is near-trivial by aliasing with P025, but for MF / Dirichlet it is a genuine refinement).
5. `catalog_st_label_sister` — document `st_label` as a sister finer-granularity axis to `P037`, with explicit `P037 ⊃ P037_st_label` nesting in tautology profile.

*End of draft.*
