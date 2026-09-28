# G2 FRESH SET 2: seed record (Amendment C10 s5). The SHA of the commit that adds this file is the seed

- **Nestor's tracer, re-frozen v3:**
  * commit b187824e6ac1ee75c0d8403259c04cec7c5b2a07;
  * TRACER_FREEZE.json sha256 (LF) 77a822acb7203295c28187b16a93d368bb0a8cf1bc72a3630aed304015d4bc3e, verified by Archaeon;
  * run_production.py c31cca76b7458dfb048c6b4d895935926353021919501185ef27ab0daf4c42c4 (unchanged).
- **Reference, re-frozen C10:** ref_tracer_npe.py sha256 (LF)
  157374444597750fe114602cd83fa02faa36048161889b06f15e40d4ec7d7368 (commit 9d7eafcf5).
- **Generator:** npe_fresh_set.py, unchanged since set 1.
- **Exporter:** npe_fresh_ref.py, with the C10 serialization (2a0d58b6c).
- **Comparison:** npe_fresh_compare.py, unchanged in logic.
  * The sealed hashes are read from SEALED_HASHES_SET2.json, which is committed before either output is opened.
- **Declaration:** as for set 1 (FRESH_SET_COMPARISON_DECLARATION.md), except that no MUTATION encoding gap is expected.
  * **GATE:** raw, per class, >= 0.995, on label, addr, ctrl and exec, applied to set A AND to set M.
  * **Diagnostics:** d1-d4.
- **S3 (ctrl_slice):** open, non-gating, diagnosed as the IN guard (D6: Nestor's reading is empty, the reference's is a's deps).
