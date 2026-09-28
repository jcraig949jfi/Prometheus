REPORT

1. WHAT I SET OUT TO TEST

Whether a record of failed attempts is useful material for choosing what to try next, at a matched
proposal budget: if a proposer is allowed to see only past failures, does it pick "useful"
configurations more often than a blind (uniform) proposer picking the same number? And, the sharper
form of the question: does the *content* of a failure (how a run died, how far it got) add anything
over a plain pass/fail verdict learner? Earlier tests of this in the program used hidden-bitstring
toy landscapes with tiny fossil sets and came out null; here I used the one large, committed,
per-candidate, verifier-scored run record that exists today (the z80atlas observatory index,
23,471 runs over a 16-factor configuration space), offline, with no new runs. This tests SELECTION
among configurations the campaign already drew, not GENERATION of new ones.

2. WHAT I DID

Data: roles/Nestor/campaigns/z80atlas-2026-09-19/observatory/{INDEX.jsonl.gz, ADJUDICATION.json}
@3b407946e, exported with git archive into src/ (read-only use).
Code (all in /home/jcraig/artemis-selftest/work/R-28/scripts, stdlib + numpy):
  fvb.py   pre-specified test (PREREG.md written before any outcome model was fit)
  fvb2.py  same plus post-hoc control arms (flagged exploratory)
  wsweep.py, nested.py  exploratory weight sweep and an honest nested version of it
Outputs: out/results.json, out/results2.json, out/summary_posthoc.txt, out/weight_sweep.txt,
out/nested.json, out/nested.txt.

Design. Unit = a distinct 16-factor cell in the test half; label = mean usefulness of its test runs.
Nearly every cell was run once (20,638 distinct cells), so every proposer must generalise over
factor levels to unseen cells. Split by seed (seed-matched experiment/control pairs stay together):
primary = seed parity both ways, robustness = 20 random seed-hash splits (8 more in the nested test).
Usefulness, fixed in advance: U1 = not extinct AND endogenous births > 0 (base rate ~0.21);
U2 = crossed (~0.27); U3 = run carries an ADMISSIBLE adjudicated special flag (~0.027).
Proposers (naive-Bayes over factor levels, add-1 smoothing, random tie-break):
  B  blind: uniform.
  F  failure rows only: rank cells least like past failures (-log P(cell|failure)).
  S  success rows only: log P(cell|success).
  V  bare-verdict learner (ERM baseline): log-odds from all train rows, verdict only.
  T  failure-trace only: additive per-level model of a graded "near-miss" score fitted on train
     failures (survival fraction, any endogenous birth, replicated, comp_max, held_max, not extinct).
  VT V + T (z-scores summed, weight 1, fixed in advance).
Post-hoc: N = outcome-free "rarely tried" proposer from the attempt ledger (controls for F just
avoiding common design levels); Ta/VTa = a trace target aligned to each label. Then an exploratory
weight sweep and a nested test in which the trace weight is chosen on an inner split of TRAIN only.
Metric precision@k, k in {50,100,200,500,1000}, primary k=200 (~2% of ~11k test cells);
permutation null over cell labels (1000), paired bootstrap over test cells (500-1000).
Note: with a complete attempt ledger, "failures + ledger" equals the full verdict record (attempts
minus failures = successes), so failure-only vs verdict ERM is the only meaningful information split;
what failures could add beyond V is their trace content.

3. RESULT

Precision@200, primary seed-parity splits (even->odd / odd->even); blind = base rate.
                        U1              U2              U3
  B (blind)            0.216/0.212     0.272/0.274     0.026/0.028
  F failures only      0.820/0.845     0.403/0.403     0.000/0.000
  S successes only     0.775/0.740     0.845/0.848     0.958/0.990
  V bare verdicts      0.940/0.910     0.901/0.879     0.959/0.983
  VT verdicts+trace    0.270/0.287     0.640/0.711     0.735/0.795   (pre-specified weight 1)
  N novelty, no outcome 0.365/0.325    0.015/0.040     0.000/0.000   (post-hoc)
Paired bootstrap 95% CIs at k=200:
  F - B:  U1 +0.60 [+0.55,+0.66] / +0.63 [+0.58,+0.68];  U2 +0.13 [+0.06,+0.19] both splits;
          U3 -0.03 (F finds nothing).  Permutation p = 0.001 for U1, U2.
  F - N (post-hoc): U1 +0.46/+0.52, U2 +0.38/+0.36, CIs exclude 0 -> F's gain is not just
          "try rarely-tried levels"; failures do carry outcome information.
  F - S:  U1 +0.05 [-0.03,+0.13] / +0.11 [+0.03,+0.18];  U2 -0.45;  U3 -0.97.
  F - V:  negative on every label (U1 -0.12/-0.07, U2 -0.50/-0.48, U3 -0.96).
  VT - V (pre-specified weight 1): -0.66/-0.62 (U1), -0.25/-0.17 (U2), -0.22/-0.19 (U3).
20 random splits agree in sign and rough size for every arm above.

Exploratory, nested (trace weight chosen on train only, 10 splits, k=200):
  U1: generic trace adds +0.02 to +0.08 over V in 10/10 splits (mean ~+0.05, CI excludes 0 in 9/10);
      V alone is 0.905-0.96, so this closes about half of the remaining gap.
  U2: generic trace weight selected as 0 in 8/10 splits (no gain); the label-aligned trace adds
      ~+0.02 on average (CI excludes 0 in 3/10 splits).
  U3: at ceiling, nothing to add.
(The splits overlap in data, so the 10/10 is not ten independent replications.)

Plain conclusion. (a) A failure-only proposer beats blind choice by a large margin where
successes are common (U1 about 4x, U2 about 1.5x the base rate) and the gain is not explained by
novelty-seeking; but it is useless for the rare target (U3), where the failure record is
essentially the attempt distribution. (b) The failure half of the record is not systematically
more informative than the success half (better on one label, far worse on two). (c) A plain
verdict learner beats every failure-only proposer on every label. (d) Failure-trace content added
at the pre-specified weight made things much worse; tuned honestly on train, it gives a small
consistent gain (~+0.05) on the one label whose definition is itself a conjunction of trace fields
(non-extinction and endogenous births), and ~nothing elsewhere. That U1 gain most likely reflects the
naive verdict learner missing an interaction the trace decomposes, not "failure is metabolic
material" in a stronger sense; a stronger verdict learner was not tried.

4. DID IT RESOLVE THE QUESTION

Partly. For selection among already-drawn configurations in the one big committed per-candidate
corpus: yes, P(useful | failure record) > P(useful | blind) at matched budget, clearly, for common
targets; no for a rare target. The more decision-relevant form -- do rich failure traces beat bare
verdicts -- gets a weak, label-dependent, exploratory-only yes (U1) and a null elsewhere; the
pre-specified combination rule failed. It does not address generation of new candidates (the
question's own limit), nor transfer to engines where a failure is not exact information about the
target beyond this one. Which corpus is big enough today: this z80atlas index (23,471 per-run,
verifier-scored rows) is usable and committed; I did not re-verify the other corpora.

5. CONSEQUENCES

- Positive result (modest, selection only): failure-only records do carry selection information
  in a real multi-physics run index, unlike the null in the toy fossil seasons. This contradicts a
  strong "records are pure exhaust" reading at the configuration level.
- But the practically relevant comparison favours bare verdicts: nearly all value is in the
  pass/fail label, which a verdict learner exploits better than any failure-only proposer. Rich
  failure traces add at most a few points of precision, only for some targets, and only with tuned
  weighting. This supports keeping a freeze on enlarging failure corpora for their own sake, with
  an exception for storing a small set of per-candidate trace fields that decompose the target
  (cheap, and showed a small honest gain).
- Recommended next test before any investment: repeat the nested comparison with a stronger
  verdict learner (pairwise interactions / logistic) to see if the U1 trace gain survives; if it
  does, only then take it to a generative engine.
- Premise note: "failure-only vs success-only" is ill-posed when the attempt ledger is kept,
  because failures + ledger = full verdicts; the only real question is trace content vs verdict.
- Harness note (not a defect in the data): usefulness in this index is strongly predictable from
  one or two factors (reproduction mode for U1, the spontaneity/seeding factors for U3), so
  precision@k saturates near 0.9-1.0; future tests should condition on those factors or use a
  harder target.
- Who should know: the seat deciding on the failure-corpus freeze, the fossil-metabolism owners
  (their toy null does not transfer as a blanket null), and the observatory owners (their index is
  the one corpus fit for this question today).

6. COST

About 45 minutes of my time. CPU about 13-14 CPU-minutes total (four scripts, single process,
peak RAM ~0.3 GB). No new runs, no holdout used, no database access. Not done: stronger verdict
learner; cell-level interactions; generative follow-up; verification of other corpora's size/location.
