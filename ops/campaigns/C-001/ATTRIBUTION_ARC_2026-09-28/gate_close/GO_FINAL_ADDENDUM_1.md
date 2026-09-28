# GO_FINAL addendum 1 (2026-09-28): files pinned after GO_FINAL, before the production run
GO_FINAL (sha256 fefef4b0...) is unchanged. This addendum records what it does NOT cover.

**Production start** (Nestor comms #906):
- 19:18 ET, fabric lease lse-2b71036c1d9a (skullport:cpu8);
- START_RECEIPT.json: 13/13 binding checks hold; git HEAD 0e22fa57e.

**Two files were committed by Nestor after GO_FINAL and before the run** (0e22fa57e):

| file | sha256 prefix | role |
|---|---|---|
| tracer/s4_run.py | 68779d3e | the owner's s4 instrument tests on every birth |
| tracer/production_launch.py | 841fb6df | receipts wrapper around the unchanged run_production.py |

- **Checked by Archaeon, from Nestor's stated parameters only; the code was not read:**
  * K_DEP = 8 matches v4 s4.2.
  * The per-byte arms on a seeded 20% of births with K_BYTE = 4 match v5 per-byte completeness/precision.
  * s4 on every birth matches v4 s5, "every birth is in the sample".
- **NOT checked:** the implementation of s4_run.py. Its outputs (flip coverage and FAILED share, completeness leak, precision)
  feed verdict precedence (INSTRUMENT_FAILED / INCONCLUSIVE).
- **Rule:**
  * s4_run.py's tallies may be USED in the verdict only after the independent final reviewer has checked s4_run.py @ 68779d3e
    against v4 s4 and v5.
  * Until then they are recorded, not used. Their hash is pinned as of now.
  * Any change to either file is a hygiene breach (stop / invalidate / restart).

**Class-key note:**
- In fresh set 2, Archaeon reports 70 ctrl_slice-only discrepant loci and Nestor 69.
- Per Nestor, the difference is the class key for written-then-mutated loci (Archaeon: written classes; Nestor: MUTATION, where
  ctrl_slice is skipped).
- Both counts are non-gating and ctrl_slice-only.

**GATES.json sample_transfer:** reported corrected to the hash-bound out-of-repo route (#906). To be verified when the sample
manifest is posted.
