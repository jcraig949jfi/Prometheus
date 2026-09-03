import os
D = os.path.dirname(os.path.abspath(__file__))
def w(n, t):
    open(os.path.join(D, n), 'w', encoding='utf-8', newline='\n').write(t)
    print('wrote', n)

w('06_CANDIDATE_WORLDS.md', """# 06 - CANDIDATE MODERN-COLLIDER WORLDS

Nominated from ACTUAL inspection of the current stack, not from what a world
would ideally look like. Nothing was executed.

Sources inspected:
    SerendipityFoundry/SerendipityFoundryEngine/sfe/executors.py
    SerendipityFoundry/SerendipityFoundryEngine/sfe/api.py
    SerendipityFoundry/stackvm_admission/STACKVM_ADMISSION_SPEC.md

FIRST STRUCTURAL FINDING. The SFE is an EXPERIMENT ORCHESTRATION engine --
worlds, hypotheses, predictions, budgets, forks, observations, failures, work
claim/heartbeat/complete. It is NOT itself a genotype substrate. The substrate
is whatever implements the Executor ABC. So "SFE" is not a candidate world;
Executors are.

---------------------------------------------------------------------------
CANDIDATE A -- bitstring-onemax (sfe.executors.BitStringExecutor)
---------------------------------------------------------------------------
genotype            bitstring, default length 24
alphabet            A = 2
phenotype P(g)      per-position MATCH VECTOR against the hidden target
scalar s(g)         score = fraction of matching positions
projection pi       s = |P| / L  -- a TRUE world-applied projection. The world
                    computes exactly this. Seam S1 is SATISFIED natively.
determinism         BIT_DETERMINISTIC by construction; target derived by
                    SHA-256 from the world seed, so identical landscape iff
                    identical seed
neighbourhood       substitution only, |N1| = L*(A-1) = 24. Trivially exhaustive.
invalid class       empty (any bitstring is valid)
cost                24 evaluations per genotype. Negligible.

DEGENERACY: 2^24 match vectors collapse onto 25 scalar levels -- far more
extreme than Avida's 512 -> 26.

VERDICT: CALIBRATION ONLY. DO NOT USE AS THE TEST.

REASON, and it is the most useful finding of this pass. On onemax the answer is
ANALYTICALLY KNOWN WITHOUT RUNNING ANYTHING. If g currently mismatches k
positions, then all k improving flips yield the SAME scalar (+1/L) while
producing k DIFFERENT match vectors. So

    RESIDUAL(g) for the improving class = log2(k)   exactly

RESIDUAL is positive by construction, for every genotype, always. A world that
guarantees a positive cannot test a hypothesis. It can only qualify the
implementation -- which is genuinely valuable, and is what it should be used
for. This is precisely the trap contract A4 exists to prevent.

---------------------------------------------------------------------------
CANDIDATE B -- stackvm-v1 (foundry/engines/gp/stackvm/vm.py)
---------------------------------------------------------------------------
genotype            byte string, create_random length uniform in [16, 96]
alphabet            A = 256 (opcode = byte % 33; 33 opcodes)
observables         steps, halt class (end/steps/wall), output (signed stack
                    top), |opcodes_executed|, |memory_written|, final stack depth
determinism         bit-deterministic in (code, inputs, max_steps) EXCEPT the
                    wall-clock backstop; halt == "wall" is a declared
                    nondeterminism channel and the spec itself says exclude it
neighbourhood       substitution |N1| = L*255, i.e. 4,080 (L=16) to 24,480 (L=96)
invalid class       EMPTY BY DESIGN -- "every byte sequence is a legal program"
cost                ~2.4e4 evaluations per genotype at max length. Tractable.

BLOCKING SEAM: NO NATURAL SCALAR SELECTION CHANNEL. The spec states plainly
that "Task success is not an available observable, because task definitions
come from the corpus." All canonical observables are INTRINSIC execution
measures. There is no selection rule, hence no world-applied pi, hence any
scalar the analyst picks is INVENTED -- which triggers PROJECTION_INVENTED and
voids the experiment before it starts.

VERDICT: STRONGEST SUBSTRATE, NOT YET USABLE. Requires a declared selection
rule that is part of the world rather than of the analysis. That is a Daedalus
or SFE decision, not Ergon's to make.

Its empty invalid class is also a physics difference from Avida worth stating:
the BOTTOM machinery in the contract will be exercised nowhere here.

---------------------------------------------------------------------------
CANDIDATE C -- NondeterministicExecutor (sfe.executors)
---------------------------------------------------------------------------
Deliberately nondeterministic; exists so tests can prove the Foundry does not
falsely claim deterministic reproduction.

VERDICT: NEGATIVE CONTROL ONLY. It is the ready-made instrument for the
EXECUTION_STOCHASTICITY_DOMINATES class. The detector run against it MUST
return NONDETERMINISM_DETECTED. If it returns a residual instead, the detector
is broken. Use it as a fail-closed test, never as a world.

---------------------------------------------------------------------------
RECOMMENDATION
---------------------------------------------------------------------------
Prefer the simplest world that can KILL the hypothesis cleanly. None of the
three can yet, and the honest recommendation is therefore a sequence:

  1. Run A as CALIBRATION. Confirm the implementation reproduces
     RESIDUAL = log2(k) analytically. Confirm b6 (scalar neighbourhood
     summary) ALSO separates the improving class perfectly -- on onemax it
     does, which is exactly why A cannot test the hypothesis.
  2. Run C as a FAIL-CLOSED test. Expect NONDETERMINISM_DETECTED.
  3. Do NOT run B until a world-applied selection rule exists. Requesting one
     is the single highest-value integration ask (seam S1).

FIRST EXECUTION CANDIDATE: none is ready. The first EXECUTION should be
calibration A plus fail-closed C, which spend almost nothing and can only
qualify or falsify the implementation. The first SCIENTIFIC execution must wait
on B acquiring a declared selection rule.
""")

w('07_INTEGRATION_SEAMS.md', """# 07 - INTEGRATION SEAMS DISCOVERED

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
""")

w('08_AVIDA_CORRECTION.md', """# 08 - PERMANENT RECORD: THE AVIDA V0.1 CORRECTION

Preserved because it is a concrete Prometheus failure specimen, not as a
general methodological essay.

    ORIGINAL CLAIM (V0.1)
        Seven lineage genomes (pd 3, 60, 84, 94, 101, 103, 106) were damaged by
        PDF extraction/transcription loss. Diagnosis offered: "the extractor
        dropped bolded mutation glyphs". Two independent extractors (pypdf and
        pdfplumber) agreed byte-for-byte, including reproducing the same seven
        underscores, which was cited as evidence that the loss was real and in
        the PDF text layer.

    CORRECTION (final bounded pass)
        ZERO were damaged. Recovering the 2003-06-08 capture of
        case-study/lineage.html yielded the legend verbatim:
            "point mutations are printed in red, insertions in green;
             deletions are marked by blue asterisks"
        The blue asterisk is a DOCUMENTED DELETION MARKER. The PDF text layer
        rendered it as an underscore. Nothing was lost.

    CONSEQUENCES
        1. The evaluator-based lineage-repair justification is WITHDRAWN. One of
           the three stated reasons for building a 2003 binary evaporated.
        2. Those seven genomes are each ONE INSTRUCTION SHORTER than V0
           recorded; the marker occupies a display column and is not an
           instruction. Five now read len = prev-1 (clean deletion), two read
           len = prev (deletion plus compensating insertion, consistent with
           independent 0.05 divide-insert / divide-delete rates).
        3. pd 101, a frozen checkpoint, was declared BLOCKED on a defect that
           did not exist.
        4. Transcription status UPGRADED to validated: 105 of 105 undamaged
           rows agree EXACTLY across two independent PRIMARY renderings.

    THE SPECIFIC LESSON
        Two independent extractors agreeing establishes REPRODUCIBILITY, not
        SEMANTIC CORRECTNESS. Both were faithfully reproducing a source
        notation that the analyst had not read. The agreement was cited AS
        EVIDENCE FOR the damage hypothesis, when it was equally consistent with
        -- and in fact caused by -- correct transcription of a symbol whose
        meaning was documented in a file that had not yet been fetched.

    WHAT WOULD HAVE CAUGHT IT EARLIER
        Reading the source legend before diagnosing the source. The legend was
        in an object listed on the site index from the first capture in 2003.

    EVIDENCE PRESERVED
        genome_display retains the original rendering verbatim; genome holds
        the corrected instruction sequence; deletion_marker_positions records
        where the markers were. The erroneous parse is preserved in
        lineage_of_descent.jsonl alongside the corrected
        lineage_of_descent_corrected.jsonl. Nothing was overwritten.
""")

w('09_HARMONIA_HANDOFF.md', """# 09 - HARMONIA-FACING INVOCATION AND PROVENANCE

Written so the detector can be invoked without this conversation.

## What you provide

    world_adapter     an object satisfying 02_MINIMUM_WORLD_API REQUIRED set
    genotypes         an ordered sequence of genotypes to measure. For a
                      temporal test this is a lineage in order; for a
                      cross-sectional test it is a matched set.
    events            indices at which a realized phenotype change occurred.
                      MAY BE EMPTY -- the detector then reports descriptive
                      statistics only and MUST NOT claim predictive value.
    compute_ceiling   maximum neighbour evaluations. Exceeding it returns
                      NEIGHBOURHOOD_INTRACTABLE, never a subsample, unless a
                      sampling design is separately preregistered.

## What you receive

Per genotype, per neighbourhood type (sub / ins / del):

    residual_bits, support_size, effective_number,
    distinct_phenotypes, distinct_scalar_classes,
    hidden_transitions_per_scalar_class,
    bottom_fraction, duplicate_fraction,
    all eight baseline values b1-b8

Per run: a verdict from 04_NEGATIVES, plus the provenance block below.

## What constitutes DETECTOR FAILURE (not a scientific result)

    WORLD_API_INSUFFICIENT, NONDETERMINISM_DETECTED, PROJECTION_UNVERIFIED,
    NEIGHBOURHOOD_INTRACTABLE, PROJECTION_INVENTED

These are engineering outcomes. They must never be reported as evidence about
the hypothesis in either direction.

## What constitutes an INTERPRETABLE NEGATIVE

Any outcome in 04 other than the five above. The most valuable is
LATENT_VARIATION_BASELINE_EXPLAINED, especially via b6.

## Provenance that MUST be recorded

    world identity + version + seed
    genotype serialisation hash for every genotype measured
    the exact projection pi, and the world's assertion that it applies it
    determinism evidence: a repeat evaluation of at least one genotype,
        bit-compared
    the frozen denominator (VIABLE) and the frozen enumeration convention
        (uniform over sites and symbols)
    compute ceiling and whether it bound
    detector contract hash, so the measurement can be tied to frozen T_

## What must NEVER be inferred from missing fields

A missing scalar is not zero. A missing phenotype is not empty. A missing
validity flag is not "valid". A missing indel operator is not "no indels
occur". Absence is reported as absence.

## How you know the measurement corresponds to frozen T_

The run record carries the sha256 of 01_DETECTOR_CONTRACT.md. If that hash is
not the frozen one, the measurement is a variant and must be labelled as one.

## If the stack cannot support this today

It cannot -- see 07. Seams S1, S2 and S3 are blocking for a scientific run.
Calibration against candidate A and the fail-closed test against candidate C
are possible without them.
""")
print('done')
