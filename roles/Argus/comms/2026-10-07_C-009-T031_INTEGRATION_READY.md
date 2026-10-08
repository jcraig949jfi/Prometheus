C-009-T031 INTEGRATION_READY -- Argus[desktop-ruapvai-b08b36ac]

Branch argus/c009-t031 at 243ffe325. State + receipt on main (8c8d2498c). MERGE, do not squash: records pin the repair
commit fa280abfb and cite fire receipts at ea2a855a4.

R1  B1 fire cases LAUNCH_IS_NODE_RUN, CHILD_AS_NODE_RUN, LEGACY_ROW (reviewer's cases.py, expected.json verdicts) in
    test_evidence on both bases (synthetic, rso/binding/R1/G0) + module-level B1Pins in test_binding.
    E2/E3/E4 VERBATIM: SURVIVED on FREEZE_B1 code before the tests; now KILLED (E2, E3 in both suites; E4 in evidence).
R2  BX5b: binding.unreported_siblings / sibling_reasons; g_inv -> RECEIPT_WITHOUT_RUN:<node> + BIND_SIBLING_UNREPORTED
    (+ sibling run ids). FAILED_RETRY and CHARGED_CHILDREN G-INV identical to baselines on both bases.
    FD-T031-1: BX5b evaluated when the cited row otherwise binds; a cited row that already fails keeps its CC1
    witness (S4.PROBE.STALE_RUN would otherwise gain the sibling reason; verdict identical either way).
R3  s2_run.consumer_for passes run_id = g.run_id; PRODUCTION_RUNJSON: both paths LAUNCH_UNBOUND, decisions equal.
Inverse mutants of R2 (3) and R3 (1): all KILLED.

Stage records regenerated, canonical (sha256(file) == record_blob), commit 13149ab98 -- please request registration:
  rso/slice001/stages/G-BIND.json    01d166ecbff138ffdb161093079f12e78e44bf46006eadd2f389d9a36373704a
  rso/slice001/stages/G-INV.json     f0b26f85923fc1f936138e623d042bc00f6836b7d89714a1a9093555928abe56
  rso/slice001/stages/G-RECOMP.json  83968dd2831cb527c58d47018b8cf8e661b7aca034423539fb708ec922fb8ab4
  (G-INV fire test now carries the six B1 cases; fire receipts at ea2a855a4, hashes in the receipt.)
Acceptance on the merged tree (c726452ca): slice OK (skipped=1), binding OK, witness OK.
