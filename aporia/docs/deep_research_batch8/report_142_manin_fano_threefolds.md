# Deep Research Report #142: Manin Conjecture for Fano Threefolds

**Target Agent:** Charon
**Date:** 2026-04-25
**Front:** Diophantine geometry / Batyrev-Manin-Peyre — opens Diophantine front (Batches 5-7 stayed in arithmetic statistics)

## 1. Problem Statement

For a Fano variety X/Q with anticanonical embedding, let U ⊂ X be the open complement of accumulating subvarieties and let H be the anticanonical height. The Batyrev-Manin conjecture predicts

  N_U(B) := #{x ∈ U(Q) : H(x) ≤ B} ~ c · B^a · (log B)^(b−1),  B → ∞,

with **a = 1** (anticanonical exponent) and **b = ρ(X)** (Picard rank). Peyre (1995) refined c to a Tamagawa-type constant

  c_Peyre = α(X) · β(X) · τ_∞(X) · ∏_p τ_p(X),

where α(X) is a volume in the dual of the effective cone, β(X) = #H¹(Gal, Pic(X̄)), and τ_v are local densities. For Fano threefolds the prediction is sharp: a = 1, b = ρ(X) ∈ {1, ..., 10}, and c_Peyre is computable family-by-family. This report tests (a, b) empirically across the Mori-Mukai classification.

## 2. Literature

- **Manin (1989, with Franke-Manin-Tschinkel):** original asymptotic for flag varieties via Eisenstein series.
- **Batyrev-Manin (1990):** general conjecture, log-power = Picard rank conjecture.
- **Peyre (1995, Duke):** Tamagawa interpretation pinning down c.
- **Batyrev-Tschinkel (1996-98):** proved for toric Fano (any dimension) and equivariant compactifications of G_a^n.
- **Chambert-Loir-Tschinkel (2002, 2010):** equivariant compactifications of unipotent groups.
- **Browning, Heath-Brown (2000s):** circle method for cubic surfaces, del Pezzo; Browning's 2009 *Quantitative Arithmetic of Projective Varieties* survey is canonical.
- **Le Rudulier, Derenthal, Loughran:** thin-set obstructions; Peyre's "freedom" refinement (2017).
- **Status for Fano threefolds:** open in general; proved for V_5 (quintic del Pezzo threefold via Manin-Tschinkel), toric subfamilies, P^1 × del Pezzo bundles. The 105 Mori-Mukai families are mostly untested empirically at scale.

## 3. LMFDB Data

Fano threefolds are not a first-class LMFDB object, but bridges exist:

- **`av_fq_search`** (abelian varieties / smooth projective varieties over F_q): smooth proj 3-folds appear via point-count Weil polynomials; useful for local τ_p.
- **`g2c_curves`**: Jacobians of genus-2 curves embed as degenerate Fano-3-fold strata (Kummer threefolds).
- **`nf_fields`**: needed for height computations over number-field bases (skipped here, restrict to Q).
- **External (load into local Postgres):**
  - **Mori-Mukai 1981/82** classification tables (105 deformation families, indexed by (ρ, −K^3, h^{1,2})), e.g. V_22 (Mukai, ρ=1, deg 22), V_5, intersections of two quadrics in P^5, P^1 × P^2, blow-ups of P^3.
  - **Fanography** (`fanography.info`, Belmans 2020+): per-family Picard rank, anticanonical degree, projective embeddings, Hodge numbers — already structured as JSON.
  - **LMFDB extension `fano3folds`** does not yet exist; this report flags it as a candidate table (silent island, see §7).

## 4. Test Design

Pick ~10 Mori-Mukai families spanning ρ ∈ {1, 2, 3, 5}: V_5, V_{12}, V_{14}, V_{16}, V_{18}, V_{22} (all ρ=1); P^1×P^2 (ρ=2); blow-up of P^3 along a curve (ρ=2); intersection of two quadrics in P^5 (ρ=1); P^1×P^1×P^1 (ρ=3).

**Step 1.** Pull each family's anticanonical projective embedding from Fanography JSON; load defining equations into Sage.

**Step 2.** For B ∈ {10, 100, 1000, 10000}, enumerate Q-points of height ≤ B on X(Q) using Sage `ProjectiveSpace.points_of_bounded_height` filtered by the defining equations (or, for high degree, a SAT/SMT enumerator over coordinate boxes).

**Step 3.** Strip accumulating subvarieties (lines on V_5, conics on V_{22}) by Möbius inversion against subvariety counts.

**Step 4.** Fit log N_U(B) = log c + a log B + (b−1) log log B by weighted least squares across the 4 height tiers; bootstrap (a, b) confidence intervals.

**Step 5.** Compare (a_obs, b_obs) to (1, ρ(X)). Compute c_obs = N_U(B) / [B^a (log B)^(b−1)] at B = 10⁴ and compare to c_Peyre from Fanography local-density tables.

## 5. Falsification

- **Confirm:** |a_obs − 1| < 0.05 AND |b_obs − ρ(X)| < 0.05 across ≥7/10 families.
- **Strong kill:** |a_obs − 1| > 0.10 on a smooth family with no accumulating subvariety left → counterexample to Batyrev-Manin (publishable; almost certainly a missed accumulating subvariety, i.e. a Manin-style obstruction).
- **Soft kill:** b_obs systematically off by integer → Pic(X) computed wrong on Fanography for that family.
- **Null:** random projective-space height count in P^N of same ambient dim. Must give a = N+1, b = 1, distinguishable from Fano signature.

## 6. Budget

~1 day. Sage scripts: `fano3_height_enum.py` (per-family enumerator, ~200 LOC), `mm_fit.py` (log-log fit + bootstrap). Postgres bridge: pull Fanography JSON → table `charon.fano3folds` (family_id, rho, deg, embedding_eqs, expected_a, expected_b, c_peyre_predicted). Largest enum (B=10⁴ on intersection of two quadrics in P^5) bounded by ~10⁸ candidate points → ~6 CPU-h with sieve pruning; fits within day on M2.

## 7. Expected Outcome

Measure (a, b, c) for ~10 Mori-Mukai families. Prior: most confirm to within 5%. **Value is twofold.** First, any family with anomalous (a, b) — especially V_22 or V_{12} where accumulating subvarieties are subtle — gets flagged for Charon's database-augmentation queue and possibly a literature dive. Second, this opens the Diophantine front Charon has not touched: Fano threefolds are a **silent island** by Aporia's void-detection criterion (high mathematical importance, near-zero LMFDB presence, no canonical computational table). Proposing `fano3folds` as a new LMFDB-style table is a concrete void-fill. Connects to project_silent_islands.md and project_genus2_rosetta.md (Kummer-threefold degeneration ties Fano-3-folds to g2c_curves).

**Word count: 798**
