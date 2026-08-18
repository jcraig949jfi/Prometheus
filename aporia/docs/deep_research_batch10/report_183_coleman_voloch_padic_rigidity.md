# Report 183 — Coleman-Voloch arithmetic on rigid analytic spaces: empirical p-adic L-function rigidity

**Domain:** p-adic Hodge theory / arithmetic of rigid analytic varieties
**Substrate role:** operator behavior in the p-adic structural region of L-function space
**Date:** 2026-04-28

## 1. Problem Statement

Coleman's p-adic integration on rigid analytic spaces (1985-1990s) and the Mazur-Tate-Teitelbaum (MTT) construction produced the first p-adic L-functions L_p(E, s) attached to elliptic curves. Subsequent work by Stevens, Pollack, Bellaiche, and Voloch refined these via overconvergent modular symbols and characteristic-p analogues, exposing a family of **rigidity conditions** the analytic objects must satisfy: a symmetric functional equation (sign w_p tied to the global root number), the exceptional zero phenomenon at split-multiplicative primes (the L-invariant L(E,p) governing the leading term), and prescribed growth/integrality at trivial zeros. These rigidity conditions are theorems in the ranges where they have been proven, but the **empirical leakage rate** — how cleanly they hold in finite-precision computation across a large LMFDB sample — is uncalibrated. The substrate question: produce a quantitative calibration map of "rigidity-residual" by (E, p, ord_p) so that genuine refinement candidates can be separated from arithmetic-of-precision artifacts.

## 2. Literature

- Coleman, R. F. (1985). *Torsion points on curves and p-adic abelian integrals.* Annals of Math.
- Mazur, B., Tate, J., Teitelbaum, J. (1986). *On p-adic analogues of the conjectures of Birch and Swinnerton-Dyer.* Invent. Math. — foundational MTT construction and L-invariant.
- Greenberg, R., Stevens, G. (1993). *p-adic L-functions and p-adic periods of modular forms.* Invent. Math. — exceptional zero conjecture proof for weight 2.
- Pollack, R. (2003). *On the p-adic L-function of a modular form at a supersingular prime.* Duke Math. J. — half/plus-minus L-functions.
- Stevens, G. (notes, ~2000). *Rigid analytic modular symbols.* — overconvergent framework.
- Pollack, R., Stevens, G. (2011). *Overconvergent modular symbols and p-adic L-functions.* Annales ENS — algorithm currently used by sage `padic_lseries`.
- Bellaiche, J., Stevens, G. (2007). *p-adic families of overconvergent eigensymbols.* — eigenvariety-side rigidity.
- Voloch, J. F. (1990s-2000s). Series on p-adic torsion / integrality on abelian varieties — the "Coleman-Voloch" arithmetic of leakage bounds.
- Recent: Kim-Pollack-Sprung (2020s) on Iwasawa main conjecture verifications.

## 3. LMFDB / Corpus Data

- `ec_curves` (LMFDB Postgres mirror via Mnemosyne): label, conductor, rank, ap-data, root number, list of split-multiplicative primes per curve.
- `ec_padic` / `lfunc_padic_data` if mirrored locally — confirm with Mnemosyne; otherwise compute.
- `sage.schemes.elliptic_curves.padic_lseries` (Pollack-Stevens overconvergent symbol algorithm) — primary computational engine.
- `pari/gp` `ellpadicL` — secondary/cross-check engine.
- Coleman integration via sage (`coleman_integral`) for rigidity-symmetry residuals on the analytic side.

## 4. Test Design

1. **Sample selection.** Pull all rank-0 and rank-1 elliptic curves of conductor N <= 5000 from `ec_curves`, stratified by (rank, conductor band, reduction type at p) for p in {3, 5, 7, 11}. Target ~2000 (E, p) pairs after stratification, ensuring all four reduction types (good ordinary, good supersingular, multiplicative split, multiplicative non-split) are populated. **PATTERN_BASE_RATE_NEGLECT** guard: precompute the population rate of each (rank, reduction-type) cell so deviation z-scores are reduction-type-conditional, not pooled.
2. **Compute L_p to N digits.** For each (E, p) compute L_p(E, T) to precision N = 30 via Pollack-Stevens overconvergent symbols at two distinct working precisions (N and N+10) and record the digit-stable prefix length S(E, p, N).
3. **Functional-equation residual.** Apply the predicted symmetry T -> ((1+T)^{-1} - 1) (or the Iwasawa-algebra involution appropriate to the chosen variable) and compute the residual in p-adic norm vs. the predicted sign w_p. Log r_FE(E, p) = -log_p ||L_p - w_p * L_p^iota||.
4. **Exceptional-zero verification.** For curves with split-multiplicative reduction at p, compute the L-invariant L(E, p) via the MTT formula and verify the leading-term identity L_p'(E, 1) = L(E, p) * (1 - 1/p) * L(E, 1)/Omega_E. Log r_EZ(E, p).
5. **Rigidity-residual map.** Tabulate (E, p, ord_p, r_FE, r_EZ, S) and compute the calibration function rho(E, p, ord_p) = r_FE - alpha * S — where alpha is the per-digit precision-loss slope fit from a control subsample of MTT-verified small cases. Persist as a tensor slice keyed on (curve_signature, p) per **feedback_tensor_first**.

## 5. Falsification

- **Calibration anchors.** MTT (1986) verified small-conductor cases (11a, 14a, 15a, 17a) to ~20 p-adic digits at p=5,7. Any pipeline whose r_FE on these anchors falls short of N - 5 digits is a pipeline bug, not a discovery. Hard-fail the sweep until anchors land cleanly.
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT.** Re-run the entire pipeline at an auxiliary prime p' adjacent to each test prime (e.g., 3 -> 13, 5 -> 17). A rigidity violation that survives at p but vanishes at p' is suspect: the pattern frequently masquerades as a "p-adic effect" when it is a fixed-prime numerical coincidence. Require violation persistence across at least one auxiliary prime.
- **PATTERN_CONDUCTOR_CONFOUND.** Stratify residuals by conductor band; check the residual-vs-conductor slope. A monotone slope is the conductor-confound signature and downgrades any "anomaly" claim to a sample-selection artifact.
- A surviving residual — anchored, prime-portable, conductor-flat, and exceeding the per-digit precision-loss slope alpha by > 5 sigma — is a refinement candidate (not a discovery): forward to literature for known L-invariant corrections before any further claim.

## 6. Budget

Charon: ~10h wall-clock. Sage `padic_lseries` at N=30 dominates (~10-30s per (E, p) at small conductor, longer at supersingular). Pari `ellpadicL` cross-check adds ~30%. Tensor write and rigidity-residual tabulation are negligible.

## 7. Expected Outcome

A populated calibration table rho(E, p, ord_p) over ~2000 (E, p) pairs, anchored on the MTT-verified small cases. Per **feedback_calibration_anchors_in_depth**, calibration anchors in p-adic L-function rigidity are currently sparse in the substrate; this brief is anchor-production-first, discovery-second. Even a fully-null run (every residual within precision-loss slope) is a load-bearing artifact: it gives the substrate a quantitative noise floor against which any future p-adic anomaly can be measured. Rigidity violations, if any, are forwarded as refinement candidates, not findings.

Word count: ~795
