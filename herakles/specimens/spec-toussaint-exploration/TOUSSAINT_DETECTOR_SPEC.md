# C. TOUSSAINT DETECTOR SPEC

**Status: T0 COMPLETE for this file. Every statement below was read by this seat in a recovered primary source, not recalled.**

Primary evidence: `SRC-PHD-2003` = `original/03-toussaint-phd.pdf`, sha256 `9f485f1a068372ba...` (full digest in `RECOVERED_ARTIFACT_MANIFEST.jsonl`), section 1.5.3 "First experiment: Neutral sigma-evolution", pages 59-63, Table 1.7 and Figures 1.4, 1.5, 1.6.
Corroborating evidence: `SRC-ARXIV-2001` = arXiv physics/0102009v1 section 5.2, Figures 3 and 4.
Executable evidence: `ART-CODE-STRINGRULE`, the recovered `02-stringRuleJTB/main.cpp` driver.

---

## Answers to the twelve questions of directive section 2

**1. What mathematical object did he call the exploration distribution?**
The *phenotypic exploration distribution*, written `Xi_sigma`. It is the probability distribution over the phenotype of a single offspring produced from a given parent genotype under the mutation operators. `sigma` denotes the genetic representation, so `Xi_sigma` is the phenotype distribution *induced by* that representation.

**2. Distribution over phenotypes, offspring effects, search steps, or something else?**
Over **phenotypes**. In the thesis model the phenotype is a symbol string of length 25 over an eight-letter alphabet, so `Xi_sigma` is a distribution over strings, treated as 25 phenotypic variables.

**3. What random variable was sampled?**
The phenotype of one mutated offspring of a fixed parent genotype, developed through the genotype-phenotype map.

**4. What operator induced the distribution?**
The full mutation operator of the model, applied in a fixed order: **second-type mutations first, then first-type mutations**. First-type mutations are symbol replacement, duplication and deletion in every sequence of the genotype, Poisson with mean `alpha * sequence-length`. Second-type mutations are the five structural rewrites of the genetic system (operator application, inverse application, deletion, global application-then-deletion, and creation of a new operator by extracting a random subsequence of stochastic length `2 + Poisson(1)`), Poisson with mean `beta`. Source: thesis Table 1.6.

**5. What statistic was actually reported?**
Three statistics, all features of `Xi_sigma`, plus two genotype descriptors:
- **neutral degree** `n = Xi_sigma(x)`, the probability that the offspring phenotype equals the parent phenotype `x`. This is mutational robustness.
- **normalised mutual information matrix** between phenotypic variables, `I'_ij = 2*I_ij / (H_i + H_j)`, with `I_ij` the mutual information between the i-th and j-th phenotypic variable under `Xi_sigma` and `H_i` the marginal entropy. Rendered as a 25x25 grey-shade matrix, black 0, white 1.
- **modular degree**, defined specifically for this scenario: the sum over `k = 1..4` of the probability that, when a variation occurs at phenotype position `i`, the same variation also occurs at position `[(i + k*5) mod 25]`. A self-similarity-of-variability measure.
- plus **genome length** (egg cell plus all operators) and **operator usage** (operators applied during ontogenesis), which are genotype properties, not features of `Xi_sigma`.

**6. Was the estimator Monte Carlo?**
Yes. Thesis, section 1.5.3, Measures: the three features "are calculated from a finite size sample (of size 2000) of the distribution for each individual".

**7. Was the remembered sample count of 2,000 correct?**
**Yes, for the thesis.** Table 1.7 lists the row `2000  number of samples to analyze the exploration distributions`. The prior seat suspicion that 2000 was a misread of a generation-axis label is **refuted**; it is a genuine parameter row.
The 2001 paper uses a **different** count for a different experiment: arXiv physics/0102009 Figure 3 states the exploration density "is analyzed by taking 10 000 samples at each time step" for a single tracked individual under (1+1) selection. Both numbers are real and belong to different experiments. There is no contradiction.

**8. Was the 2,000 per individual, per population, per generation, or per checkpoint?**
**Per individual, per generation.** The thesis says "for each individual". The recovered driver `02-stringRuleJTB/main.cpp` confirms the per-generation part: `monitor()` calls `best->spectrum(...)` and then loops `for(i=0;i<pop.N();i++) pop(i).spectrum(...)`, and `Evolution::evolve()` calls `monitor()` once per generation (`evolution.h` line 00133).

**9. Was the detector computed population-wide?**
**Yes.** Thesis Figure 1.6 is captioned "Features of the phenotypic exploration distribution averaged over the population", over the whole offspring population of `lambda = 100`. The recovered source shows the same: an explicit loop over all `pop.N()` individuals accumulating `neudeg`, `avgfit`, `moddeg`, `rules`, `length`, then divided by the count.

**10. Was it longitudinal?**
**Yes.** Figures 1.5 and 1.6 plot all four measures against generation over 0 to 1000 generations. The mutual information matrix is longitudinal but only three snapshots were printed (thesis Figure 1.4 prints matrices at ten selected generations for one individual; the 2001 paper prints three, at generations 50, 500 and 2000).

**11. Were distributions retained, or reduced to a scalar?**
Both, at different rates. The scalars (neutral degree, modular degree, genome length, operator usage) were written every generation to the report stream. The full 25x25 mutual information matrix was also written every generation, to a separate `mutInfo` stream in the recovered driver, but only a handful of snapshots were ever printed in the thesis.

**12. What uncertainty or estimator noise was reported?**
**None. No error bars, no standard error, no repeat estimates, anywhere.** Experiment 1 is a single run. This is the single largest gap in the historical instrument and it is why the HC-T01 preregistration cannot set a change-point threshold until the shakedown measures the estimator's own noise.

---

## One fact the prior ledger did not contain, and it is the most important one

The recovered driver computes a **fifth** spectrum component, `avgfit`, alongside the four that were plotted:

```
best->spectrum(neudeg,avgfit,moddeg,rules,length,data);
```

`avgfit` is the mean fitness of the sampled offspring, that is, the expected fitness of a variant, computed from the same 2000-sample estimate. **It appears in no figure of the thesis and in no figure of any paper recovered here.** It is the most direct evolvability measure in the whole programme and it was computed every generation, for every individual, and never reported.

---

## Detector classification

- Object: distribution over phenotypes reachable in ONE variation step.
- Estimator: Monte Carlo, 2000 samples, per individual, per generation, population-wide.
- Longitudinal: yes.
- Causal capability by itself: none. It is an observational instrument; causal capability requires an intervention, which is what `TOUSSAINT_ABLATION_SPEC.md` supplies.
- Known confound: the estimator is a function of the mutation operator, so any parameter of that operator moves the detector mechanically. See TRAP 1 in `HC_T01_PREREGISTRATION.md`.
