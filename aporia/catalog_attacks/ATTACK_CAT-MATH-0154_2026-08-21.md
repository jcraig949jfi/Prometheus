# ATTACK CAT-MATH-0154 — EFL small-case (CALIBRATION, spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P56) | Code: attack_0129_0154.py | Data: attack_0129_0154_results.json

Pre-stated readings: ALL-COLORABLE (expected; classically settled small n) /
VIOLATION-FOUND (instrument-bug-first at extreme prior) / SEARCH-BUDGET-EXCEEDED
(honest timeout class, counted not hidden).

Result (generation pinned per the reviewer's correction):
- EXHAUSTIVE canonical enumeration for n<=4 (cliques added with fresh-vertex ordering,
  deduped by intersection-signature canonicalization over clique relabelings):
  n=2: 2 configs, n=3: 5, n=4: 16 — all n-colorable (0 violations).
- RANDOMIZED SAMPLING (stated as sampling, NOT exhaustive) for n=5..7: 200 seeded
  configs each, all n-colorable, 0 search timeouts (budget 2e6 nodes).

CALIBRATION (label binding): certifies the configuration-generation + exact-coloring
harness. Small-n EFL is classically settled and the large-n theorem (AA-068, KKKMO) is
where the result actually lives; a PASS here is harness certification only.

Trace-vector: problem_id CAT-MATH-0154 | operations [canonical-generation,
intersection-signature-dedup, most-constrained-first-backtracking, seeded-sampling] |
kill_pattern none | residue: the timeout CLASS in the pre-stated readings (count,
never hide) is what keeps sampling honest when search cost varies per instance
