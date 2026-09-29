# PKG-F: Causal selectivity by restoring the discarded distinctions (research-ready package, design v0.2)

Owner: Ensorain (ARC3). Status: DESIGN, instrument validated on dev (RESULTS_PKGF_PROBE.md: lossless 9e-16, PC-help
fires, sham ignored by the learned readout, forced sham hurts). Nothing is run; per the directive (Block F) nothing launches before the LM01
results are integrated, except a cheap prerequisite probe (s9). Pickup: readable cold; it assumes only the repo.

## 1. Question

Does DISCARDING particular distinctions CAUSE better future generalization? Or is a selective learner's advantage due
to capacity, fitting, regularization, readout or query compute, with the discarded information harmless if it were
still there?

## 2. Why the obvious designs fail (from LM01)

- A swap of the selective state for a relevance-blind merge (D11) is decided by construction: the merge cannot
  generalize at all, so the gap equals the selective learner's competence.
- Retraining on a subsample (#728) measures the value of the DATA, not the requirement for SELECTIVITY: both arms stay
  selective.
- The only clean manipulation keeps the selective state FIXED and changes only whether the discarded distinctions are
  AVAILABLE. This is the WTP analogue of PTE's SI01-REQ ANTI-MERGE, with a size-matched sham.

## 3. Operational definition of "discarded" (no answer built in)

For a trained selective learner S with persistent state theta_S and admitted history H = {(c_i, y_i, t_i)}:
- r_i = y_i - recon_S(c_i). The residual is what S's persistent state cannot reproduce (recon_S = the declared
  reconstruction map; recover.py).
- The DISCARDED CHANNEL D_S = {(c_i, t_i, r_i)}: the exact residual records. By construction, (theta_S, D_S) is
  lossless for H: y_i = recon_S(c_i) + r_i.
- Nothing about relevance is used to define D_S. Relevance enters ONLY in the analysis (from the generator, G2).

## 4. Arms (each with the SAME fitted theta_S; only the readout / available channel differs)

- S: theta_S with its own readout. The baseline.
- S+D/unused: theta_S + D_S stored and charged, readout = S's own. D_S is present but unused. It checks storage
  burden (expected: equal to S; a difference means an instrument error).
- S+D/learned: theta_S + D_S, with a readout that MAY use D_S: prediction = recon_S(q) + g(q; D_S), where g is a
  residual smoother (k-NN or kernel over D_S, bandwidth/k fit on a training split). It can learn to ignore D_S (g -> 0
  as the bandwidth grows).
- S+D/forced: g at a fixed, pre-declared k (it cannot opt out). Measures what D_S does when used.
- SHAM: theta_S + a size-matched channel of residuals from an INDEPENDENT stream of the same world (the same size, the
  same marginal distribution of r), same readouts. It separates "these particular distinctions" from "any extra
  records of this size".
- S+D/learned-recent: as S+D/learned, but the weight a is chosen on a holdout of the MOST RECENT 20% of records.
  Added after the dev probe (RESULTS_PKGF_PROBE.md): it separates "obsolete information hurts" from "the readout's
  selection is fooled by obsolete data".
- ORACLE-GATED: S+D with the readout restricted to the part of D_S the GENERATOR marks as relevant (analysis-only
  upper reference).
- S+D/learned-regime (added v0.2, from dev probes v3-v5b in RESULTS_PKGF_PROBE.md): the weight a is chosen on a
  holdout of the DISCOVERED current regime. The detector is MODEL-FREE: successive same-cell record disagreement across
  a candidate split, within-cell time-permutation null (p < .01, recursive on the later part); if no split, it falls
  back to the random holdout.
  - Dev (F3/F2 L2, fresh seeds): 16/16 switches found, 0/16 false on stationary twins, F3 harm 0.000 vs -1.26 with
    the all-history holdout.
  - Power vanishes below ~100 same-cell pairs (thinning test v5b).
  - REJECTED detector variants, which must not be revived without new evidence:
    - residual segmentation on the trained substrate (v3). It inherits the bounded substrate's retention recency and
      fires on stationary worlds (2/8 no-change);
    - residual segmentation on an order-agnostic substrate (v4). It has no power on F3 (4/8 detected).
  - Claim wording: v3 must not be cited as "discovered recency". Only v5 discovers.

## 5. Nuisance kinds (Block G). Each is a world variant in which D_S carries a different kind of distinction

- N1 independent noise: F2 worlds. r ~ observation noise plus unrepresented signal.
- N2 spurious correlate: F5 nuisance coordinate, nuis_p .5 (predictive in training, independent at test).
- N3 obsolete structure: F3 switch. D_S carries earlier-episode records.
- N4 episodic identity: F1. The exact cell identity; residual = the idiosyncratic cell value.
- N5 regime-specific / drifting: a new "decaying reliability" world. A distinction's predictive weight decays linearly
  to 0 over the life (T06).

## 6. Readings (per stratum, the LM01 decision rule: DELTA .30 AC, 90% paired CI)

Let d_X = AC(X) - AC(S) on the headline test set.
- RESTORE_WORKS, a positive control that the channel carries information when it is needed: on the T22 CHANGED-QUESTION
  test (a target that depends on the discarded distinction, e.g. the nuisance coordinate or the old-episode value),
  S+D/learned WINS over S. Required; if it fails, INSTRUMENT_FAILURE.
- STORAGE_INERT: d(S+D/unused) EQUIVALENT to 0. Required; if it fails, INSTRUMENT_FAILURE.
- SELECTIVITY_CAUSAL: d(S+D/learned) < -DELTA (CI), AND d(SHAM/learned) EQUIVALENT to 0, AND the oracle-gated arm is
  not worse than S. The specific discarded distinctions hurt when made available, even to a readout that could ignore
  them, and a same-size sham does not.
- GENERIC_BURDEN: both d(S+D/learned) and d(SHAM/learned) < -DELTA. Any extra records hurt: a readout or optimization
  burden, not selectivity.
- INERT (selectivity not causal here): d(S+D/learned) EQUIVALENT to 0, with RESTORE_WORKS passed. The information was
  available, the readout ignored it, and nothing changed.
- RESTORATION_HELPS: d(S+D/learned) > +DELTA. Discarding was HARMFUL, a counterexample to necessity.
- Route decomposition when harm appears:
  - forced vs learned: the harm exists only under forced use -> the learned readout avoids it; selectivity is not
    required at storage;
  - k-NN vs kernel g: retrieval interference;
  - bandwidth path: optimization burden.

## 7. Positive / negative controls (must fire before any stratum is read)

- PC-harm: a planted world where D_S contains a strong spurious correlate that flips sign at test. S+D/forced must LOSE
  by > DELTA. Shows the instrument can see harm.
- PC-help: T22 changed-question on a planted world. S+D must WIN. Shows restoration restores.
- NC: the SHAM on a world with no nuisance (N1 at zero noise) must be EQUIVALENT to 0.
- NO-CHANGE CONTROL (lit/LIT_FORGETTING_ABSTRACTION.md). Forgetting can help on STATIONARY problems through the fitted
  WEIGHTS (Sutton, Koop, Silver 2007; the Ash and Adams 2020 warm-start penalty; Nikishin et al. 2022 resets). Any
  forgetting benefit must therefore be shown ABSENT in a matched stationary world before it is attributed to
  obsolete or nuisance CONTENT. Run every N-kind with a stationary twin (same generator, no switch, no spurious
  channel).

## 8. Accounting

The D_S bytes, reads, and g's query ops are charged (accounting.py). All comparisons are reported on the Pareto surface
(bytes, query ops, AC) as well as by AC.

## 9. Cheap prerequisite probe (allowed before the LM01 integration)

On 4 dev worlds per nuisance kind (dev seeds 9_800_000+), S = the frozen LM01 SELECTIVE substrate at cap cells/4:
- (a) verify (theta_S, D_S) reconstructs H exactly (lossless check);
- (b) PC-help and PC-harm fire;
- (c) wall per world.
Single process, < 30 min, off M2 if another node is free.

## 9b. External prior (recorded before any data; it may be wrong)
Kirichenko et al. 2023: spurious-feature harm lives mostly in the LAST LAYER, and the core features remain encoded.
Last-layer retraining restores robustness; information-removing fixes (IRM) do no better than ERM in general
(Rosenfeld et al. 2021; Gulrajani and Lopez-Paz 2021). Feature use depends on how easily a feature is extracted as well
as how predictive it is (Hermann et al. 2024). The prior therefore predicts:
- harm under S+D/forced;
- INERT under S+D/learned for N2.
The design reports both, so the prior can be falsified.

## 9c. Dev-probe status (v2-v5b; not preregistered; 4-8 worlds per stratum; one readout family)

- Obsolete stored history hurts through SELECTION, not storage: with a holdout from the current regime (handed in, v2;
  or discovered model-free, v5) the harm is ~0.
- Discovery works when regimes are separated by a sharp switch and same-cell repeats are dense (L2: ~4,700 pairs).
- Exploratory (v5b): detector power and the harm itself BOTH fade as repeats thin out. The detector may fail mainly
  where it is not needed. This must be tested on a design where harm and repeats are decoupled before it is claimed.
- Untested: multiple or gradual switches; F5 nuisance drift; N5 decaying reliability.

## 9d. Required headline splits (added after the v6 control, RESULTS_PKGF_PROBE.md)

- The F3 "never_seen" test is unseen in the FINAL episode only. 87-89% of its cells were recorded in earlier episodes.
- Every PKG-F reading must be reported on two splits:
  - (a) STALE-RECALL: cells seen only in earlier regimes;
  - (b) GENERALIZATION: cells unseen in the whole stream.
- The v2-v6 F3 results are split (a) results.

## 9e. Next world designs (design only, 2026-09-29; not built)

All are built from the frozen LM01 helpers (read-only), like v6/v7, and scored on BOTH headline splits (s9d).

W-MULTI (several switches of varying size):
- K = 6 equal episodes. The redraw fraction for each switch is drawn from {1, .5, .1, 0}, recorded per world.
- The v5 detector recurses on the later part, so it should stop at the LAST switch it can resolve.
- Question: when the last switch is small (rho = .1) but an earlier one was large, does the detector stop at the
  large one?
  - Then the holdout is too old but still post-large-switch.
  - Or it finds the small one, and the holdout is short but correct.
- Prediction candidate: stale-recall dAC(SD_cp3) >= dAC(SD_all) in >= 80% of worlds; never below -0.2.

W-DRIFT (gradual change; the v5 statistic assumes a step):
- One transition, x_t = (1 - lam(t)) * x_old + lam(t) * x_new, with lam ramping linearly from 0 to 1 over a window of
  width w (fractions of the stream: w in {.02, .2, .5}), centred at 2/3.
- Question: does the step detector localize a ramp, and where? The start, the middle, or the end?
- The right holdout is after the ramp ends. A detector that fires at the ramp's middle gives a holdout that still
  contains partly-stale records.
- Prediction candidates:
  - detection in >= 7/8 at w = .02 and .2, and <= 4/8 at w = .5;
  - the detected start falls inside the ramp.

N5 (decaying reliability; the Block G nuisance kind not yet probed):
- The noise SD grows linearly over the stream (x fixed), so old records are MORE reliable than recent ones: the
  opposite of recency.
- Question: does anything tempt the readout toward recency here?
  - The v5 detector should find NO regime change: the within-cell mean is unchanged and only the variance grows.
    Its statistic is squared disagreement, so it may fire on the variance growth. That is a known risk, to be tested.
  - The recency holdout (v2, "last 20%") would pick its weight on the noisiest records.
- Prediction candidates:
  - v5 false detection >= 4/8 (it IS variance-sensitive, and that is a limitation);
  - the recency holdout is worse than the all-history holdout on stale recall.

Build order: N5 first. It is the sharpest test of whether "recency" and "regime detection" are confused anywhere in
this pipeline. Then W-DRIFT, then W-MULTI. Each is precommitted before its run with the thresholds above, or with
thresholds tightened after a world-property check that runs no detector.

## 10. What it cannot establish

- Necessity beyond the tested readout families (k-NN / kernel residual smoothers). A cleverer readout might use D_S
  without harm.
- Anything about learners that never form a theta_S (it presupposes a selective learner).
- Causality of the ORIGINAL discarding event over the life (it tests AVAILABILITY after the fact, not a learner trained
  with D_S available from the start; that is PKG-F2: train S+D jointly online).

## 11. Open design questions (for the adversarial reviewer)

- Q1: Is recon_S + g a fair readout, or does additive composition favour INERT?
- Q2: Should theta_S be refit jointly with D_S available (F2)? That confounds optimization.
- Q3: How should the SHAM be matched: residual marginals, or the full (c, r) joint of an independent stream?
