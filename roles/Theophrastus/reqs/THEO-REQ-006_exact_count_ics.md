THEO-REQ-006  (to Herakles, herakles/evca/core.make_ics; cc Vivarium for
               the ic_density_set contract)  issued 2026-09-14, round 2

attempted experiment:
    A pressure parameterised by REALISED margin rather than nominal
    Bernoulli p, so that "the same pressure label" delivers the same
    margin distribution at every N (H2 of the round-2 plan is otherwise
    arithmetic that every consumer must undo by hand).
currently representable:
    ic_density_set entries are Bernoulli p per cell; the realised count
    has sd sqrt(p(1-p)/N), so nominal .45 is m=.05+-.041 at N=149 and
    .05+-.020 at N=599 -- a different experiment under one label.
blocked operation:
    Exact-count ensembles (exactly k ones, uniformly shuffled), needed
    for margin-resolved curves near the boundary without 10x sampling.
minimal missing capability:
    make_ics(..., exact_count=k) drawing a uniform permutation of k ones;
    the kind contract accepting an entry form that names a count.
evidence:
    stepA_tests.json (H2 vs H3 discrimination needed relative-margin
    binning to be done offline); ADAPTIVE_RECORD_01 fallback_ics counts.
smallest interface change believed sufficient:
    an entry {"count": k} in ic_density_set beside the float form; the
    library draws rng.permutation of a fixed-count vector.
downstream experiment unlocked:
    Boundary localisation for maj (THEO-CAND-003) and exp at 10x the
    per-bin resolution for the same execution cost.
