# F. PARAMETER CERTAINTY TABLE

**Status: T0 COMPLETE.** Source for every VERIFIED row is `SRC-PHD-2003`, Tables 1.6 and 1.7 and section 1.5.4, unless stated.

Tags: VERIFIED_EXACT / VERIFIED_RANGE / INFERRED / UNSPECIFIED / ASSUMED_FOR_RECONSTRUCTION.

## Model and representation

| parameter | value | tag | locator |
|---|---|---|---|
| genotype | egg cell `Psi(0)` plus ordered operator sequence `Pi = <pi_1..pi_r>` | VERIFIED_EXACT | 1.5.1 |
| operator form | replacement rule `<a0 : a1,a2,..>`, replaces every occurrence of promoter `a0` | VERIFIED_EXACT | 1.5.1 |
| development | apply operators in sequential order, `T` steps | VERIFIED_EXACT | 1.5.1 |
| stopping time `T` | 1 | VERIFIED_EXACT | Table 1.7 |
| alphabet `A` | `a..h`, 8 symbols | VERIFIED_EXACT | Table 1.7 |
| phenotype target | `5 x abcde`, length 25 | VERIFIED_EXACT | 1.5.3, 1.5.4 |

## Mutation operators

| parameter | value | tag | locator |
|---|---|---|---|
| 1st-type kinds | symbol replacement, duplication, deletion, equal probabilities | VERIFIED_EXACT | Table 1.6 |
| 1st-type count | Poisson, mean `alpha * sequence-length`, per sequence | VERIFIED_EXACT | Table 1.6 |
| 2nd-type kinds | 5 listed rewrites, equal probabilities | VERIFIED_EXACT | Table 1.6 |
| 2nd-type count | Poisson, mean `beta`, per genotype | VERIFIED_EXACT | Table 1.6 |
| operator-creation length | random subsequence of stochastic length `2 + Poisson(1)` | VERIFIED_EXACT | Table 1.6 |
| order of application | 2nd-type first, then 1st-type | VERIFIED_EXACT | Table 1.6 |
| operator-deletion guard | delete `pi` only if it was never applied during ontogenesis | VERIFIED_EXACT | Table 1.6 |

## Experiment 1 (detector experiment)

| parameter | value | tag | locator |
|---|---|---|---|
| `lambda` offspring population | 100 | VERIFIED_EXACT | Table 1.7 |
| `mu` parent population | 30 | VERIFIED_EXACT | Table 1.7 |
| `alpha` replacement | 0.03 | VERIFIED_EXACT | Table 1.7 |
| `alpha` insertion/deletion | 0.0 | VERIFIED_EXACT | Table 1.7 |
| `beta` | 0.1 | VERIFIED_EXACT | Table 1.7 |
| detector samples | 2000 per individual per generation | VERIFIED_EXACT | Table 1.7 + 1.5.3 Measures |
| selection | only "correct" phenotypes selected, uniform among them; `(mu, lambda)`; parents drawn by roulette wheel | VERIFIED_EXACT | 1.5.3 |
| crossover | none simulated | VERIFIED_EXACT | 1.5.3 |
| initialisation | direct encoding, no operators, `Psi(0)` = target | VERIFIED_EXACT | 1.5.3 |
| run length | 1000 generations | VERIFIED_EXACT | Figures 1.5, 1.6 axes |
| replicates | 1 | VERIFIED_EXACT | single run described |

## Experiment 2 (the ablation)

| parameter | value | tag | locator |
|---|---|---|---|
| design | 2x2 | VERIFIED_EXACT | Figure 1.7 caption |
| `beta` enabled arm | **0.1 or 0.01** | **VERIFIED_RANGE** | caption and Table 1.7 say 0.1; body text of 1.5.4 says 0.01, twice. Contradiction in the published record. Test both. |
| `beta` ablated arm | 0 | VERIFIED_EXACT | Figure 1.7 caption |
| `alpha` low / high | 0.03 / 0.06 | VERIFIED_EXACT | Figure 1.7 caption |
| initialisation | `Psi(0) = <a>`, no operators | VERIFIED_EXACT | 1.5.4 |
| selection | `(mu, lambda)` on Hamming distance to target | VERIFIED_EXACT | 1.5.4 |
| fitness | negative percentage of non-matching symbols | VERIFIED_EXACT | Figure 1.7 caption |
| replicates | 10 per cell, 40 total | VERIFIED_EXACT | Figure 1.7 caption |
| `lambda`, `mu`, alphabet, `T` | inherited from Experiment 1 | VERIFIED_EXACT | "All remaining parameters are the same as for the first experiment" |
| **run length** | **not stated; differs between alpha levels** | **UNSPECIFIED** | Figure 1.7 caption |
| detector settings in this experiment | 2000-sample row is inherited by the same sentence, but no detector output was reported | INFERRED | see below |
| random seeds | not stated | UNSPECIFIED | - |
| `alpha` insertion/deletion in exp 2 | Table 1.7 sets it to 0.0, but 1.5.4 says alpha applies "w.r.t. symbol replacement, insertion, and deletion" | **VERIFIED_RANGE** | conflict between Table 1.7 and 1.5.4 text; test both |

## Assumptions that must be declared if the reconstruction proceeds

| assumption | tag | does it plausibly determine the outcome? |
|---|---|---|
| run length for Experiment 2 set long enough for all arms to plateau or to a preregistered cap | ASSUMED_FOR_RECONSTRUCTION | No, provided the cap is reported and the same for all arms within an alpha level. |
| `beta` = 0.1 taken as primary, 0.01 run as a sensitivity arm | ASSUMED_FOR_RECONSTRUCTION | Possibly. It is a tenfold change in the ablated mechanism's rate. Both must be run. |
| insertion/deletion rate: 0.0 primary per Table 1.7, non-zero as sensitivity | ASSUMED_FOR_RECONSTRUCTION | Possibly, since it changes whether length can drift under 1st-type mutation alone. |
| roulette-wheel cloning of the `mu` selected parents, as in Experiment 1 | ASSUMED_FOR_RECONSTRUCTION | No. |
| seeds fresh per run, recorded | ASSUMED_FOR_RECONSTRUCTION | No. |

**Verdict on reconstructability: RECONSTRUCTABLE, with two parameters requiring a sensitivity arm rather than a guess.** No assumption is load-bearing on the missing-cell question itself, because that question is about whether the detector separates the `beta > 0` and `beta = 0` arms, and `beta = 0` is unambiguous.
