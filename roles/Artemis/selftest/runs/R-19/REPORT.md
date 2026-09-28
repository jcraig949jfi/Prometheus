# REPORT

## 1. WHAT I SET OUT TO TEST

The program has three connected proposals that were never started. (a) A "reversible
core" experiment: an agent whose update is a bijection, whose state is bounded and which
receives fresh input, must push one item per step out through a priced export channel.
Does it learn to export irrelevant state, compared with random export (and FIFO export)
at a matched elimination curve? (b) A distinction-survival assay: which input distinctions
survive in a system's accessible state, with counter-keyed RNG and a matched blind control.
(c) A common replay-and-perturb hook with full-state hashes (RNG included). No reversible
agent substrate exists on any host, so within this budget I built the smallest honest one
myself and used it to answer the design question behind (a), and to calibrate the parts of
(b) and (c) that can be checked on a toy: does the experiment as specified discriminate
anything, and do the proposed controls and fixtures behave as the stewards expected?

## 2. WHAT I DID

Inputs: only the design memo, falsifier table and M2 attack notes (read, not run) at
repo origin/main 6ff2b2f8a (memo first committed at d50103524). No engine code was run;
I did not archive or execute repository code. All code is new, under
/home/jcraig/artemis-selftest/work/R-19/src:
- revcore.py (sha256 27cff279...): bounded reversible agent. K=8 slots; each step one new
  item (value bit, tag bit, birth stamp) arrives; the policy picks one of the K+1
  candidates and swaps it onto an export tape (outside the boundary, never read back).
  Latent relevance rel~Bern(0.25) is generator-side; tag = rel with prob (1+rho)/2.
  Competence = recall of target weight held (accuracy = 0.5 + 0.5*recall), queried every
  step after t=100 of N=400. Two regimes: "decorr" (target uniform over all relevant items
  so far: relevance independent of age by construction) and "coupled" (target weight
  exp(-age/16): relevance correlated with recency). RNG is counter-based splitmix keyed by
  (seed, t, site, purpose), with a "seq" option (sequential stream whose tie-break draw
  count depends on state) for the cheat fixture. Includes an explicit inverse and a
  full-state SHA-256 (slots + RNG counter/key + clock).
- selftest.py: inverse run from final state + tape back to the empty initial state
  (64 episodes x 400 steps): exact. Replay to t=200 gives identical full-state hashes in
  both RNG modes; a perturbation at t=150 changes the hash.
- experiment.py (sha256 4eb9181c...): per (regime, rho in {0,.1,.25,.5,1}): learn a
  3-weight linear export score (tag, age/K, tag*age/K) by cross-entropy ES (12 gens x 16,
  256 training seeds); evaluate on 2000 held-out seeds with common random numbers:
  learned, random, FIFO, blind_matched (the learned policy fed an independent tag with
  the same marginal: relevance-blind, same dynamics), planted (export lowest tag; positive
  control). Equivalence margin = 95th pct |random - random| over 10 independently keyed
  pairs on 512 dev seeds; verdicts by 90% CI (TOST) against that margin. Merge-time curve =
  distribution of residence time at export (KS distance reported).
- dsa.py (sha256 bac18a34...): paired runs (2000 pairs) differing only in one item born at
  t*=200 (value flip = inert distinction; tag flip = dynamics-relevant distinction);
  fraction of pairs whose accessible state still differs at t*+h, stratified by that
  item's generator relevance; random vs tag-selective export; keyed vs sequential RNG.
Commands: python3 selftest.py; python3 experiment.py (outputs experiment.log,
out_experiment.json); python3 dsa.py (dsa.log, out_dsa.json). A first experiment run
(experiment_v1.log, out_experiment_v1.json) scaled age by N; that made the age feature
too small for the learner to use (it could not rediscover FIFO in the coupled regime,
learned 0.297 vs FIFO 0.368 on training seeds). I fixed the scaling to age/K and reran; v2
is reported. The decorr results are unchanged between versions.

## 3. RESULT

Reversible core (recall; margin decorr 0.0005, coupled 0.0036; CI = 90%):

  regime   rho  I(tag;rel)  learned random fifo  blindM planted  learned-random (verdict)      learned-blindM (verdict)
  decorr   0    0.000       .0370   .0369  .0369 .0363  .0370    +.0001 [-.0006,.0008] UNRESOLVED +.0007 UNRESOLVED
  decorr   .1   0.005       .0429   .0369  .0369 .0369  .0429    +.0060 SELECTIVE             +.0060 SELECTIVE
  decorr   .5   0.143       .0745   .0369  .0369 .0370  .0745    +.0375 SELECTIVE             +.0375 SELECTIVE
  decorr   1    0.811       .1501   .0369  .0369 .0364  .1501    +.113  SELECTIVE             +.114  SELECTIVE
  coupled  0    0.000       .3676   .3090  .3676 .3676  .2301    +.0586 SELECTIVE (false)     .0000 EQUIVALENT
  coupled  .1   0.005       .3745   .3090  .3676 .3577  .2601    +.0655 SELECTIVE             +.0168 SELECTIVE
  coupled  .25  0.034       .4147   .3090  .3676 .3231  .3090    +.106  SELECTIVE             +.092  SELECTIVE
  coupled  1    0.811       .8505   .3090  .3676 .2073  .6307    +.542  SELECTIVE             +.643  SELECTIVE

- Export rate is identical for every policy (exactly 1 item/step) by conservation; it
  needs no matching. The merge-time (residence) curves are NOT matched by random export
  (KS learned vs random 0.17-0.83) but are matched by blind_matched (KS <= 0.001).
- The outcome is set by the generator: whenever the observable features carry any
  information about future relevance (even 0.005 bits/item), the learned exporter beats
  random far beyond dev noise. With zero information (decorr, rho=0) every policy is
  identical in expectation; the "random = learned" reading then comes out EQUIVALENT or
  UNRESOLVED depending only on how noisy the arbitrary learned weights are (v1:
  EQUIVALENT; v2: UNRESOLVED, CI half-width just above the margin).
- Coupled regime, rho=0: the learner rediscovers FIFO. Against RANDOM export it earns a
  large, significant "selective advantage" (+.059) that is pure recency. The
  curve-matched blind control (and FIFO) read EQUIVALENT (0.0000), correctly.
- The planted positive control (tag-only selective policy) FAILS to beat random in the
  coupled regime at rho <= .25 (-.079 at rho=0, 0.000 at .25), because it discards recency.
  A positive control that works in one task can be silent in another.
- blind_matched can be WORSE than random (coupled rho=1: .207 vs .309): holding the
  learner's age profile with blind content is a different, harsher baseline.

Distinction-survival assay on the reversible core (fraction of pairs still differing):
- Keyed RNG: every distinction leaves accessible state once its item is exported (differ
  -> 0.000-0.003 by h=199). In a reversible core "merging" in accessible state is export
  and nothing else; the full state (including the tape) never merges.
- Relevance stratification works on this substrate: rho=1, selective export, inert (value)
  flip: relevant items differ 0.906/0.743/0.349/0.027 at h=0/8/32/128, irrelevant items
  0.000 at all h; random export shows no strata difference (0.131 vs 0.129 at h=16).
- Cheat fixture reproduced: with a sequential RNG whose draw count depends on ties, a
  tag flip leaves 49% (rho=0) and 67% (rho=1) of pairs NEVER reconverging at h=199,
  versus 0.0% and 0.3% with keyed RNG. The inert value flip is immune (does not change
  draw counts). The contamination starts at once (h=1: 0.96 seq vs 0.85 keyed).
- Pair-type matters: tag flips (which change how the item is treated) erase the relevance
  strata (rel .743 vs irr .698 at h=8), value flips show them cleanly.
- My own harness bug, fixed before reporting: the first DSA run took the relevance oracle
  from the keyed generator path while the sequential-RNG runs drew items from another
  stream, so the strata were wrong in seq mode. The oracle must come from the same
  generator path as the specimen.

Replay-and-perturb hook: a common interface is small in a toy (replay to t, perturb one
item, full-state hash including RNG counter; bit-identical replays). On origin/main a
term grep found checkpoint state hashes only in SFE (currently down); no cross-engine
replay-and-perturb interface. That was a grep, not a code audit.

## 4. DID IT RESOLVE THE QUESTION

Partly. On the design question behind the reversible-core experiment: yes, at toy scale.
The experiment as specified is mostly decided by construction. A bounded reversible
agent that can learn will export selectively exactly when observable state carries
information about future relevance; the falsifying reading "random export does as well
as learned export" holds exactly when the generator provides none. The quantity that
determines the result, I(observable features at export time; future relevance), is
fixed by whoever designs the task. The real experiment was not built on an engine (no
NPE substrate), and the DSA was not applied to any frozen specimen (PTE, AGE, Z80). The
replay hook was demonstrated only in the toy. Those remain.

## 5. CONSEQUENCES

- False or weak premise: the reversible-core experiment is not a strong attack on the
  "reversible" and "indiscriminate loss" countermodels unless the preregistration (i)
  measures and reports I(features; relevance) per task before the run, (ii) treats a
  "random = learned" result at I=0 as uninformative (decided by the generator, not the
  agent), and (iii) says what it would mean for the law if a learner is selective whenever
  I>0 (which is close to a theorem about learners). Whoever owns the selective-
  irreversibility hypothesis and falsifier table, and the engine seat named to build the
  reversible core, should know.
- Positive result for the stewards' design rules: rate matching is automatic on a
  reversible substrate and random export is NOT curve-matched; the random control issues a
  false selectivity certificate when relevance tracks recency (+.059), while a
  curve-matched blind control (same policy fed a shuffled cue) catches it. The FIFO third
  arm only helps where recency-relevance decorrelation is measured. Recommend the
  shuffled-cue, curve-matched control as the primary blind arm, with random reported too.
- Instrument caution: a planted positive control can be silent when the task has a
  second relevant axis (recency). Positive controls must be validated per task.
- Reproduction of a predicted defect: the sequential-RNG cheat fixture behaves exactly as
  the M2 attack predicted (up to 67% false non-merging). Engines whose RNG streams consume
  state-dependent draw counts must be keyed before any DSA reading.
- DSA on reversible substrates must read export (distinction leaves accessible state), not
  exact merge; the relevance oracle must come from the same generator path as the
  specimen; inert vs dynamics-relevant perturbations give different strata.
- Harness lesson from my own run: feature scaling in the learner (age/N) silently hid a
  whole policy class; a "learned" arm needs a check that it can rediscover known
  baselines (FIFO) before its non-difference is read.

## 6. COST

About 1.5 hours of my time. CPU about 40 minutes total (experiment v1 12 min, v2 20 min,
DSA two runs about 4 min, one accidental duplicate start about 2 min that I killed before
it wrote output, small checks). At most 2 processes of mine at a time, under 150 MB RAM,
CPU only. Not done: an engine-hosted reversible core (NPE), DSA adapters on frozen PTE /
AGE / Z80 specimens, a code audit of each engine's RNG and state for a common replay hook,
a closed-form bound linking advantage to I(tag; rel), and replication over K, p, N and
learner seeds.
