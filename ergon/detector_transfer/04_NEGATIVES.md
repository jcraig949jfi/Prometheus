# 04 - NEGATIVE-RESULT TAXONOMY

Each outcome names what it kills and what survives.

    NO_PHENOTYPE_VARIATION
        neighbourhood phenotypes all equal P(g).
        KILLS: nothing. SURVIVES: everything. The world is uninformative and
        must be replaced.

    PHENOTYPE_VARIATION_FULLY_FITNESS_VISIBLE
        RESIDUAL = 0 everywhere.
        KILLS: the information-loss premise IN THIS WORLD.
        SURVIVES: the premise elsewhere -- but a world whose pi is injective was
        a poor choice and that is a design error, not a finding.

    LATENT_VARIATION_BASELINE_EXPLAINED
        RESIDUAL > 0 but a frozen baseline predicts events equally well.
        KILLS: THE HYPOTHESIS. Strongest available kill. If b6 fires, the
        historical-class instrument sufficed.
        SURVIVES: nothing of the detector.

    LATENT_VARIATION_TOO_SPARSE
        residual real, events too few to test.
        KILLS: claims of predictive value. SURVIVES: the hypothesis, pending a
        world with more events.

    MUTATION_CLASS_DEPENDENT_ONLY
        effect in indel but not substitution neighbourhoods, or vice versa.
        KILLS: the general claim. SURVIVES: a narrower operator-specific claim.
        Report as such; do NOT aggregate neighbourhoods to rescue it.

    EXECUTION_STOCHASTICITY_DOMINATES
        residual not reproducible under repeat evaluation.
        KILLS: any claim from this world. SURVIVES: the hypothesis; the world
        violated the determinism requirement.

    INVALID_FRACTION_ARTEFACT
        residual tracks the BOTTOM fraction.
        KILLS: the claim as stated. SURVIVES: a robustness claim, which is a
        different and already-studied thing.

    DETECTOR_UNIDENTIFIABLE
        residual inseparable from L or support size.
        KILLS: the measurement as specified. SURVIVES: the question, pending a
        length-controlled design.

    WORLD_API_INSUFFICIENT
        a REQUIRED capability absent. An engineering result, not a scientific
        one.

    PROJECTION_INVENTED
        s was not a world-applied projection of P.
        KILLS: the entire experiment, retroactively. Must be caught BEFORE
        running (seam S1).

The two most likely real outcomes are LATENT_VARIATION_BASELINE_EXPLAINED (b6
wins) and DETECTOR_UNIDENTIFIABLE (length confound). Both are cheap to reach
and both are worth having.
