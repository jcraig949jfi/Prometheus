# Catalog Entry Draft — P031 Frobenius-Schur Indicator stratification

**Task:** `catalog_artin_indicator`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 4)
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Proposal:** insert under Section 4 (Stratifications) immediately after P028 Katz-Sarnak (sessionB) with which it is theoretically paired.

*ID path: drafted at P031 (tick 4). Briefly renumbered to P032 (tick 6) after a short-lived collision with sessionB's character parity. sessionA ID_ASSIGNMENT 1776424150490-0 (tick 7) restored P031 to this entry (APPROVED as drafted); sessionB's character parity is now P032. Current: **P031**.*

---

## P031 — Frobenius-Schur Indicator stratification

**Code:** `WHERE "Indicator" = v` on `lmfdb.artin_reps` (indexed via `idx_artin_dim_conductor`; Indicator itself is unindexed — add `idx_artin_indicator` if this becomes a hot path)
**Type:** stratification (symmetry / self-duality axis, classical representation theory)

**What it resolves:**
- **Self-duality and symmetry type of a complex irreducible representation.** For an irreducible character χ of a finite group, the Frobenius-Schur indicator ν(χ) ∈ {-1, 0, +1} classifies:
  - `+1` — χ is the complexification of a real (orthogonal) representation — fixes a symmetric bilinear form.
  - `-1` — χ is quaternionic (symplectic) — fixes an alternating bilinear form.
  - ` 0` — χ is not self-conjugate (complex type in the reality sense).
- **Expected L-function symmetry type** for the Artin L-function attached to the rep. The Katz-Sarnak symmetry type (`P028`) follows directly from ν via:
  - `ν = +1` with `Is_Even = True`  → `SO_even` family.
  - `ν = +1` with `Is_Even = False` → `SO_odd`  family.
  - `ν = -1`                        → `Sp`        family.
  - `ν = 0`                         → `U`         family.
  This is the arithmetic companion of `P028`'s random-matrix classification.
- **Whether the rep descends to a real form**, which matters for base-change arguments and for selecting out the self-dual subfamily in cross-specimen analyses.

**What it collapses:**
- **Within-indicator distinctions.** Two `ν = +1` reps of different dimensions, different Galois groups, different conductors all map to the same stratum. Use `P031` as a coarse symmetry filter; stratify further by dimension or Galois label when needed.
- **Representation content beyond symmetry.** The full character values are lost; only the self-duality class survives.
- **The `Is_Even = False` ⇒ `ν ≠ -1` forbidden cell** makes joint `P031 × Is_Even` non-orthogonal (see tautology profile below).

**Tautology profile:**
- **`P031` ↔ `Is_Even` (partial tautology, asymmetric).** Empirical from `artin_reps` (798,140 rows, 2026-04-17):
  - `Is_Even = False`: 478,851 rows — all `ν ∈ {0, +1}` — no `ν = -1` (symplectic reps are even by definition).
  - `Is_Even = True`:  319,289 rows — `ν ∈ {-1, 0, +1}` distributed (785 / 14,865 / 303,639).
  The implication `ν = -1 ⇒ Is_Even = True` is a representation-theory fact, not a finding. Joint `P031 × Is_Even` has forbidden cells; do not treat the axes as independent without accounting for this.
- **`P031` ↔ `Dim` (partial tautology).** Symplectic reps occur only in even dimension. Empirical distribution of `ν = -1`: Dim=2 (761), Dim=4 (12), Dim=6 (12); zero at all odd dims. Joint `P031 × Dim` has forbidden cells at (`ν = -1`, odd Dim).
- **`P031` ↔ `P028` Katz-Sarnak (near-redundancy).** Per the symmetry-type map above, `P031` plus `Is_Even` determines `P028` exactly in the Artin case. Applying both axes independently is double-counting; within the Artin family, one is a rename of the other. `P028` extends to families beyond Artin (quadratic twists, Dirichlet, etc.) where `P031` does not apply — outside Artin, the two are genuinely distinct.

**Stratum-count summary (live `artin_reps` query, 2026-04-17):**
- `ν = +1` (orthogonal / real): 768,164 (96.3%)
- `ν = 0` (complex / non-self-dual): 29,191 (3.7%)
- `ν = -1` (symplectic): 785 (0.1%)
- Total: 798,140 irreducible reps.

**Small-n strata discipline (post-sessionB Liouville lesson, 2026-04-17):**
- Joint `P031 × Dim × Is_Even` strata quickly drop below `n = 100` for `ν = -1` (785 total symplectic reps distributed across Dim = 2 / 4 / 6 at 761 / 12 / 12).
- sessionB's `liouville_side_check_F012` demonstrated that small-n strata produce spurious `|z|` under normal-approximation tests (Pattern 19 candidate: "tensor-entry staleness via small-n stratum inflation"). Enforce `n ≥ 100` per adequate stratum at entry time, not as an optional reporting caveat. For `ν = -1` jointly with any other axis, effective adequacy is capped by 785.
- For `ν = 0` (29,191 rows), joint with Dim gives useful strata at Dim ≤ 6 (sum ~26,000) and drops rapidly beyond.
- For `ν = +1`, most joint strata are adequate; this is the "default stratum" that dominates pooled analysis by 96%.

**Calibration anchors:**
- **Frobenius-Schur identity.** For a finite group G and its character table: ∑_χ ν(χ) · χ(1) = #{g ∈ G : g² = 1}. Any implementation that disagrees numerically on a small test group (S₄, Q₈, D₄) is broken.
- **Dimension-1 reps are self-dual with ν ∈ {0, +1} only** (a 1-dim rep cannot be symplectic). Empirical: 194,258 dim-1 reps in `artin_reps`; zero at `ν = -1`. Holds.
- **Q₈ (quaternion group) has a unique 2-dim irreducible at `ν = -1`.** This is the textbook example for symplectic reps and should appear in `artin_reps` for the relevant Galois label.
- **Cross-projection to `P028` on the Artin slice** (see tautology): `ν = +1, Is_Even = False` must match `SO_odd` assignment; any row where these disagree flags a data-quality issue.

**Known failure modes:**
- **Pooled analysis by `Indicator` is effectively a `ν = +1` analysis.** 96.3% of the rows carry `ν = +1`; any "artin_reps feature" measured without `P031` stratification is reporting the `ν = +1` stratum by default. This is a Pattern 4 sampling-frame trap with `P031` hidden inside the pool.
- **Treating `P031 × Is_Even` as orthogonal** reintroduces the forbidden-cell tautology. Observed empirical probability of `ν = -1 | Is_Even = False` = 0; treat as structural constraint, not sampling noise.
- **Small-n at `ν = -1`.** Any test stratified at the `ν = -1` level cannot extrapolate beyond the 785-rep subpopulation. Pattern 9 (delinquent frontier) applies when higher-dimensional symplectic reps are needed — they do not exist in the data.

**When to use:**
- **Cross-projection calibration with `P028`** (Katz-Sarnak) for Artin-type L-functions: `P031` + `Is_Even` → `P028` map is a hard calibration anchor. Both sides must agree on every row.
- **Filtering to self-dual reps** (drop `ν = 0`) before applying tools that assume self-duality (e.g., real-coefficient L-function moment conjectures).
- **Probing the symplectic frontier.** The 785 `ν = -1` reps are a narrow, textured subfamily worth its own walk (Pattern 16 — obscure, well-defined, likely unmapped).
- **Joint with `Dim`** when dimension-specific symmetry effects are at stake (e.g., dim-2 orthogonal-vs-symplectic split relevant to certain modular lifts).

**When NOT to use:**
- **Alongside `P028` on the Artin slice as independent axes.** Pick one. `P028` is more portable (works beyond Artin); `P031` is the raw LMFDB column and cheaper to query.
- **As the sole axis** for any cross-projection claim. The 96.3% `ν = +1` dominance means the signal will usually be a `ν = +1` signal regardless. Always stratify within Indicator to extract non-pooled structure.
- **For dim-1 reps** — the three-valued axis collapses to two (`ν ∈ {0, +1}` only); dim-specific stratification is more informative here.

**Related projections / edges in the projection graph:**
- **`P028` Katz-Sarnak (sessionB) — near-redundancy for Artin**. Proposed edge: `P031 --[is_arithmetic_companion_of]--> P028` with note: "on the Artin slice, `P031 + Is_Even` → `P028` exactly; distinct outside Artin."
- **`P027` ADE-type (via Galois label)** — heuristic proxy, not a direct companion. `P031` is the cleaner self-duality axis; `P027` was a killed hypothesis for F011 resolution.
- **`Is_Even`** is not itself a catalogued projection yet but should be — it is a primitive parity axis used jointly with `P031` and `P028`. Candidate P031 or later.

---

## Proposed tensor update

Add column P031 to `landscape_tensor.npz` with the following initial invariance cells (others remain 0 = not tested):

| Feature | P031 | Justification |
|---|---|---|
| F010 NF backbone | 0 | Artin side is the coupling partner; worth an explicit test. `ν` could sharpen or kill the F010 signal if the Artin reps entering the ρ=0.40 regime are all `ν = +1` by selection. |
| F026 Artin dim-2/dim-3 (H61 killed) | 0 | H61 used `Dim`; adding `P031` as joint stratification is a candidate re-check (was there a `ν`-mediated effect inside the pooled dim-2 count?). |

---

## Language-discipline check

- "Projection", "resolves", "collapses", "stratification", "invariance", "self-dual" used consistently.
- No "cross-domain" or "bridge" language.
- Described `P031`↔`P028` as projections with a theoretical correspondence *on the Artin slice*, not as bridges between domains.

---

## Follow-ups this entry uncovered

1. **`Is_Even` is not catalogued.** It is a primitive binary axis used everywhere in Galois-rep analysis, jointly with `P031` and `P028`. File as the next catalog entry (candidate P031 or whichever is free).
2. **Build `idx_artin_indicator`** (single-column B-tree). `P031` stratification without this index does a full scan of 798K rows per query; trivial to add.
3. **Symplectic Artin reps are a Category-3 specimen candidate** (Pattern 16). 785 rows at `ν = -1`, concentrated in Dim ∈ {2, 4, 6}, likely contain structure that is invisible in pooled Artin analysis.
4. **`P031`↔`P028` cross-check as calibration** — for every Artin-origin L-function, `ν + Is_Even` must match the `symmetry_type` column in `bsd_joined`/`lfunc_lfunctions`. Any disagreement flags a data-quality issue (candidate calibration anchor `F006` once verified).
5. **sessionB Pattern 19 reinforcement.** The 785-count of `ν = -1` is an immediate application of the small-n discipline sessionB demonstrated this session — any `ν = -1` finding without explicit `n_per_stratum` reporting should be treated as provisional.

*End of draft.*