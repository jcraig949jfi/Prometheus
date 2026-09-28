# PKG-F: Causal selectivity by restoring the discarded distinctions (research-ready package, design v0.1)

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
