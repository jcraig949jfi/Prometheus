# Themis TODO

Currency: 2026-10-06T10:20Z (UTC). Closed items are deleted with the closing commit and date, purged after
24 h (base role s7). Full list: BACKLOG_H0H5.md. Lane C state: ops/campaigns/C-008/.

Lane C (C-008, OP-LC1):

- [ ] T005 D5 node auto-join without auto-authorization: moonshot/epoch/join.py + tests/test_d5_join.py,
      then one real join on ubu002 against a LAN remote
- [ ] T003 D4 LAN baseline -- BLOCKED: M2 saturated by Aether AIM02 (frozen rig R1 = 6 workers on M2), or
      ssh from M2 to ubu003-006 (then amend the prereg rig BEFORE any data). Tooling ready (moonshot/epoch/bench.py)
- [ ] T004 D4 GitHub arm -- BLOCKED on the operator: dedicated private repository + deploy key
      ~/.ssh/moonshot_c008_t004_deploy.pub (or gh login on M2). Then: ssh -T spillover check, G1-G7, <= 250 writes
- [ ] Review packet for C-008 at session close
- (closed 2026-10-06, 2a86d4db9) T001 D1+D2 under the D3 matrix; T002 D4 preregistration

Other lanes (not Lane C; unchanged):

- [ ] Lane A: draft the M1 claim-map message to Palamedes (hold for operator approval before sending)
- [ ] Lane B: write the wforge F09 red affordability regression and hand it to Daedalus
- [ ] THEMIS-12: literature check on evolved integer/quantized nets as organism primitives

Housekeeping:

- [ ] First chartered wake still owes a full read of roles/base-role/MONITORS.md (no loop is owned yet)
