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
