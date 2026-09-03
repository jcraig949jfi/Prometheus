# The Watson 2014 Developmental Memory Model, Recovered

All equations are RECOVERED verbatim from S1 unless marked otherwise.

## Objects

| symbol | object | RECOVERED phrasing |
|---|---|---|
| `G = <g_1 ... g_N>` | genotype: direct effects on the embryonic phenotype | "a vector of direct effects on traits" |
| `B`, elements `b_ij` | interaction matrix, "the weighted influence of each character on each other character" | "`b_ij` represents the interaction coefficient between trait i and trait j within a dynamical ontogenetic process" |
| `P(t)` | phenotype vector at developmental time t | |
| `P(0) = G` | embryonic phenotype | "Let the initial embryonic phenotype ... `P(0) = G`" |
| `P*` | adult phenotype after T developmental steps | used in the selection-coefficient derivation |
| `S` | selection vector / target environment | enters fitness only as `P* . S` |

## Developmental dynamics — Equation 1, RECOVERED

    P(t+1) = P(t) + tau_1 * sigma( B . P(t) ) - tau_2 * P(t)

    tau_1 = 1        rate constant on the interaction term
    tau_2 = 0.2      decay rate
    sigma(x) = tanh(x), applied ELEMENTWISE

RECOVERED gloss: sigma is "a sigmoidal function ... that non-linearly limits the influence of
interactions". The off-diagonal elements of B "introduce interdependencies among the different
characters, where the size of one trait influences how much another trait grows at any time
step."

## The linear degenerate case, RECOVERED

With `sigma(x) = x` and a single step (T = 1):

    P = G + tau_1 (B . G) - tau_2 G        and, with rescaled B,        P = B . G

S1 explicitly identifies this as the model of Lipson, Pollack & Suh (2002) and Kashtan et al.
(2009). **This matters for the whole programme**: the linear single-step form is the prior art,
and the 2014 contribution is precisely what changes when the map becomes recurrent and
non-linear.

## Are the properties load-bearing?

| property | value in S1 | does the result depend on it? |
|---|---|---|
| linear vs non-linear | non-linear, `tanh` | **YES — RECOVERED.** "Some non-linearity in the mapping is important (as we will show)." The linear arm produces only "phenotypes that are intermediate within this range of possibilities": it interpolates and does not generate the discrete new combinations. |
| recurrent vs single-step | recurrent, T steps | **YES — DERIVED.** Attractor behaviour and the many-characters-per-mutation effect both require iteration. The clean Hebbian derivation is done at T=1 and is an approximation otherwise. |
| symmetric vs asymmetric `B` | no symmetry constraint recovered | **UNRESOLVED.** S1's recovered text states no symmetry constraint on B. Hopfield-style associative-memory guarantees normally require symmetry, so how far the "associative memory" reading is licensed is genuinely open. Marked as a gap, asserted in neither direction. |
| continuous vs discrete | continuous P, continuous B | **DERIVED, likely load-bearing.** `tanh` saturation bounds growth and shapes the basin structure. Whether the motif survives discretisation is exactly falsifier K5, and S1 does not answer it. |

## What the model does not contain

- No fitness landscape beyond the linear form `P* . S`.
- No population structure inside Eq. 1; selection enters only through the coefficient.
- **No mechanism by which the rule that updates `B` is itself under selection.** This is the
  recursion question (directive §18) and S1 does not provide it. See
  `SYNTHETIC_REASONING_CIRCUIT_HYPOTHESES.md`.
