# BEL-48H Window 4 -- Computation, reproduction and hereditary conflict

Campaign BEL-48H-2026-10-08, Bellerophon[ubu005-0eb14d49]. Prereg s5 (frozen ebc3daaae) + amendment 2 (paired seeds ->
McNemar beside Fisher). Analysis tools/analyze_w4.py (committed 4e6d89fa4 before the runs). Runs 1,050/1,050, 0 voids,
2.25 h active (6 workers, 12:01:45Z -> 14:16:49Z), physics v3 (historical COMMON + V3 configuration of the coupling
campaign), instrument tools/comp.py (CompWorld: competence x FUNC per birth + anatomy; invariance-tested).
Receipt receipts/W4_ANALYSIS.json; raw ~/bel48h_runs/w4.

## 0. The recovered historical disposition (not assumed below)

Coupling campaign (frozen c9bed96de): READY_FOR_MULTIDAY; P1-P4 HOLD; P5 preservation FAILS at ceiling; P6 conflict
repair FAILS underpowered (4/60 vs 0/60, p 0.125). Multi-day: LADDER1 and COPIER HOLD, LADDER2 FAILS.

## 1. Frozen predictions

| id | result | verdict |
|---|---|---|
| W4-P1 conflict repair, powered (REP + BAD, INC, K16) | competent self-replicator alive at tick 500: ON 10/300 [1.8, 6.0%] vs OFF 0/300 [0, 1.3%]; Fisher one-sided p = 0.0009; seed-paired McNemar 10 vs 0, p = 0.002 | HOLDS -- historical P6 (underpowered) is now CONFIRMED at 5x the sample on fresh seeds |
| W4-P2 de novo acquisition (seeded copiers, ECHO, K40) | ON 20/150 [8.8, 19.7%], OFF 0/150, SHUFFLED 3/150; Holm p < 0.001 for both; paired McNemar 20 vs 0 and 20 vs 3 | HOLDS -- historical B-cop direction replicated (29/150 vs 6/150 there) |
| W4-P3 anatomy of the repaired machine (M1 ON, 10 runs) | SINGLE_LINEAGE_BAD 8, OTHER 2, CROSS_LINEAGE 0 | HOLDS -- repair happens inside the damaging lineage, not by recombining it with the clean copier |
| W4-P4 protection (task loss per competent-FUNC writer birth, ON vs OFF) | only 11 ON runs and 0 OFF runs had >= 20 such births | NOT TESTABLE (descriptive): pooled ON task_loss 11 per 330,953 births from competent FUNC writers |
| W4-P5 competence bytes newly made (M2 ON) | as written: 0/20 -> FALSIFIED; CORRECTED: 19/20 | ANALYSIS DEFECT in a frozen rule: analyze_w4 tested lower-case 'n'/'c' while comp.py records tag kinds upper-case ('N','C'); the rule could never be satisfied. Corrected reading (same rule, correct case): 19/20 HOLDS. Both are reported; the correction is recorded in the calibration ledger |

## 2. What the corrected instruments add

**Computation that pays changes what is inherited, causally.** Contingent payment (ON) versus the same copier
population without it (OFF) or with payment decoupled from the organism's own answer (SHUFFLED) is the only difference;
the competent self-replicator at the end appears only with contingency (W4-P1, W4-P2). CAUSALLY_CONFIRMED (seed-paired
intervention, fresh seeds, two task settings).

**Where the competence comes from.** In 19/20 ECHO machines at least one competence-critical byte is a post-founding
change; the rest of the task-critical bytes are the seeded copier's own bytes (founder 'seed' in 12/20). The machinery
for the task is built mostly out of the copier's existing bytes plus 1-3 new bytes (IN_A 0x40 / OUT_A 0x41 typically).

**Entanglement of computation and reproduction (PROVISIONAL; 16/20 detector + 4 traced).** In 16/20 ECHO machines the
competence-critical and replication-critical sets SHARE bytes, usually LD C,0x40 or LD T,0x40 of the copy routine.
Execution traces of four specimens (w4_00714, w4_00735, w4_00606, w4_00963): the shared operand byte is NOT executed as
an opcode (no overlapping reading frame); instead the answer is produced AFTER the copy, when execution falls through
into the freshly written child in the window (first OUT at step 74-91 in w4_00735 / w4_00714), so the copy routine's
parameters decide whether the output instruction is ever reached. One specimen (w4_00963) keeps the two machines
separate (IN_A; OUT_A at bytes 0-1, copier later). Consequence for the historical P5 question (preservation): in an
entangled machine a mutation that breaks the copy routine also breaks the computation, so 'reproduction damages
computation' is not a separable event -- part of why task_loss is ~0 here.

**Conflict repair is in-place repair.** The 8 SINGLE_LINEAGE_BAD repairs keep the BAD founder's bytes in both critical
sets: the damaging sweep is repaired by changes inside the damaging machine. CROSS_LINEAGE assembly (copier from REP +
task code from BAD) was predicted possible and never observed (0/10).

## 3. Answers (directive W4)

Useful computation influences hereditary success: yes, causally, under contingent payment (two settings). Reproductive
machinery damaging task machinery: the repair route exists at 3.3% of seed-paired worlds per 500 ticks, by in-place
changes in the damaging lineage. Task-preserving copy strategy: the entangled architecture (output produced through the
child copy) is the dominant evolved form (16/20) in de novo ECHO acquisition; whether selection favours it over the
separated form is NOT tested here (next experiments).

## 4. Limits

Single coupling physics (v3) and parameter sets (K16 / K40); ECHO and INC only; W4-P4 untestable at this n; entanglement
mechanism traced on 4 specimens; competence is the configured verifier's exact-answer test (tasks.verify_exact).

## CORRECTION (2026-10-08T18:26:36Z) -- the entanglement mechanism in s2 was wrong; it is BUDGET COUPLING

s2 said the answer is produced "after the copy, when execution falls through into the freshly written child". An
automated test (analyze_w6b3.out_from_child: is the OUT_A executed from [L,2L) or from the organism's own tape?) gives
OUT executed in the child copy in 0/20 W4 machines -- the claim is RETRACTED. What the four traced specimens actually
show, now tested causally on w4_00735: competence survives every copy length C except C = 0 (an unbounded 256-byte
LDIR), and with the execution budget raised from 256 to 512 steps the C = 0 variant is competent again. The copy routine's
length operand is competence-critical because an unbounded copy consumes the whole step budget before the task code
(which runs AFTER the copy, own tape, step 74 in w4_00735) is reached: computation and reproduction compete for ONE
execution budget. Classifier (frozen for W6 block 3): BUDGET_COUPLED = a shared critical byte whose knockout kills
competence at budget 256 but not at 512. Retrospective (post-hoc, labelled) on the 20 W4 ECHO machines: BUDGET_COUPLED
10, OTHER_SHARED 7 (shared byte kills competence at both budgets, e.g. w4_00606: knocking out the LD T opcode exposes its
operand 0x40 = IN_A as an instruction -- a knockout frame-shift effect, not dual use), SEPARATED 3. The 'shared bytes'
detector of s2 therefore mixes a genuine coupling (budget) with a ruler artifact (operand exposure). CL-11 corrected.
