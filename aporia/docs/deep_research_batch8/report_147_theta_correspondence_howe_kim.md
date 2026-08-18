# Deep Research Report #147: Theta Correspondence Howe-Kim Duality at LMFDB Scale

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** theta / dual reductive pairs
**Companion:** Reports #118-119 (Hecke-Frobenius transport)

## 1. Problem Statement

For a dual reductive pair (G, G') = (O(V), Sp(W)) inside a symplectic Sp(V ⊗ W) over a number field F, the global theta lift sends an automorphic form pi on G(A) to an automorphic form Theta(pi) on G'(A) (or zero). Howe's conjecture — proved archimedean by Howe (1989) and extended to many non-archimedean cases by Kim (2014) — asserts the correspondence pi ↔ Theta(pi) is a *bijection* on the unramified spectrum, modulo a determined "Howe correspondence character" twist depending on the splitting of V.

**Empirical question.** At LMFDB scale, do theta lifts of weight-2 GL(2)/Q newforms — viewed as forms on PGL(2) ≅ SO(2,1) — match expected targets on Sp(4) (Hilbert modular forms over real quadratic K, or genus-2 Jacobian L-functions)? The Rallis-Howe seesaw predicts an explicit L-function identity at unramified primes; we test whether LMFDB-stored Hecke and Euler data confirms this on ~200 forms.

## 2. Literature

- **Howe 1979** *Theta series and reductive dual pairs* — the framework.
- **Howe 1989** (Israel J. Math.) — archimedean Howe duality.
- **Waldspurger 1980, 1991** — theta correspondence SL(2) ↔ PGL(2), central-value formula.
- **Kim 2014** — preservation principle, non-archimedean Howe for tame pairs.
- **Gan-Takeda 2011** (Annals) — proof of Howe duality for orthogonal-symplectic over p-adic.
- **Gan-Ichino 2014** (Inventiones) — refined Howe with central L-values for (Sp(4), O(V)).
- **Sakellaridis-Venkatesh 2017** — modern reformulation via spherical varieties; relevant to void detection in automorphic transfer.

## 3. LMFDB Data

- `mf_newforms`: GL(2)/Q weight-2 forms; columns label, weight, level, dim, char_orbit_index, hecke_ring, atkin_lehner_eigenvals. Source of theta input.
- `mf_hecke_nf`: stored a_p eigenvalues; needed for first-20-prime comparison.
- `hmf_forms`, `hmf_hecke`: parallel weight-2 HMF over real quadratic K; candidate targets for theta on (Sp(2)/Q, O(2)/K) with K determining quadratic space V.
- `g2c_curves`: genus-2 Jacobians as abelian surfaces; columns label, cond, num_rat_pts, analytic_rank, euler_factors. Candidates for SO(4) ⊂ Sp(4) theta targets when Jac splits as restriction of scalars.
- `lfunc_instances` / `lfunc_lfunctions`: cross-domain matching by L-function origin tag.
- `nf_fields`: field discriminants determining V.

## 4. Test Design

**Step 1.** Query `mf_newforms` WHERE weight=2 AND level<5000 AND char_orbit_index=1 AND dim<=4. Sample ~200 forms f with non-CM and trivial nebentypus to keep the lift well-defined.

**Step 2.** For each f, fix a real quadratic K (loop over disc(K) in {5, 8, 12, 13, 17, 21, 24, ...}, ~10 fields) and form predicted theta lift Theta_K(f) onto Sp(4) via the (PGL(2), PGSO(2,2)/K) seesaw. Predicted L-function: L(Theta_K(f), s) = L(f, s) · L(f ⊗ chi_K, s) where chi_K is the quadratic character of K (Howe-Rallis identity).

**Step 3.** Search `hmf_forms` for HMF over K with parallel weight 2 and matching analytic conductor. Pull `hmf_hecke` eigenvalues for first 20 split primes.

**Step 4.** Compute predicted a_P(Theta_K(f)) from a_p(f) and a_p(f⊗chi_K) via Rallis inner product formula, compare to LMFDB a_P. Record exact matches, off-by-twist matches, and outliers.

**Step 5.** Parallel branch: search `g2c_curves` for Jacobians with euler_factors matching predicted Spin L-function of Theta_K(f); cross-check `lfunc_instances` for shared origin tags.

**Step 6.** Null: random pairing of f to unrelated K; expected match rate at random within Hasse band ~ 0.

## 5. Falsification

- **Confirm Howe-Kim:** >=80% of (f, K) pairs yield a target HMF or g2c L-function with matching first-20 Hecke eigenvalues at unramified primes -> Howe correspondence empirically validated at LMFDB scale.
- **Twist anomaly:** match modulo a uniform character -> "Howe correspondence character" miscalibration in LMFDB labelling; report.
- **Ramified-prime failure expected:** Howe is an unramified statement; classify failures by ord_p(level(f)) and ramification of p in K.
- **Structural kill:** <40% match outside ramification -> either theta lift is zero generically (Theta(f)=0 in Waldspurger-vanishing sense) or LMFDB target population is too thin; isolate via central-value L(1/2, f x chi_K) (Waldspurger non-vanishing criterion).
- **Null sanity:** shuffled (f, K) pairings must score <<5% match.

## 6. Budget

~1 day. Sage `ModularForms` + `lcalc` for L-values (~3h), Postgres pulls from `mf_hecke_nf`/`hmf_hecke`/`g2c_curves` (~2h), 200 x 10 K-choices x 20 primes ~ 40K comparisons (trivial), stratification + writeup (~3h).

## 7. Expected Outcome

Measure theta-lift consistency rate on ~200 forms; emit anomaly cells where Hecke match fails at unramified primes despite Waldspurger non-vanishing. Connects Aporia void-detection: theta correspondence is an automorphic-transfer phoneme *distinct* from Hecke transport (#118-119) — Hecke transport is endoscopic/base-change (same group, different field), theta is dual-pair (different group, same field). A confirmed "theta channel" becomes V4 in the Megethos basis, separating the silent islands (knots, Bianchi) by which transfer phoneme reaches them. If theta channel illuminates g2c labels currently dark to Hecke transport, we have a second receiver for the genus-2 Rosetta program.

**Word count: 748**
