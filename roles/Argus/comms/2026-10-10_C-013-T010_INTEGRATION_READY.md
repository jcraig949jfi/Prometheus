C-013-T010 INTEGRATION_READY -- Argus[harry1-6417c3ea] (claude-opus-5-5, Q2)

Branch argus/c013-t010 head e3cbcb30e (base 9b1893d6f; origin/main 2bd280452 merged explicitly; 76 tests green on the
merged tree). Receipt: ops/campaigns/C-013/tasks/C-013-T010/attempts/A-001/RECEIPT.json (DONE_CLEAN).

Deliverables (rso/reach/):
- REACHABILITY_CARTOGRAPHY_V0.md: five questions, ten measurements with minimal protocols, five mechanisms kept
  distinct (genotype copying is never state restoration), never-impossibility rule, worked p1_slice example, sheet schema.
- PREREGISTRATION.md v1.0.0 + FREEZE_D1.md: frozen at code commit 307afe4b1 BEFORE any confirmatory lineage.
  Arms chain_strict, chain_neutral, X1, X2, X3 (Nyx 3318a2098) + X3G (genotype hash, buckets matched outcome-blind);
  contrasts C1 neutral acceptance, C2 retention, C3 count selection, C4 admission of worse into new cells, C5 behaviour
  cells vs matched hash; d = 1, 3, 8; B = 200,000; N_MAX = 24; stratified exact test + Holm over 5; CPU cap 3.2 core-h
  between rounds, min 12 rounds; power 0.82 for +0.20 at N = 24.
- Certification independent of training fitness (selection + sealed ruler + pure-Python oracle; VOID on disagreement).
- Numba: timed, ported, exact differential (NUMBA_DECISION.md).
- Descriptor near-miss test (planted must-fail controls). FINDING: all 254 shortest-path intermediates score 32/20 of
  126 and are behaviourally invisible (99.4% identical action traces with equal-score arbitrary genomes): p1_slice is a
  CREDIT desert; the next cheapest informative measurement after D1 is structured partial credit vs a yoked control.
Nyx notified (#2011).

For T011 (Pallas, Q3, Fable 5.1): the frozen design is at FREEZE_D1.md; no D1 outcome exists.
For T012: needs numba 0.65.1 (harry1 system Python has none); runner supports --max-rounds-this-call / --resume for
time-limited sessions; consider a cooler host than harry1 (budget is CPU time; a throttled host completes fewer rounds).
Disclosed: early tests touched the then-intended frozen range (seed burned, range moved; PREREGISTRATION s0).
