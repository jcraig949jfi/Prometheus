# Catalog Entry Draft — P040 Isogeny class size stratification

**Task:** `catalog_isogeny_class_size`
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Reserved P-ID:** `P040` (pre-reserved in task payload).
**Status:** DRAFT — awaiting sessionA/B review before merging.
**Proposal:** insert under Section 4 (Stratifications) after P039 Galois ℓ-adic image (sessionD) and before Section 5, once P039 merge lands.

---

## P040 — Isogeny class size stratification

**Code:** `WHERE class_size = k` on `lmfdb.ec_curvedata`. 100% coverage across 3,824,372 EC rows. Values are members of `{1, 2, 3, 4, 6, 8}` for non-CM curves (Mazur's bound on rational cyclic isogenies); CM curves follow the same bound structure with slightly different attainable sets. Paired data: `isogeny_degrees` (array of all `d` such that an isogeny of degree `d` exists from this curve to another curve in its class) — `class_size = len(isogeny_degrees)` by construction.
**Type:** stratification (algebraic axis, finite-group-bounded)

**What it resolves:**
- **Isogeny-equivalence class membership.** Members of the same Q-isogeny class share the same L-function (hence the same `analytic_rank`, root number, local factors at all primes). `P040` picks which class-size bucket a curve sits in.
- **Q-rational cyclic-isogeny structure at the object level.** Each size bucket corresponds to a distinct shape of the isogeny graph: size 1 = isolated, size 2 = single 2-isogeny pair, size 4 = `[1,2,4]` linear chain or `[1,2]²` star, etc.
- **Cross-projection anchor for P024 torsion.** Isogenies act on rational torsion; each isogeny degree in `isogeny_degrees` corresponds to a rational cyclic subgroup. Curves with larger class sizes tend to have torsion containing cyclic subgroups of the listed degrees.
- **Cohort for L-function-invariance tests.** Any signal claimed per-curve that varies within a single isogeny class implies either an error in the measurement or a non-L-function-derived feature.

**What it collapses:**
- **Per-curve structure within a class.** Four curves in an isogeny class of size 4 share the L-function and hence many derived features, so pooled-by-class measurements hide the intra-class variation in non-L-function features (e.g., `faltings_height`, `regulator`, explicit Weierstrass coefficients).
- **The SHAPE of the isogeny graph beyond its size.** `class_size = 4` can be `[1,2,4]` (linear chain) or involve `[1,2,2]` (star). The coarse size number loses this structure; use `isogeny_degrees` for finer resolution.
- **Degree-of-individual-isogeny information.** `class_size` is a cardinality; the individual isogeny degrees (2, 3, 5, 7, 11, 13, 37, etc.) are only recoverable via `isogeny_degrees`.

**Tautology profile:**
- **P040 ↔ `isogeny_degrees` (strict near-identity).** `class_size = len(isogeny_degrees)` by construction. `isogeny_degrees` is the finer projection; `P040` is the cardinality summary. Independent use of both risks double-counting.
- **P040 ↔ L-function invariants (analytic_rank, root number, conductor, local factors).** All members of an isogeny class share the same L-function → stratifying by `class_size` while also using `analytic_rank` or root number as a response variable does not reveal class-size structure in those variables (they are invariant within class by definition).
- **P040 ↔ P024 Torsion.** Isogeny degree `d` rational cyclic isogenies correspond to rational subgroup structure. Curves with `isogeny_degrees ∋ d` admit a rational `d`-torsion-like structure (though not always `d`-torsion proper — could be a quotient). Partial tautology: `class_size ≥ 2` implies *some* rational cyclic subgroup exists.
- **P040 ↔ P039 Galois ℓ-adic image (sessionD).** A rational cyclic isogeny of degree `d = ∏ p_i^{e_i}` forces each `p_i` into `nonmax_primes`. Therefore `class_size ≥ 2` implies `nonmax_primes ≠ []`. Partial tautology — P040 refines P039 at each non-maximal prime.
- **P040 ↔ P025 CM.** CM curves have distinguished isogeny structure: the endomorphism ring is larger than Z, so isogeny classes can be structurally distinct from non-CM classes. Stratifying by `P040 × P025` jointly is orthogonal in principle but the CM subfamily (~5K rows) has small-n strata issues at every `class_size > 1`.
- **P040 ↔ P022 aut_grp (EC-only concept).** For EC, aut_grp is usually trivial `{±1}`; rarely larger for CM curves. The aut_grp-isogeny interaction is not a tautology but joint coverage is sparse.

**Stratum-count summary (100% coverage across 3,824,372 EC rows):**
- `class_size = 1` (isolated): 2,244,844 (58.70%) — dominant stratum.
- `class_size = 2`: 1,120,652 (29.30%).
- `class_size = 4`: 391,176 (10.23%).
- `class_size = 6`: 37,512 (0.98%).
- `class_size = 3`: 20,628 (0.54%).
- `class_size = 8`: 9,560 (0.25%).
- Mazur-bound: `class_size ∈ {1, 2, 3, 4, 6, 8}` exhausts the observed values. No `class_size = 5, 7, ≥ 9`.
- Top `isogeny_degrees` values: `[1]` (58.70%), `[1,2]` (25.67%), `[1,2,4]` (7.15%), `[1,3]` (5.41%), `[1,2,3,6]` (1.07%), `[1,2,4,8]` (0.66%).

**Small-n strata discipline:**
- `class_size = 8` is the smallest non-CM stratum at 9,560 rows; still adequate for most analyses but drops fast when joint-stratified.
- Joint `P040 × P023 rank` at `rank ≥ 3` within any `class_size > 2` stratum quickly drops below `n = 100`. Rank ≥ 4 with any non-trivial class is <100 curves total.
- Joint `P040 × P024 torsion ≥ 4` × `class_size ≥ 4`: small; check before publication.
- Joint `P040 × P025 CM` breaks at `class_size ≥ 2` in CM subfamily (<50 curves per bucket).

**Calibration anchors:**
- **Mazur's theorem on rational torsion + Kenku-Momose-Parent ℓ-adic image bound** (proved): `class_size` for non-CM EC over Q is bounded by 8; attainable values are `{1, 2, 3, 4, 6, 8}`. A non-CM curve with `class_size = 5, 7, 9+` is a data corruption signal.
- **L-function invariance within isogeny class** (trivial consequence of isogeny): `analytic_rank`, `root_number`, `conductor` are invariant within class. Any disagreement is a data-quality violation.
- **`class_size = len(isogeny_degrees)`** must hold row-by-row. Implementation spot-check.
- **`class_deg` matches isogeny-graph traversal degree** — for the optimal curve, `class_deg` is the total degree of the Q-isogeny class as a degree of covering. Related to but distinct from `class_size`.

**Known failure modes:**
- **Pooled analysis with 58.7% `class_size = 1`**: the trivial stratum dominates any unfiltered per-curve analysis. Pattern 4 / Pattern 20 trap.
- **Stratifying by `P040` AND using L-function-derived features as response** (root number, analytic rank) gives zero variance within stratum by construction → misleading "perfect stratification." Not a finding.
- **Treating `class_size` and `isogeny_degrees` as independent axes** (near-identity).
- **Inferring torsion structure from `class_size` alone.** Class size says there's *some* rational cyclic subgroup; doesn't specify which torsion points it hits. For torsion analysis use `P024` directly.
- **CM subfamily small-n** at joint-stratification — explicit coverage reporting mandatory (Pattern 9).
- **Missing Mazur-bound audit.** Any fresh EC ingestion should check `class_size ∈ {1, 2, 3, 4, 6, 8}` for non-CM rows; violations flag upstream data quality.

**When to use:**
- **Q-rational cyclic isogeny structure** when analyzing EC-family structure at the object level.
- **L-function-equivalence cohort analysis** — filter to unique classes (e.g., one representative per class) to avoid over-counting L-functions. `WHERE class_size = 1 OR lmfdb_number = '1'` picks the optimal-curve-per-class cohort.
- **Cross-projection with P039 Galois ℓ-adic image** — `class_size ≥ 2` ⇔ non-trivial `nonmax_primes`; joint usage locates where the non-maximality manifests.
- **Pattern 16 Category-3 candidates** — small exotic strata (`class_size = 3, 6, 8`) are under-studied compared to `class_size = 1, 2`; worth a walk.
- **Mazur-bound spot-checks** on EC data imports.

**When NOT to use:**
- **Alongside L-function-derived response variables** (circular; root number and analytic rank are class-invariant by definition).
- **Jointly with `isogeny_degrees` as if orthogonal** — near-identity.
- **As a torsion proxy without `P024` cross-check** — `class_size` is not torsion.
- **For CM subfamily fine stratification** without explicit coverage (small-n).
- **On non-EC objects.** `class_size` is EC-specific; MF isogeny classes exist but live in `mf_newforms.is_twist_minimal` / related columns, not here.

**Related projections:**
- **P024 Torsion stratification:** partial tautology at `class_size ≥ 2` (rational cyclic subgroups). Standard joint axis for "torsion plus isogeny" analyses.
- **P039 Galois ℓ-adic image (sessionD):** partial tautology — `class_size ≥ 2` ⇒ `nonmax_primes ≠ []`. P040 refines P039 at each non-maximal prime.
- **P025 CM vs non-CM:** orthogonal-in-principle, small-n in CM cohort for joint stratification.
- **P023 Rank:** independent axis; useful for rank-per-class-size analyses (all class members share rank).
- **`class_deg` column:** related finer-granularity — total degree of the isogeny class as a covering; distinct from class cardinality.
- **`isogeny_degrees` column:** direct finer projection (tautology-partner).

**Follow-ups this entry motivates:**
1. **`audit_mazur_bound_class_size`** — verify `class_size ∈ {1, 2, 3, 4, 6, 8}` for all non-CM `ec_curvedata` rows. Any violation is a data-quality signal (candidate F-level anchor).
2. **`wsw_F003_by_P040`** — re-examine the F003 BSD-parity calibration anchor stratified by `class_size`. Expected: anchor holds exactly within each stratum by isogeny invariance; Pattern 7 spot-check.
3. **`catalog_isogeny_degrees_sister`** — document `isogeny_degrees` as a sister finer-granularity axis with explicit nesting tautology note.
4. **`catalog_class_deg_sister`** — document `class_deg` as a distinct concept (isogeny-class covering degree, not cardinality).
5. **`wsw_category3_class_size_3_6_8`** — Pattern-16 candidate walk on the rare `class_size = 3, 6, 8` strata (small but texture-rich).
6. **L-function invariance audit** (`audit_class_size_Linv`) — verify `analytic_rank`, `root_number`, `conductor` agree within every isogeny class. Disagreements flag upstream data issues.

---

## Proposed tensor update

Add column `P040` to `landscape_tensor.npz` with initial invariance cells:

| Feature | P040 | Justification |
|---|---|---|
| F003 BSD parity | +1 | Anchor holds within each isogeny class by L-function invariance; P040 stratification should leave F003 anchor unchanged. |
| F005 High-Sha parity | 0 | High-Sha cohort may concentrate in specific class sizes; untested. |
| F010 NF backbone | 0 | NF-side specimen; P040 is EC-specific. |
| F011 GUE deficit | 0 | Zero-statistics specimen; P040 tests L-function-invariant features which are expected to hold across class sizes → anchor check, not discovery. |

---

## Language-discipline check

- "Projection," "stratification," "tautology," "isogeny class," "L-function invariance," "Mazur bound" used consistently.
- No "cross-domain" or "bridge" language.
- L-function equivalence within class described as *invariance through the projection*, not as cross-domain linkage.

---

*End of draft. Per worker protocol, catalog entry is NOT appended to
`harmonia/memory/coordinate_system_catalog.md` directly. SessionA/B to
review and merge via `merge_P040_isogeny_class_size` task.*
