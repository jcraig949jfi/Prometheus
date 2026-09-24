# Campaign 0, run 2 (code f31339054, prereg 1d4465df9 + amendment A1) -- RESULT

Run: 2026-09-23 11:54:50Z -> ~12:27Z (wall 1957 s). Artifacts: run2_f31339054/ (REPORT.json,
REPORT.txt, adversary.json, mine_initial.json, sampler_eta.json, G1.json, quotient.json,
receipts.jsonl, atlas/ export; SQLite store sha256 in STORE_SHA256.txt, file kept under
COSMOS_HOME). Run 1 (1d4465df9) crashed at mining (BrokenProcessPool); its G1 and eta outputs
are byte-identical to run 2's (determinism check).

## RAN
Pools 3 x 1200 worlds (private oracle). G1. Sampler eta (4 strategies x budgets 30/60 x 3
seeds). Main dataset: active sampler, 80/family. Matched neighbours (99 DEFORMATION_OF edges).
Mining v1 (primary), v2, raw. Three adversary rounds (48 attacks/family/round + replicate
confirmation). 867 chamber queries beyond the oracle. Graph: 721 nodes, 243 edges
(60 CONTROL_OF, 84 COORD_PRESERVING, 99 DEFORMATION_OF), 799 runs, 3 laws.
NOT RAN: G5, G6 (no surviving law; prereg s2.6). The sealed family was not executed.

## OBSERVED
Gates: G0 PASS | G1 FAIL | G2 NOT REACHED | G3 (separate receipt) | G4 FAIL | G5 NOT REACHED |
G6 NOT REACHED | G7 NOT REACHED.

Initial mining (240 rows, 3 lineages, 19 permutations; p = 0.05 is the attainable floor):
  v1  ((N - K) * C) <= -0.1584 AND (C - exp(-(C * N))) <= -0.136        LOLO .891/.930/.836
  v2  ((C / G) + N) <= 0.9605 AND (C / (log(C) / K)) <= -0.06323        LOLO .895/.977/.866
  raw (C * log(G + K)) >= 0.0635 AND ((N - K) * exp(-C)) <= -0.1254    score .732 (v1 .838)
  family dependence of v1: mu = -0.054 bits/row, p = 0.98 (no residual family information)

Law ledger (all three FAILED, kept with counterexamples):
  424fa143b7 v1 (cmap v1)  round 0: 17/108 confirmed contradictions (15.7%)
  d45d1069e0 v2 (cmap v1)  ((C + K) * C) >= 0.1647 AND (C - G exp(-N)) <= -0.0614  round 1: 11/108 (10.2%)
  964c086e6d v3 (cmap v2)  (C * K) >= 0.1608 AND (C - G exp(-N)) <= -0.0870        round 2: 25/108 (23.1%)

Counterexample shapes:
  round 0: regs V=2 high-C worlds predicted PAYS (law had no G term; memoryless guess at 1/2
           beats paying C); ring worlds within ~0.05 of the margin at identical coordinates.
  round 1: all 11 in ca, r = 3, p = 0.03 (N_v1 3.6 - 14.4): predicted QUIET, observed PAYS by
           0.15 - 0.65. Majority repair keeps the cue; the raw flip count is the wrong hazard.
  round 2: 12 ring, all n = 3 with K >= 4 and C ~ 0: predicted QUIET (logger ties at no cost),
           observed PAYS by 0.34 - 0.94: the ring EVICTS the logger's cue. 13 ca (r=3 / Lc=24).
Metamorphic pairs (equal declared coordinates, different microphysics): verdict flips
  ca 0/1/2, ring 0/0/1, regs 0/0/0 over ~9 pairs per family per round.
Quotient: 721 worlds -> 8 verdict classes (4-probe battery); boundary edge fraction
  DEFORMATION_OF 0.27, COORD_PRESERVING 0.095, CONTROL_OF 0.73 (sham flips PAYS worlds).
Sampler: active 0.790 / random 0.788 law-BA at B=30; 0.807 / 0.831 at B=60 (P4 LOST).
G1 failure: cost-up matched edges with non-increasing SEL fitness ca 7/8, ring 7/8, regs 8/8
  vs the >= 90% rule.

## INSTRUMENT DEFECTS FOUND (evidence about CWE, not about the worlds)
I1 adversary evaluated every law with v1 coordinates, including the v2 law of round 2.
   Round 2's verdict does not depend on it: the ring counterexamples alone (ring v1 == v2)
   are 12/108 = 11% > 5%. The ca part of round 2 is INVALID as evidence against law v3.
I2 G1b is under-powered and noise-blind: 8 edges, a 90% rule that tolerates zero violations,
   and each world of a matched pair on independent random numbers (seed from its own id).
I3 G2/G7 are computed only for a SURVIVED law, so a campaign that kills every law reports
   them NOT REACHED even though the initial-law numbers above exist (reported here instead).

## INFERRED (visible families only; PROVISIONAL)
- The declared coordinate set {C, N, K, G} is not sufficient for SELECTIVE_PAYS.v1 across these
  three families. Two missing or mis-stated variables were exposed by the adversary rather than
  by fitting: (a) logger CAPACITY (ring n, ca Lc) -- when the carrier cannot hold K+1 items the
  logger loses the cue and selectivity pays at zero cost; (b) the effective HAZARD after native
  repair (ca r = 3) -- N_v1 overstates it by orders of magnitude.
- Normalization earns itself on these data (v1 .838 vs raw .732), and family identity carries
  no residual information for the initial law (mu ~ 0) -- yet the law dies under attack. LOLO
  plus a permutation null did NOT detect the missing variables; the adversary did.

## CONCLUDED
Campaign 0 (as preregistered) ends with NO SURVIVING INVARIANT. Qualification is NOT achieved;
G5/G6 were not reached and the holdout remains sealed and unused. "No law" is the result.

## Precommitments
P1 HELD (band: logger floor C*(K-N) and a cost ceiling). P2 LOST as stated (round 0 did fail,
but not through the ca redundancy transform, and the first revision picked v1, not v2; the
redundancy mechanism did kill round 1). P3 HELD (capacity generated the round-2 counterexamples).
P4 LOST. P5 NOT TESTED.
