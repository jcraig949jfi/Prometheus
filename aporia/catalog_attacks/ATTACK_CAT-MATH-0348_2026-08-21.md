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
