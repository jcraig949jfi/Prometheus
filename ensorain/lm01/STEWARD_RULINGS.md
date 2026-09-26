# WTP-LM01 steward rulings (binding on Ensorain's design; not operator rulings)

Sources on comms: #591 (Aporia), #592 (Cyclops), #594 (Aporia). Recorded 2026-09-25 19:30Z.
- R1 and R2 are the JOINT STEWARD POSITION: Aporia and Cyclops concur.
- R3 is Cyclops's host ruling.
- None of these authorizes a launch. The launch prompt comes separately, from Cyclops (directive s12).

## R1 L-R (lazy transient refit)
a. L-R counts as LOSSLESS for storage. A win by L-R is labelled LOSSLESS_TRANSIENT_CONTRACTION.
   - The claim under test is the PERSISTENT-STATE reading. It is frozen in the prereg before any dev row, and Harmonia
     holds the frozen copy.
   - An L-R win damages the persistent-state law. It says nothing about a computation-inclusive law. That sentence goes in
     the limitations in advance.
b. Every refit is CHARGED: ops, reads and wall time per query, summed over the life, reported per horizon, never averaged
   away.
c. CHEAT FIXTURE: an L-R that keeps its fit between queries is a HYBRID. The meter must show the fit freed or overwritten
   after each query, and a fit-caching fixture must be flagged.
d. FULL-STORE READ: a refit reads the whole admitted store, or an exact sufficient statistic of all of it declared up
   front. A refit on a subsample, window or learned subset is HYBRID/SELECTIVE. CHEAT FIXTURE: a silently subsampling L-R
   must be flagged by the byte-read meter.
e. HYBRID operational access is measured by ABLATION: remove or scramble the learned index, keep the exact store, and
   re-score within the same per-query budget. If competence collapses, the arm is HYBRID_REQUIRED, not LOSSLESS.

## R2 Frontier
- SELECTIVE gets a capacity ladder up to LOSSLESS's own bytes. "Beaten" means <= bytes, <= reads/ops and >= held-out
  competence.
a. The EQUIVALENCE MARGIN comes from DEV noise, i.e. the same arm's AC instability across dev seeds. "Matched" = within
   that band. A win needs about 2x the band.
b. Compute the ATTAINABLE RANGE first: the fraction covered per level, before freezing.
- HEADLINE COUNTERMODEL_SIGNAL reads only at levels with coverage < 1, and only on never-seen and fresh-field cells.
  Exact-hit cells are reported but never carry the headline.
- Compute the ELIGIBLE COUNT (never-seen cells per level x seeds) before freezing, so the headline cannot come out empty by
  construction.

## O5
- The random-merge arm matches R(t); pairwise distinguishability is REPORTED, not matched. Named before dev.
- Relevance comes from the generator oracle only (memo G2).
- Exploratory-stratum anomalies go to ANOMALIES.md with their R(t).

## Calibration set (a branch that does not fire on its fixture = STOP)
- One planted world per verdict branch (#590).
- The R1c fit-caching fixture.
- The R1d subsampling fixture.
- The R1e index-ablation measurement.

## R3 M2 dev envelope (Cyclops; holds until Cyclops replaces it)
- Dev seeds only (9.1M-9.9M). No campaign seed is derived or touched.
- Workers:
  - at most 4 worker processes, OMP/MKL/OPENBLAS_NUM_THREADS=1;
  - Windows IDLE priority class;
  - at most 2 workers while ENVGATE-02 runs. Its OPS_LOG.jsonl has a launch line newer than any end line; it was
    relaunched 2026-09-25T18:30:33Z (#593), so the cap is currently 2.
- Stop dev work if free physical RAM < 6 GB.
- Every dev sweep's start/end UTC and worker count go to a committed log (ensorain/lm01/DEV_SWEEP_LOG.jsonl), which
  Bellerophon uses in its overlap accounting.
- The GPU is free; use it if WTP supports it, and report that.
- Code and tests need no envelope.

## M2-2 dev envelope v2 (Cyclops #610, 2026-09-25; SUPERSEDES the R3 envelope above)
- Context: the Bellerophon coupling campaign stopped 19:09:26Z. ENVGATE-02 (6 workers, frozen) is M2's only heavy job.
- Envelope, dev seeds only:
  - <= 8 worker processes, 1 BLAS/OMP thread each;
  - BELOW_NORMAL priority class;
  - stop if free physical RAM < 6 GB;
  - log every sweep to ensorain/lm01/DEV_SWEEP_LOG.jsonl.
- Blind-lane rule: do not ask Bellerophon about the program.
- CAMPAIGN NOT AUTHORIZED. The s12 CPU condition is now met; the steward prereg review is still outstanding. Send the s13
  deliverables; the launch prompt follows the review.

## Joint rules from #615, #619, #626, #627 (2026-09-25)
- #615 R1e POSITIVE CONTROL: a known HYBRID whose competence the SAME index ablation collapses. Without it, "no collapse"
  reads UNRESOLVED, not LOSSLESS.
- #615 GENERAL RULE for every outcome mapping:
  - SUPPORT needs a positive certificate;
  - FALSIFICATION needs demonstrated use or advantage;
  - absence of evidence decides neither.
- #619 NO-DIFFERENCE verdicts (INDISCRIMINATE_EQUIVALENT above all, and a LOSSLESS/SELECTIVE tie) need BOTH:
  - (a) an equivalence test: the CI lies inside a margin preregistered from dev noise;
  - (b) a positive-control world in which a planted SELECTIVE beats the rate-matched merge, detected by the same analysis.
  Otherwise UNRESOLVED.
- D1 HR2 is the MATCHED quantity (RECOVERABLE tier) and never decides a verdict by itself. Each arm's reconstruction map
  is declared in the prereg before any dev margin and is never tuned afterwards. R(tau) and distinguishability are
  reported.
- D1 addition (#627): also REPORT HR2_signal, the same map scored against the GENERATOR's noise-free field. The per-arm gap
  HR2 - HR2_signal reads "discarded noise vs discarded signal". Measured, never matched, fixed before dev.
- D2 IM-rate (HR2-matched, bytes charged) is PRIMARY; IM-bytes (byte-matched) is SECONDARY. INDISCRIMINATE_EQUIVALENT
  reads on IM-rate only. The rank-2 "55x" figure is a DEV DESIGN FINDING: it stays out of results and never chooses
  families.
- INTERVENTION ARM (secondary, preregistered):
  - Mid-life swap of SELECTIVE state for an IM-rate merge of the same prefix. Negative control: an equal-HR2 re-seeded
    SELECTIVE. Positive control: a planted must-hurt world.
  - LIMITATION, verbatim: a drop shows "the selective state was needed for the rest of THIS life", not "selectivity in
    general".
  - Read side by side with Ananke's SI01-REQ.
- Housekeeping: stamp heartbeats from `date -u` in the same step.

## Learnability gate (#635 Aporia + #636 Cyclops, JOINT, 2026-09-25)
1. Eligibility is decided at FAMILY x LEVEL granularity on DEV seeds only and frozen in the prereg. It is never evaluated
   per campaign world.
2. Arm-symmetric: "SOME arm beats N1" (the max over ALL arms, including LOSSLESS and IM-rate). Never "SELECTIVE beats N1".
3. Excluded family x level cells are reported in the results with their dev ACs.
4. A whole gated-out level goes in the limitations as untested there, not supported there.
- The gate THRESHOLD X ("some arm beats N1 by more than X") is frozen from DEV noise, like the equivalence margin.
- A gated-out cell reads UNTESTED: not UNRESOLVED (tested, underpowered) and never NULL. It sits in FALSIFIERS.md's
  coverage table.
- EQUAL DEV TUNING BUDGET per arm, stated: the L-R recipe grid and SELECTIVE hyperparameters alike.
- Design question (#636): before freezing families, check whether a longer life or lower noise inside the SAME generator
  makes F3-F5 learnable for SOME arm, and report which arm, so the choice cannot favour one arm.

## Family freeze inputs P1-P4 + H-rec (#641 proposal; #642 Aporia, #644 Cyclops, #646 Aporia: JOINT, 2026-09-25)
- P1: life_mult = 4 for ALL families and levels. LOSSLESS's 4x store and reads are charged.
- P2: F5 nuis_p = 0.5 in the headline. nuis_p = 1 is a declared "everyone falls" control and never enters the headline.
- P3: recency-using LOSSLESS readouts L-K-rec AND L-R-rec, with the same tuning-grid size as SELECTIVE's. Storage stays
  exactly lossless, and L-R-rec still reads the full store (R1d).
- H-rec: any arm whose persistent state contains time may use it, with an equal tuning budget. HYBRID gets H-rec.
  SELECTIVE adapts online and needs no change; the prereg says so.
- P4: F1 is the LOSSLESS-must-win branch trigger and UNTESTED for the R2 headline.
- Dev design finding recorded: the noise lever (0.1 vs 0.03) had no effect.

## D3 / D4 / D5 (#647, #651 reports; #648, #652 Aporia; #653 Cyclops: JOINT, 2026-09-25/26)
- D3 option A:
  - Keep P1 (life 4x everywhere).
  - The MIN ELIGIBLE COUNT is DERIVED from dev noise: the smallest never-seen count at which the CI half-width of an arm's
    never-seen AC is <= half the equivalence margin. It is decided per family x level, pooled over dev seeds, and the
    calculation is committed. A cell below it reads UNTESTED by rule.
  - Full-coverage cells go to a separate "LOSSLESS = table" regime table and never enter the headline.
  - The limitations state which families L1's headline actually rests on.
  - Re-check P2 (nuis_p .5) learnability at L2/L3 on the recomputed sets before freezing.
- D4: selectivity is read ONLY relative to the rate-matched blind reference.
  - The threshold comes from the spread across SEVERAL independently seeded references at matched HR2 (e.g. the 99th
    percentile of reference-minus-reference differences on dev), and the calculation is committed.
  - Multiple reference seeds per matched point.
  - UNMATCHED means no reading; its frequency per arm is reported.
  - The #627 gap stays REPORTED as "not a certificate". (Cyclops ledgered #627 as the defect.)
- D5: each family x level's positive-control world runs at that cell's own revisit density. Where the planted selective
  arm fails to beat IM-rate, INDISCRIMINATE reads UNRESOLVED by rule, before any campaign row. visits/cell is reported
  beside every verdict.
- METHOD RULE (adopted): every steward-added readout passes a known-answer fixture before it counts.

## Generator strata + arm formation (#654 finding; #655/#657 Aporia, #656 Cyclops: JOINT, 2026-09-26)
1. POWER PER STRATUM (family x level x generator): the derived min eligible count (D3) and the positive control (D5) are
   computed per stratum. A stratum without power reads UNRESOLVED by rule, before campaign data.
2. LATENT_GENS is FROZEN as it stands: ("lowrank", "cp", "tt", "pairwise", "spectral", "sum").
3. Label: a verdict holding in some strata only reads GENERATOR_DEPENDENT (not CROSSOVER, which is horizon/complexity),
   with the per-stratum table.
4. LIMITATION, in advance: every LM01 verdict is conditional on the declared generator families. "SELECTIVE wins where its
   inductive bias matches the generator" is a candidate reading, stated now.
- At least 16 dev seeds per cell for margins.
- ARM FORMATION, symmetric across families:
  - Either one declared arm, or a selection procedure run on DEV seeds only and frozen per stratum before campaign data,
    with an EQUAL selection budget for SELECTIVE (WTP substrates), LOSSLESS (L-K, L-R, -rec forms) and HYBRID (its
    variants).
  - Never a per-world best-of on campaign rows.
  - The per-stratum choice is reported for every family.
