# 01 - LATENT-NEIGHBOURHOOD DETECTOR CONTRACT (frozen)

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
