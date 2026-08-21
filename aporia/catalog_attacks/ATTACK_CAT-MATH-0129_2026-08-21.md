# ATTACK CAT-MATH-0129 — Erdos minimum overlap, exact n<=12 (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P56) | Code: attack_0129_0154.py | Data: attack_0129_0154_results.json

Pre-stated readings: REVIEWER-REPRODUCED-EXACT (M(1..12)=1,1,2,2,3,3,3,4,4,5,5,5) /
MISMATCH (instrument audit first) + TREND-DESCRIPTIVE (no bracket comparison — the
reviewer's correction removed an unfalsifiable criterion).

Result: exact match on all 12 values in 5s — FFT cross-correlation over all subsets
with 1 pinned in A (complement symmetry halves the space; n=12 sweeps C(23,11) =
1,352,078 subsets in chunked rfft batches). M(n)/n trend: 1.0, 0.5, 0.667, 0.5, 0.6,
0.5, 0.4286, 0.5, 0.4444, 0.5, 0.4545, 0.4167 — descriptive only; the n<=12 regime
oscillates and licenses no statement about the limit constant.

Trace-vector: problem_id CAT-MATH-0129 | operations [complement-symmetry-pinning,
chunked-fft-cross-correlation, exact-min-max] | kill_pattern none | residue: FFT
cross-correlation turns per-subset difference histograms into a batched O(L log L)
primitive — reusable for any translation-overlap optimization
