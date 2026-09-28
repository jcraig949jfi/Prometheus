# Cosmos GRAVEYARD (killed laws are scientific output)

Currency: 2026-09-28. Machine-checked. Each entry: `### <id> | <campaign> | <law id(s)>` then keys
law, campaign, killed_by, evidence, fragments. `killed_by` names the TRANSFORMATION or TEST that
killed the law. If it has not yet been recovered from the stores, it starts with UNRECOVERED and the
checker counts it. Backfilling those entries is thread T-I1. Nothing is ever deleted from this file.

Seeded from the public C0 record (roles/Cosmos/campaigns/HANDOFF_2026-09-23.md s5), copied exactly.
Coordinates C N K G Q are C0's declared coordinate maps (prometheus/cosmos/contract.py).

### G-0001 | C0 | 424fa143b7 v1
- law: ((N-K)C) <= -.158 AND C - exp(-CN) <= -.136
- campaign: C0
- killed_by: UNRECOVERED -- ledger records FAILED (15.7%); the killing test is to be read from the C0 store
- evidence: HANDOFF_2026-09-23.md s5
- fragments: second atom has the C - f(N) <= t shape shared with survivors

### G-0002 | C0 | d45d1069e0 v1
- law: ((C+K)C) >= .165 AND C - G exp(-N) <= -.061
- campaign: C0
- killed_by: UNRECOVERED -- ledger records FAILED (10.2%)
- evidence: HANDOFF_2026-09-23.md s5
- fragments: atom C - G exp(-N) <= t recurs in SURVIVED law B and in G-0005

### G-0003 | C0 | 964c086e6d v2
- law: C K >= .161 AND C - G exp(-N) <= -.087
- campaign: C0
- killed_by: UNRECOVERED -- ledger records FAILED (23.1%)
- evidence: HANDOFF_2026-09-23.md s5
- fragments: atom C - G exp(-N) <= t (see G-0002); C K product recurs in G-0005 and in law A's (C - log Q) K

### G-0004 | C1 | eec9c5a571 / 9ed4a83871 / 78d3bd6297 (v4)
- law: three v4 candidates (expressions in the C1 store)
- campaign: C1
- killed_by: LOCATION GATE -- the boundary was measured to be in a different place from where the law put it (locate.py)
- evidence: HANDOFF_2026-09-23.md s5; campaigns/c1/
- fragments: UNRECOVERED -- expressions not copied into the handoff; read them from the C1 store

### G-0005 | C2 | c5cd50beb1 v4
- law: C - G exp(-N) <= -.103 AND C K + exp(-Q) >= .512
- campaign: C2
- killed_by: LOCATION GATE -- regs family boundary offset -.168 (outside tolerance)
- evidence: HANDOFF_2026-09-23.md s5; campaigns/c2/
- fragments: the ceiling atom survived in law B (a079ad5ec1) with t = -.102; the location kill came from the other atom or from where the family sits (to be separated, T-I1)

## Cross-entry note (a pattern, not yet a claim)
The atom C - G exp(-N) <= t appears in 3 FAILED laws (G-0002, G-0003, G-0005) and in SURVIVED law B.
Law A carries the related C - (G + exp(-N)) instead. A recurrence like this
is only evidence once it is compared with the base rate of equal-size atoms in the same grammar
(T-I1 kill criterion). Directive s3's warning applies: the C0 law is the shared task's economics
(97.5% agreement with a hand-derived law), so this recurrence may just mean the grammar keeps finding
the planted economics.
