# Aporia #184 — Mahler-Manin p-adic Mahler measure (deep research brief)

Status: open empirical question. Owner: Charon (extends Batch 9 Lehmer audit infrastructure). Date: 2026-04-28.

## 1. Problem Statement

For P(x) = a_d * prod (x - alpha_i) in Z[x], the (archimedean) Mahler measure is M(P) = |a_d| * prod_{|alpha_i|>1} |alpha_i|, and m(P) = log M(P). Lehmer (1933) asked whether inf m(P) over non-cyclotomic P is bounded below by a positive constant; Lehmer's polynomial L(x) = x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1 attains M(L) = 1.17628081825991... and remains the empirical record after ninety-three years (Smyth, Boyd, Mossinghoff, Mossinghoff-Rhin-Wu). The conjecture is open.

Mahler-Manin (1980s-2000s, formalised in work of Manin, Besser-Deninger, Brunault-Zudilin) extends the construction to a non-archimedean place v | p of Q_bar by replacing |alpha_i| with the p-adic absolute value |alpha_i|_p (normalised so |p|_p = 1/p). Define m_p(P) = sum_{|alpha_i|_p > 1} log_p |alpha_i|_p. Open empirical question: across LMFDB number fields and explicit polynomial families, do p-adic Mahler measures cluster, and is there a Lehmer-analogue lower bound m_p >= c_p > 0 for non-degenerate (non-cyclotomic, non-p-power-cyclotomic) inputs?

## 2. Literature

- Lehmer, "Factorization of certain cyclotomic functions," Ann. Math. 34 (1933) — origin polynomial and bound.
- Smyth, "On the product of conjugates outside the unit circle of an algebraic integer," Bull. LMS 3 (1971) — non-reciprocal lower bound 1.32... (Smyth's constant).
- Boyd, "Reciprocal polynomials having small measure," Math. Comp. 35 (1980); Mossinghoff catalogue (mossinghoff.info/lehmer/) — Salem/Lehmer reciprocals up to degree 44.
- Manin, "p-adic automorphic functions" (1973) and later notes on p-adic Mahler measure.
- Besser-Deninger, "p-adic Mahler measures," J. Reine Angew. Math. 517 (1999) — formal m_p(P) with regulator interpretation.
- Brunault-Zudilin, "Many Variations of Mahler Measures," CUP 2020 — survey, non-archimedean chapter.
- Borwein-Dobrowolski-Mossinghoff (2007) — Mahler measure and Lehmer's problem for polynomials with odd coefficients.
- Mossinghoff-Rhin-Wu (2008-2018) — exhaustive search to degree 44 (archimedean); no exhaustive p-adic analogue known to substrate.

## 3. LMFDB / Corpus Data

- `nf_fields` (LMFDB mirror, devmirror.lmfdb.xyz; reference_lmfdb_postgres.md): defining polynomials, discriminants, signature for degree 1-47.
- `F:/Prometheus/charon/scripts/lehmer_spectrum_audit.py` — already pulls nf_fields per degree d in [2..60], parses coeffs, calls `techne.lib.mahler_measure.mahler_measure`. Direct fork target.
- `F:/Prometheus/charon/scripts/lehmer_exhaustive_deg8_14.py` — exhaustive monic enumeration deg 8..14, archimedean.
- `F:/Prometheus/charon/scripts/lehmer_nf_scan.py`, `lehmer_gap_deep.py` — sibling Batch 9 scripts.
- Mossinghoff Salem/Lehmer reciprocal catalogue (external, mirrored under harmonia/memory/catalogs/lehmer.md per audit script header).
- Cyclotomic family: phi_n(x) for n <= 200 (constructed; m = 0 archimedean, m_p = 0 unless p | n).

## 4. Test Design

1. **Pull polynomial corpus.** Reuse `lehmer_spectrum_audit.py` cursor logic for NF defining polynomials degree 2..14 (cap 10K/degree); union with cyclotomic phi_n (n in [3,200]), Mossinghoff Salem catalogue (~80 polys), Lehmer-style reciprocal sweep from `lehmer_exhaustive_deg8_14.py` outputs.
2. **Compute m_p.** For each P and p in {2,3,5,7}: factor P over Q_p via Newton polygon (slopes of conv hull of (i, v_p(a_i)) give multiplicities of |alpha|_p = p^{-slope}). Sum negative slopes weighted by multiplicity to get m_p(P) = sum (-slope_i) * mult_i * log p. Implement in `techne/lib/padic_mahler.py` (numpy + sympy QQ, no Sage dependency).
3. **Stratify (degree, family, p).** Calibration map axes: d in 2..14 x family in {NF, cyclotomic, Salem, Pisot, Lehmer-reciprocal} x p in {2,3,5,7}. Report min, p1, p5, p50, max of m_p; count m_p == 0; count m_p in (0, log p / d).
4. **p-stability check.** Per P, vector (m_2, m_3, m_5, m_7); Spearman across pairs. If r > 0.9 across all pairs, suspect PATTERN_PRIME_GRAVITATIONAL_OVERFIT — m_p driven by global structure (disc factorisation), not p-local content. Detrend by sum_p m_p before any clustering claim.
5. **Lehmer-analogue lower bound probe.** Per (d, p), min m_p over non-cyclotomic, non-p-power-cyclotomic P. Fit m_p_min(d) = c_p + C_p * d^{-alpha_p} mirroring archimedean fit. Report (c_p, alpha_p) per p with bootstrap CI; flag any P with m_p < c_p / 10 as candidate p-adic Lehmer outlier (verify by hand).

## 5. Falsification

Calibration anchors (must hit, else implementation is wrong):
- Cyclotomic phi_n: m_p(phi_n) = 0 unless p | n; if p | n, m_p computed from ramification of Q_p(zeta_n)/Q_p.
- Lehmer's L(x) at archimedean: m_infty(L) = 0.16235767... (sanity for shared `mahler_measure` path).
- Mahler inequality, p-adic form: m_p(P) <= (1/2) log_p |disc(P)|_p + O(1). Any m_p exceeding disc-derived ceiling is a bug.

Pattern hazards:
- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** — m_p inflated whenever p | disc(P); claim must survive disc-stratification (bin by v_p(disc)).
- **PATTERN_CONDUCTOR_CONFOUND** — degree d acts as conductor analogue (more roots, more chances for |alpha|_p > 1). Report rate per degree, compare against d * E[m_p | random Newton polygon].
- **PATTERN_BASE_RATE_NEGLECT** — most NF polys have m_p = 0 for fixed p (unramified); interesting tail is small. Do not let "median m_p = 0" be sold as a clustering result.

## 6. Budget

Charon ~6 hours: 1h port audit script to p-adic via Newton polygon (`techne/lib/padic_mahler.py`); 1h calibration anchors (cyclotomic, Lehmer, disc bound); 2h corpus sweep deg 2..14 x p in {2,3,5,7}; 1h stratification + null; 1h JSON artefact + discoveries note. Pure CPU; no LLM cost.

## 7. Expected Outcome

Per feedback_calibration_anchors_in_depth: deliverable is the (degree, family, p) -> m_p calibration map itself, written to `aporia/mathematics/mahler_padic_v1.json` and indexed for the unified tensor (feedback_tensor_first). Whether or not a Lehmer-analogue c_p > 0 emerges, the substrate gains a non-archimedean coordinate alongside the archimedean Lehmer audit, currently a one-place picture. Pairs with the archimedean Lehmer attack stack (Batch 9, audit + exhaustive deg 8..14). Negative result (m_p collapses to disc-driven trivialities after stratification) is equally valuable — it kills the naive p-adic Lehmer formulation and forces a non-degeneracy condition (Besser-Deninger's "tempered" hypothesis) into the statement.

Word count ~770
