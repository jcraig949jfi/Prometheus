# Themis TODO

Currency: 2026-10-10T11:48Z (UTC). Closed items are deleted with the closing commit and date, purged after
24 h (base role s7). Full list: BACKLOG_H0H5.md. Native fabric: ops/campaigns/C-012/ (OP-NF2).

C-012 native execution fabric (OP-NF2, 48 h from 2026-10-10T07:15Z):

- [ ] Operator decision on the review packet's s7 (moonshot/pivot/C012_NF2_REVIEW_2026-10-10.md): A adopt and
      park (lean) / B harden now / C stop / D offer to the RSO Observatory -- awaiting the operator
- [ ] T001 contract: Pan reviewed s6, no change (#2031); Odysseus #1987 pending (last active 2026-10-03); write
      contract v0.3 recording what T004-T007 added (receipts and materializations as events, catalog_v, the
      native runtime, the production schema)
- [ ] T004 Arm S (P5): only if the operator wants it, M2 idle, under the frozen preregistration
- [ ] Odysseus backlog proposals (#2026): worker-side capability demand; signal-stopped workers do not deregister
- (closed 2026-10-10, de91e199e) T002 PostgreSQL publication layer
- (closed 2026-10-10, 974275bca) T003 two-node demonstration Q20261010A
- (closed 2026-10-10, b08cb59fd) T004 preregistered benchmark R1
- (closed 2026-10-10, eaf9feba4) T005 lake materialization
- (closed 2026-10-10, b82a0cc0d) T006 engineering review packet
- (closed 2026-10-10, 454f86443) T007 first native-world epochs N20261010A
- (done 2026-10-10, #2043 + correction #2044) C-013's N1-N5 asks of C-012 answered

Other lanes:

- [ ] Lane A: claim map v0.1 DRAFT sent to Palamedes (#2028; design/CLAIM_MAP_v0.1.md) -- answers after C-013
      (ends 2026-10-12T06:45Z) become v0.2; contract-level gaps go their versioned route (operator)
- [ ] Lane B: F09 regression handed to Daedalus (#2021; ownership question to Hestia #2022) -- await answer
- [ ] THEMIS-12: literature check on evolved integer/quantized nets as organism primitives

Housekeeping:

- [ ] First chartered wake still owes a full read of roles/base-role/MONITORS.md (no loop is owned yet)
- [ ] evidence_wiki pool leak reported as #2002 to Mnemosyne; await acknowledgement
