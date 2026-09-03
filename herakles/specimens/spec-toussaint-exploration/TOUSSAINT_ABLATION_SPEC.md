# D. TOUSSAINT ABLATION SPEC

**Status: T0 COMPLETE for this file. Every statement below was read by this seat in a recovered primary source.**

Primary evidence: `SRC-PHD-2003` = `original/03-toussaint-phd.pdf`, section 1.5.4 "Second experiment: sigma-evolution for phenotypic innovation", pages 64-66, and Figure 1.7.

---

## Answers to the fifteen questions of directive section 3

**1. What mechanism was ablated?**
**Second-type mutations**, the structural rewrites of the genetic system that create, apply, invert and delete production rules. These are the mechanism by which a genetic representation can change at all. They are governed by the single rate parameter `beta`. Setting `beta = 0` freezes the representation: as the thesis puts it, "Without 2nd-type mutations, neutral sets are not explored, no operators are created and the encoding remains a direct one, as it was initialized."

**2. What were the treatment arms?**
Four. Second-type mutations on or off, crossed with two first-type mutation rates.

**3. Was it truly a 2x2 design?**
**Yes, confirmed.** Figure 1.7 caption: "The four graphs display the evolution with and without 2nd-type mutations (beta = 0.1 and beta = 0) and with low and high mutation rate (alpha = 0.03 and alpha = 0.06)." The prior seat doubt about the 2x2 claim is resolved in favour of the claim.

**4. What varied along each axis?**
Axis 1, the representational mechanism: `beta = 0.1` versus `beta = 0`.
Axis 2, the ordinary mutation rate: `alpha = 0.03` versus `alpha = 0.06`. The thesis notes 0.03 is "moderate" in the sense `alpha < 1/25` for a phenotype of length 25, and that at 0.06 a direct encoding of length 25 is above the error threshold and not stable.

**5. What was held fixed?**
"All remaining parameters are the same as for the first experiment", that is Table 1.7: offspring population `lambda = 100`, parent population `mu = 30`, alphabet `a..h`, development stopping time `T = 1`, and the detector's 2000-sample setting.

**6. What outcome was measured?**
Fitness only. Figure 1.7 caption: "The fitness depicted here is the negative percentage of symbols of a phenotype that do not match with the correct phenotype." Each panel shows 10 dotted per-trial curves and their average.

**7. Did adaptive acquisition occur?**
**Yes, and this is the decisive difference from the CEC 2002 sphere experiment.** The population starts from `Psi(0) = <a>` with no operators and must acquire a modular 25-symbol target, `5 x abcde`. There is a real *what* being acquired, namely a modular encoding, not merely a *how fast*. The thesis describes acquisition qualitatively: with second-type mutations enabled, "a few small steps of innovation occur at the beginning; then huge steps of innovation occur when 2nd-type mutations have generated operators, changed the exploration distribution, and enabled a modular and self-similar growth of the phenotype".

**8. Was selection active?** Yes. `(mu, lambda)` selection with respect to Hamming distance to the target; the `mu` individuals closest to the correct phenotype are selected.

**9. Was neutrality active?** Yes, inherently. The genotype-phenotype map is many-to-one by construction; second-type mutations are the moves along neutral sets.

**10. Was representation self-adaptation active?** In the `beta = 0.1` arms, yes; that is exactly what the ablation removes in the `beta = 0` arms.

**11. Population size and run length?**
`lambda = 100`, `mu = 30`. **Run length is not stated.** The caption says only "the time scales are different for different mutation rates alpha". This is the single most important UNSPECIFIED parameter.

**12. How many independent replicates?**
**10 independent trials per cell**, 40 runs in total. Confirmed by the Figure 1.7 caption and by the narrative, which discusses "Four of the 10 runs".

**13. Which plots/results were reported?** One figure, Figure 1.7, four panels of fitness against time. Plus a prose account of four anomalous runs with their genotypes printed.

**14. Was only fitness shown?**
**Yes. Only fitness.**

**15. Were exploration-distribution measurements absent from this experiment?**
**Yes, absent.** This seat searched the full extracted text of the thesis for every detector statistic. `modular degree` occurs at six places, all inside section 1.5.3, the first experiment. `neutral degree` occurs in section 1.5.3, in the theory validation of the first experiment, once in section 1.5.4 as a purely theoretical remark about which pressure acts on sigma-evolution, and twice in the end-matter glossary. No mutual information matrix, no neutral degree curve and no modular degree curve is reported for any arm of the second experiment.

---

## The internal inconsistency in the published record

The thesis states `beta` for the enabled arms **twice as `beta = 0.01`** in the body of section 1.5.4 ("with 2nd-type mutations enabled, beta = 0.01", and again "when 2nd-type mutations are enabled, beta = 0.01"), while **Figure 1.7's own caption says `beta = 0.1`** and Table 1.7 sets `beta = .1` for the first experiment, from which section 1.5.4 says all remaining parameters are inherited.

Two of the three statements say 0.1 and one says 0.01, and they cannot all be right. This is carried into `PARAMETER_CERTAINTY_TABLE.md` as a VERIFIED_RANGE, not a VERIFIED_EXACT, and the reconstruction must test both values.

---

## What the historical record asserts but never measured

The thesis states the mechanism's effect on the detector as a causal chain, in prose:

> "...huge steps of innovation occur when 2nd-type mutations have generated operators, **changed the exploration distribution**, and enabled a modular and self-similar growth of the phenotype"

The middle link of that chain is exactly the quantity the detector measures, and it was not measured in this experiment. The claim is transferred by analogy from Experiment 1, which had no fitness and no ablation, to Experiment 2, which had both and no detector.

**That transfer is the missing cell.**
