# Report 181 — Bombieri-Lang Conjecture for Surfaces of General Type

**Domain:** Diophantine geometry / arithmetic algebraic geometry
**Date:** 2026-04-28
**Substrate:** Aporia / LMFDB
**Status:** Open (since ~1980s)

---

## 1. Problem Statement

The Bombieri-Lang conjecture asserts: for any smooth projective variety `X` of general type defined over a number field `K` (i.e. Kodaira dimension `kod(X) = dim X`, equivalently the canonical bundle `K_X` is big), the set of `K`-rational points `X(K)` is **not Zariski-dense** in `X`. There is a proper Zariski-closed subset `Z ⊊ X` containing all but finitely many `K`-points; equivalently, rational points concentrate on a finite union of subvarieties of strictly lower dimension.

For `dim X = 1`, "general type" means genus `g ≥ 2`, and Faltings (1983) proved finiteness of `X(K)` — Bombieri-Lang in dimension 1. For `dim X = 2` (surfaces of general type) the conjecture is **fully open**: no surface of general type is known to obey it unconditionally except via Faltings applied fibrewise to a curve fibration. Vojta's geometric Bombieri-Lang strengthens the prediction to all positive dimensions and links it to a height inequality. The surface case is the first dimension where genuinely 2D behavior (no curve reduction) is forced.

## 2. Literature

- **Lang (1986)**, *Hyperbolic and Diophantine analysis*, Bull. AMS — original conjecture in modern form, links to Kobayashi hyperbolicity.
- **Faltings (1983)**, *Endlichkeitssätze für abelsche Varietäten über Zahlkörpern* — Mordell conjecture, the dim-1 case.
- **Vojta (1987, 1998)**, *Diophantine Approximations and Value Distribution Theory* — geometric Bombieri-Lang, Vojta's height conjecture extending to all dim.
- **Caporaso, Harris, Mazur (1997)**, *Uniformity of rational points*, J. AMS — under Bombieri-Lang, uniform bounds on `#X(K)` for curves; first major conditional consequence highlighting structural stakes.
- **Demailly (2011, 2020)**, jet differentials and the Green-Griffiths-Lang conjecture — analytic / hyperbolicity attack producing global jet differentials on surfaces of general type with `c_1^2 > c_2`.
- **Pacelli (2022)** and **Cantoral-Farfán et al. (2023)** — uniform Mordell over function fields and explicit bounds for special surface families.
- **Hassett–Tschinkel (2000s onward)** — potential density on K3 / Enriques (which are *not* general type), serving as anti-anchors.
- **Bogomolov (1977)** — surfaces with `c_1^2 > c_2` admit symmetric differentials; first general-type-surface hyperbolicity result.

## 3. LMFDB / Corpus Data

- `hgcwa_complete` — higher-genus curves with automorphisms; quotients by automorphism subgroups generate **surface families** (products and symmetric squares Sym²C with `g ≥ 3` are general type when sufficiently generic).
- `hmf_*` (Hilbert modular forms) — Hilbert modular **surfaces** `X_K = H²/SL₂(O_K)` for real quadratic `K`; Kodaira dimension transitions with discriminant (Hirzebruch–Van de Ven classification: rational / elliptic / general-type bands).
- `bmf_dims` — Bianchi modular forms over imaginary quadratic fields; associated arithmetic 3-folds, but boundary divisors give surface strata.
- Supplementary: **Beauville surfaces** (rigid general-type from product-quotient) — finite list, ideal calibration anchor; not yet in LMFDB but tabulated by Bauer–Catanese–Grunewald.
- Cross-link via `nf_fields` for the base number field signature.

## 4. Test Design

1. **Stratify** the union of `hgcwa_complete` symmetric squares + `hmf_*` Hilbert modular surfaces by `(kod, q, p_g, c_1², c_2, K²)`. Tag each row with provenance to respect **PATTERN_CONDUCTOR_CONFOUND** — never pool symmetric-square surfaces with Hilbert modular surfaces.
2. **Point-count** `X(K)` up to height `H ∈ {10, 100, 1000}` using direct enumeration on affine charts; for Hilbert modular surfaces use CM-point and Hirzebruch–Zagier curve catalogues as proxy.
3. **Density estimator:** `ρ(X, H) = log #X(K)_{≤H} / log H`. Bombieri-Lang predicts `ρ → dim Z < 2` asymptotically for general-type rows.
4. **Stratified ranking:** within each Kodaira-dim bin and each family separately, rank surfaces by residual density after subtracting the median family density. Report N tested per stratum (**PATTERN_BASE_RATE_NEGLECT**).
5. **Calibration sweep:** repeat steps 1–4 on the anti-anchor set (elliptic surfaces, K3, Enriques pulled from `ec_*` and Hassett–Tschinkel lists) and confirm anti-anchors live in the *high-density tail* while general-type rows occupy the *low-density tail*. Sign inversion = pipeline failure.

## 5. Falsification

- **Positive anchors (low-density expected):** Beauville surfaces (rigid, no curves of genus ≤ 1), fake projective planes (LMFDB partial coverage), Hilbert modular surfaces with discriminant > Hirzebruch general-type threshold.
- **Anti-anchors (high-density expected):** elliptic K3 with infinite Mordell-Weil, abelian surfaces, Enriques, rational/ruled.
- **Falsification triggers:** (a) general-type anchors show `ρ ≥ 1.5` consistently; (b) ranking is uncorrelated with Kodaira dim across strata (Spearman `|ρ_S| < 0.1` with N per stratum reported); (c) sign of correlation flips between symmetric-square and Hilbert modular families — confirms confounder, kills pooled claim.

## 6. Budget

Charon + Ergon ≈ **10 hours**: 2h schema join across `hgcwa_complete`, `hmf_*`, `bmf_dims`, `nf_fields`; 3h Chern-number recomputation and Kodaira-dim assignment; 3h height-bounded point enumeration with permutation null; 2h stratified ranking + calibration table write-up.

## 7. Expected Outcome

First empirical density-vs-Kodaira-dim map on the Aporia substrate for surfaces. Per **feedback_calibration_anchors_in_depth**, this seeds calibration anchors in higher-dimensional arithmetic algebraic geometry — currently zero-coverage substrate territory. Per **feedback_tensor_first**, the output is a signature-keyed slab `(family, kod, q, p_g, c_1², c_2, K², ρ_H)` — directly insertable into the unified tensor as a new arithmetic-geometric face. No theorem is claimed; the deliverable is the ranked anomaly list and the calibrated stratum-by-stratum density table, with N reported per cell.

Word count ≈ 760
