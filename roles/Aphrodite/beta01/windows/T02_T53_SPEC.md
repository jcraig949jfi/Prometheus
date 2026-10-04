# T02 -- T53: D-STRATIFIED, TRIBUNAL-v1a RE-SCORE OF A23 CAPABILITY (FROZEN SPEC)

C-006 (C-P2B-APH-BETA-01), cycle 2. Frozen in DEV-2, 2026-10-04, before any T02 walk. Threads: TH-018
(compounding) and TH-021 (instruments). Evidence tier 2. It is a NEW experiment on preserved A23 data. A23
(E-011) labels are NOT changed. The bridge results are correction/interpretation-class.

## 1. Question (rungs R4 SOLVED, R5 REUSED, R6 CAUSAL, measured budget-free)
How much of A23's reported CAPABILITY_SAME survives under all three of the following repairs?
- (a) the budget-free D endpoint: first TRIBUNAL-QUALIFIED program, walking past spurious hits, cap 10M;
- (b) the repaired tribunal T4 v1a;
- (c) LIVE controls. In A23 the P and OFF_0 arms could not score on REUSED/CAPABILITY_SAME by construction: no
  families were ever assigned to them (a20_c3.py:245 key=None for P; no "OFF_0:SAME" tclass exists).

Secondary: is capability concentrated in donors that RECOVERED the planted motif?

## 2. Frozen identities
- Runner: `engine/v2b/t53_rescore.py`, sha256 `48e44d0ec09eacb8cbc68cd647f1904e9909ba3151c9f7be19a1750d50728cc9`.
- Plan: `beta01/runs/T02_T53/T53_PLAN.json`, sha256 `32ca8197b3e11e6c4aaf5faf8b8aa0695c8a9ddbad65a42d8d666223c38875f1`. 10 replicates (1,2,3,4,5,7,8,9,10,11; replicates 0 and 6 were unfillable
  in A23). 3,600 jobs, **2,912 unique exact walks**, 66 libraries.
- Apparatus v2b-1 (APPARATUS_ID in the plan). T4 v1a; ruler v2.1; W5; cap 10,000,000; 4 cells per family.
  A23's own cell seeds are used (label `A23-CON<r>-rx`, Q2 dev sizes).
- Qualified apparatus: T01 QUALIFIED; conformance GREEN (200/200/40).

## 3. Arms
Libraries on each held abstraction A's 2 SAME and 2 OTHER families:
- PRISTINE;
- START_A;
- SEL_<arm> for each arm holding A (G1 -> G1 and G1_NC);
- SEL_P and SEL_OFF_0 (live controls).

G1 SAME families also get three in-run apparatus controls:

| Control | Library | Known answer |
|---|---|---|
| PC_MOTIF | [entry(m_G1)] + START | solves every SAME family that START cannot reach |
| PC_ONE | [single-body entry: SAME#1 witness body] + START | solves SAME#1 in >= 3/4 cells and SAME#2 in <= 1/4 |
| NC_OTHER | [entry(o_G1)] + START | no SAME capability |

## 4. Frozen rules
- **Family capability:** a family counts for an arm iff, in >= 2 of 4 cells, the arm's library reaches a
  T4-v1a-qualified program at <= 10M AND START is censored at 10M in that cell.
- **Replicate CAP_D_SAME:** true iff >= 2 SAME families count. CAP_D_OTHER is defined the same way on OTHER families.
- **Measurement gate (it can fail):** MEASURED iff all three hold:
  - PC_MOTIF is good in >= n-1 replicates;
  - PC_ONE is good in >= n-2;
  - NC_OTHER is good (0 SAME capability families) in >= n-1.
  Otherwise MEASUREMENT_FAILED. Any technical failure means TECHNICAL_FAILURE, with up to 3 reruns.
- **Readouts** (n = 10, k = ceil(0.58 n) = 6, as in A23's verdict):

  | Readout | Definition |
  |---|---|
  | R_SURVIVES | YES iff SEL_G1 CAP_D_SAME >= k |
  | R_G1_SPECIFIC | YES iff the G1 count minus the max over SEL_SHAM_k counts is > 0 (the generic-cliff control) |
  | R_LIVE_CONTROLS_BEATEN | one-sided sign tests of SEL_G1 vs SEL_G1_NC, SEL_P and SEL_OFF_0 on G1 SAME families, each p < 0.05 |
  | R_RECOVERY_ONLY | capability occurs ONLY in donors whose selection is EQUAL (ruler v2.1) to the planted motif |

- **Bridge:** per (replicate, arm), A23 CAPABILITY_SAME vs the new CAP_D_SAME (agree / historical-only / new-only).
- **Continuity:** A23 transfer cells where SELECTED's first hit qualified at <= 250k must reproduce the identical
  charge whenever the first qualified program is that first hit.
- **D-stratified summary:** for G1 SAME cells, every SEL arm against the START reference (COVERED / WINDOW / CENSORED).

## 5. Interpretation table (frozen)

| Result | Reading |
|---|---|
| R_SURVIVES YES, R_G1_SPECIFIC NO | A23's capability survives budget-free re-scoring at 10M with tribunal v1a, but it is a generic inheritance+composition+recurrence effect. This is consistent with A23 GENERIC 3/3 |
| R_SURVIVES NO | A23's CAPABILITY_SAME depended on the v1 tribunal, the first-hit endpoint, or the 250k/10M ladder construction. The CAPABILITY rung of A23 is not supported under repaired instruments. Its REUSED rung is separate |
| R_LIVE_CONTROLS_BEATEN NO via SEL_P or SEL_OFF_0 | a selected library WITHOUT the held abstraction also reaches the families. Inheritance is not necessary for the capability |
| R_RECOVERY_ONLY YES | capability is planted-motif recovery, not abstraction beyond the plant |
| MEASUREMENT_FAILED | nothing is read; return to DEV |

## 6. Compute
M4, 4 local workers, about 10-17 CPU-h estimated (a censored 10M walk is about 21 s). It is inside R2 (<= 16 core-h
per item, with the upper estimate at the edge; reported as actually measured). The experiment finishes in place
if it outlasts the 4 h window. There is no Fabric dependency.
