+============================================================================+
| REVIEW PACKET: CAMPAIGN 0 -- RSI ASSAY QUALIFICATION                       |
| Author: Aphrodite (charter adopted 2026-09-18), M4 host harry1             |
| Date: 2026-09-18                                                           |
| For: the operator (HITL) and external reviewers                            |
| Status: PASS (primary analysis). EVIDENCE TIER 2. STOPPED for review.      |
| Self-contained: no repository access needed.                               |
+============================================================================+

-----
0. SUMMARY
-----
The operator approved Campaign 0 (APHRODITE-14): prove the transplant
assay can recover a planted causal truth before any real-model
experiment. Nine synthetic worlds were planted:
- the operator's six: true transfer, memory cheat, compute cheat,
  specialisation, transferred module, null;
- worker transfer and mixed, added to meet the pass condition;
- a heterogeneous null, added by amendment.
A blind analysis tried to name each world's cause at 16, 32 and 64
independent lineages, 200 replicates each.
Verdict: PASS. Every world is recovered reliably at some L <= 64, and
both nulls keep the false-positive upper bound <= 0.10 at every L.
The required lineage count is 64. The measurement floor at 64 is about
4.7 points of tasks solved. Specialisation is the fragile distinction.
This is a result about the assay under a model the seat wrote. It is
not evidence about RSI and does not authorise Campaign 1.

-----
1. COMMITTED BEFORE MEASUREMENT
-----
- Prereg f0e04de11: worlds, assay, rules, grid, pass and stop
  conditions.
- Amendment 1 addb5d4cd, committed before any run. It added the
  heterogeneous null W9, after the pseudoreplication cheat control
  failed at the controls stage on the exact null.
- Code 6195af410, with 7 controls. Run from 769740128 on a clean tree:
  153 s, 14,400 jobs, 41,400 rows.
- The analysis never sees the world table; a test enforces this.

-----
2. THE ASSAY (what Campaign 1 would do)
-----
- Per lineage: I_8 vs I_0 on sealed VAULT families and on DEV families,
  with state M and worker A stripped. Also: value of state (M_8 vs M_0),
  worker transfer (A_8 vs A_0), as-run vs externally enforced budget,
  the naive as-run comparison, and module necessity and sufficiency
  swaps.
- One number per lineage per contrast. t-test across lineages; Holm
  over 16 contrasts; TOST against delta 0.03 (provisional).
- Four verdicts per contrast: SUPERIOR / TRIVIAL / EQUIVALENT /
  INDETERMINATE.
- Recovery = the assay's flag set EXACTLY equals the planted cause set.

-----
3. RESULTS (recovery; * reliable = >= 0.90 with Wilson lower >= 0.85)
-----
  world                 L16      L32      L64     min L
  W1 TRUE TRANSFER      0.795    0.985*   0.985*   32
  W2 MEMORY CHEAT       0.735    0.990*   0.990*   32
  W3 COMPUTE CHEAT      0.395    0.840    0.985*   64
  W4 SPECIALIZATION     0.070    0.505    0.905*   64
  W5 TRANSFERRED MOD    0.680    0.975*   1.000*   32
  W6 NULL               0.975*   0.985*   1.000*   16
  W7 WORKER TRANSFER    0.910*   0.985*   0.985*   16
  W8 MIXED              0.090    0.690    0.980*   64
  W9 HETERO NULL        0.995*   0.990*   0.990*   16
- False flags: 0-3% in every world at every L. Null false positives:
  W6 1.5 / 1.5 / 0.0%; W9 0.5 / 1.0 / 1.0% (L 16 / 32 / 64).
- Ambiguity (transfer vs specialisation undecided): W4 73 / 49 / 9%.
- Proving "no transfer" (EQUIVALENT in the exact null): 7 / 44.5 / 87%.
- MDE (80% transfer recovery): 0.4 / 0.3 / 0.2 logit, about 9.6 / 7.1 /
  4.7 points.
- Module attribution:
  - one dominant module (W5): 200/200 correct at L 32 and 64;
  - three small modules (W1): often none named (64/200 at L 64).

-----
4. SENSITIVITY
-----
- Holm is load-bearing: without it null false positives are 10.5-17.5%.
- Treating tasks as independent (pseudoreplication) manufactures power
  (W1 at L 16: 0.795 -> 0.94) and false equivalence (W9 at L 32: 0.375
  vs 0.085). It raised false positives only a little here.
- delta decides specialisation: W4 at L 64 recovers 0.385 / 0.905 /
  1.000 at delta 0.02 / 0.03 / 0.05.
- Corrected bootstrap agrees with the t analysis at L 32/64 (every world
  within 0.065). It is liberal at L 16.
- Misspecified generator (heterogeneity doubled): all worlds except W4
  stay reliable at L <= 64; W4 drops to 0.815.

-----
5. DEFECTS (calibration ledger, 3 rows)
-----
- The cheat control could not see pseudoreplication on an exact null.
  Fixed by Amendment 1, before any run.
- The bootstrap arm used 300 resamples. Its p-value floor (1/300) times
  Holm's 16 is 0.053, so it could never find significance. Corrected
  with 4000 resamples on identical observations; the primary analysis
  was unaffected.
- The expected harm of pseudoreplication was stated as fact in the
  prereg. It turned out to be overconfidence, not false alarms.

-----
6. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES: under this generative model, the assay tells apart
- better machinery (W1, W5);
- better memory (W2);
- more compute (W3);
- specialisation (W4);
- worker transfer (W7);
- mixtures (W8);
- no effect (W6, W9).
It needs 64 lineages and a justified delta to do so.
DOES NOT: say anything about real evolved improvers, RSI, or GPU cost.
It assumes additive logit effects, binomial tasks and the prereg's
variance components; real lineages may be heavier-tailed or interact.

-----
7. FOR THE OPERATOR'S REVIEW (stop condition)
-----
- Recovered cleanly: all nine at L = 64. At L = 32: all except compute
  cheat, specialisation and mixed.
- Measurement floor: ~4.7 points of tasks solved at L = 64.
- Required lineage count: 64.
- Unresolved: specialisation depends on delta and is fragile to
  misspecification; multi-module attribution is weak; the analysis is
  conditional on the generator.
- Hardware: 1,760 task evaluations per lineage for the assay; about
  112,640 at L = 64. This excludes evolving 64 lineages through 8
  generations, the dominant cost, not estimated. Converting to GPU
  hours needs the substrate and host decision (APHRODITE-32).
Seat's lean: the assay is fit to design Campaign 1 around, IF Campaign 1
can afford 64 independent lineages. If it cannot, the program should
plan for "no detectable difference" as the likely null verdict and
de-scope specialisation claims.

-----
8. QUESTIONS FOR THE REVIEWER
-----
1. Is additive logit effects plus binomial tasks too kind a generator?
   Which realistic violation would most change L?
2. Is flag-set exact match the right recovery criterion, or too strict
   for W8?
3. What delta is decision-relevant, and who owns that judgement?
4. What should we stop?

-----
9. ARTIFACTS
-----
science/campaign0/PREREG_C0_ASSAY_QUALIFICATION_2026-09-18.md   f0e04de11, addb5d4cd
science/campaign0/{worlds,assay,run_c0,summarize_c0}.py, tests/  6195af410
science/campaign0/ledgers/, RESULTS_C0_2026-09-18.md             3bee29f83
Numbers traced: every figure above is from ledgers/C0_VERDICT.json,
C0_SENS_BOOT_V2.json or c0_rows.jsonl at 3bee29f83 (APHRODITE-35).

+============================================================================+
| "Not worth continuing" is a first-class answer.                            |
+============================================================================+
