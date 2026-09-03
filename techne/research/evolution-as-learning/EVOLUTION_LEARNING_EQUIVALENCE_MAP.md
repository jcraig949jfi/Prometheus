# Evolution–Learning Equivalence Map

The directive demands equations or the tag ANALOGICAL_ONLY. This is the audit.

## The one genuine derivation — FORMAL, and conditional

RECOVERED from S1, section *"Selection pressures on interaction coefficients are Hebbian"*:

    selection coefficient of a mutation:

        [ w(P* + dP*) - w(P*) ] / w(P*)  =  (dP* . S) / (1 + P* . S)

    result:

        delta b_ij = r * s_i * s_j          (r > 0)

    Hebb's rule, RECOVERED:

        delta w_ij = r * s_i * s_j

**The equivalence is real. It is also conditional, and the condition is in the source:**

> "when natural selection is sufficiently efficacious that phenotypic characters at least have
> the same sign as the direction of selection on those characters"

**And the clean derivation is performed in the LINEAR SINGLE-STEP case.** RECOVERED:

> "to build intuition, first imagine that development is represented by a single-step linear
> mapping (i.e., T = 1, one iteration of Equation 1, and sigma(x) = x); in this case the change
> in phenotypic character p_x due to a change in b_ij is zero for all x != i."

### The sharpest finding in this document — DERIVED

The Hebbian equivalence is cleanest exactly where the interesting behaviour is **absent**, and
approximate exactly where the interesting behaviour **lives**.

In the single-step linear map, one mutation touches one trait, so `delta b_ij ∝ s_i s_j` falls
straight out. In the recurrent non-linear map — the one that produces attractors, modules and
generalisation — S1 itself states that *"a single mutation that alters an interaction
coefficient by delta b_ij may affect many phenotypic characters"*. Credit assignment is then no
longer local to the pair (i,j), and the outer-product form is an approximation whose error is
not characterised in the recovered text.

This does not refute the claim. It **bounds** it:

    FORMAL in the degenerate regime;  APPROXIMATE in the operative regime.

Any downstream use of this lineage asserting "selection *is* Hebbian learning" without that
qualifier is over-reading the source.

## Claim-by-claim

| claim | status | basis |
|---|---|---|
| selection on interaction coefficients follows Hebb's rule | **FORMAL (conditional)** | derived in S1; sign-agreement condition; exact at T=1 linear |
| gene-regulatory weights ↔ neural weights | **FORMAL** | both are the same object in the same update form |
| historically selected phenotypes ↔ training patterns | **FORMAL** | targets enter via S; the Hebbian term is the outer product of the selected pattern |
| phenotypic correlations ↔ learned correlations | **FORMAL** | this *is* the content of the Hebbian result |
| developmental attractor ↔ associative memory | **ANALOGICAL_ONLY** | S1's recovered text establishes no symmetry or energy condition; recurrent `tanh` dynamics with unconstrained B carries no Hopfield storage guarantee |
| development ↔ recall / pattern completion | **SIMULATED** | demonstrated experimentally in S1, not proved |
| evolvability ↔ generalisation | **FORMAL-BY-DEFINITION (S3)** | Kouvaris *defines* evolvability as generalisation to unseen environments, then transfers learning-theory results. A definitional bridge is legitimate but is not a discovered identity, and should never be cited as one |
| over-fitting remedies transfer | **FORMAL + SIMULATED (S3)** | "training with noisy data (jittering)" ↔ extrinsic environmental noise; "L2/L1 regularisation" ↔ "the reproduction cost of the gene regulatory interactions" |
| "evolution learns" in general | **ANALOGICAL_ONLY** | S2 is an Opinion piece; its scope claims are framing, not theorems |

## Limits of the equivalence — DERIVED

1. Conditional on sign-agreement between phenotype and selection direction.
2. Exact only at T=1 with `sigma` = identity.
3. Fitness enters only as linear `P* . S`; nothing establishes the result for general fitness.
4. No symmetry constraint on `B` is recovered, so associative-memory guarantees are unlicensed.
5. Hebbian storage here is unnormalised — which is exactly why the lock-in failure modes in
   `MEMORY_VS_LOCKIN.md` are predicted rather than surprising.
