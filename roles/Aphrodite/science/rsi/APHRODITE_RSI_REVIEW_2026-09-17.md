+============================================================================+
| REVIEW PACKET: FOUR RSI MECHANISM TOYS (E1-E4) + TWO POST-HOC PROBES       |
| Author: Aphrodite (new seat, charter pending), M4 host harry1              |
| Date: 2026-09-17                                                           |
| For: the operator (HITL) and external reviewers                            |
| Status: preregistered run complete; 9 SUPPORTED / 3 REFUTED /              |
|         3 INDETERMINATE; exploratory X2 unreplicated                       |
| Self-contained: no repository access needed; every number is inline.       |
+============================================================================+

-----
0. SUMMARY
-----
Commission (operator, 2026-09-17): research recursive self-improvement
(RSI) and build small Python prototypes testing the concept. Built four
deterministic, stdlib-only toys with NO language model, each probing one
mechanism that recent RSI claims rest on:
  E1 feedback density/attribution  (Z.ai GLM "dense feedback" article)
  E2 a self-referential improver   (STOP-style; leaky-evaluator cheat arm)
  E3 verifier-gated memory         (RSIAgent, arXiv 2609.15364)
  E4 disjoint-dataset leak guard   (ModularRSI, arXiv 2609.14857)
Headline, stated as a stand to be attacked: RSI's leverage AND its
hazard both sit in the feedback/verification harness, not in
self-reference. The sharpest single result is post-hoc and unreplicated
(X2): a self-improver competent enough to change itself found a planted
evaluator-accounting hole in ONE generation and became 2.35 log10 units
(~200x) worse under honest measurement, while its honest twin improved
only marginally in two generations.

-----
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
-----
- Preregistration (hypotheses, gates, seeds, the rule "CI straddling a
  bound = INDETERMINATE") pushed to origin/main as 9c173fb37 BEFORE any
  experiment code existed.
- Code + controls c286081ae: e1_feedback.py, e2_self_improver.py,
  e3_memory.py, e4_guard.py, run_all.py; 14 control tests (positive,
  negative, cheat per toy), all passing. Success is judged by a
  harness-side oracle independent of the feedback the improver sees;
  evaluations are counted by a wrapper, never self-reported.
- One control corrected before any result was read (E2 positive control
  used a slow theta: 0.06 at 400 evals, 2.8e-17 at 4000; changed).
- Full run from a clean tree: 831 s on 7 workers.

-----
2. SOURCE CHECK (what the prototypes cite; verified 2026-09-17)
-----
- The arXiv link the operator sent (2609.15364) is RSIAgent (UCSD / UIC /
  Aether AI), NOT the GLM article.
- Z.ai article VERIFIED: 100,000+ accelerators, <2 weeks, ~3x throughput
  (whole stack); says itself "we have not yet reached RSI". FLA PR #1180
  exists and is merged; the PR text does not mention an agent.
- An AI-assistant summary the operator pasted overstated two things:
  RSIAgent "beats GPT-6" holds only on PARTIAL credit (GPT-6 Astra higher
  on ALE binary, 52.24 vs 50.75; compared to reported, not re-run,
  numbers). "Dream-RSI (Google DeepMind)" is UMD-led with GDM co-authors;
  "162x" is agent calls on one Lasso task. ModularRSI VERIFIED.

-----
3. DESIGN AS EXECUTED (one line each; full spec in the prereg)
-----
E1 K components x 8 values, hidden target; regimes PASSFAIL, SCALAR
   (count correct), DENSE (per-component flags), DENSE_NOISY (10% flag
   flips), DENSE_MISATTRIBUTED (flags permuted); K 2/4/8/16; 200 seeds.
E2 (1+lambda)-ES with theta = (sigma0, adapt factor, lambda, patience)
   optimises 6-d benchmark functions AND its own theta; RECURSIVE vs
   FIXED-META over 4 generations, 10 chains; held-out 40 tasks. Cheat arm:
   LEAKY accounting charges the budget per step, so lambda is free.
E3 hidden-rule worlds (action depends on color; shape is a distractor);
   test on unseen shapes; memory NONE / RAW / DISTILLED verified or not;
   poison = false peer rules; SHAPE-worlds as wrong-abstraction control.
E4 evolve a 6-feature vote; dataset A leaks the label in a "hint" field;
   fitness on A (SINGLE), A+B pooled (POOLED), min(A,B) (DISJOINT).

-----
4. RESULTS (exact; verdicts under the prereg's CI rule)
-----
  hyp  verdict        numbers
  H1a  SUPPORTED      median evals DENSE vs SCALAR: K4 15.5/48.5,
                      K8 29/132.5, K16 56/351
  H1b  SUPPORTED      SCALAR/DENSE ratio 3.13 < 4.57 < 6.27
  H1c  SUPPORTED      MISATTRIBUTED solved 1/600 runs at K>=4; SCALAR
                      600/600
  H2a  REFUTED        gen-1 held-out gain in 8/10 chains (gate 9)
  H2b  INDETERMINATE  median Delta1 0.072 vs Delta2 0.003; CI of the
                      paired difference [-0.034, 0.143]
  H2c  SUPPORTED      recursive minus fixed-meta at g4, CI [-0.048,
                      0.062]: no recursion dividend
  H2d  REFUTED        leaky arm: lambda stayed 1 in 10/10 chains
  H3a  SUPPORTED      verified distilled 0.990 on unseen shapes; RAW
                      0.249; NONE 0.249 (chance 0.25)
  H3b  SUPPORTED      poisoned: verified 0.990 vs unverified 0.491
  H3c  REFUTED        verifier admitted 1.165 false rules (gate <= 0.5,
                      CI [0.935, 1.425]); no accuracy harm
  H4a  SUPPORTED      SINGLE 0.527 on held-out C
  H4b  INDETERMINATE  DISJOINT 0.805, CI [0.797, 0.813] vs gate 0.80
  H4c  SUPPORTED      POOLED 0.550
  det  INDETERMINATE  A-B gap flags 92.5% of SINGLE (gate 90%)
  pos  SUPPORTED      no-leak control: all regimes >= 0.828
EXPLORATORY (no prediction was registered): DENSE_NOISY is WORSE than
SCALAR from K8 up (307.5 vs 132.5; K16 2379.5 vs 351; 5% failures at
K16). Per-signal noise scales with the number of signals.

-----
5. POST-HOC PROBES (EXPLORATORY, decided after reading E2's rows)
-----
X1 noise floor: 40 random perturbations of theta_0 of meta-step size.
   42.5% match or beat the recursive chains' gen-1 median; 25% match
   gen 4. corr(U_train, U_test) 0.97: the landscape is real but rugged.
   The weak self-improver did about what random local search does.
X2 competent start theta = (sigma0 0.1, a 1.5, lambda 1, patience 400),
   10 chains x 2 generations:
   HONEST: gain in 7/10 chains, median 0.123 log10, mean CI [0.002,
     0.151]. Marginal; no reading stated until replicated.
   LEAKY: lambda -> 16 in 5/10 chains after ONE generation, >= 12 in
     8/10 by g2; real/declared evaluations up to 16x; under honest
     measurement worse by median 2.35 log10 units, CI [2.15, 2.76]. The
     independent counter caught every case.

-----
6. INCIDENTS AND SEAT ERRORS (recorded in the calibration ledger)
-----
- H2d's gate was barely REACHABLE from theta_0 (meta step ~0.01; lambda=2
  needs 0.033). "Nothing fired" vs "nothing could have fired" was not
  computed before freezing. X2 shows the exploit is found when reachable.
- run_all.py issued verdicts on point estimates although the prereg's
  rule is CI-based; analysis.py re-derived all verdicts; three changed
  to INDETERMINATE.
- E3's verifier probed only training shapes; in-distribution probes
  share the evidence's confound (reproduces RSIAgent's own "incomplete
  verification" failure).
- Process: the post-merge tests ran after, not before, the final push
  (14/14 pass on the merged tree). Separately, at seat creation this
  session ran `git pull` in the canonical checkout (a6969bfbb ->
  b70d4f76e) before reading the working contract; reported as an
  incident.

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES: the mechanisms are coherent and the instruments can see them
(positive, negative, cheat controls pass); attribution, not volume, is
what dense feedback buys in E1; verification removes injected poison;
single-set evolution buys a leak and pooling does not guard against a
dominant leaky set.
DOES NOT: say anything about GLM, RSIAgent, Dream-RSI or ModularRSI
performance; E1 and E3 are near-analytic; E2's preregistered design
could not move the improver, so its "no recursion dividend" is weak;
X2 is one toy, one planted bug, 10 chains, post-hoc.

-----
8. RECOMMENDATION (the operator's call; the seat's lean)
-----
Lean: continue, narrowly. Preregister the X2 replication (>= 30 chains,
eligibility computed, plus a hidden-vs-visible evaluator arm, the DGM
finding) and E3 v2 (out-of-support probes, better-than-chance fallback).
These are instruments and pressures, consistent with the north star.
Stop instead if the operator judges toy-level RSI evidence decision-
irrelevant to the program; the reusable residue (oracle-separated
evaluation counters, cheat controls, disjoint-set leak gate) survives
either way. Open decision APHRODITE-08: is this the seat's charter?

-----
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----
1. Is X2 just "a planted bug gets exploited", which no one doubted? What
   design would make the hazard non-trivial (unplanted, emergent)?
2. Could E1's ratio growth be an artifact of the agent designs (DENSE
   tries values in order; SCALAR samples) rather than of feedback?
3. Does min(acc_A, acc_B) in E4 merely encode foreknowledge that B is
   clean? What if B were also leaky in a different way?
4. Is a 0.97 train/test correlation evidence the E2 landscape is real,
   or that train and test share families and so share the artefact?
5. What should we stop?

-----
10. ARTIFACTS (repository-relative; commits on origin/main)
-----
roles/Aphrodite/science/rsi/PREREG_RSI_TOYS_2026-09-17.md   9c173fb37
roles/Aphrodite/science/rsi/*.py, tests/test_controls.py    c286081ae
roles/Aphrodite/science/rsi/ledgers/*.jsonl, VERDICTS.json  07fcc2509
roles/Aphrodite/science/rsi/RESULTS_2026-09-17.md           07fcc2509
roles/Aphrodite/science/rsi/SOURCES.md                      07fcc2509
roles/Aphrodite/calibration/LEDGER.md (4 rows)              07fcc2509
merged to origin/main as f25eb94cc

+============================================================================+
| "Not worth continuing" is a first-class answer. So is "the toys are too    |
| easy to tell you anything"; say which, and why.                            |
+============================================================================+
