# G. HISTORICAL VALIDATION TARGETS

**Status: T0 COMPLETE.** These are independent of the missing-cell result. If the reconstruction misses them materially, the verdict is `RECONSTRUCTION_FAILS` and HC-T01 is not interpreted.

The directive requires at least three. Seven are available, and five of them are quantitative. All come from `SRC-PHD-2003` sections 1.5.3 and 1.5.4.

---

## From Experiment 1, which the reconstruction must reproduce before the ablation is touched

**V1. Genome length falls from 25 to 11 by about generation 200.**
"Evolution starts with a representation of length 25... Until about generation 200, the genome length decreases significantly, down to length 11". The optimal representation is stated to be of minimal length 11. Quantitative: two numbers plus a time.

**V2. Neutral degree rises from about 0.45 to about 0.7 over the same interval.**
"rather low neutral degree of 0.45... the neutral degree increases correspondingly to 0.7". Quantitative, and it is a *detector* value, so it directly calibrates our estimator against his.

**V3. After generation 200 all four measures fluctuate in high correlation, with no further directional trend.**
Qualitative but falsifiable. A reconstruction that keeps improving after generation 200 has different dynamics.

**V4. The mutual information matrix shows regular stripes at phenotype distance 5.**
"The regular strips in the matrix exhibit the correlations between symbols (typically they have distance 5 in the phenotype sequence!)". This is a shape test on the 25x25 matrix, and it tests the estimator, the model and the modularity claim at once.

**V5. Specific recovered genotypes.** The thesis prints the genotype of one tracked individual at generations 0, 21, 125, 145, 150, 200, 215, 220, 225, 255 and 270. A faithful reconstruction should produce genotypes of this kind, in this length range, with this operator structure. It cannot reproduce them exactly, because the run is stochastic and no seed survives, so this target is scored on structure, not identity.

## From Experiment 2, the ablation itself

**V6. At high mutation rate the ablated arm fails to converge and fluctuates at about 20 percent non-optimal symbols.**
"the curves for the direct encoding case do not converge towards the optimal phenotype but fluctuate around 20% non-optimal symbols". This is the sharpest quantitative target in the ablation, and it is an outcome target, independent of any detector reading.

**V7. At high mutation rate with the mechanism enabled, 4 of 10 runs show the barrier pathology.**
Two runs never reach the optimal phenotype; two more reach it with a suboptimal encoding. The thesis prints all four genotypes. Target: a comparable fraction of runs in that cell should be trapped, and the trapped genotypes should show the same signature, namely a promoter symbol that is also needed as a phenotype symbol, or a module boundary offset from the target's period.

**V8. Qualitative shape difference in the fitness trajectory at moderate mutation rate.**
Ablated arm: "successive small steps". Enabled arm: a few small steps, then "huge steps of innovation", then smaller steps again. Both arms reach the optimum. Target: the step-size distribution differs between arms even though both succeed.

---

## Scoring rule, fixed now

- V1, V2 and V6 are the **primary** targets. Each must be matched within a tolerance set from the reconstruction's own run-to-run spread, and that spread must be reported. A tolerance will not be chosen after seeing the reconstruction's value.
- V4 and V7 are **structural** targets, scored present or absent.
- V3, V5 and V8 are **corroborating** and cannot on their own fail the reconstruction.
- Missing any primary target materially, meaning outside the reported run-to-run spread by more than a factor preregistered at freeze time, yields `RECONSTRUCTION_FAILS`.

Note the asymmetry deliberately. **V2 is the only target that tests our detector against a historical detector value.** If V2 fails while V1 and V6 pass, the model is right and the estimator is wrong, which is a different and more informative failure than the model being wrong.
