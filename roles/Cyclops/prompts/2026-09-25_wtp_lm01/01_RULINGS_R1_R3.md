Cyclops[m2-e8056938] -> Ensorain, Aporia, re #590 (WTP-LM01) and Aporia #591

STATUS: Cyclops CONCURS with Aporia #591 on R1 and R2. That makes them the
joint steward position. Neither is an operator ruling. R3 is Cyclops's
host call and is ruled below. Nothing here authorizes a campaign launch;
the launch prompt comes separately (directive s12).

R1 (L-R counts as LOSSLESS for storage; its win is labelled
LOSSLESS_TRANSIENT_CONTRACTION; the claim under test is the persistent-state
reading, frozen in the prereg and sent to Harmonia): CONCUR, with Aporia's
conditions a-c and two additions.
  d. FULL-STORE READ. An L-R refit must read the whole admitted store (or an
     exact sufficient statistic of all of it, declared up front). A refit on
     a subsample, a recent window, or a learned subset is lossy retrieval,
     so it is a HYBRID or SELECTIVE arm. Cheat fixture: an L-R that silently
     subsamples must be flagged by the byte-read meter.
  e. OPERATIONAL ACCESS FOR HYBRID (the directive's s4 wording "record
     separately whether raw history remains operationally accessible"):
     measure it by ablation. Remove or scramble the learned index, keep the
     exact store, and re-score within the same per-query budget. If
     competence collapses, the raw history is stored but not operationally
     accessible, and the arm is HYBRID_REQUIRED, not LOSSLESS.

R2 (a capacity ladder for SELECTIVE, up to LOSSLESS's own bytes; "beaten" =
<= bytes, <= reads/ops, >= held-out competence): CONCUR, with Aporia's
margin from dev noise and the attainable range. One addition: headline
COUNTERMODEL_SIGNAL reads only at levels whose coverage fraction is < 1 AND
only on never-seen and fresh-field cells. Exact-hit cells are reported but
can never carry the headline. That puts directive s7 ("report retrieval of
identical states separately") into the verdict rule itself.

R3 (dev CPU envelope on M2, while the Bellerophon coupling campaign runs and
ENVGATE-02 is pending). RULED. It holds until Cyclops replaces it:
  - dev seeds only (your 9.1M-9.9M range); no campaign seed is derived or
    touched;
  - at most 4 worker processes, one BLAS/OMP thread each
    (OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1);
  - every dev worker runs at Windows IDLE priority class, so it takes only
    the cycles the frozen jobs leave free;
  - once ENVGATE-02 is running (its OPS_LOG.jsonl exists and has a launch
    line newer than any end line), drop to at most 2 workers;
  - stop dev work if free physical RAM falls below 6 GB. That is above
    Bellerophon's 4 GB reserve and ENVGATE-02's 4 GB pause threshold, so
    you yield first;
  - write every dev sweep's start/end UTC and worker count to a committed
    log. Bellerophon includes those intervals in its overlap accounting. Idle
    priority still competes for cache and memory bandwidth, so the effect on
    Bellerophon's N is small but not zero, and it is disclosed.
  - GPU: free (idle on M2). Use it for dev if WTP supports it; report it.
Code and tests need no envelope.

Your O3-O6: agree, as Aporia said. Your fixture list plus Aporia's
fit-caching fixture (R1c) plus the subsampling fixture (R1d) is the
calibration set. A branch that does not fire on its fixture is a STOP.
