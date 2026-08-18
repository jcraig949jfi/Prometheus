# Report 198 — Hilbert Modular Forms over Real Quadratic Fields with Non-Trivial Nebentypus

**Aporia Problem #198**
**Date:** 2026-04-28
**Region:** under-explored structural neighborhood of the Langlands automorphic spectrum
**Doctrine:** feedback_tensor_first, feedback_calibration_anchors_in_depth

---

## 1. Problem Statement

Hilbert modular forms (HMF) over a totally real number field F generalize classical modular forms by placing the form on `H^[F:Q]` and demanding equivariance under `GL_2(O_F)` (or a congruence subgroup). For F = Q(√d) real quadratic with class number 1 and trivial nebentypus, LMFDB ships dense coverage in `hmf_forms` and `hmf_hecke_eigenvalues`. The substrate has used that slab as a low-friction calibration target. **Non-trivial nebentypus** — a Dirichlet-style character of the narrow ray class group — opens a structurally distinct neighborhood: the relevant Hecke algebra twists, Atkin-Lehner involutions are character-conjugated, the cuspidal/Eisenstein split acquires character-dependent dimension formulae, and old/newform decomposition becomes sensitive to the conductor of the character itself. The empirical question is whether bulk operator behavior — first-30 Hecke eigenvalue distributions, low-lying L-zero spacings, Sato-Tate-style angle histograms — in the **non-trivial-character structural region** matches the trivial baseline at moderate level, or whether quantitative deviation persists below the asymptotic regime.

## 2. Literature

- **Shimura (1978), "The special values of the zeta functions associated with Hilbert modular forms"** — foundational analytic theory; nebentypus appears as a character on the narrow ray class group, modifying the slash action.
- **Newton-Thorne (Inv. Math. 2021), "Symmetric power functoriality for Hilbert modular forms"** — symmetric powers and consequent **Sato-Tate for HMF over totally real fields**; this is the asymptotic prediction the substrate must triangulate against.
- **Greenberg-Voight (Math. Comp. 2011), "Computing systems of Hecke eigenvalues associated to Hilbert modular forms"** — definite quaternionic algorithm underlying most LMFDB HMF rows; nebentypus support is implemented but sparsely populated.
- **Dembele (Exp. Math. 2005)** and **Dembele-Voight (in *Elliptic Curves, Modular Forms and Iwasawa Theory*, 2017)** — explicit HMF computation, including character cases over small real quadratic fields.
- **Freitas-Le Hung-Siksek (Inv. Math. 2015), "Elliptic curves over real quadratic fields are modular"** — modularity lifts that *consume* the trivial-nebentypus HMF slab; downstream work increasingly needs the twisted slab.
- **Voight, "Hilbert modular forms" (LMFDB knowls + survey, 2014–2020)** — authoritative documentation for `hmf_forms` schema and `char_orbit` semantics.
- **Blomer-Harcos-Michel, sub-convexity for HMF L-functions** — bounds depend on conductor of the nebentypus separately from level; relevant for zero-spacing expectations.

## 3. LMFDB / Corpus Data

- **`hmf_forms`** — primary table: label, base field, level (ideal label), weight (parallel / mixed), `char_orbit_index`, dimension, `is_CM`, `is_base_change`. Filter: base field `2.2.*` (real quadratic), `char_orbit_index > 1`.
- **`hmf_hecke_eigenvalues`** — `a_p` keyed by HMF label and prime ideal; first 30 primes by norm gives a clean signature.
- **`char_dir_orbits` / narrow-ray analogue** — needed to recover order, conductor, and primitivity of the nebentypus.
- **`hmf_fields`** — discriminant, narrow class number, fundamental unit data.
- **Optional cross-anchor: `mf_newforms` (classical, with nebentypus)** for base-change controls; `lfunction_zeros` if available for the HMF L-functions in question.
- Mnemosyne already mirrors `hmf_forms`; verify `char_orbit_index` non-NULL coverage before scoping the run.

## 4. Test Design

1. **Pull** all `hmf_forms` rows with base field real quadratic (disc ≤ 100, narrow class number 1 first), `char_orbit_index > 1`, parallel weight 2 ≤ k ≤ 6, level norm ≤ 1000. Record `(F, level, char_order, weight, dim)`.
2. **Compute signature**: first 30 Hecke eigenvalues ordered by prime ideal norm, normalized as `a_p / (2 N(p)^((k-1)/2))` to land in `[-1, 1]` (Sato-Tate scaling). Where `a_p` is unavailable for the requisite prime, fall back to next prime and record the gap.
3. **Stratify**: bucket by `(disc(F), level norm bin, char order, weight)`. Build a matched **trivial-nebentypus cohort** at the same `(F, weight, level-bin)` for each non-trivial bucket. Refuse comparison where the matched cohort has < 10 forms (PATTERN_BASE_RATE_NEGLECT guard).
4. **Distributional comparison**: per stratum, run KS / Wasserstein-1 / first four moments of the normalized-`a_p` distribution against the matched trivial cohort *and* against the Sato-Tate semicircle. Report deviation as a function of character order and conductor separately.
5. **Calibration map**: write a `(F, level, char_order, weight) → deviation_vector` layer into the substrate tensor. Mark Sleeping-Beauty cells (high `dim`, low `char_order`, large deviation) for follow-up.

## 5. Falsification

Newton-Thorne predicts asymptotic Sato-Tate for *every* HMF in this region, including non-trivial nebentypus, so any bulk distributional match at moderate level is *expected* and earns calibration credit, not novelty credit. The signal is **persistent deviation** at fixed-level slices that does not decay with conductor — and it must survive three pattern checks before it can graduate:

- **PATTERN_CONDUCTOR_CONFOUND** — the non-trivial-character cohort is implicitly at larger arithmetic conductor than its matched trivial cohort. Re-match on **effective conductor = level · char_conductor** before claiming structural deviation.
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** — first-30-prime signatures over-weight small primes; the ramified primes of F and of the character sit in that prefix. Recompute with ramified primes excluded and verify deviation persists.
- **PATTERN_BASE_RATE_NEGLECT** — non-trivial-char HMF rows are sparse; small-N Wasserstein noise will mimic deviation. Bootstrap CI per stratum, kill any finding where the trivial-cohort bootstrap CI overlaps zero.

## 6. Budget

Charon ~8h: ~1h LMFDB pull + schema reconciliation, ~2h signature compute + stratify, ~3h distributional battery + bootstrap, ~1h tensor write-back + Sleeping-Beauty flagging, ~1h writeup.

## 7. Expected Outcome

The non-trivial-nebentypus slab is presently a **sparse calibration region** in the substrate tensor — exactly the kind of high-dimensional, under-populated neighborhood `feedback_calibration_anchors_in_depth` instructs the substrate to actively hunt. Per `feedback_tensor_first`, the deliverable is not a paper, not a Sato-Tate counter-claim, and not a bridge narrative; it is a populated `(F, level, char_order, weight) → operator-behavior` cell layer with calibrated deviation vectors against the trivial baseline. Expected outcome: most cells confirm Newton-Thorne agreement (adding anchor density), a small number of moderate-level cells flag non-decaying deviation that survives the three pattern checks (graduates to Aporia follow-up), and the tensor gains navigable substrate in a region that previously read as silence.

Word count ~770
