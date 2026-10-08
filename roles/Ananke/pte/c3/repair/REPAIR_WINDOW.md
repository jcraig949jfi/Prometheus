# 72h push: hours 0-4, repair/instrument window (operator order s2)

Verification. No C1 or C2 result changed.
1. Reductions reproduce from raw rows. REDUCE_C2A/C2B/C2C.json were recomputed from production/rows_*.jsonl.gz with
   the frozen reducers, and each is byte-identical as a parsed object.
2. Prefix and digest tests are exact on current code:
   - the C2B B4X prefix matches C2A at RELAY-0027 idx 2 and FLIP-0167 idx 3: population, champion, status and curve
     all equal (prefix_c2b.json);
   - the C2BX prefix matches C2B at RELAY-0032 idx 7: the gen-144 population and the 36-144 statuses are equal
     (prefix_c2bx.json).
3. CPU/GPU conformance: test_conformance with CUDA, together with test_c2b and test_c2c, gave 110 passed. test_c2a,
   test_c2b and test_c2c on CPU gave 20 passed.
4. Mirror-pair instrument: an independent adversarial review found no FATAL defect and 4 MATERIAL verdict-layer
   issues (research/CORRECTIONS_2026-10-07_SWAP_REVIEW.md). The strongest fixtures still pass: the reviewer ran 42
   tests, and hold_latch S reads FLIP.

New instrumentation:
- **Golden digests:** golden.py and golden_v1.json, 15 specimens. They cover C2 plants, C2A, C2C and C2BX champions,
  and the C1 6f82f9c7 champion. Each is digested through both the training and the held evaluation paths, and the
  check passes.
- **swap_v2.py:** the checked swap described in the corrections note. It supports single register components, so it
  can be used on any new persistent register.
- **Per-generation lineage function curves:** c3_common.evolve_c3, built with C3S.
