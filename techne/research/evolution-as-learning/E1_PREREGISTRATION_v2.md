# E1 — Same-Probe Counterfactual: revised preregistration (v2)

**Status: FROZEN before any simulation code was written and before any result was seen.**
Supersedes the v1 sketch in `SFE_EXPERIMENT_CANDIDATES.md`, which external review returned as
`REVISE FIRST`.

## 0. What this experiment does and does not test

It does **not** test whether evolution "learns", nor whether the Hebbian equivalence is
load-bearing for memory and generalisation. Those remain separate questions (the latter is E3).

It tests exactly one thing:

> Is the present observable state sufficient to predict the distribution of nearby futures, or
> does history reside in the generator in a way that remains causally visible after the present
> state has been matched?

## 1. Hypotheses — DISTRIBUTIONAL, not moment-specific

The v1 formulation ("same mean, different shape") is **withdrawn**. Review correctly noted that
a large, real history effect expressed partly through the mean would have *violated* the
predicted signature. The generator owes us no unchanged mean.

    H0:  Conditional on a matched adult phenotype and an identical mutation operator, the
         offspring phenotype displacement distributions are EXCHANGEABLE across historical
         treatments.

    H1:  They are not exchangeable.

Mean-preservation with shape-change is retained **only as a secondary mechanistic signature**,
reported if observed, and it does not define success.

## 2. The object being measured

Neutral naming, per review. **"Future cone" is not used.**

    CONDITIONAL VARIATION KERNEL        K( P' | P*, H )

with `H` the historical treatment. The causal question is whether

    K( P' | P*, H=A )  !=  K( P' | P*, H=B )

after conditioning on the present observable state.

## 3. Substrate — Watson 2014 Equation 1, RECOVERED

    P(t+1) = P(t) + tau_1 * tanh( B . P(t) ) - tau_2 * P(t)
    P(0) = G ,  tau_1 = 1 ,  tau_2 = 0.2 ,  T developmental steps
    fitness  w = P* . S     for target/selection vector S

Parameters fixed here and not tuned afterwards: `N = 16` traits, `T = 10` developmental steps,
population 200, 2000 generations, mutation on both `G` and `B` at rates fixed below.

## 4. Two preregistered estimands

    E1A  phenotype-conditioned historical residue
         match P*;  allow G and B to differ.
         Asks: is current phenotype a sufficient state description?

    E1B  developmental-memory-specific residue
         match P*;  ADDITIONALLY constrain G as tightly as feasible;  allow B to differ.
         Asks: does variation stored in developmental interactions remain predictive once
         direct genetic effects are controlled?

Both are run. `B` is **never** matched — it is the proposed memory substrate, and matching it
would condition away the mechanism.

## 5. Matching protocol — declared in advance

| item | value |
|---|---|
| distance metric | Euclidean on the adult phenotype vector `P*` |
| matching | nearest-neighbour across treatments, greedy, without replacement |
| tolerance `tau_match` | `||P*_A - P*_B|| <= 0.05 * sqrt(N)` |
| E1B additional constraint | `||G_A - G_B|| <= 0.10 * sqrt(N)` |
| minimum matched pairs | 30; if fewer, the arm reports INSUFFICIENT_MATCHES and is not interpreted |
| rejection | pairs exceeding tolerance are discarded, not stretched |

## 6. Paired perturbations — same coupling, not merely same distribution

Per review, the comparison is a paired counterfactual, not two Monte Carlo clouds. For each
matched pair and each perturbation index k, the **same** coefficient, sign, magnitude and random
variate are applied to both members:

    P'_A,k = F( G_A, B_A + eps_k )
    P'_B,k = F( G_B, B_B + eps_k )

    Delta_k = P'_A,k - P'_B,k

`K = 200` shared perturbations per pair. Perturbation scale `sigma_mut = 0.05`, applied to a
single uniformly chosen entry of `B` per perturbation.

## 7. Measured quantities — the local generator, not one summary

For each arm, per matched pair:

- offspring displacement `dP = P'_offspring - P*_parent`
- mean displacement
- **local response covariance `C = E[ dP dP^T ]`** and its principal directions
- anisotropy: eigenvalue spectrum of `C`
- pairwise mutation-response divergence `||Delta_k||`
- neighbourhood occupancy / support
- attractor identity where deterministically defined, and probability of qualitative
  attractor transition

## 8. Primary test

Permutation test on exchangeability of the displacement distributions across history labels,
using **energy distance** as the statistic (sensitive to mean, covariance and higher moments —
which is the point of the correction).

    statistic:  E-distance between {dP | H=A} and {dP | H=B}
    null:       10,000 permutations of the history label
    alpha:      0.01
    effect size reported alongside p, with a bootstrap CI

## 9. Required controls — all four, run before interpretation

    C0  SAME HISTORY / SAME MATCHING ERROR
        Pairs drawn WITHIN one treatment whose P* mismatch equals the residual mismatch of the
        cross-history pairs. Estimates the floor induced by imperfect matching.
        **If C0 is significant, E1 is uninterpretable and reports CONFOUNDED.**

    C1  NO HISTORY DIFFERENCE
        Independently evolved replicate populations under the SAME targets. Expect null.

    C2  SHUFFLED HISTORY LABELS
        The analysis pipeline must return null under permutation of labels. A non-null here
        means the pipeline itself manufactures signal.

    C3  DEGENERATE LINEAR ARM
        T = 1, sigma(x) = x. Runs the whole protocol in the regime where the Hebbian derivation
        is exact. This is the control that speaks to the packet's crux: it begins separating
        exact Hebbian correspondence from nonlinear developmental memory.

## 10. Bounded interpretation of a null — K2 is a bounded falsifier

The v1 wording ("K2 fires and developmental memory is a current-phenotype effect only") is
**withdrawn as too strong**. A null establishes only:

> Under the tested histories, matching tolerance, perturbation scale, developmental regime and
> detector power, no history-conditioned difference in the assayed local variation distribution
> remained after conditioning on current phenotype.

It does not establish that developmental memory generally affects only current phenotype. A
null is reported with the sensitivity analysis in §11 attached.

## 11. Sensitivity analysis, run regardless of outcome

Perturbation scale is swept over `sigma_mut in {0.01, 0.05, 0.2}`. A result that exists at only
one scale is reported as scale-dependent, not as a finding.

## 12. What a positive result would and would not license

    LICENSED:      an experimentally demonstrated history-conditioned generator --
                   K(P'|P*,H) depends on H after matching P*
    NOT LICENSED:  that evolution learns; that the Hebbian identity is load-bearing;
                   that the effect generalises out-of-family; any cognition vocabulary;
                   adoption of "future cone" into canonical language

## 13. Escalation path, fixed in advance

    E1 null  -> bound and record the mechanism in the tested regime. Do NOT escalate.
    E1 positive -> E2 (which geometric property changed) -> E3 (which motif components are
                   necessary). Only after E3 is a common-abstraction question productive.
