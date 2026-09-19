# Phase 2 -- the frozen pilot selection

FROZEN 2026-09-19T12:42:52Z, before any BEE run. Machine-readable: SELECTION_FROZEN.json, sha256(LF) = 2ea70e5908625c1c07292b09aa21c264ff9f72840db065f6a72ee767eef98be9.
The six were chosen from the Atlas index (M1, read-only) by the rule in the JSON; the file also records what was
NOT selected and why.

| slot | role | Atlas experiment_key | engine | class | executor-free question (short) |
|---|---|---|---|---|---|
| 1 | established positive result | nestor.graphworld/r1:E10-linear-closed-vs-open-128-seeds | npe | POSITIVE | closed-loop vs open-loop organisms: held-out seed generalisation |
| 2 | established null / failed hypothesis | nestor.cw01/cw01-2026-09-17:cw01-e05 | npe | NULL | mixture superadditivity over solo-transplant additive prediction; load-bearing members |
| 3 | persistent state / memory matters | nestor.cw01/cw01-2026-09-17:cw01-e01 | npe | POSITIVE | retention under necessity: use, advantage over non-retaining control, dependence (erase vs cost-matched sham) |
| 4 | transfer / reuse / recombination / inherited artifact | archaeon.campaign/cmp3:C3-SFE-10 | sfe | NEGATIVE | injected mature vs permuted-control organisms: takeover by competence or by mechanics |
| 5 | environmental / regime change or adaptation | archaeon.campaign/cmp2:C2-SFE-06 | sfe | WEAK_POSITIVE | delay ladder 0->1->2->4: forgetting of rung 0, revisit share p, cost on the top rung |
| 6 | deliberately difficult: assumptions may not fit BEE | nestor.cw01/cw01-2026-09-17:cw01-e07 | npe | INCONCLUSIVE | computational weather / damage to organism state: can the world be qualified (P1-P5) |

Evidence pointers, original outcomes (with numbers) and the per-experiment rationale are in the JSON. Engines: 4 NPE (two
campaign lanes: graphworld r1 and cw01) and 2 SFE (campaigns 2 and 3). The NPE campaign directories are on Nestor's
M1-local branch and were read only through Atlas facts; the SFE PREREG/RECEIPT/rows files are on origin/main and were
read directly.

Rule adopted for this pilot: no experiment is re-selected after a BEE result; a translation that turns out UNREPRESENTABLE
is reported as such against this frozen list (a refusal is a result).
