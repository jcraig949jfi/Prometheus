import os
D = os.path.dirname(os.path.abspath(__file__))
def w(n, t):
    open(os.path.join(D, n), 'w', encoding='utf-8', newline='\n').write(t)
    print('wrote', n)

w('01_DETECTOR_CONTRACT.md', """# 01 - LATENT-NEIGHBOURHOOD DETECTOR CONTRACT (frozen)

Substrate-independent. Derived from the Avida T_ spec with every Avida-specific
assumption named and removed.

## A1. The surviving question

> Before a genotype's REALIZED behaviour changes, does its COUNTERFACTUAL
> one-mutation neighbourhood reorganise in a way the substrate's SCALAR
> selection channel does not expose?

Two channels:

    PHENOTYPE CHANNEL   P(g)   a vector-valued observable
    SCALAR CHANNEL      s(g)   the scalar the world's SELECTION actually uses

REQUIRED RELATION: s must be a function of P, i.e. s = pi(P) for a projection
the WORLD ITSELF applies. This is load-bearing and easy to violate by accident.
If s is invented by the analyst, the detector answers "does an arbitrary
projection lose information", whose answer is trivially yes and scientifically
empty. See seam S1.

In Avida this held natively: merit was a product of task rewards, so
s = 2^(sum of reward exponents over P).

## A2. Operational definitions -- ambiguities surfaced, not silently resolved

    g            a genotype: finite serialisable sequence over a finite alphabet
    g'           a neighbour of g under EXACTLY ONE mutation event
    N1_sub(g)    every single-symbol substitution: L*(A-1) neighbours
    N1_ins(g)    every single-symbol insertion:    (L+1)*A neighbours
    N1_del(g)    every single-symbol deletion:     L neighbours
    P(g)         the world's vector observable, deterministically evaluated
    s(g)         the world's scalar selection observable
    s-class      the equivalence class of g' under the WORLD'S OWN comparator,
                 never a binning invented by the analyst. If the world exposes
                 only a continuous scalar, the class is exact equality at the
                 world's native precision.

ENUMERATION IS UNIFORM OVER SITES AND SYMBOLS, NOT OVER REALISED MUTATION
RATES. Deliberate, and it differs from the substrate's actual mutational
process. The question concerns the REACHABLE SET, not what the process is
likely to sample. A rate-weighted variant is a SEPARATE measurement and must be
labelled as such.

DUPLICATE RESULTING GENOTYPES. Distinct mutation events can yield the same g'
(common under indels). FROZEN: duplicates counted ONCE for set-valued
quantities (richness) and WITH MULTIPLICITY for distributional quantities
(entropy), because multiplicity is a real property of neighbourhood shape.
Both are reported.

INVALID / LETHAL / NON-TERMINATING NEIGHBOURS. Represented as a distinct
absorbing value BOTTOM, never dropped, never merged with a real phenotype.
Their fraction is always reported. NOTE: some substrates have NO invalid
programs by construction (stackvm-v1), so the class is empty there. That is a
physics difference, not a measurement success.

INDELS ARE NEVER AGGREGATED WITH SUBSTITUTIONS. Three neighbourhoods, three
result sets, always.

NORMALISATION. Entropies in bits, unnormalised, reported beside the effective
number exp2(H) and the support size. Dividing by log2(support) is FORBIDDEN in
the primary report because it hides support size, the quantity that varies most
across genotypes.

## A3. Primary quantity

    RESIDUAL(g) = H( P(g') | s-class(g'), g )

phenotype entropy remaining after conditioning on everything the scalar channel
reports, over the frozen neighbourhood. EXACT ENUMERATION where the
neighbourhood is small enough, so no estimator bias enters.

Denominator: VIABLE neighbours (inherited freeze). All three reported; only
this one enters comparisons.

## A4. WHAT A POSITIVE IS NOT

RESIDUAL > 0 IS NOT A POSITIVE RESULT. In most substrates it is positive by
counting alone: whenever two distinct phenotypes share a scalar value the
residual is nonzero, whether or not anything interesting is happening. The
onemax world in 06 makes this concrete -- there RESIDUAL is analytically
positive and can be written down without running anything.

A positive requires ALL of:

    P1  RESIDUAL(g) changes materially BEFORE a realized phenotype change,
        while s(g) and the scalar neighbourhood summary are approximately
        unchanged
    P2  the change is not explained by any frozen baseline (03)
    P3  the effect appears before MORE THAN ONE realized acquisition, not only
        before the single most interesting endpoint
    P4  it is not attributable to execution stochasticity, mutation-class
        mixture, or the invalid-neighbour fraction alone (04)

## A5. Scope limit that travels with the contract

On a single successful lineage this can QUALIFY AN INSTRUMENT. It cannot show
any pattern is unusual, because there is no base rate without controls.
Survivorship is not solved by changing substrate; it is solved by controls,
which a modern world can actually supply and Avida could not.
""")

w('02_MINIMUM_WORLD_API.md', """# 02 - MINIMUM WORLD API

Smallest interface a controlled world must expose. The detector FAILS CLOSED:
a missing REQUIRED field aborts, never defaults.

## REQUIRED

    genotype serialisation   bytes <-> genotype, stable and injective
    finite alphabet          alphabet_size() -> A
    length                   len(g) -> L
    deterministic evaluation evaluate(g, context) -> Observation,
                             bit-identical on repeat
    phenotype observable     Observation.phenotype -> vector
    scalar selection obs.    Observation.scalar -> comparable
    projection guarantee     world asserts scalar is DERIVED FROM phenotype
    validity state           Observation.valid -> bool + reason code
    substitution enumeration neighbours_sub(g) -> iterator

## OPTIONAL (measured if present; absence reported, never imputed)

insertion enumeration; deletion enumeration; execution seed; environment or
resource state; execution trace; step count; halt class; parent pointer.

## FORBIDDEN TO INFER

The detector must NEVER synthesise:

    a scalar channel when the world exposes none -- inventing pi destroys the
      question (seam S1)
    a phenotype vector assembled from ANALYST-CHOSEN probes, unless the world
      defines the probe set. An analyst-chosen probe set makes P richer than
      anything selection ever saw, guaranteeing a positive.
    viability, when the world has no validity notion
    determinism, when the world declares NONDETERMINISTIC
    a mutation operator the world does not implement

## Fail-closed codes

    WORLD_API_INSUFFICIENT      a REQUIRED capability is absent
    NONDETERMINISM_DETECTED     repeat evaluation differs
    PROJECTION_UNVERIFIED       world will not assert scalar = pi(phenotype)
    NEIGHBOURHOOD_INTRACTABLE   |N1| exceeds the declared compute ceiling
""")

w('03_BASELINES.md', """# 03 - BASELINE TRANSLATION TABLE

The eight baselines frozen in T_, carried forward with preregistered status
preserved. Where translation changed a baseline, ORIGINAL / TRANSLATED /
REASON / CONSEQUENCE are recorded rather than edited silently.

    id  ORIGINAL (Avida T_)          TRANSLATED
    --  ---------------------------  ------------------------------------------
    b1  current task count           count of nonzero components of P(g)
    b2  current merit                s(g)
    b3  current fitness              s(g) after the world's selection transform,
                                     if distinct from b2
    b4  genome length                L
    b5  pd-distance to next change   steps to next realized change  [LOOK-AHEAD]
    b6  cLandscape POS/NEUT/NEG/DEAD scalar neighbourhood summary: fractions of
                                     neighbours better / equal / worse / invalid
    b7  mutation viability           1 - fraction(BOTTOM)
    b8  pd-distance to EQU           steps to the endpoint of interest [LOOK-AHEAD]

    id  Failure mode caught                      If it fires
    --  ---------------------------------------  ---------------------------
    b1  detector tracks current capability       signal is a capability proxy
    b2  detector tracks the very scalar it       FATAL: channel adds nothing
        claims to beat
    b3  as b2, selection-scaled                  as b2
    b4  entropy grows mechanically with          signal is a LENGTH ARTEFACT
        neighbourhood size L*(A-1)
    b5  ceiling: a real detector cannot use it   not competitive with knowing
                                                 the answer
    b6  the historical instrument, reconstructed FATAL: the scalar
                                                 neighbourhood already had it
    b7  signal is just robustness                robustness, not latent structure
    b8  ceiling                                  as b5

TWO TRANSLATION NOTES, recorded rather than absorbed:

b4 IS PROMOTED IN IMPORTANCE. In Avida, length varied only 50->61. In a general
substrate L may vary widely, and since |N1| = L*(A-1), entropy over a larger
neighbourhood is mechanically larger. Any modern report MUST condition on L or
hold it fixed. CONSEQUENCE: an uncontrolled-L design is uninterpretable and
should return DETECTOR_UNIDENTIFIABLE.

b6 IS THE DECISIVE BASELINE. It is the modern reconstruction of the historical
cLandscape instrument. If b6 predicts the events as well as the phenotype
channel, the hypothesis is dead. This is the cheapest available kill and should
be computed FIRST.

Decision rule preserved from T_: if any of b1-b4, b6, b7 predicts realized
events as well as the phenotype-partitioned measures, the signal is KILLED.
""")

w('04_NEGATIVES.md', """# 04 - NEGATIVE-RESULT TAXONOMY

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
""")

w('05_CALIBRATION.md', """# 05 - INTERNAL CALIBRATION CASES

The 14 realized Avida acquisitions plus EQU are ported ONLY as calibration
cases. They are NOT evidence that any modern world contains the effect and may
not be cited as support for the hypothesis.

## The binding historical constraint

    On the realized Avida lineage ALL 14 phenotype-changing transitions were
    MERIT-VISIBLE. 15 distinct phenotypes mapped to 15 distinct merit levels;
    zero collisions on the realized path.

This CONSTRAINS the detector rather than supporting it:

    A detector that fires on the realized Avida transitions has demonstrated
    nothing, because the scalar channel already saw every one of them.

## Cases

    C1  reproduce the 15 realized phenotypes from the corrected lineage
        TESTS: genotype parsing and phenotype extraction agree with a known
        primary source
    C2  reproduce merit from the 2001 reward table
        TESTS: the scalar projection is implemented AS THE WORLD APPLIED IT,
        not as the analyst imagines
    C3  confirm ZERO realized-path collisions
        TESTS: the detector does NOT claim an advantage on the realized path.
        A detector reporting a gap here is BROKEN. This is a NEGATIVE
        calibration and it is the important one.
    C4  confirm the counterfactual collision structure: 512 phenotypes -> 26
        merit levels, 12 phenotypes sharing merit with {EQU}
        TESTS: neighbourhood-level gap computed correctly
    C5  deletion-marker handling at pd 3,60,84,94,101,103,106
        TESTS: the parser respects source notation instead of treating it as
        damage. See 08.

## Status

SPECIFIED, NOT RUN. C1-C4 require a phenotype evaluator for the Avida
instruction set, which was never recovered (Avida 1.6 unrecovered). C5 is
already satisfied by the corrected lineage artifact.
""")
print('core done')
