# D. HISTORICAL DETECTOR SPEC — Kouvaris et al. 2017

*(directive §4 names this `KOUVARIS2017_DETECTOR_SPEC.md`; §24 names it
`HISTORICAL_DETECTOR_SPEC.md`. Same document.)*

This is the central question of the pass. The detector is fully recovered from two independent
primary sources that agree with each other: the published Methods section *Estimating the empirical
distributions*, and the recovered implementation `findErrors.m` + `histP.m`.

---

## 1. The detector in one paragraph

Draw **5000 points uniformly at random in the continuous hypercube `[−1,1]^16`** using a scrambled
Sobol low-discrepancy sequence. Treat each point as an embryonic phenotype `G`. Develop each one
through the **current** regulatory matrix `B`, holding `B` fixed. Take the sign of each resulting
adult phenotype, giving a 16-bit pattern. Count how many of the 5000 land on each target pattern.
Normalise to a distribution. Compare that distribution by **χ²** against two reference
distributions: one built from the 3 training targets (**training error**) and one built from all 8
class members (**test error**). Repeat for every stored `B` along the evolutionary trajectory.

**The object measured is "what phenotypes can this developmental map express, from anywhere in
embryonic-phenotype space". It is not "what phenotypes can this organism's offspring be".**

## 2. The exact code, quoted

From `findErrors.m` (recovered, `KostasKouvaris_Evolvability`):

```
No_Samples = 5000;
H = (2*(net(scramble(sobolset(M,'Skip',500,'Leap',0),'MatousekAffineOwen'),No_Samples))-1)';
...
for i = 1:N
    B = vec2mat(outB(i,:),M);
    Test_Error(i,:)     = HD(H, B, Test_Set,     tau1, tau2, T, Ideal_histD_Test,     aIdeal_histD_Test);
    Training_Error(i,:) = HD(H, B, Training_Set, tau1, tau2, T, Ideal_histD_Training, aIdeal_histD_Training);
end
```

Three things are settled by those eight lines and are not visible in the paper:

1. **`H` is generated once, outside the loop.** The identical 5000-point probe set is used at every
   time point and in every arm. This is a *same-probe counterfactual* by construction: differences
   between time points and between arms cannot be probe-resampling noise. That is a genuine design
   strength and a stealable part.
2. **`outB` is the stored trajectory of `B`, one row per epoch** (written by `GRN.m` as
   `output_b(ceil(t/(mult*N*on_period))+1,:) = B(:)'`). The detector is applied by **replaying the
   trajectory afterwards**, not inside the evolutionary loop.
3. **The χ² reference distribution is not the raw target set.** It is the distribution produced by
   developing the same `H` through an **ideal Hebbian matrix** — `Ideal_B = Hebbian(Training_Set, lr)`
   with `lr = 2`, and likewise for the test set. So "error" is distance from *what a Hebbian-ideal
   developmental map would produce*, not distance from a uniform distribution over targets. The
   published Methods do not state this.

From `histP.m`: phenotypes are binarised by `sign()`, mapped to integers, and counted against the
target list; `Accuracy` is the fraction of the 5000 samples landing on any target.

## 3. The fourteen directive questions, answered

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | One-step offspring variation from a fixed parent? | **NO** | The sample is uniform over the whole hypercube. The actual one-step operator perturbs **one** gene by at most 0.1 (`mutate_gene.m`); the probe set ignores the operator entirely. |
| 2 | Sampled locally around individual genotypes? | **NO** | No locality of any kind. `H` is independent of the current `G`. |
| 3 | Sampled uniformly over larger genotype space? | **YES — this is exactly what it is** | Paper: *"5000 embryonic phenotypes, P(0)=G, are uniformly generated at random in the hypercube [−1,1]^N"*; and *"we estimate drift with a uniformly random distribution over G (keeping B constant)"*. |
| 4 | Measured population-wide? | **N/A, and the question does not apply** | There is no population; the system is a single genotype under SSWM. The detector is over *genotype space*, not over a population. |
| 5 | Measured longitudinally during evolution? | **YES** | Fig 3 (error vs evolutionary time, 4 panels); S1 Fig B (pictorial distribution across epochs); S1 Fig D (entropy vs time); S1 Fig A/S4 (regulatory coefficients vs time). Code: the `for i = 1:N` loop over `outB`. |
| 6 | Measured in every intervention arm? | **YES** | Fig 3 has one panel per arm: A control, B noise, C L2, D L1. |
| 7 | Retained as a distribution or reduced to a summary? | **BOTH, and the distribution is shown** | The full distribution is displayed pictorially (Fig 2, S1 Fig B) and reduced to χ² training/test error for the time series, plus Shannon entropy in S1 Fig D. |
| 8 | How many samples? | **5000** per estimate for χ²; **5×10⁵** for the entropy figure | Methods; S1 Fig D caption. |
| 9 | Sampling repeated through generations? | **YES, but the same fixed sample is re-used** — the probe set is not redrawn | `H` generated once in `findErrors.m`. |
| 10 | What uncertainty is reported? | **NONE.** No error bars, no bands, no intervals on any longitudinal detector figure; the number of evolutionary replicates is never stated | Article body; `GRN.m` has no replicate loop. |
| 11 | Is the detector used for selection? | **NO** | S1, explicitly: *"natural selection did not directly select either for correlations, or for matching the exploration distribution to the fitness distribution … Natural selection selected for immediate fitness differences"*. |
| 12 | Is the detector scientist-side only? | **YES** | S1: *"The evaluation of the developmental process performed here against the training and the test set was a post hoc analysis, and hence not part of the actual evolutionary dynamics."* |
| 13 | Does the detector alter the experiment? | **NO** | It is a replay of stored `B` matrices. It cannot perturb the run. |
| 14 | Current variation, or future acquisition probability? | **Current expressive capacity of the map.** It characterises what `B` produces now. Its relation to future acquisition is asserted separately, at arm level, by a different experiment (Fig 5) | See `H_TEMPORALITY_ANALYSIS.md`. |

## 4. Directive §9 — which distribution, exactly

For each reported measure, what is sampled:

| Measure | What is sampled | Class |
|---|---|---|
| Phenotypic distribution (Figs 2, 3, 4; S1 Figs B, C) | **random genotype samples** — uniform Sobol points over the whole embryonic-phenotype hypercube, developed through the current fixed `B` | `A-global` |
| Shannon entropy (S1 Fig D) | same sample, 5×10⁵ points | `A-global` |
| Regulatory-coefficient trajectories (S1 Fig A/S4) | not a sample at all — the raw `B` entries over time | not a variation detector |
| Adaptation rate (Fig 5) | **not a distribution** — 1000 hill-climbing runs of `G` under frozen `B`, counting generations to target | acquisition outcome, not a detector |
| Exhaustive training-set analysis (S1 Fig A/S5) | same `A-global` probe, but `B` from **Hebb's rule** rather than from evolution | `A-global`, non-evolutionary |

**None of them is the immediate-mutant cloud of the evolved genotype.** The authors are explicit
about why: they are approximating *drift*, and they justify the uniform draw by noting that mutation
on `G` is much larger than mutation on `B`, so over the timescale on which `B` is fixed, `G` wanders
freely. That is a defensible modelling choice for their question. It is a different object from
"what is reachable in one variation step from here".

**Why the difference is not implementation trivia.** In this very model the one-step neighbourhood
of `G` is a perturbation of at most 0.1 on one of 16 coordinates — a set of measure ~0 relative to
the `[−1,1]^16` cube the detector samples. A map `B` could concentrate the uniform-sample
distribution on the class while the *local* neighbourhood of the current `G` reaches nothing new,
or the reverse. The two detectors are not approximations of each other, and no result about one
transfers to the other without an argument the paper does not make.

## 5. Cost

5000 developmental simulations of 10–15 steps on a 16-node network per time point per arm, plus
5×10⁵ for the entropy figure. On 2017 hardware this is seconds per time point; it is why the
authors could afford to run it at every epoch. **The detector was never the expensive part.** That
matters for §18: the reason nobody composed this detector with an operator ablation is not cost.

## 6. What this detector can and cannot see

**Can see:** whether the evolved map's expressible-phenotype distribution has concentrated on the
selected targets (canalisation), spread over the structural family (generalisation), or collapsed
(under-fitting). It can see this *as a trajectory*, and it can see it identically across arms
because the probe is shared.

**Cannot see:**
- anything about the *current organism's* adjacent possible — locality is absent by construction;
- anything about the *variation operator*, which never enters the estimate;
- any uncertainty, because it was run without replication;
- any within-run relation to what the lineage subsequently acquired, because acquisition is measured
  only after evolution stops, on a frozen map.

## 7. The entropy trajectory, added at publication

S1 Fig D reports Shannon entropy of the induced distribution over evolutionary time, falling from
**16 bits** (uniform over the phenotype space) to **4 bits** under L1 (four independent modules), and
to **below 4 bits** under over-fitting. This figure is **absent from the preprint** and appears only
in the published S1. It is the cleanest single scalar in the paper: it distinguishes generalisation
(exactly 4 bits) from over-fitting (fewer than 4) on a principled scale with a known attainable
range. It is recorded as a stealable part in `L_HISTORICAL_DETECTOR_PARTS.jsonl`.

## 8. The unreported sibling detector

`computeM.m` and `evalMutCorr.m`, in the author's *Phenotypic-Plasticity-Logical-Inference*
repository, implement a genuinely **local** detector: for each individual in a population, apply
`mNum = 300` **single** mutations (structural flip with probability `alpha = 0.2`, else a weight
perturbation `N(0, 0.5)`), develop each mutant, and record `B = mPhens − uPhens`, the
mutational-effect vectors. From these it computes the mutational correlation matrix and mutational
variance — the **M-matrix**, estimated from one-step mutants of real current individuals,
population-wide, with the mutation draws frozen in `rand_nums.mat` and **re-used across replicates**.

This is `A-local`, population-wide, same-probe, and replicated. It is **not** longitudinal: it loads
one saved population per replicate (`replicate_N_Pop.mat`) and there is no loop over generations.

**It appears in no publication and in no chapter of the thesis** — the strings "mutational
correlation", "mutational variance" and "M-matrix" occur **zero** times in 159 thesis pages. It is
unreported instrumentation, exactly parallel to the unreported `avgfit` that Herakles found in
Toussaint's own code. Its existence is the strongest single fact this pass found *against* HC-T01's
novelty, and it is handled in `F_ABCD_COMPOSITION_MATRIX.md` §5.
