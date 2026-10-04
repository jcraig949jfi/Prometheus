# T01 -- KNOWN-ANSWER APPARATUS ASSAY (FROZEN SPEC)

Campaign C-006 (C-P2B-APH-BETA-01), thread TH-P2B-APHRODITE-V2B. Frozen in DEV window 1, 2026-10-04, before any T01
walk ran. Evidence tier 2 (apparatus calibration). Rungs exercised: R0 (representable), R2 (findable), R4 (solved),
R6 (causal knockout), plus the measurement layer (tribunal, ruler, D endpoint, gates, supply).

## 1. Question
Can the repaired v2b pipeline return PASS, NO, NOT_A_SHAM, REPRESENTATION_LIMITED, INVALID_DESIGN, SUPPLY_LIMITED,
and an instrument difference, each FOR THE RIGHT REASON, on cases whose answers are known by construction? If it
cannot, the next DEV continues repair. No frontier science is launched on an unqualified apparatus.

## 2. Frozen identities

| Item | Value |
|---|---|
| runner | `roles/Aphrodite/engine/v2b/t1_known_answer.py`, sha256 `e5853caf922a4df759b0efdf4b50cf9f29954bebb9c63516498a270433885705` |
| plan (pre-freeze supply screen output) | `roles/Aphrodite/beta01/runs/T01/T01_PLAN.json`, sha256 `f698991a3b263391b870e78fe612a3270fcc39ec483acd3710d3b1b9e5d40585` |
| apparatus | v2b-1. APPARATUS_ID is recorded inside the plan (`apparatus.apparatus_id`). Tribunal T4 **v1a**; ruler **v2.1**; world W5; cap **2,000,000** charges; 4 cells per family |
| conformance | GREEN (engine/v2b/receipts/CONFORMANCE_V2B_2026-10-04_quick.json): walker == fast_cost; fast_cost == reference; artifact == direct tribunal 16/16 (v1, v1a); ruler v2.1 == W7 47/47; v2b lint-clean |

## 3. Cases and the PRE-DECLARED expected outcomes
Libraries are `[one inherited entry] + PRISTINE`. Transfer families are 4 seeded instances of the planted motif
M = `(v * (acc + {H}))`. They are T4-admissible and PRISTINE-censored at 2M on cell 0:

| Family | Body |
|---|---|
| toaa | (v * (acc + (last - 1))) |
| tcnb | (v * (acc + (v + v))) |
| tvzc | (v * (acc + (1 + 1))) |
| twme | (v * (acc + (first + first))) |

Every inherited entry has 161 instantiations (equal expressivity).

| Case | Construction | Expected | Reason that must hold |
|---|---|---|---|
| K1 PLANTED_ABSTRACTION | entry = M | PASS: T qualifies in >= 3/4 cells on >= 3/4 families | CENSORED-stratum cell excess of T over the best control (SHAM_X, SIBLING, NULL) >= 6 of 16 |
| K1b KNOCKOUT_SIBLING | entry = SIBLING `pow(v, (acc + {H}))`, a different composition of the same G1 | NO (<= 1 family) | the effect is structure-specific (causal knockout of M) |
| K2 NULL | entry = OFF_0 `math.gcd(abs((acc // {H})), abs(first))` | NO | -- |
| K3a SHAM_EQUAL_EXPRESSIVITY | entry = `pow(first, (acc + {H}))`, size-matched, ruler-DISTINCT from M | NO | the sham must be DISTINCT by ruler v2.1 |
| K3b REEXPRESSION | entry = `((acc + {H}) * v)`, a re-expression of M | NOT_A_SHAM | ruler v2.1 EQUAL_ANY makes Control.check_distinct refuse it. This is the CON1/SHAM_0 confound, caught by the instrument. It is expected to solve like M; its solves are recorded |
| K4 MEMORISATION_CHEAT | entry = literal (init, body, final) triples of 8 OTHER instances of M | NO | memory of sibling programs does not transfer |
| K5 UNREPRESENTABLE | probe body `(((acc + v) * v) + ((v * v) - first))` | REPRESENTATION_LIMITED | not in W5 and not in any library: R0 fails, so NO is never returned |
| K6 CONSTANT_GATE_DESIGN | a gate `lambda ev: True` presented for seal | INVALID_DESIGN | Gate.qualify raises GateUnreachable |
| K7 SUPPLY_SHORTFALL | quota 6 replicates from 4 fillable | SUPPLY_LIMITED | supply.screen fails closed |
| K8 TRIBUNAL_VERSION | family qbda (A19 C2), PRISTINE, T4 v1 vs v1a | V1_BLIND_V1A_SOLVES: v1 0/4 cells, v1a >= 3/4 | under v1 the walker passes >= 1 spurious (query-1/2) hit |

**QUALIFIED** iff every case passes (class AND reason) and no walk ends in TECHNICAL_FAILURE (an evaluator
disagreement between the artifact and direct tribunal paths counts as technical).

## 4. Technical-rerun rule
Up to 3 reruns after the original attempt for technical failure only. A changed scientific variable gives a new
version (T01-v2).

## 5. Execution
On M4 (light): `python t1_known_answer.py run 3`, then `report`. Outputs go to `beta01/runs/T01/` (T01_WALKS.jsonl,
T01_RESULT.json). Expected run time is under 1 h. There is no Fabric need.
