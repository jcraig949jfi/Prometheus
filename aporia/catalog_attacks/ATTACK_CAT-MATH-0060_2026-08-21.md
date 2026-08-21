# ATTACK CAT-MATH-0060 — level repulsion in the 30 stored zeta zeros (spec ELENCHUS-CORRECTED)
Date: 2026-08-21 (Aporia P61) | Code: attack_0060_0368.py | Data: attack_0060_0368_results.json
Grounding: RH itself untouched and untouchable here (stored zeros are on the line by
construction); the reviewer's cardinality re-scope is binding — 30 zeros support a
REPULSION test, not a pair-correlation curve.

Pre-stated readings: STEP0-PASS then REPULSION-PRESENT (both statistics beat >=99.9%
of Poisson) / REPULSION-ABSENT (instrument-bug-first) / AMBIGUOUS (split verdict).

Result:
- Step-0: zeta row 1-1-1.1-r0-0-0 fetched in 30ms via the P49 index (was 60s timeout
  pre-index); 30 zeros spanning [14.1347, 101.3179] — cardinality recorded first.
- Unfolded by mean spacing (single-mean unfolding; density variation over this span is
  mild and the approximation is stated). Two pre-registered statistics vs 10,000
  uniform-Poisson same-size/same-span samples (seed 20260860):
  T1 = min normalized spacing: real 0.4056, Poisson P(min >= real) = 0.0000 (0/10000)
  T2 = mean log spacing:       real -0.0876, Poisson P(T2 >= real) = 0.0000 (0/10000)
Reading: REPULSION-PRESENT, decisively, on both statistics — reproducing the reviewer's
power design (their 0/4000 -> 0/10000 here). The 30 stored zeros are inconsistent with
Poisson spacing and consistent with level repulsion.

NOT claimed: nothing about RH, nothing about GUE beyond repulsion (the curve is not
resolvable at n=30 — that is the point of the re-scope), nothing beyond this span.

Trace-vector: problem_id CAT-MATH-0060 | operations [indexed-fetch, mean-spacing-unfold,
dual-preregistered-statistics, seeded-poisson-null] | kill_pattern none |
residue: the reviewer's cardinality doctrine executed cleanly — the honest test at the
data's actual size was stronger than a fake version of the famous test
