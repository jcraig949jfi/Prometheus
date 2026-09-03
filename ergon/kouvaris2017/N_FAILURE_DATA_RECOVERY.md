# N. FAILURE DATA RECOVERY — Kouvaris et al. 2017

Directive §20: recover what the experiment records about *failed* adaptation, and ask whether
trajectory structure was reduced to final scores and discarded. This is where the Historical Collider
may add resolution even to a strong detector.

---

## 1. What failure data exists, and in what form

| Failure type | Recorded? | Form it survives in | What was discarded |
|---|---|---|---|
| **Unreachable targets** (a class member the evolved map cannot express at any budget) | **YES** | Fig 5 boxplot **outliers**, censored at the 2500-generation ceiling; the text names them: *"The outliers … indicate the inability of the developmental system to express the target phenotypic pattern for that selective environment due to the strong developmental constraints"* | the identity of which of the 8 targets failed in which arm is described in prose and readable only off a boxplot; no table, no per-target counts |
| **Phenotype regions never reached** | **YES, as a picture** | Fig 2 and S1 Fig B show the induced distribution pictorially; *"phenotypes with frequency less than 0.01 were ignored"* | the sub-0.01 tail is **thresholded away**. Everything rare — which is where a nascent capability would first appear — is deleted before display |
| **Over-fitting architecture classes** | **YES, and well** | Fig 3A test-error rise with a marked change point; S1 Fig A/S4 shows the coefficient trajectories that produce it | no replication, so no distribution of change-point times |
| **Adaptation-rate plateaus** | **PARTIAL** | Fig 3B/3C describe a plateau in test error under noise and L2 | not quantified; described in prose |
| **Under-fitting at extreme parameters** | **YES** | Fig 4: very high λ returns the system to the *"'no model' situation"* | endpoint values only; no trajectory for the failing cells |
| **Maladaptive mutants** | **NO** | — | Individual rejected mutants are never recorded. Under SSWM the vast majority of proposals are rejected and every one is discarded |
| **Training sets that fail to generalise** | **YES, and this is the best failure dataset in the paper** | S1 Fig A/S5: all 2^16 training subsets, with and without L1, with error bars; *"in situations like the ones of 1 or 2 patterns the parsimony pressure had no effect … and in some situations between 3 to 8 patterns it had little effect"* | **the identity of the failing subsets is not reported.** Which 3-pattern subsets generalise and which do not is exactly the structure that would say *what makes a training set informative*, and it is reduced to a mean and an error bar |
| **Runs that fail** | **UNKNOWN** | — | with the replicate count unstated, it is not knowable whether any evolutionary run failed, or whether the figures show a selected run |

## 2. The four places trajectory structure was reduced to a score

1. **The sub-0.01 frequency cut.** The pictorial distributions discard every phenotype below 1%
   frequency. A phenotype whose accessibility is *rising* from 0.001 to 0.009 over an epoch is
   invisible, and that is precisely the signal a precursor detector is looking for. The underlying
   counts exist in the estimate and were thrown away at plot time.
2. **χ² collapses a distribution to a scalar.** Two maps with identical χ² can be missing different
   members of the class. The paper's own most interesting observation — that the same phenotype is
   missing from Fig 2's distribution and censored in Fig 5 — required going behind the scalar, and
   the paper does that once, in prose, for one phenotype.
3. **The 2^16 enumeration is reported as a mean over subset size.** The dependence of generalisation
   on *which* patterns are in the training set is averaged away. The authors note the effect exists
   (*"different training sets entailed different information about the class, some of which were
   better representatives than others"*) and then do not report which.
4. **Fig 5 reports medians and outliers.** The full distribution of generations-to-target over 1000
   runs per cell exists in the computation and survives only as a boxplot.

## 3. What was never recorded at all

- **Rejected mutants.** The SSWM loop in `GRN.m` evaluates a mutant every step and keeps it only if
  fitter. Every rejection is discarded. This is the largest volume of failure data in the experiment
  and none of it survives. It is also, precisely, a sample of the local offspring cloud — **the
  experiment was generating the A-local data HC-T01 wants, one draw per generation, for 9×10⁶
  generations, and threw all of it away.**
- **Per-run identity.** No seeds, no run indices, no per-run outputs.
- **Any raw data.** S1 states *"No data sets are associated with this publication."*

## 4. Where the Historical Collider adds resolution — ranked by cheapness

This is the answer to the directive's question about whether the Collider can still contribute
against a strong detector. It can, and the cheapest contribution is not a new instrument.

1. **Keep the rejections.** Logging the rejected mutant's phenotype at every step costs one write per
   generation and yields a free, unbiased, one-step offspring sample *taken with the real operator at
   the real current state*, at every generation of the run. This converts the specimen's own design
   into an A-local longitudinal detector **without changing the physics at all**. It is the single
   highest-value change available and it would have been available in 2017.
2. **Remove the 0.01 cut and keep the full count vector** at every checkpoint, not the χ² scalar.
   Storage is 5000 integers per checkpoint.
3. **Report the identity of failing training subsets** from the 2^16 enumeration, not just the mean
   by subset size. The computation already runs; only the reporting is lossy.
4. **Record per-target acquisition outcomes as a table**, including censoring counts, rather than a
   boxplot.

Items 1 and 2 together are what would let anyone ask, on this exact specimen, whether local
accessibility moves before global expressibility does — the question `E_D_LEVEL_ADJUDICATION.md` §7
identifies as the one that remained unanswered in April 2017.

## 5. A negative worth recording

The paper's failure data is, by the standards of this literature, **unusually good**. It reports an
optimum with degradation on both sides for both tuned parameters (Fig 4), it names its own
under-fitting regime, it marks the onset of over-fitting with a line, and it reports censored
failures rather than dropping them. The Historical Collider's usual entry point — *"they discarded
the failures"* — is only partly available here. What was discarded is the **within-distribution
detail** and the **rejected-mutant stream**, not the failure summary.

That is a more accurate and less flattering description of the opportunity than "they could not see
what we can see", and it should be carried into the review packet.
