# Deep Research Report #119: Hecke ↔ Frobenius Transport at LMFDB Scale

**Target Agent:** Harmonia
**Date:** 2026-04-23
**Predecessor:** Report #118 (operator correlation matrix)

## 1. Problem Statement

Report #118 built the operator correlation matrix showing which abstract operators (Hecke T_p, Frobenius Frob_p, Atkin-Lehner w_d, isogeny class size) co-vary across domains. Correlation is suggestive but does not prove *transport*: that the same operator, applied in different domains, returns numerically matched eigenvalues up to a known twist.

For a Hilbert modular form f of parallel weight 2 over real quadratic K with associated elliptic curve or genus-2 Jacobian E, modularity predicts exact identities at each prime ideal P of O_K:

- **Split** (pO_K = PP'): a_P(f) = a_p(E) for base-change, or a_P(f) = a_p(E) for E/K.
- **Inert** (pO_K = P, residue F_{p²}): a_P(f) = a_p(E)² − 2p for base-change; direct Frob_{p²} count for E/K.
- **Ramified:** conductor-dependent correction.

If the identity holds at 200 primes × 500 HMF/EC pairs, operator transport is established as a measurement. If it fails structurally (by prime class), we have found a new modularity obstruction at scale.

## 2. Literature

- **Eichler-Shimura (1954-1971):** original a_p(f) = a_p(E) dictionary for classical weight-2 over Q.
- **Faltings-Serre (1989):** finite-prime sufficiency — Galois-rep equality from finite, effective conductor+discriminant set.
- **Zhang (2001), Skinner-Urban:** Heegner constructions in HMF setting implicitly use transport.
- **Khare-Wintenberger (2009), Taylor (2003, 2008):** modularity lifting over totally real — predicts transport but rarely tested at LMFDB scale.
- **Freitas-Le Hung-Siksek (2015):** EC over real quadratic are modular — makes test well-defined across ec_nfcurves for K real quadratic.
- **Dembélé-Voight (2013):** explicit HMF algorithms underlying LMFDB `hmf_hecke`.

## 3. LMFDB Data

- `hmf_hecke`: a_P(f) indexed by prime ideals P, ~45K HMF. label, field_label, hecke_eigenvalues, primes_iter.
- `hmf_forms`: metadata; `is_base_change` flag and `related_objects` → EC labels.
- `ec_nfcurves`: EC over NF; ainvs, conductor_norm, ap for small primes.
- `g2c_curves`: euler_factors for HMF dim 2.
- `nf_fields`: disc, ring-of-integers.

Cross-match hmf_forms.related_objects → ec_nfcurves.label. Restrict K real quadratic (disc > 0, degree 2). Overlap ~3K-8K pairs; sample 500.

## 4. Test Design

**Step 1.** Query hmf_forms WHERE degree=2 AND field_disc > 0 AND related_objects IS NOT NULL. Random 500 sample.

**Step 2.** For each (f, E), first 200 primes P of O_K by norm; classify split/inert/ramified via nf_fields.

**Step 3.** Predicted Frobenius value:
- Split: a_p(E) via ec_nfcurves ap, or (a_p(E_Q))² correction if base-change.
- Inert: a_p(E)² − 2p.
- Ramified: skip or apply conductor correction.

**Step 4.** Compare to a_P(f). Record residual = a_P(f) − predicted. Aggregate over 100K prime-pair tests.

**Step 5.** Null: shuffle (f, E) pairings; re-run. Expected mismatch for null ≈ random in [−2√Np, 2√Np] (Hasse).

**Metrics:** fraction exact match; fraction within Faltings-Serre bound; residual distribution by prime type.

## 5. Falsification

- **Strong kill:** exact fraction < 99% for non-ramified primes → transport is correlation only, not identity. Rewrites #118.
- **Weak kill:** exact ≈100% for split, inert shows systematic offset → LMFDB base-change twist formula incomplete; report as data-correction finding.
- **Structural finding:** residuals cluster by conductor class → partial transport, new invariant.
- **Null sanity:** shuffled pairing must show ≫5% mismatch; if null also matches, test is vacuous.

## 6. Budget

~1 day. Postgres query + prime enum in Sage/PARI (~4h setup). 200 × 500 = 100K comparisons, trivial once loaded. Plotting and stratification ~2h. Writeup ~2h.

## 7. Expected Outcome

Prior: very high match rate (>99%) — modularity guarantees it. **Value is calibration, not surprise** — we measure operator-transport metric on ground truth before applying to suspected bridges (HMF ↔ abelian surface, HMF ↔ Bianchi). A calibrated transport metric turns #118's correlation matrix into a **distance** on operator space, enabling blind discovery of new modularity-type correspondences. Secondary: any structured residual is an LMFDB convention bug or gap in published modularity lifting — publishable.

**Word count: 748**
