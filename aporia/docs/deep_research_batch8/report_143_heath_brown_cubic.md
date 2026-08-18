# Deep Research Report #143: Heath-Brown Circle Method for Cubic Forms

**Target Agent:** Ergon
**Date:** 2026-04-25
**Front:** Diophantine analytic NT
**Sister report:** #142 (Fano threefolds)

## 1. Problem Statement

For a cubic form F(x_1,...,x_n) in Z[x_1,...,x_n] of degree 3, the Hardy-Littlewood circle method predicts that the count

  N(F, B) = #{ x in Z^n : F(x) = 0, |x|_infty <= B }

satisfies, as B -> infty,

  N(F, B) ~ c_HL * B^{n-3},  c_HL = sigma_infty * prod_p sigma_p,

where sigma_infty is the singular integral (real density on F=0) and sigma_p is the local p-adic density derived from solution counts mod p^k. Hooley's theorem (1988, refining Davenport) establishes this, plus the weak Hasse principle, for non-singular cubic forms in n >= 8 variables. For n=4 (cubic surfaces in P^3) and n=5 (cubic threefolds), the asymptotic is conjectural — Manin's conjecture predicts N(B) ~ c * B * (log B)^{rho-1} where rho is the Picard rank of the smooth locus, and the constant should match Peyre's refinement of Hardy-Littlewood with Brauer-Manin correction. The empirical question: for a fixed sample of cubics, does the *measured* leading constant match c_HL computed from finite local data, and which surfaces flag deviations consistent with a Brauer-Manin obstruction?

## 2. Literature

- **Davenport (1959, 1963):** Cubic forms in 16, then 9 variables represent zero non-trivially over Q.
- **Heath-Brown (1983):** Cubic forms in 10 variables; refined to 9 in later work, with sharpened minor-arc estimates via Kloosterman refinement.
- **Hooley (1988, 1991):** Non-singular cubic forms in 9 variables satisfy weak Hasse; later extended to 8 conditional on RH-type hypotheses.
- **Browning-Heath-Brown (2009):** Cubic surfaces with three coplanar lines (split case) — Manin's conjecture proved for diagonal subfamilies.
- **Browning (2009 survey, "Quantitative Arithmetic of Projective Varieties"):** standard reference for circle method applied below the Davenport threshold.
- **Beresnevich-Vaughan-Velani:** metric Diophantine approximation on manifolds — gives the singular integral framework used to compute sigma_infty.

## 3. LMFDB Data

Cubic surfaces are not a first-class LMFDB table. Available bridges:

- `g2c_curves`: Jacobian-Kummer cubic models accessible via `eqn` for genus-2 curves whose Kummer surface admits a cubic embedding; columns `disc`, `cond`, `analytic_rank`.
- `nf_fields`: cubic field discriminants via `degree=3`, `disc_abs`, used to anchor sigma_p computations against known cubic-resolvent statistics.
- `ec_curves`: trivial 1-variable cubic test (Weierstrass) — calibration sanity for the singular series machinery.

Primary external sources: explicit Mordell-Weil-known surfaces (Cayley nodal cubic, Clebsch diagonal, Schur quartic-cubic pencil) and du Val singular catalogues. To get a usable n=4 sample, build a synthetic catalogue: sample integer-coefficient cubics from [-10, 10]^{20} (the 20 monomials of degree 3 in 4 variables), reject non-smooth via discriminant non-vanishing, target ~200 surviving forms.

## 4. Test Design

**Step 1.** Construct sample S of ~200 smooth cubic forms in n in {4, 5} variables.

**Step 2.** For each F in S and B in {10, 100, 1000}, compute N(F, B) using Sage `points_of_bounded_height` on the projective scheme V(F), or direct integer enumeration with PARI for n=4.

**Step 3.** Fit log N(B) vs log B to model log c + (n-3) log B + (rho-1) log log B, where rho is computed from the Picard lattice of F (Sage `picard_number` for smooth cubic surfaces returns up to 7).

**Step 4.** Compute c_HL:
- sigma_p by counting #{ x mod p^k : F(x) = 0 mod p^k } / p^{k(n-1)} for p in {2,3,5,7,11,13} and k chosen so p^k > 50; truncate Euler product at p=100 and apply tail bound.
- sigma_infty by Monte Carlo estimation of real density on the F=0 hypersurface inside the unit box.

**Step 5.** Ratio r = c_measured / c_HL.

## 5. Falsification

- **Confirm:** |r - 1| < 0.10 across >= 80% of sample → Hardy-Littlewood empirically validated at low-variable regime.
- **Strong finding:** |r - 1| > 0.25 with positive sign → likely accumulating subvariety (line, conic) not yet excised; standard fix.
- **Publishable:** r < 0.5 with sigma_p > 0 for all p tested, sigma_infty > 0 → Brauer-Manin obstruction candidate; cross-check against Colliot-Thelene / Wittenberg surface lists.
- **Null:** shuffle coefficient vectors to produce random non-cubic integer scoring; expected r distribution flat — null rejection at p < 0.01 required.

## 6. Budget

~8 hours. Sample construction + smoothness filter (1h Sage). Per-cubic point counting at B=1000 is ~5s; 200 cubics x 3 B-values ~1h. Local density loop ~2h (Chinese remainder + Hensel lifting). Singular integral Monte Carlo ~1h. Aggregation, plot, writeup ~3h.

## 7. Expected Outcome

Measured Hardy-Littlewood constants for ~200 cubics in n in {4,5}, ratio histogram r vs unity, and a flagged shortlist (~5-15 surfaces) where |r-1| > 0.25. Connects directly to Aporia void-detection: cubic surfaces are a Diophantine silent-island sister to Fano threefolds (#142) — both have rich expected-density theory and almost no LMFDB ground truth, so any deviation flagged here is either a genuine Brauer-Manin discovery or a data-side density bug. Calibrated against `nf_fields` cubic-discriminant statistics. Pipeline reusable for quartic surfaces in #144.

**Word count: 762**
