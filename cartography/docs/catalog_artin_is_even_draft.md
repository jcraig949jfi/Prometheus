# Catalog Entry Draft — P033 Artin `Is_Even` (parity) stratification

**Task:** `catalog_artin_is_even`
**Drafted by:** Harmonia_M2_sessionD, 2026-04-17 (tick 9)
**Status:** DRAFT — awaiting sessionA/B review before merging into `harmonia/memory/coordinate_system_catalog.md`
**Reserved P-ID:** `P033` (atomically reserved at claim-time via `agora.work_queue.reserve_p_id()` — first use of sessionB's `infra_reserve_p_id` helper).
**Proposal:** insert under Section 4 (Stratifications), immediately after P031 Frobenius-Schur Indicator (sessionD, pending sessionA's P-ID resolution) and before P032 character parity (sessionB, pending).

---

## P033 — Artin `Is_Even` (parity) stratification

**Code:** `WHERE "Is_Even" = <True|False>` on `lmfdb.artin_reps` (no dedicated index; covered by pooled scans or by joint `idx_artin_dim_conductor`).
**Type:** stratification (binary parity axis, Galois-representation parity / determinantal sign)

**What it resolves:**
- **Parity of the Artin representation**, i.e. the sign of `det(ρ(c))` where `c ∈ Gal(Q̄/Q)` is complex conjugation. `Is_Even=True` ⇔ `det ρ(c) = +1`; `Is_Even=False` ⇔ `det ρ(c) = -1`.
- **The Deligne-Serre stratum at (Dim=2, Is_Even=False).** Weight-1 newforms correspond bijectively to odd 2-dimensional Artin representations with `Is_Even=False`. 244,811 such reps in LMFDB — the largest single `Is_Even × Dim` cell.
- **Functional-equation archimedean parity.** Combined with the Frobenius-Schur indicator `P031` (ν), `Is_Even` decides the Γ-factor type at infinity and the SO_even vs SO_odd split on the Artin side (when ν=+1, `Is_Even` picks between SO_even and SO_odd; when ν=-1, symplectic; when ν=0, unitary).
- **Conjugacy of `c`-action.** Since `c²=e`, `Is_Even` is the single bit of information `c` carries; joint with `Dim` it determines the signature of the real form.

**What it collapses:**
- **Any structure not depending on `c`-parity.** Two `Is_Even=True` reps at different dimensions / Galois groups / conductors all map to the same stratum; further stratification by `Dim` and `Galois label` is usually required.
- **The `Is_Even=False` ⇒ ν≠−1 forbidden cell** makes joint `P033 × P031` non-orthogonal (symplectic reps are automatically even).
- **Parity-free features** — anything only depending on the image of ρ without reference to `c`'s image (e.g. the finite group itself, ignoring the embedding of conjugation) is invariant under `Is_Even` and collapses in this projection.

**Tautology profile:**
- **`P033` ↔ `P031` Frobenius-Schur Indicator (asymmetric forbidden cells).** Empirical from `artin_reps`:
  - `Is_Even=False`, ν=−1: 0 rows (symplectic reps are even by definition).
  - `Is_Even=False`, ν=0: 14,326 rows.
  - `Is_Even=False`, ν=+1: 464,525 rows.
  - `Is_Even=True`, ν=−1: 785 rows.
  - `Is_Even=True`, ν=0: 14,865 rows.
  - `Is_Even=True`, ν=+1: 303,639 rows.
  Joint `P033 × P031` has a forbidden cell at `(Is_Even=False, ν=−1)`. Do not treat as independent.
- **`P033` ↔ `P028` Katz-Sarnak (near-redundancy via P031).** On the Artin slice, `P031 + P033` determines Katz-Sarnak symmetry type exactly:
  - ν=+1 AND Is_Even=True → SO_even
  - ν=+1 AND Is_Even=False → SO_odd
  - ν=−1 → Sp (implies Is_Even=True)
  - ν=0 → U
  Applying `P033`, `P031`, and `P028` independently on the Artin slice is triple-counting; pick one or two, not all three.
- **`P033` ↔ `Dim` (statistical, not structural).** Empirical distribution across dimensions is highly non-uniform:
  - Dim=1: False 139,182 (71.7%) / True 55,076 (28.3%) — odd-dominated.
  - Dim=2: False 244,811 (77.3%) / True 72,032 (22.7%) — odd-dominated (Deligne-Serre cell is the bulk).
  - Dim=4: False 32,564 (26.2%) / True 91,900 (73.8%) — even-dominated (reverse of Dim=1/2).
  - Dim=6: nearly balanced (False 26,164 / True 22,673).
  - Dim≥7: increasingly even-dominated; `Is_Even=False` at Dim=7 drops to 69 rows (Pattern 9 / coverage cliff for odd reps at higher dim).
  The Dim=1/2 vs Dim=4+ parity flip is a non-trivial structural fact about the distribution of Galois representations in LMFDB and is not a tautology — it encodes which Galois groups have admissible faithful reps at each dimension with each parity.
- **`P033` ↔ `Dets` (Is_Even is derivable from the Dets field).** The `Dets` column records det ρ as a Dirichlet character; `Is_Even` is the parity of that character at infinity. Treat `Is_Even` as the binary summary of the more detailed `Dets` projection. Any claim using both independently risks double-counting.

**Calibration anchors:**
- **Deligne-Serre bijection.** Weight-1 newforms (MF, P029 with weight=1, 19,306 rows) are in bijection with odd 2-dimensional Artin representations (Dim=2, Is_Even=False, 244,811 rows — many of these are non-rational and are split across Galois conjugates that the weight-1 newform count collapses). Counting mismatch is expected; *bijection-preserving sub-sampling* should recover it.
- **Trivial representation** (1-dim, ρ ≡ 1): det=1 at `c`, so `Is_Even=True`, ν=+1. Should be present exactly once per number field.
- **Sign character.** The non-trivial 1-dim character of `Z/2Z` takes ρ(c)=−1, so `Is_Even=False`, ν=+1. Standard small-group test.
- **Artin-conductor parity.** Even representations have Artin conductor of a specific local-factor signature at infinity; odd representations differ. Any implementation that computes Artin conductor from ρ should be auditable against the `Is_Even` value.

**Small-n strata discipline (post-sessionB Liouville lesson, 2026-04-17):**
- Joint `P033 × Dim` strata drop below `n=100` at `Is_Even=False, Dim=7` (n=69), `Dim=10` (n=108 — just adequate), `Dim=11` (n=27), `Dim=17+` (single digits).
- Joint `P033 × P031 × Dim` strata become sparse faster: ν=−1 has 785 total, concentrated at Dim=2/4/6, so any triple stratification with `Is_Even` drops below adequacy very quickly.
- Enforce `n ≥ 100` per adequate stratum at entry time per sessionB's `wsw_F012` / Liouville lesson (Pattern 19). For any analysis at Dim≥7 odd, explicit coverage reporting is mandatory (Pattern 9 applies: absence of signal may be absence of data).

**Known failure modes:**
- **Pooled artin_reps analysis is 60:40 split toward `Is_Even=False`** (by raw count). This is NOT a false-positive trap by itself (40% is substantial), but any "artin_reps feature" measured without `P033` stratification is silently reporting the weighted average of two structurally different subfamilies. Pattern 4 variant.
- **Dim=2 / Is_Even=False is the Deligne-Serre stratum** — any coupling with weight-1 MF must use this joint restriction. Pooled Dim=2 (across `Is_Even`) includes both Deligne-Serre-relevant (odd) and Deligne-Serre-irrelevant (even, weight-2-flavored or non-modular) reps.
- **`Is_Even` on dim-1 reps is the character parity**, which is uniquely determined by the character itself. Treating `P033` as an independent axis for dim-1 reps is redundant with character-level stratification.
- **Cross-specimen with `P028` Katz-Sarnak:** using `Is_Even` without also accounting for ν gives you "even vs odd" which is NOT the same as "SO_even vs SO_odd" — the latter requires ν=+1 (Pattern 1 family).

**When to use:**
- **Deligne-Serre-oriented analyses** — restrict to Dim=2, `Is_Even=False`.
- **Joint with `P031` and `P028`** to decompose Artin L-functions into Katz-Sarnak symmetry strata at the object level rather than the L-function level.
- **Parity-aware functional-equation analyses** — root numbers, L-value-at-center-point vanishing, local root-number factorizations.
- **Calibration of root-number / ε-factor code** — any implementation that computes functional-equation parity from ρ can be audited against `Is_Even`.

**When NOT to use:**
- **As a sole axis on low-dim reps** — character-level stratification is finer and subsumes parity at Dim=1.
- **Jointly with `P031` AND `P028`** — that's triple-counting on the Artin slice; pick two.
- **For projections of Artin L-functions to the EC world.** On the EC side, "parity" is carried by the root number (which relates to `signD` conceptually, or to Atkin-Lehner via modularity), not `Is_Even`. Do not conflate.
- **Without `Dim` stratification** — the Dim=1/2 vs Dim=4+ reversal means pooled parity splits across Dim and hides structure.

**Related projections / proposed edges in the projection graph:**
- `P033 ↔ P031` — forbidden-cell partial tautology (symplectic ⇒ even).
- `P033 ↔ P028` — via P031, determines Katz-Sarnak symmetry type exactly on the Artin slice.
- `P033 ↔ P029` (MF weight) — cross-tabulates for Deligne-Serre (weight=1 MF ↔ Dim=2 Is_Even=False Artin).
- `P033 ↔ Dets` (the full character field) — Is_Even is the binary summary; `Dets` is the finer projection.

---

## Proposed tensor update

Add column P033 to `landscape_tensor.npz` with the following initial invariance cells (others remain 0 = not tested):

| Feature | P033 | Justification |
|---|---|---|
| F010 NF backbone (via Galois-label) | 0 | Artin-side partner is a candidate test: does the ρ=0.40 signal survive restricting Artin to `Is_Even=False` (Deligne-Serre regime)? Untested. |
| F026 Artin dim-2/dim-3 (H61 killed) | 0 | H61 killed at pooled dim-2; stratifying by `Is_Even` inside dim-2 may resolve. Worth a re-check. |

---

## Language-discipline check

- "Projection", "resolves", "collapses", "stratification", "invariance", "forbidden cell" used consistently.
- No "cross-domain" or "bridge" language.
- Deligne-Serre described as *correspondence visible through the (Dim=2, Is_Even=False) stratum*, not as a bridge between domains.

---

## Follow-ups this entry uncovered

1. **Deligne-Serre count reconciliation** — 19,306 weight-1 MF newforms vs 244,811 Dim=2 Is_Even=False Artin reps. The count mismatch reflects (a) Galois conjugates being separate Artin reps but one weight-1 newform and (b) the primitive/imprimitive distinction. A `wsw` walk establishing the exact bijection-preserving projection would be a high-value calibration candidate.
2. **`Dets` as a standalone catalog entry** — the full character projection is finer than `P033` and deserves its own slot (candidate P034 slot was assigned to AlignmentCoupling by sessionB; `Dets` can take P035 or section-appropriate slot per `infra_reserve_p_id`).
3. **`F010` restricted to Is_Even=False Artin side** — does the NF backbone signal sharpen under Deligne-Serre restriction? One-tick wsw task candidate.
4. **F026 H61 re-examination** — the killed dim-2/dim-3 ratio may have Is_Even structure inside it. Inexpensive re-check.
5. **Pattern 1 tautology-pair table extension** — add `(Is_Even, Dets)` as a partial tautology pair (Is_Even is the boolean summary of Dets' parity character).

*End of draft.*
