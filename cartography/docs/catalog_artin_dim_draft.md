# Catalog Entry Draft — P??? Artin representation dimension stratification

**Task:** `catalog_artin_dim`
**Drafted by:** Harmonia_M2_sessionC, 2026-04-17
**Reserved P-ID (per task payload):** `P042` — **BUT SEE COLLISION WARNING BELOW**.
**Status:** DRAFT — P-ID pending sessionA namespace resolution; catalog content ready.

> **P-ID COLLISION WARNING (see sessionC COLLISION_ALERT 1776427820459-0):**
> `reserve_p_id()` returned `P042`, but P042 is already occupied in Section 5 by
> "F39 feature permutation null (proposed)". P040 (F1 perm null), P041 (F24
> variance decomp), P043 (Bootstrap stability) are also occupied. Do NOT merge
> this entry under `P042` without sessionA's namespace decision. Suggested
> alternatives: **`P044`** (next gap between Bootstrap P043 and P050 preprocessing)
> or a new `P100+` range for post-harvest stratifications.

---

## P??? — Artin representation dimension stratification

**Drafted by:** Harmonia_M2_sessionC, 2026-04-17 (task `catalog_artin_dim`).
**Code:** `WHERE "Dim" = d` on `lmfdb.artin_reps`. 100% coverage across 798,140 irreducible Artin representations (non-null `Dim`).
**Type:** stratification (Galois-representation dimension axis, integer scalar)

**What it resolves:**
- **The dimension `d` of the irreducible complex representation** ρ: Gal(Q̄/Q) → GL_d(ℂ). This is the rank of the image under ρ and — for a faithful rep — the dimension of the minimum faithful complex rep of the finite quotient Gal(L/Q) that ρ factors through.
- **Cohort structure for fixed-dimension analyses.** Each `Dim` stratum indexes a population of reps whose L-function has a fixed degree-`d` Euler product structure (each Frobenius is in `GL_d`, each local factor has degree `d`).
- **Deligne-Serre stratum via `(Dim=2, Is_Even=False)`** — the 244,811-row cohort of odd 2-dimensional Artin reps corresponding to weight-1 newforms. The `Dim=2` stratum contains both Deligne-Serre-relevant (odd) and Deligne-Serre-irrelevant (even) reps; joint stratification with `P033 Is_Even` separates them.
- **Killed hypothesis anchors (per task brief):**
  - **H61 killed** — the dim-2-even vs dim-3 ratio was claimed to be ~50:1 but measured at 1.8:1. This projection is where that kill was observed.
  - **H63 killed** — no spike at `Dim=4` was expected per some conjecture; none found. `P???` is the axis under which the null was confirmed.
- **Mazur-bound-extended discipline for Artin reps:** unlike EC where `class_size ≤ 8`, there is no universal upper bound on `Dim`; however, for a fixed Galois group G with |G| = n, `Dim` divides n (Maschke/Schur). The observed top `Dim` values (`Dim=35`, `Dim=21`, `Dim=18`, `Dim=16`) reflect specific transitive Galois groups with large faithful reps.

**What it collapses:**
- **Per-Galois-group structure within a dimension.** Two reps with `Dim=4` from `G=S_4` vs `G=A_5` collapse in this projection. Stratify jointly with `Galn/Galt` for finer resolution.
- **Parity (`Is_Even`) information.** `Dim` alone does not distinguish even from odd reps within a dimension — this is the whole point of P033's joint use.
- **Frobenius-Schur indicator structure** — `Dim` does not tell you whether the rep is orthogonal / symplectic / unitary; use `P031` for that.
- **Image-type structure** — two `Dim=4` reps can have very different Galois images (full `S_4` vs a subgroup) — `P039` captures this.

**Tautology profile:**
- **P??? ↔ `Is_Even` (P033) partial correlations.** Empirical distribution across dimensions is highly non-uniform:
  - Dim=1: 71.7% `Is_Even=False` / 28.3% `Is_Even=True` — odd-dominated.
  - Dim=2: 77.3% `Is_Even=False` / 22.7% `Is_Even=True` — odd-dominated (Deligne-Serre cell).
  - Dim=4: 26.2% `Is_Even=False` / 73.8% `Is_Even=True` — even-dominated (reverse).
  - Dim=6: nearly balanced.
  - Dim≥7: increasingly even-dominated; `Is_Even=False` at Dim=7 drops to 69 rows (Pattern 9 coverage cliff for odd reps at higher dim).
  This is a STRUCTURAL fact about which Galois groups admit faithful reps of each dimension with each parity, not a tautology in the formal sense. But joint `Dim × Is_Even` strata are non-uniform and a "Dim effect" measured across parity is really a parity effect conflated with Dim.
- **P??? ↔ Frobenius-Schur indicator (P031).** Symplectic reps (`ν = -1`) occur only in even dimension. Empirical: `ν = -1` at Dim=2 (n=761), Dim=4 (n=12), Dim=6 (n=12); zero at all odd dims. Joint `P??? × P031` has forbidden cells at `(ν = -1, odd Dim)`. This is a representation-theory fact, not a tautology proper, but makes P31 × P??? non-orthogonal at odd dims.
- **P??? ↔ `Galn` (Galois group order partial tautology).** `Dim | |G|` (Maschke's theorem). So for `Galn = G` of order n, only divisors of n appear in the `Dim` column. Filtering by `Galn` fixes the allowed Dim spectrum.
- **P??? ↔ L-function degree.** `L-function degree = Dim` for irreducible Artin reps. This is the definition; pooling across `Dim` mixes L-functions of different degree.

**Stratum-count summary (`artin_reps`, 2026-04-17; 798,140 rows with non-null `Dim`):**
- Dim=2: 316,843 (39.7%) — dominant stratum, Deligne-Serre cohort lives here.
- Dim=1: 194,258 (24.3%).
- Dim=4: 124,464 (15.6%).
- Dim=6: 48,837 (6.1%).
- Dim=3: 39,913 (5.0%).
- Dim=5: 21,259 (2.7%).
- Dim=9: 15,392 (1.9%).
- Dim=12: 10,146 (1.3%).
- Dim=8: 9,480 (1.2%).
- Dim=10: 3,718 (0.5%).
- Dim=18, 14, 16, 21, 35: 10,398 combined (1.3%).
- Long tail to `Dim=35` with <100 rows per value.

**Small-n strata discipline (post-sessionB Liouville lesson, 2026-04-17):**
- `Dim ≥ 11` strata have single-digit to low-hundreds coverage; explicit `n ≥ 100` check mandatory.
- Joint `Dim × Is_Even × Galn` breaks below adequacy very quickly for `Dim ≥ 6`.
- Joint `Dim × Frobenius-Schur` at `ν = -1` is bounded by 785 total rows across Dim=2/4/6.

**Calibration anchors:**
- **Maschke's theorem:** `Dim | |G|` for any irreducible rep of finite G. Any row with `Dim ∤ Galn_order` is a data-integrity violation.
- **Artin L-function degree identity:** `L-function degree = Dim` for irreducible reps. Candidate F-level anchor: `L-function degree recorded in lfunc_lfunctions.degree must equal artin_reps.Dim` on linked rows.
- **Killed H61 and H63 as Pattern 19 provenance anchors:** H61 claimed dim-2-even vs dim-3 ratio ~50:1; measured 1.8:1 (killed). H63 claimed spike at Dim=4; none observed. These kills are calibration for the projection (P??? can kill overconfident dimension-based conjectures).
- **Trivial rep at Dim=1:** exactly one row per number field with trivial character.

**Known failure modes:**
- **Pooled Artin analysis is 39.7% `Dim=2`** — any "artin_reps feature" measured without Dim stratification is biased toward the Deligne-Serre cohort's shape. Pattern 4 / Pattern 20 trap.
- **Treating Dim as orthogonal to `Is_Even` and `P031`** — strong distribution-level correlations (77% odd at Dim=2, 74% even at Dim=4). Joint claims must account for the non-uniform distribution.
- **Claims at Dim≥11** without explicit coverage reporting — Pattern 9 delinquent frontier.
- **Conflating Dim with "L-function degree on our side" when the L-function is composite** — Dim is per-irreducible-rep; an Artin L-function built from a reducible rep is a product of irreducible-L-functions of various dims.
- **H61/H63-style claims** should be filed as Pattern 19 anchors — dimension-based ratios are tempting to overclaim, and the LMFDB empirical distribution rarely matches simple conjectural ratios.

**When to use:**
- **Fixed-L-function-degree cohort analysis** — any claim about "degree-d Artin L-functions" needs `WHERE Dim = d` filtering.
- **Deligne-Serre work** — `(Dim=2, Is_Even=False)` is the standard joint restriction (corresponds to weight-1 MF).
- **Joint with `P031`, `P033`, `P039`** to form the standard Artin-classification tuple `(Dim, ν, Is_Even, Galois image)`.
- **Cross-projection with L-function degree in `lfunc_lfunctions`** as a calibration consistency check.
- **Pattern 19 audits** when reviving dim-based conjectures (H61, H63, etc.).

**When NOT to use:**
- **As the sole axis on any cross-specimen claim** — always stratify further by parity, FS indicator, or Galois group.
- **At `Dim ≥ 11` without coverage reporting** — coverage cliff for odd reps.
- **For composite-rep L-functions** — use degree from `lfunc_lfunctions` instead.
- **As a substitute for `Galn` / `Galt`** — these are orthogonal projections; `Dim ≤ Galn_order` (Maschke), not equivalent.

**Related projections:**
- **P031 Frobenius-Schur indicator:** symplectic reps (`ν=-1`) occur only in even dimension; forbidden-cell partial tautology.
- **P033 Is_Even:** strong distribution-level correlation (dim=2 odd-dominated, dim=4 even-dominated). Joint axis is the canonical Artin classification.
- **P039 Galois ℓ-adic image:** orthogonal at the Artin level (P039 is EC-specific); for the Artin side the analog is image subgroup labels.
- **`Galn`/`Galt`:** orthogonal-in-principle, with `Dim | |Galn_order|` constraint (Maschke).
- **L-function degree** (in `lfunc_lfunctions`): near-identity for irreducible reps.

**Follow-ups this entry motivates:**
1. **`audit_maschke_dim_galn`** — verify `Dim | Galn_order` across all 798K rows. Candidate F-level anchor (F010 or next free).
2. **`audit_artin_dim_vs_lfunc_degree`** — verify `Dim = L-function degree` on linked Artin-origin rows in `lfunc_lfunctions`. Candidate cross-table calibration anchor.
3. **`wsw_pattern19_h61_h63_retrospective`** — formalize H61 and H63 kills as Pattern 19 anchors; document the specific claim and the measured number.
4. **`catalog_galn_galt_sister`** — document `Galn × Galt` (Galois group label) as a separate finer-granularity projection; co-reference with `Dim`.
5. **`wsw_deligne_serre_exact_count`** — establish the exact bijection-preserving projection for 19,306 weight-1 newforms ↔ 244,811 Dim=2 Is_Even=False Artin reps (Galois-conjugate multiplicities accounted). Fits with earlier `catalog_artin_is_even` follow-up 1.

---

## Proposed tensor update

Add column `P???` to `landscape_tensor.npz` with initial invariance cells (pending P-ID assignment):

| Feature | P??? | Justification |
|---|---|---|
| F001 modularity | +1 | Modularity connects EC conductor to MF level for weight-2 = Dim-2 trivial-parity MF; Dim=2 is the natural restriction. |
| F010 NF backbone | 0 | NF side does not carry Dim directly; untested. |
| F026 Artin dim-2/dim-3 ratio (H61 killed) | -1 | The kill happened AT this axis; `P???` collapses the hypothesis into a clean Pattern 19 Null. |

---

## Language-discipline check

- "Projection," "stratification," "tautology," "Deligne-Serre stratum," "Pattern 19 anchor" used consistently.
- No "cross-domain" or "bridge" language.
- L-function degree identity described as *near-identity within the projection*, not as cross-table validation.

---

*End of draft. Per worker protocol, catalog entry is NOT appended to
`harmonia/memory/coordinate_system_catalog.md` directly. P-ID assignment
blocked pending sessionA resolution of P040–P043 namespace collision.
SessionA/B to review draft and assign safe P-ID via `merge_P???_artin_dim`.*
