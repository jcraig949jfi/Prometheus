# Ananke calibration ledger

Currency: 2026-09-24. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-24 | own env design: exact per-world target balance (sampling without replacement) makes every constant policy score exactly 0.5, so it is a clean baseline | it made consecutive targets anti-correlated (P(same)=1/3 in FLIP's 4-trial blocks, 7/15 over 16 trials); a "copy last teacher" policy scored 0.346 under zero-comm, so "opposite of last" would have scored ~0.65 with no adaptation | plant probe (FLIP x relay_flood x zero_comm) before any search | i.i.d. targets + mirror-paired worlds; every env ships a sequential-exploit check (lag-1 target correlation) in its tests
2026-09-24 | STATUS.md stamped "2026-09-24T12:10Z" at launch | `date -u` read 12:06:01Z a minute later; the stamp was an estimate written ahead of the clock (the Cosmos ledger's first row, repeated) | heartbeat.json updated_at vs date -u | every status timestamp comes from `date -u` in the same step
2026-09-24 | own gate design: PREREG s8 boundary criterion applied to every dial | it fires on categorical dials (arbitrary level order), on zero-variance deterministic metrics (3-SE clause vacuous) and on single-level dips (counted as two boundaries); 37 wave-B candidates include all three kinds | reading boundaries_B.json at the B -> B2 transition | ordinal dials only, a variance floor, and a monotone-run requirement, fixed in the next prereg before data; C1 labels unchanged, flagged in the report
2026-09-25 | P2: HOLD evolved competence at decay_shift=1 is NULL | 3 of 9 HOLD A1 cells at decay 1 reached SIGNAL | c1_report/summary.json predictions | the sign-asymmetric decay keeps positive latches; predict per-sign, not per-dial
2026-09-25 | P6: zero DISTRIBUTED_MEMORY_UNDER_DECAY flags | one flag (3291f6c2); post-hoc it depends on in-lifetime adaptation (0.50 when off) | c1_posthoc/posthoc_adjudication.json | memory-under-decay needs an adaptation arm in its detector
2026-09-25 | P8: >= 1 ANTI_CORRELATED cell with decay | no ANTI_CORRELATED cell at all; the asymmetry appears as a 0.75 dip (half the targets at 0.5 credit) | summary.json | S0 = 0 scores 0.5, so a sign-erasing mechanism cannot go below chance; think through the scoring rule before predicting its tail
2026-09-25 | own causal rules (PREREG s7): the family's expected control defines CAUSAL_SUPPORT | two of the three most interesting mechanisms (delay-line HOLD memory, self-modifying timing-locked MAJ) were labelled NOT_SUPPORTED because they are not the mechanism the rule assumed | wave D + post-hoc batteries | label from the whole ablation fingerprint in C2
2026-09-25 | own wave-C design: HOLD env variants (d, delta) | HOLD reads neither; 22 "transfers" re-ran the training condition | C transfer rows | every transfer variant asserts it changes a parameter the family reads (no-op guard for env variants)
2026-09-25 | edited the shared roles/base-role/MONITORS.md row (state -> "DONE ...") and pushed after running only prometheus/ananke tests | column 9 needs a state word (ACTIVE/DORMANT/DEAD/DISABLED/UNLOCATED); test_base_role failed on main for every seat until fixed (reported by Atlas-M2 #567 and Cosmos #569) | sibling defect reports | any edit to a base-role file runs archaeon/tests/test_base_role.py on the merged tree before push
