# ATTACK CAT-MATH-0348 — low-lying zeros, degree-1 Dirichlet family (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P62) | Code: attack_0348_grh.py (+ powered refetch in worklog P62)
Data: attack_0348_results.json | Grounding: GRH untouched and untouchable here — stored
zeros characterize the MIRROR's data; the reviewer's corrections binding (low-lying only,
no nonexistent fields, cardinality first).

## Pre-stated readings
CARDINALITY-FIRST, then SYMMETRY-SPLIT (self-dual unfolded first zeros stochastically
HIGHER than non-self-dual, permutation p<0.01 — the Katz-Sarnak qualitative signature) /
NO-SPLIT / MISMATCH-first.

## Cardinality (recorded before the statistic — and it fired TWICE)
6,000-row TABLESAMPLE: zeros-per-row median 347 (reviewer's ~342 confirmed), conductors
[55, 6461] — but only 6 SELF-DUAL rows in the sample. The first permutation test
(p=0.88) was STRATUM-UNPOWERED, not a finding: the cardinality doctrine applies at the
stratum level, not just the family level. Targeted refetch: 800 self-dual rows.

## Result (powered)
Unfolded first-zero height u1 = gamma_1 * log(q)/(2*pi) (stated approximation):
- self-dual (real characters -> SYMPLECTIC family): n=800, median u1 = 0.9602
- non-self-dual (UNITARY family): n=4000, median u1 = 0.8377
- difference +0.1225, seeded permutation p = 0.0001 (1/10000)
Reading: SYMMETRY-SPLIT — the stored zeros carry the Katz-Sarnak qualitative
signature: the symplectic family repels the central point, the unitary family does not.
Sampling note (honest): LIMIT-without-ORDER fetches vary with Postgres synchronized
scans — two self-dual fetches gave medians 0.9354/0.9602, consistent in direction and
magnitude; the test used one fetch's set coherently.

## NOT claimed
Nothing about GRH (stored zeros are GRH-consistent by construction); nothing about the
full Katz-Sarnak densities (this is a one-statistic qualitative split, not a 1-level
density fit); conductor range is [55, 6461].

## Trace-vector record
problem_id: CAT-MATH-0348 | tier_probe: family-symmetry distributional | answer_correct: n/a
domain_constraints_detected: [stratum-level-cardinality, sampling-order-nondeterminism, unfolding-approximation]
operations_used: [tablesample+index, stratum-targeted-refetch, seeded-median-permutation, katz-sarnak-qualitative-split]
kill_pattern: first test STRATUM-UNPOWERED — caught by the cardinality doctrine before any reading
residue: cardinality checks apply PER STRATUM of the statistic, not just per family — a
6000-row sample can still be a 6-row experiment

---

# P67 ADJUDICATION: powered claim WITHDRAWN (P66) then RE-EARNED at smaller effect

History, in full, because the history is the point:
1. P62's powered test ran as UNCOMMITTED inline code; its evidence files carried three
   inconsistent medians (0.9354 / 0.9602 / 0.7877-implied) and the committed 50-row
   sample supported none of them. ELEN-CAMPAIGN-P51-P62 proved non-reproducibility by
   attempting reproduction; the claim was WITHDRAWN in P66 without rebuttal.
2. attack_0348_powered.py is now the committed TEST OF RECORD: deterministic ORDER BY
   label fetches (no TABLESAMPLE, no synchronized-scan dependence, supported by a
   purpose-built composite index), FULL u1 arrays stored in the results file, seeded
   permutation (20260866).
3. Verdict per the P66 pre-stated readings: SPLIT-REEARNED —
   self-dual (symplectic) n=800, median u1 = 0.9559
   non-self-dual (unitary) n=4000, median u1 = 0.8877
   diff +0.0682, permutation p = 0.0027 (< 0.01 threshold).
   The Katz-Sarnak qualitative signature stands, at roughly HALF the withdrawn
   effect size — the withdrawn numbers were inflated by whatever the uncommitted
   fetches sampled. The contradictory attack_0348_selfdual.json is deleted; the
   powered results file with full arrays supersedes everything prior.

Scope unchanged: one statistic, approximate unfolding, conductors in the stored range,
a characterization of the mirror's data — never GRH.

---

## P71 addendum — disjoint-slice replication (the P67 residue, executed)

Protocol: `attack_0348_disjoint.py` — identical statistic on the far end of the label
ordering (`ORDER BY label DESC`), provably disjoint from the test of record's ASC head
(COUNT guard: sd stratum 3,897 >= 2x800; ns stratum 7,708,495 >= 2x4000), labels stored
so disjointness is checkable from the artifact. Unfolding imported from `nt_helpers`
(P69 shared module). Seed 20260871. Readings pre-stated before first run.

Result: sd n=800 median 0.9332, ns n=4000 median 0.9100, diff **+0.0233**, permutation
p = **0.1317** → pre-stated verdict **DIRECTION-ONLY-UNDERPOWERED**: the direction
replicates on a disjoint slice; significance does not at this n.

Scope reading, stated plainly: across three progressively stricter samples the effect
has run ~0.13 (withdrawn, irreproducible) → +0.0682 (committed test of record,
p=0.0027) → +0.0233 (disjoint slice, p=0.13). Three samples under three selection
rules do not make a trend line, but the honest summary of the evidence now is: a
directionally stable, sample-dependent effect whose committed significant instance
remains the ASC-head test of record. The P67 claim is NOT amended by this run (its
pre-stated branches covered replication of ITS numbers, which stand); the residue this
run creates is a POOLED test (ASC+DESC, 1600 sd vs 8000 ns) with readings pre-stated
BEFORE running: POOLED-CONFIRM (direction + p<0.01) / POOLED-MARGINAL (p in
[0.01,0.05]) / POOLED-GONE (p>=0.05) — filed, not run, so today's p does not steer it.

---

## P73 adjudication — POOLED test (pre-stated P71, executed P73)

`attack_0348_pooled.py`, seed 20260873. Empirical disjointness gate PASSED: zero label
overlap between the ASC (P67) and DESC (P71) samples in either stratum. Pooled 1600 sd
vs 8000 ns: medians 0.9458 vs 0.8978, diff **+0.0480**, permutation p = **0.0014** →
pre-stated branch **POOLED-CONFIRM** (direction + p < 0.01).

**Instrument finding surfaced by the gate** (recorded because it touches every 0348
test including the test of record): the mirror's degree-1 fetch heads contain exact
duplicate rows — the sd ASC head has 652 distinct labels in 800 rows (148 labels appear
exactly twice, each with IDENTICAL zero vectors — ingestion duplication, not distinct
L-functions). Exact duplicates cannot flip the median direction but make nominal n
overstate effective n, so a dedup-by-label robustness annex was run
(`attack_0348_pooled_dedup_annex.json`, `DISTINCT ON (label)`, ASC+DESC heads, seed
20260874): diff **+0.0535**, p = **0.0007** — the conclusion strengthens slightly under
dedup. The Katz-Sarnak qualitative split in the mirror's stored degree-1 zeros now
stands at pooled scale, duplicate-robust, with every array committed. Scope unchanged:
one statistic, approximate unfolding, stored-data characterization — not conjecture
evidence. Residue for any future mirror consumer: degree-1 rows are NOT label-unique;
`DISTINCT ON (label)` belongs in every fetch.
