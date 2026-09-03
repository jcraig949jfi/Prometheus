# I - RPD SPEC (reachable phenotype diversity)

## Definitions

    Omega1(g)  the SET of distinct viable phenotype vectors reachable under one
               point substitution, EXCLUDING P(g) itself
    R1(g)      = |Omega1(g)|                                  reachable richness
    H1(g)      = - sum_j p_j log2 p_j                         reachable entropy

## The denominator, frozen before any comparison

`p_j` is the empirical probability that a random valid one-step point mutant
produces phenotype j. Three denominators are defensible and they answer
different questions:

    (a) ALL mutations          L*25, lethals included as their own outcome
    (b) VIABLE mutations       lethals excluded
    (c) NOVEL VIABLE mutations viable and P(m) != P(g)

**PRIMARY DEFINITION, FROZEN: (b) VIABLE mutations.**

Reason, fixed in advance: (a) makes H1 dominated by the lethal fraction, which
P-MED already reports separately as `f_lethal`, so (a) would double-count the
single largest and least interesting component. (c) discards the silent class,
which is precisely the robustness signal that a precursor hypothesis might turn
on. (b) is the only choice that keeps silence and novelty in the same
distribution while not being swamped by lethality.

All three are cheap, so **all three are reported**; only (b) enters any
preregistered comparison. Denominator choice is hereby removed from the
analysis degrees of freedom.

## Two-step accessibility - bounded, sampled, never exhaustive

Exhaustive k=2 is (L*25)^2 / 2, roughly 1.2 million ordered pairs at L=61 -
affordable in isolation but not across checkpoints x controls x replicates once
each mutant needs a full Avida colony test. It is therefore SAMPLED.

    N2                    frozen sample size, set after the convergence check
    path distribution     uniform over ordered pairs of distinct sites, with
                          the second substitution drawn uniformly from the 25
                          alternatives at its site
    repeated mutation     a site may not be hit twice; same-site double
                          substitutions are excluded and that exclusion is
                          reported as a fraction
    reversions            a second mutation restoring the original instruction
                          is impossible under the above rule and so cannot
                          silently inflate SILENT
    viability             a path whose FIRST step is lethal is still evaluated
                          at step two, because Avida viability is a property of
                          the final genome, not of a trajectory
    seed                  deterministic, recorded per genotype

Estimates `R2*` and `H2*` are reported with bootstrap confidence intervals.

**Convergence is checked BEFORE labels are revealed**, and N2 is frozen for all
genotypes simultaneously. N2 may not be increased for a genotype that "looks
interesting" - that is the specific abuse this paragraph exists to forbid.

## Interpretive discipline

H1 is attractive and dangerous. High entropy is not evolvability: a genotype
with many reachable but useless phenotypes scores high and may go nowhere. R1
and H1 are **local accessibility descriptors**, not fitness proxies and not
evolvability scores. Their only job in H1A is to serve as candidate detectors.
If they show no predictive structure, the correct response is to stop, not to
add a fourth descriptor.
