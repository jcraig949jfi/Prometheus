# The Minimal Memory Motif

Strip the biology. What is the smallest algorithmic object that reproduces the demonstrated
phenomenon?

## The motif — DERIVED from S1

    state        x in R^N                     (phenotype vector)
    parameters   W in R^{NxN}                 (interaction matrix)
    seed         x(0) = g                     (genotype supplies the initial state)

    INNER LOOP (fast, within one lifetime):
        x(t+1) = x(t) + a * sigma(W x(t)) - b * x(t)          T steps
        x*     = x(T)

    OUTER LOOP (slow, across generations):
        environment supplies a target direction s
        W <- W + r * outer(x*, x*) restricted to the selected direction
             i.e.  delta w_ij ∝ s_i s_j  under the sign-agreement condition

    READOUT: the distribution of x* obtainable from perturbed g is now biased by W.

## What is essential, and what is scaffolding

| ingredient | essential? | reasoning |
|---|---|---|
| **two timescales** (fast state, slow parameters) | **ESSENTIAL** | with one timescale there is nothing that persists across the fast dynamics; memory *is* the timescale separation |
| **outer-product / correlational parameter update** | **ESSENTIAL** | this is what makes the stored object a *correlation* rather than a *value*. Storing a best state would give recall but not the combinatorial generalisation |
| **recurrence in the inner loop** | **ESSENTIAL** | RECOVERED: the linear single-step arm produces only intermediates. Iteration is what turns stored correlations into basins |
| **saturating non-linearity** | **ESSENTIAL** | RECOVERED: "Some non-linearity in the mapping is important". It is what makes outputs discrete-ish and composable rather than blended |
| `tanh` specifically | **NOT essential (DERIVED)** | any bounded monotone saturation should serve; nothing in S1 turns on the exact function |
| `tau_1 = 1`, `tau_2 = 0.2` | **NOT essential** | rate/decay constants, not structure |
| biological interpretation of x as traits | **NOT essential** | the motif never uses it |
| population, mutation, reproduction | **NOT essential to the MOTIF** | they are how the outer update is *implemented* in biology. The motif needs only "an outer process that adds correlations of selected states to W" |

## Reduced form — the claim

> **A memory-of-history motif is: a recurrent saturating map whose parameters accumulate the
> outer product of states that an external filter selected.**

Four parts: `recurrence`, `saturation`, `correlational parameter accumulation`, `timescale
separation`. Remove any one and DERIVED reasoning says the phenomenon degrades:

- remove recurrence → interpolation only (RECOVERED: the linear arm)
- remove saturation → linear blending, no composable modules
- remove correlational accumulation → you can store a *state*, not a *structure*
- remove timescale separation → no memory at all

## What it is NOT

It is **not** a gene-regulatory network, and reproducing one would be a category error. It is
also **not** yet an associative memory in the Hopfield sense — that requires symmetry
conditions this motif does not impose (see the equivalence map). Calling it associative memory
imports guarantees the source does not establish.

## Candidate part

    PART CANDIDATE: correlational-parameter recurrent map  (see the parts registry)

Named neutrally. No cognition vocabulary. It becomes a Prometheus part only if the causal
support in `GENERALIZATION_LEVEL_ANALYSIS.md` and the composition tests in
`MISSING_COMPOSITIONS.md` hold.
