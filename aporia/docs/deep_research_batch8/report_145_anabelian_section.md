# Deep Research Report #145: Anabelian Section Conjecture for Elliptic Curves

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** Anabelian geometry / fundamental-group channel for V4

## 1. Problem Statement

Let X/K be a smooth projective hyperbolic curve over a number field K. Grothendieck's section conjecture (1983 letter to Faltings) predicts a bijection

  X(K) ↔ {conjugacy classes of sections s: G_K → π_1(X) of the homotopy exact sequence 1 → π_1(X_Kbar) → π_1(X) → G_K → 1}.

The conjecture is open in general; the only major positive results are p-adic local cases (Mochizuki 1999) and birational variants. The genus-1 case is *degenerate*: an elliptic curve E/K is not hyperbolic (Euler char 0), so the original statement does not apply. A torsor-of-sections variant due to Stix-Wickelgren-Esnault replaces π_1(E) with the Tate module T_l E and asks whether H¹(G_K, T_l E)-classes recover E(K) ⊗ Z_l up to obstruction.

**Empirical question:** for an LMFDB sample of (E, K), can we count Galois sections (Selmer-style H¹ classes) and compare against #E(K)? A systematic match would supply the first numerical evidence for the elliptic section conjecture; a structured excess would calibrate the genus-1 degeneracy.

## 2. Literature

- **Grothendieck (1983):** *Brief an Faltings*, original conjecture.
- **Nakamura (1990):** anabelian for genus ≥ 2 over number fields, tame case.
- **Mochizuki (1999):** absolute anabelian theorem for hyperbolic curves over sub-p-adic fields.
- **Esnault-Hai (2008):** étale fundamental group and torsor obstruction for non-hyperbolic curves.
- **Wickelgren (2012):** 2-nilpotent obstruction; computable section-count bounds via lower central series.
- **Stix (2013):** *Rational Points and Arithmetic of Fundamental Groups* (LNM 2054) — section set for genus 1, relation to Selmer.

## 3. LMFDB Data

- **`ec_nfcurves`:** E/K with `label`, `field_label`, `ainvs`, `rank`, `torsion_structure`, `regulator`, `sha` (analytic), `conductor_norm`, `ap` for small primes, `selmer_rank` where computed.
- **`nf_fields`:** `label`, `degree`, `disc_abs`, `class_number`, `signature`, `galois_group`.
- **`ec_galrep`:** mod-l Galois image data, useful for picking l where T_l E is split or has small image.

For each (E, K), π_1^ab(E_Kbar) ⊗ Z_l ≃ T_l E ≃ Z_l² with G_K-action via `ec_galrep`. Sections classified up to abelianization by H¹(G_K, T_l E); compute via Sage `EllipticCurve.padic_height`, `selmer_rank`, and `kummer_map` for finite-prime localization. Restrict K imaginary quadratic so G_K has manageable cohomological dimension (cd_l = 2) and `class_number` is small.

## 4. Test Design

**Step 1.** Query `ec_nfcurves` WHERE `field_label` ∈ imaginary quadratic (signature [0,1]) AND `rank` ∈ {0,1,2} AND `conductor_norm` < 10⁴. Stratify ~200 curves: ~80 rank 0, ~80 rank 1, ~40 rank 2.

**Step 2.** For each (E, K) and l ∈ {2, 3, 5}:
  (a) #E(K) from `ec_nfcurves.rank` + `torsion_structure` (count torsion + free generators mod l^k).
  (b) #Sections_l := #H¹(G_K, T_l E / l^k) computed via Selmer group at S = primes of bad reduction ∪ {l}; use Sage `selmer_group` and Tate local duality.
  (c) Brauer-Manin obstruction estimated via `ec_nfcurves.sha` (analytic Sha contribution at l).

**Step 3.** Predicted match: #Sections_l ≈ #E(K)/l^k · #Sha[l^k] under section conjecture + Cassels-Tate.

**Step 4.** Stratify by rank, l, `disc_abs(K)`, `conductor_norm`. Record Section/Point ratio.

**Step 5.** Null: replace T_l E with a randomly twisted Z_l²-module of matched local conditions; recompute H¹. Expected ratio ≠ 1.

## 5. Falsification

- **Strong support:** ≥150/200 (E, K) show Section/Point ratio ∈ [1, 1+#Sha[l^∞]] — empirical evidence elliptic section variant holds; publishable as first LMFDB-scale measurement.
- **Structural excess:** ratio scales with rank (excess at rank 2) → documents genus-1 degeneracy quantitatively; aligns with Stix-Wickelgren prediction that non-hyperbolic curves have honest torsor obstruction.
- **Strong kill:** ratio random across all strata → conjecture's elliptic variant is not a measurement artifact at LMFDB scale; null indistinguishable from signal.
- **Null sanity:** randomly-twisted T_l E null must show ratio ≠ 1 with z > 3, otherwise H¹ counting is dominated by ambient cohomology and the test is vacuous.

## 6. Budget

~1 day. LMFDB Postgres pull (~1h). Sage Galois cohomology + Selmer computation, ~200 curves × 3 primes ≈ 600 jobs at ~30s each (~5h, parallelizable on Skullport). Stratification and plotting ~2h. Writeup ~2h.

## 7. Expected Outcome

First LMFDB-scale measurement of the Section/Point ratio for elliptic curves over imaginary quadratic K. Three deliverables:

1. **Calibration:** numerical ratio distribution + scaling with rank/`disc_abs`/`conductor_norm` — turns a folkloric expectation into a measured curve.
2. **Anomaly catalogue:** specific (E, K) flagged with anomalous excess (Section/Point > 1 + #Sha[l^∞]) — candidate counterexamples or missing Sha at LMFDB.
3. **Aporia void-detection:** anabelian methods are currently a *silent island* in the tensor (no operator coverage in V3.4 inventory; cf. `project_silent_islands`). Adding a "fundamental-group" channel — Section/Point ratio per (E, K) — gives V4 a new column orthogonal to existing Hecke/Frobenius/Selmer channels. Couples directly to Harmonia's operator-correlation matrix (#118) and to genus-2 Rosetta (`project_genus2_rosetta`) where the hyperbolic case is non-degenerate.

**Word count: 748**
