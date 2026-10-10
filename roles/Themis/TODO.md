# Themis TODO

Currency: 2026-10-10T09:45Z (UTC). Closed items are deleted with the closing commit and date, purged after
24 h (base role s7). Full list: BACKLOG_H0H5.md. Native fabric: ops/campaigns/C-012/ (OP-NF2).

C-012 native execution fabric (OP-NF2, 48 h from 2026-10-10T07:15Z):

- [ ] T004 fleet benchmark: prereg FROZEN 2f4b38ef0; run R1 (Arm N + R on ubu001/ubu002) IN PROGRESS from 09:37Z;
      Arm S (M2 ceiling) DEFERRED until M2 is idle (operator experiments on M2 since ~09:30Z); then report + receipt
- [ ] T001 contract v0.2: reviews pending -- Odysseus #1987 (offline since 10-03), Pan (#2010/#2015, design of s6)
- [ ] T005 INTEGRATED, closes on Pan's review of s6 (demo D20261010A passed oracle + crash-replay)
- [ ] T006 engineering review packet (after T004's verdict): moonshot/pivot/C012_NF2_REVIEW_2026-10-10.md
- [ ] First deterministic native-world epoch through the path (OP-NF2), after T004 qualifies the path
- [ ] Odysseus backlog proposals: worker-side capability demand; signal-stopped workers do not deregister
- (closed 2026-10-10, de91e199e) T002 PostgreSQL publication layer
- (closed 2026-10-10, 974275bca) T003 two-node demonstration Q20261010A

Other lanes:

- [ ] Lane A: claim map (R-CLAIMMAP) with Palamedes -- OP-NF2 L180 "Continue ... RSO claim-mapping work with the
      respective owners": research in progress; draft v0.1 next, then propose to Palamedes
- [ ] Lane B: F09 regression handed to Daedalus (#2021; ownership question to Hestia #2022) -- await answer
- [ ] THEMIS-12: literature check on evolved integer/quantized nets as organism primitives

Housekeeping:

- [ ] First chartered wake still owes a full read of roles/base-role/MONITORS.md (no loop is owned yet)
- [ ] Report the evidence_wiki pool leak -- DONE as #2002 to Mnemosyne; await acknowledgement
