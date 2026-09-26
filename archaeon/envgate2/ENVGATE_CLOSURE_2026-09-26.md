# ENVGATE line -- closure record (2026-09-26)

Author: Archaeon[m2-1034e815]. Authority: operator ruling PORTABILITY-01 s1
(roles/Archaeon/prompts/2026-09-26_portability01/00_OPERATOR_RULING_verbatim.md). This record modifies NO frozen ENVGATE
file. PREREG, PREFLIGHT, RESULTS, RUNS_MANIFEST, runs/ and both evidence archives are left exactly as they were.

## Final state of the line

| item | state | record |
|---|---|---|
| ENVGATE-01 | frozen output GATING_CAUSALLY_SUPPORTED; **adjudicated GATING_PARTIALLY_SUPPORTED** (ruling R1) | archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md |
| ENVGATE-02 | **WINDOW_NOT_SUPPORTED**; the Phase-C gate failed on condition 6 | archaeon/envgate2/VERDICT_2026-09-26.md (c5ba19571) |
| Environmental blocking (window 120..135 open vs blocked) | **REPLICATED** under genetic identity: U 24 vs BAND0 5; 12+/2- blocks; Page's L p = 0.001 | ENVGATE-02 RESULTS.json |
| Proposed viable-window mechanism (rescue by 128 / 128..131 / 125..128) | **NOT SUPPORTED**: rescue arms 5 / 3 / 2 vs all-blocked 5 | same |
| Host-mediated reproduction (inert host executes a resident copier and emits the resident's genome) | stands as a mechanism (ruling R2): genome amplification, not origination | ADJUDICATION_ADDENDUM; archaeon/tests/test_lineage_attribution.py tests 02, 09, 10 |
| RIE-01 | **correctly NOT launched.** Its precondition, the Phase-C gate, failed. It stays staged and unfrozen | archaeon/rie/ |
| ENVGATE-03 | NOT to be launched (PORTABILITY-01 s16) | -- |

## Retained fossils (unresolved; NOT allocation targets)
- **The five BAND0 establishments.** Genetic establishments in the all-blocked arm, against a planned ~0.7 total. Per-block
  rows are in ENVGATE-02 RESULTS.json (`per_block`, `established_glins`). They stay unexplained, and no campaign will be
  spent on them now.
- **Blocks 11, 13, 14 of ENVGATE-02.** Most non-U establishments fall in these blocks, and they were also the slowest
  (5.9 / 3.3 / 5.9 h against a median of 1.0 h). They are kept as forensic fossils. Block files are in
  C:\Prometheus-data\evidence\envgate02_2026-09-26\runs\ (sha256 in RUNS_MANIFEST.json).
- **ENVGATE-01 block 13** (host rescue: a near-copier's genome propagated with help from a foreign executor) and
  **ENVGATE-01 block 15** (a takeover world whose many parent-chain host labels collapse to ONE resident genetic lineage).
  Evidence: C:\Prometheus-data\evidence\envgate01_2026-09-24\.

## Recorded deviation (ENVGATE-02 analysis entry point)
The frozen `analyze.main()` read `pre["blocks"]`, but PREREG holds the list at `pre["spec"]["blocks"]`. analyze.py was not
edited, so its preregistered hash is intact. `_analysis_wrapper_2026-09-26.py` calls the frozen `analyze.analyze()` with the
correct block count (24) and writes the same RESULTS.json main() would have written. Full text in VERDICT_2026-09-26.md.

The ENVGATE line is closed. The machinery it produced (archaeon/lineage/: taint VM, four identities per birth, genetic
lineage, genetic establishment) is carried forward into PORTABILITY-01 as ONE realization of a substrate-neutral contract.
