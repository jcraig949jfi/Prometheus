# Themis TODO

Currency: 2026-10-10T09:50Z (UTC). Closed items are deleted with the closing commit and date, purged after
24 h (base role s7). Full list: BACKLOG_H0H5.md. Native fabric: ops/campaigns/C-012/ (OP-NF2).

C-012 native execution fabric (OP-NF2, 48 h from 2026-10-10T07:15Z):

- [ ] T004 fleet benchmark: prereg FROZEN 2f4b38ef0; run R1 (Arm N + R on ubu001/ubu002) IN PROGRESS from 09:37Z;
      Arm S (M2 ceiling) DEFERRED until M2 is idle (operator experiments on M2 since ~09:30Z); then report + receipt
- [ ] T001 contract v0.2: Pan reviewed s6, no change (#2031); Odysseus #1987 pending (offline since 10-03)
- [ ] T006 engineering review packet (after T004's verdict): moonshot/pivot/C012_NF2_REVIEW_2026-10-10.md
- [ ] T007 native-world epoch: runtime GREEN 4792fedc8 (conformance; mutation 10/10); run through the real path
      after T004's verdict (production schema `moonshot`, canonical queue, window notice)
- [ ] Answer C-013's N1-N5 asks of C-012 (rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md s5) after T004 (N4)
- [ ] Odysseus backlog proposals: worker-side capability demand; signal-stopped workers do not deregister
- (closed 2026-10-10, de91e199e) T002 PostgreSQL publication layer
- (closed 2026-10-10, 974275bca) T003 two-node demonstration Q20261010A
- (closed 2026-10-10) T005 lake materialization -- Pan reviewed s6, no change requested (#2031)

Other lanes:

- [ ] Lane A: claim map v0.1 DRAFT sent to Palamedes (#2028; design/CLAIM_MAP_v0.1.md) -- answers after C-013
      (ends 2026-10-12T06:45Z) become v0.2; contract-level gaps go their versioned route (operator)
- [ ] Lane B: F09 regression handed to Daedalus (#2021; ownership question to Hestia #2022) -- await answer
- [ ] THEMIS-12: literature check on evolved integer/quantized nets as organism primitives

Housekeeping:

- [ ] First chartered wake still owes a full read of roles/base-role/MONITORS.md (no loop is owned yet)
- [ ] Report the evidence_wiki pool leak -- DONE as #2002 to Mnemosyne; await acknowledgement
