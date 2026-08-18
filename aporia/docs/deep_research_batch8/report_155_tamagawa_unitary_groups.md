# Deep Research Report #155: Tamagawa Numbers for Unitary Groups

**Target Agent:** Charon
**Date:** 2026-04-25
**Front:** Tamagawa / arithmetic densities

## 1. Problem Statement

For a reductive group G/Q, the Tamagawa number tau(G) is the volume of the adelic quotient G(A)/G(Q) under a canonical (Tamagawa) measure built from a top-degree invariant differential. The Weil conjecture, proved in the simply-connected semisimple quasi-split case by Lurie-Gaitsgory (2014), asserts tau(G_SS) = 1; for general semisimple G with isogeny cover G̃ → G, tau(G) = #pi_0(Z(G̃))^Gal · #ker(H^1(Q,Z) → ...) — yielding tau(G) = #pi_0(Z(G)) for split center.

For the unitary group U(n) attached to a CM extension K/F (F totally real, K = F(sqrt(−d))), the conjectural value is tau(U(n)) = 2: one factor from the sign character det: U(n) → U(1) and one from the order-2 Tate-Shafarevich obstruction Sha^1(F, Z(U(n))). The empirical question: do mass-formula computations on LMFDB CM-field and unitary-Shimura data reproduce tau(U(n)) = 2 across the catalogue, or are there unitary-specific deviations that would represent a Lurie-Gaitsgory exception?

## 2. Literature

- **Weil (1965)** *Sur certains groupes d'opérateurs unitaires*, Acta Math. — original conjecture and U(n) mass formula.
- **Tamagawa (1966)** *Adèles* — canonical measure construction; tau(SL_n) = 1.
- **Sansuc (1981)** J. reine angew. Math. — Tamagawa number via Galois cohomology: tau(G) = #pi_0(Pic) / #Sha^1(G).
- **Kottwitz (1988)** *Tamagawa numbers*, Ann. Math. — conjectural mass formula for arbitrary reductive G; extends Weil.
- **Bhargava-Gross (2013)** *Arithmetic invariant theory* — heuristic mass formulas via lattice-point counting; the arithmetic-statistics channel.
- **Gaitsgory-Lurie (2014)** arXiv:1306.6611 *Weil's conjecture for function fields* — full proof for simply connected SS quasi-split (over function fields, transferable).

## 3. LMFDB Data

- `nf_fields`: signature `[r1, r2]`; CM fields are exactly degree-2n fields with signature `[0, n]` plus a totally-real subfield of index 2 (filter via `is_cm` flag and `cm_field` column where present). Use `disc_abs`, `class_number`, `regulator`.
- `g2c_curves`: genus-2 Jacobians; those with `geom_end_alg` containing CM-by-K give U(1)-symmetry surrogates. Columns: `endomorphism_ring`, `cm_discriminants`.
- `ec_nfcurves`: elliptic curves over imaginary quadratic K (filter `degree=2 AND signature='[0,1]'`); each contributes a U(2)-arithmetic datum via Selmer pairing.
- `hgcwa_passports`, `belyi_passports`: tangential Galois data for cocycle computations.

Direct U(n) Tamagawa computation needs Magma's `UnitaryGroup` package or Sage `sage.modular.hecke` plus manual cohomology; for n=2,3 the volume integrals reduce to L-values L(1, eta_K/F) and L(2, eta).

## 4. Test Design

**Step 1.** Query `nf_fields WHERE degree=2 AND signature='[0,1]'` — yields ~2000 imaginary quadratic K. Sample 50 stratified by `disc_abs` (decades 10^1 .. 10^6).

**Step 2.** For each K, compute tau(U(2)/K) and tau(U(3)/K) via Sansuc:

  tau(U(n)) = #pi_0(Pic(U(n))) · vol(U(n)(A)/U(n)(Q)) / #Sha^1(Q, Z(U(n)))

with vol expressed as product of local L-factors L_p(s, eta_K)^{-1} times archimedean Gamma factors (Macdonald formula).

**Step 3.** Cross-check via Bhargava-Gross mass formula: enumerate integral Hermitian lattices over O_K of rank n up to height B, weight by 1/#Aut, and fit tau as the leading constant in the Bhargava heuristic Mass(B) ~ tau · B^{dim G} / vol_inf.

**Step 4.** Null comparator: same protocol applied to (a) GL_n/K (predicted tau = 1), (b) Sp_{2n}/K (predicted tau = 1), (c) randomly twisted inner forms.

**Metrics:** distribution of |tau_measured − 2| across 50 K; Kolmogorov-Smirnov against delta_2; null comparators must give tau = 1 (or twist value).

## 5. Falsification

- **Confirmation:** tau = 2 within 10^{-3} for all 50 cases → Lurie-Gaitsgory verified empirically on the LMFDB CM-field catalogue; closes the Tamagawa coordinate.
- **Strong kill (publishable):** any K with |tau − 2| > 10^{-2} reproducible across two independent measurements → Lurie-Gaitsgory exception or LMFDB CM-field labelling bug; either is a finding.
- **Structural finding:** deviation correlates with `class_number` or `cm_discriminants` parity → uncovers a refined Sha^1 contribution missed by Sansuc's formula.
- **Null sanity:** if GL_n null also returns ≈2, the measurement is vacuous (volume normalization off); recalibrate.

## 6. Budget

~1 day. Sage Galois-cohomology module + lattice volume via PARI `qfminim` (3h). Postgres pull and CM-field stratification (1h). 50 fields × 2 ranks × 2 methods = 200 measurements (~3h compute). Null comparators (1h). Writeup (1h).

## 7. Expected Outcome

Prior: tau(U(n)) = 2 confirmed across all 50 CM fields — Lurie-Gaitsgory holds. **Value is the calibration**, not a kill. The measured Tamagawa coordinate becomes a new arithmetic-statistics channel for Aporia void-detection: unlike BSD (rank channel) or Selmer (mod-p channel), the Tamagawa density is a global volume invariant insensitive to local ramification. This makes it a complementary axis in the Bhargava-Gross dissection tensor, useful for spotting CM fields where the arithmetic statistics deviate from the predicted universal — i.e., voids in the unitary-Shimura landscape. Secondary: any structured residual is a publishable correction to Sansuc's formula or evidence of a non-trivial Sha^1 stratum the LMFDB has not catalogued.

**Word count: 748**
