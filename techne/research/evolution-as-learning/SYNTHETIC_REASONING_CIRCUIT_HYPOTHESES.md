# Synthetic Reasoning Circuit Hypotheses

A candidate dependency graph. No claim is made that any of these transitions happened
historically, and no cognition label is applied to the motif itself.

## What the motif supplies

From MINIMAL_MEMORY_MOTIF.md, the recovered part is:

    a recurrent saturating map whose parameters accumulate the outer product
    of states that an external filter selected

Capabilities it demonstrably supports (S1, SIMULATED):

    store correlations among selected states        YES  (Hebbian term)
    reconstruct incomplete states                   YES  (recall / completion)
    constrain future generation                     YES  (biased phenotype distribution)
    compose stored substructure                     YES  (new combinations of modules, G2/G3)

Capabilities it does NOT supply:

    address stored content by query                 NO  -- there is no read port
    predict a next input                            NO  -- no temporal structure over inputs
    control its own search                          NO  -- no policy over the update
    abstract over stored items                      NO  -- superposition is not abstraction

## Candidate dependency graph, SPECULATIVE

    [correlational-parameter recurrent map]              <- recovered
              |
              +--> requires: a READ PORT (query -> completion)
              |         => associative retrieval
              |
              +--> requires: TEMPORAL ORDERING over stored states
              |         => primitive prediction
              |
              +--> requires: a SECOND-ORDER parameter that gates the update rule
              |         => search control / meta-evolvability
              |
              +--> requires: a COMPRESSION pressure over stored structure
                        => abstraction

The three "requires" nodes are exactly what is absent from S1-S3. Notably, the fourth arrow is
the one Kouvaris partially supplies: L1/L2 connection cost IS a compression pressure over
stored structure. That makes "abstraction" the nearest adjacent capability, not the furthest.

## The recursion question, directly answered

Directive section 18 asks whether the machinery encoding historical regularities becomes itself
an object of selection.

    RECOVERED recursion depth in this lineage: ONE.

    selection alters W
    W alters generated phenotypes
    generated phenotypes alter future selection      <- this loop IS closed in S1

    but: nothing selects over the RULE that updates W.

The Hebbian update is a fixed law in the model, not an evolved object. A higher-order loop --
selection over the update rule itself -- is not present in any recovered source. Any Prometheus
claim of recursive self-engineering from this lineage would be unsupported.
