# Lehmer Brute-Force — deg-12 ±5 palindromic

**Date:** 2026-05-07 (Fire #8, T-2026-05-07-T007 path-(ii) reframe of T001)
**Subspace:** deg-12 reciprocal palindromic integer polys, coefficients in [-5, 5], c_0 > 0 canonical
**Polys enumerated:** 8,857,805 (5 × 11^6 after canonical sign-fix; matches expected = 8,857,805)
**Wall time:** 437.1 seconds (sequential, single worker via `prometheus_math.lehmer_brute_force_general.run_brute_force_general`)
**Module:** `prometheus_math/lehmer_brute_force_general.py` — NEW parameterized deg-N brute-force (within Techne file ownership; NO contract change to scripts/)
**Verdict:** **INCONCLUSIVE** (raw band hits = 113; verification phase required before strength can rise above `bounded_complete`; triangulation paths to apply: high-precision mpmath, symbolic factorization, factorization-aware catalog lookup — see Day-5 Lehmer deg-14 prototype)

---

## TL;DR

8,857,805 deg-12 ±5 palindromic polynomials enumerated sequentially through the parameterized brute-force pipeline. Mahler measures computed via `techne.lib.mahler_measure.mahler_measure_padded` (numpy companion-matrix eigvals, batched in groups of 5,000). Band filter: `1.000001 < M < 1.18`.

| Outcome | Count |
|---:|---:|
| Polys enumerated | 8,857,805 |
| Raw band candidates (numpy filter) | 113 |

This is the deg-12 sister run to the Day-5 sprint's deg-14 ±5 enumeration (which surfaced 43 verified band hits → INCONCLUSIVE → triangulated to H5_CONFIRMED-local-lemma). The deg-12 enumeration uses the same algorithm and the same band semantics; the parameterized module mirrors the per-shard return shape of `scripts/_lehmer_brute_force_worker.process_shard_worker` for downstream-pipeline compatibility.

## Raw band candidates (pre-verification)

| Idx | half-coeffs | M_numpy |
|---:|---|---:|
| 0 | (1, -2, 3, -2, 2, -2, 3) | 1.000009 |
| 1 | (1, 1, 2, 1, -1, -2, -4) | 1.000010 |
| 2 | (1, 2, 2, 0, -2, -2, -2) | 1.000010 |
| 3 | (1, 2, 3, 2, 2, 2, 3) | 1.000010 |
| 4 | (1, -2, 2, 0, -2, 2, -2) | 1.000010 |
| 5 | (1, 2, 3, 4, 3, 2, 2) | 1.000011 |
| 6 | (1, -1, 2, -1, -1, 2, -4) | 1.000011 |
| 7 | (1, -1, 0, 3, -2, -1, 4) | 1.000011 |
| 8 | (1, -2, 3, -4, 3, -2, 2) | 1.000011 |
| 9 | (1, 0, 2, 2, 2, 4, 2) | 1.000011 |
| 10 | (1, 0, 1, -3, 1, -2, 4) | 1.000012 |
| 11 | (1, 1, 0, -3, -2, 1, 4) | 1.000012 |
| 12 | (1, 1, 3, 2, 3, 1, 2) | 1.000012 |
| 13 | (1, -1, 3, -2, 3, -1, 2) | 1.000012 |
| 14 | (1, 0, 1, 3, 1, 2, 4) | 1.000012 |
| 15 | (1, 0, 2, -2, 2, -4, 2) | 1.000012 |
| 16 | (1, 1, 2, 3, 4, 5, 4) | 1.000013 |
| 17 | (1, -1, 2, -3, 4, -5, 4) | 1.000013 |
| 18 | (1, 1, 1, -2, -1, -1, 2) | 1.000013 |
| 19 | (1, -2, 3, -1, -1, 4, -4) | 1.000013 |
| 20 | (1, 2, 3, 1, -1, -4, -4) | 1.000013 |
| 21 | (1, -1, 1, 2, -1, 1, 2) | 1.000013 |
| 22 | (1, 0, 3, 1, 3, 3, 2) | 1.000014 |
| 23 | (1, -1, 3, -3, 3, -4, 2) | 1.000014 |
| 24 | (1, 0, 3, -1, 3, -3, 2) | 1.000015 |
| 25 | (1, 1, 3, 3, 3, 4, 2) | 1.000015 |
| 26 | (1, 1, 3, 1, 4, 1, 5) | 1.000016 |
| 27 | (1, -2, 4, -3, 3, 0, 1) | 1.000016 |
| 28 | (1, 2, 4, 3, 3, 0, 1) | 1.000016 |
| 29 | (1, -1, 3, -1, 4, -1, 5) | 1.000016 |
| ... | (83 more entries elided) | ... |


---

## Why this run lives in `prometheus_math/` and not `scripts/`

Per ticket T-2026-05-07-T007 + Fire #1's BLOCKED resolution on T001:
`scripts/run_lehmer_brute_force.py` and `scripts/_lehmer_brute_force_worker.py`
have `DEGREE: int = 14` hardcoded at module level, and `scripts/` is outside
Techne's file ownership (sigma_kernel/, prometheus_math/,
harmonia/memory/architecture/sigma_kernel*.md). Running on deg-12 via the
existing CLI would require either (a) adding a `--degree` flag to scripts/
(contract change), or (b) modifying `DEGREE` in scripts/ (file-ownership
violation). Aporia 2026-05-07 elected path (ii): build the parameterized
module in prometheus_math/ instead. Existing scripts/ entrypoint untouched;
deg-14 runs continue to work exactly as before.

---

## What this run does NOT cover

Same scope cuts as Day-5's deg-14 raw-enumeration phase before the Path A/B/C/D
triangulation:

* Mpmath-precision recheck of band candidates (would reduce false positives from
  numpy-eigvals float-noise near band edges)
* Cyclotomic-noise filter (M ≈ 1.0001 + has_cyclotomic_factor + M_mpmath=NaN)
* Mossinghoff catalog cross-check (rediscovery vs novel)
* ExclusionCertificate registration (would consume `prometheus_math/.../exclusion_certificates/`
  pattern; needs the verification phase to certify strength=COMPLETE per Aporia
  2026-05-05 hard rule)

These verification phases are tractable as a follow-up ticket; if non-empty
band candidates surfaced (see verdict above), the next fire would queue them
for triangulation via the Day-5 protocol.

---

## Cross-reference

* Module: `prometheus_math/lehmer_brute_force_general.py`
* Tests: `prometheus_math/tests/test_lehmer_brute_force_general.py` (21 tests)
* Raw JSON: `prometheus_math/_lehmer_brute_force_deg12_results.json`
* Day-5 deg-14 prototype: `prometheus_math/LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md`
* T-2026-05-06-T001 (SUPERSEDED): see `aporia/meta/queue/techne_inbox.jsonl`
* T-2026-05-07-T007 (this fire): see `aporia/meta/queue/techne_inbox.jsonl`
