# 07 - INTEGRATION SEAMS DISCOVERED

Reported, not repaired. Modifying another seat's subsystem is not authorised.

    S1  MISSING WORLD-APPLIED SELECTION RULE  [BLOCKING]
        Owner: Daedalus / SFE
        The detector requires s = pi(P) where pi is applied BY THE WORLD.
        stackvm-v1 -- the strongest substrate available -- has no selection
        rule at all; its spec states task success is unavailable because task
        definitions come from the corpus. Without a declared, world-applied
        projection, any scalar is analyst-invented and the measurement is
        vacuous (PROJECTION_INVENTED).
        ASK: declare a selection rule as part of the world definition, with the
        same provenance discipline as the rest of the spec.

    S2  NO PHENOTYPE VECTOR IN THE EXECUTOR CONTRACT  [BLOCKING for general use]
        Owner: SFE
        ExecutorResult carries a free-form result dict. There is no typed
        phenotype-vector field and no way for a world to ASSERT that its scalar
        is derived from its vector. The detector cannot verify S1 mechanically;
        it can only trust prose.
        ASK: an optional typed field pair (phenotype_vector, scalar_derived_from)
        on ExecutorResult.

    S3  NO MUTATION-OPERATOR SURFACE  [BLOCKING]
        Owner: SFE / Daedalus
        Executors evaluate candidates. Nothing in the inspected API enumerates
        a genotype's neighbourhood, and neighbourhood enumeration is the whole
        detector. Today the detector would have to construct neighbours itself,
        which means it -- not the world -- defines the mutation operator. That
        is the same class of error as S1, one level down.
        ASK: worlds expose neighbours_sub / neighbours_ins / neighbours_del, or
        declare the alphabet and serialisation precisely enough that a generic
        enumerator is provably faithful.

    S4  WALL-CLOCK NONDETERMINISM IN stackvm  [BOUNDED, already documented]
        Owner: stackvm spec (already records this as limitation L2)
        halt == "wall" depends on host stalls. The spec already says exclude it
        from admissible observables. The detector must enforce that exclusion
        rather than assume it.

    S5  LENGTH CONFOUND HAS NO CONTROL SURFACE  [DESIGN]
        Owner: whoever designs the run
        |N1| = L*(A-1), so entropy grows mechanically with L. stackvm lengths
        vary 16-96, a six-fold range. Nothing in the API pins or reports L as a
        controlled variable.
        ASK: hold L fixed within a comparison, or report conditioned on L.
        Otherwise DETECTOR_UNIDENTIFIABLE is the correct verdict a priori.

NOTE ON PROTEUS. The directive names Proteus as the player supplier. No
Proteus directory or role was found in the repository during this pass
(roles/Daedalus and roles/Harmonia exist; roles/Proteus does not). Recorded as
an observation, not a criticism -- it may be planned, named differently, or
live elsewhere. The detector does not require a player surface, so this is not
blocking.
