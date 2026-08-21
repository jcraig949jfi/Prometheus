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
