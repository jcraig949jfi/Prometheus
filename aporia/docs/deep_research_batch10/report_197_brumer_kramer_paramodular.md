# Report 197 — Brumer–Kramer Paramodular Conjecture for Genus-2 Abelian Surfaces

**Aporia Batch 10 / Problem #197**
**Domain:** arithmetic geometry, GSp(4) Langlands modularity
**Substrate role:** operator behavior in the End_Q = Z structural region of the genus-2 abelian variety space.
**Date:** 2026-04-28

## 1. Problem Statement

Brumer–Kramer (2014) conjecture: every abelian surface A/Q with End_Q(A) = Z (the *generic* endomorphism stratum) and conductor N is paramodular. Concretely, there exists a Siegel cusp form f of weight 2 for the paramodular group K(N) ⊂ Sp_4(Q) such that the spin L-function of f equals the Hasse–Weil L-function of A: L(A, s) = L(f, s, spin), with matching local Euler factors L_p(A, T) = L_p(f, T, spin) for every prime p (including bad primes via paramodular new-vector theory). The End_Q = Z restriction excludes RM, QM, and CM surfaces, where modularity reduces to GL(2) constructions (Hilbert/Bianchi/classical). The conjecture is the GSp(4) analogue of BCDT 2001 (modularity of elliptic curves over Q). It is **open in general**; only finitely many cases have been verified, almost all at small conductor with hand-picked Galois representations. From the substrate's view, the question is whether End_Q = Z is the natural structural region in which the spin-L operator acts faithfully on (g2c, smf) pairs.

## 2. Literature

- **Brumer–Kramer (2014)**, *Paramodular abelian varieties of odd conductor*, Trans. AMS. Original conjecture, conductor tables to 1000, paramodular new-vector framework.
- **Brumer–Pacetti–Poor–Tornaria–Voight–Yuen (2019)**, *On the paramodularity of typical abelian surfaces*. Verified ~hundreds of low-conductor cases via Faltings–Serre + Hecke compatibility — the de facto numerical engine.
- **Berger–Klosin (2019, 2022)**: R=T-style results for paramodular forms; partial automorphy in residually-reducible cases — the only general theorems beyond BPP-TVY case checks.
- **Calegari–Geraghty (2018)** modularity machinery and **Boxer–Calegari–Gee–Pilloni (2021)**, *Abelian surfaces over totally real fields are potentially modular*: gives potential automorphy but not the paramodular form over Q itself.
- **Pilloni–Stroh** higher Hida theory; **Mok** GSp(4) endoscopic classification — supplies the spectral side that smf_dims tabulates.
- **He–Lee–Oliver–Pozdnyakov (2022–2024)**: ML-aided searches for paramodular eigenform candidates; useful as a calibration of computational stability vs proof.
- **Cremona–Sutherland LMFDB g2c project**: 66k+ genus-2 curves, End_Q tags, conductor, L-function hashes — operational substrate.
- **Poor–Yuen** paramodular dimension formulas underlying the smf_dims table.

## 3. LMFDB / Corpus Data

- `g2c_curves`: filter `geom_end_alg = Z` AND `end_alg = Z` (excludes the non-generic stratum); `cond <= 10^4` for tractability.
- `smf_dims`: paramodular K(N) Siegel cusp form dimensions, weight 2; rows where `dim_new >= 1` are the modularity candidates.
- `lfunc_lhash` / `lfunctions.l_functions`: cross-table join via `lhash` to test whether the surface's L-function already coincides with a known SMF L-function in LMFDB.
- `g2c_endomorphisms`: confirms End_Q stratum (essential — End mis-tags are the dominant historical false-match source).
- `mf_hecke_lpolys`: GL(2) sanity probe for the rare reducible-Galois cases.

## 4. Test Design

1. **Cohort build.** Pull all `g2c_curves` with End_Q = Z (principally polarized abelian surface) and `cond <= 10^4`. Stratify by conductor decade to defuse PATTERN_CONDUCTOR_CONFOUND (do not pool across N).
2. **SMF candidate set.** For each N, query `smf_dims` weight-2 K(N) new-form dimension. Discard N with dim = 0 (conjectural counterexample candidates — log separately).
3. **Local factor computation.** For each surface A and each prime 2 ≤ p ≤ 100, p ∤ N, compute L_p(A, T) ∈ Z[T] via point counts mod p, p^2 (degree-4 polynomial). For each candidate paramodular form f at level K(N), compute the spin Euler factor L_p(f, T, spin) from Hecke eigenvalues T(p), T_1(p^2).
4. **Match operator.** Define M(A,f) = product over p ≤ 100 of indicator{L_p(A,T) = L_p(f,T,spin)}. Calibrate on BPP-TVY anchors (must score 1.0). Bucket: (i) M=1 on verified-modular, (ii) M=1 on previously-unmatched A — *calibration candidate*, (iii) dim > 0 but no match — *open case*, (iv) dim = 0 — *conjectural obstruction*.
5. **Bad-prime audit.** For p | N, compare conductor exponents (Ogg/Saito) on A-side with paramodular level decomposition on f-side; mismatches here are the strongest individual falsifiers.

## 5. Falsification

- **Calibration anchors:** the BPP-TVY verified set must all return M = 1.0. Any anchor failure halts the run — implementation bug, not finding.
- **PATTERN_CONDUCTOR_CONFOUND:** never pool match-rates across conductor; report per-N.
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT:** small primes dominate Euler-product likelihood; require match across the full p ≤ 100 window, not just p ≤ 13.
- **PATTERN_BASE_RATE_NEGLECT:** at small N the K(N) new-form dimension is often 1, so a "match" carries low information. Report the per-N dimension and adjust evidential weight accordingly.

## 6. Budget

Charon ~10h: ~2h cohort + endomorphism filter; ~3h Euler-factor enumeration to p ≤ 100; ~3h spin-L computation from smf Hecke data; ~2h match-operator + per-N stratified report.

## 7. Expected Outcome

Per **feedback_calibration_anchors_in_depth**, the deliverable is *anchor density* in the End_Q = Z stratum of g = 2 abelian variety space — exactly the high-dimensional, under-explored substrate region the doctrine flags. Per **feedback_tensor_first**, this populates `g2c × smf` slabs in the unified signature-keyed tensor with calibrated spin-L coincidences. Per **feedback_domains_are_docstrings**, "paramodular" is a behavior of the spin-L operator on a structural region, not a discipline label — the report stays inside the operator. The frontier outcome is a clean tri-partition (verified / calibration-candidate / open) at fixed N; the backstop outcome is a refined catalogue of dim-zero conductors, each a candidate counterexample worth escalating.

Word count ~735
