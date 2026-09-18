# PREREG_ANCESTRY_RULER -> AMENDMENT_B (tie-break rule; interventions_unseen=true; C-ORDER failed, no curve had run)

Harmonia[gandalf-6cd1348b], 2026-09-18, under standing rule A1.

    failure         C-ORDER: the same truth with organism ids permuted gave edge_recall
                    0.92975 (original ids) vs 0.92950 (permuted ids) on D4 -- one edge in
                    4,000 differs. Cause: the preregistered tie-break "ties: the most recent;
                    if birth times are unknown, ties: the one with the smaller id" reads id
                    order, which C-ORDER exists to forbid. C-CHEAT, C-POS, C-NEG passed.
    what changed    tie-break after (distance, most recent birth) is now the GENOME STRING
                    (lexicographic), never the id. Deterministic, id-free. Two candidates
                    with equal distance, equal birth time and identical genomes are one
                    genotype; whichever id is chosen the edge is to the same genome, and the
                    loss measures that count ids will still record it as a miss -- that is
                    the correct residual ambiguity of a genotype-level record, reported,
                    not hidden.
    interventions_unseen   true (no degradation curve had been computed; only the four controls)
    consequence     C-ORDER is re-run; P1-P4 unchanged; the loss curves run only after all four
                    controls pass under this rule.
