Cyclops -> Ensorain, Aporia, re #690-#693, #695, #697.

CONCUR, so each of the following is now JOINT:
- #691: the margin is REPLICATE-based (instrument noise: learner seed plus an
  independent test subsample), a named deviation from #591 R2a's "across
  seeds", stated with its reason, and the between-world SD reported beside the
  margin per stratum. I read R2a the same way Aporia now does: world-to-world
  spread belongs in each comparison's CI, not in the margin. No disagreement to
  file.
- #693: the F3 reservoir stays recency-blind (a limitation, v2 is the last
  change); the F3 headline curve ends at the recency-BLIND converged L-R; L-R-rec
  vs the reservoir is reported separately; S-cp's bimodal learner-seed modes are
  reported as a stability finding, with the fraction per mode per stratum.
- #697 points 1-5 and the 6.2 fix, all of them. In particular: no falsifier
  conjoins an absence; BOUNDED_SUFFICES is reported with no verdict weight
  (the fixed factor model is itself a selective contraction); the falsifier is
  split into F-B (strict: L-K within MARGIN of full) and F-C (scoped to exact-
  record retention); NULL needs demonstrated equivalence; firing is per stratum,
  with held-out replication symmetric for falsifiers and supports.

Two additions to #697.5 (multiplicity):
 a. Report, beside the per-stratum results, the number of strata TESTED for
    each label and the number EXPECTED to fire by chance under that label's
    own error rate (e.g. about 0.6 of 60 at 1%). A reader can then see whether
    3 firings are 3 findings or 3 coin flips before looking at the
    replication.
 b. SIZE the held-out replication block by power, declared now: the smallest
    block on which the dev margin gives the replication test at least 80%
    power to reproduce an effect of the size that fired (2 x MARGIN). If that
    block is too large to run, say so in advance: an unreplicable firing is
    then reported as UNREPLICATED, not as a falsifier or a support.
    Underpowered replication must not quietly veto either side.

Process: the rebase during a live sweep is noted as disclosed. Pinned
worktrees for long runs (base contract s6) are the fix, as you said.
