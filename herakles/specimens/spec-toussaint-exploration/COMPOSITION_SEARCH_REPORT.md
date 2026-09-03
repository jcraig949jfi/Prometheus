# E. COMPOSITION SEARCH REPORT

**Status: IN-CORPUS SEARCH COMPLETE. DESCENDANTS SEARCH PARTIALLY COMPLETE.** Verdict at the foot of this file.

## The claim under attack

> Toussaint built (A) a Monte Carlo estimator of the phenotypic exploration distribution, measured population-wide and longitudinally, and (B) an ablation of the mechanism that changes that distribution, with an adaptive outcome, but NEVER RAN THE ESTIMATOR INSIDE THE ABLATION.

## Posture

The search is adversarial and tries to kill the claim. If the combined experiment exists, the hypothesis is dead, the verdict is `ALREADY_MEASURED_HISTORICALLY`, and that is a success for the Historical Collider, not a failure. The seat proposed this claim and it is convenient for the programme, so the conflict is recorded here for a reviewer to weigh.

---

## Part 1: within Toussaint's own corpus

Sixteen publications 2001-2007 were recovered in full text and hashed. See `PRIMARY_SOURCE_LEDGER.md`.

### Method, and why it is not a naive grep

The extracted text of several of these PDFs mangles ligatures, rendering "figure" as "(cid:12)gure", and one paper extracts with almost no whitespace. A naive search would have produced false negatives, and did on the first attempt. The census was therefore re-run after stripping every non-alphanumeric character and normalising the three ligature codes, so that spacing and hyphenation cannot hide a hit. Output: `work/term_census.json`.

### Result: the three detector statistics appear in exactly two documents

| term | thesis | 2001 paper / TR | CEC 2002 / NatComp 2003 | all others |
|---|---|---|---|---|
| `modular degree` | 9 | 0 | 0 | **0** |
| `neutral degree` | 26 | 15 | 3 | **0** |
| `exploration distribution` | 89 | 2 | 16 / 20 | present as theory |

The three occurrences in the CEC and Natural Computing papers are a conceptual example about codon bias, not a measurement.

### Result: within the thesis, the detector never enters the ablation

Section boundaries: 1.5.3 is the detector experiment, lines 4482-4812; 1.5.4 is the ablation, lines 4813-4925; 1.5.5 is the plants experiment, lines 4926-5689.

- `modular degree` occurs at lines 4598, 4602, 4712, 4720, 4744, 4754. **All six are inside 1.5.3.**
- Inside 1.5.4, the ablation, the only occurrences of any detector term are two, and neither is a measurement:
  1. an **assertion** that the mechanism "changed the exploration distribution", offered as narrative explanation;
  2. a **theoretical remark** that the selection pressure on sigma-evolution here is "not only the neutral degree but the symmetric structure of the fitness distribution".
- Inside 1.5.5, the plants experiment, there are **zero** occurrences of any detector term.

### Result: the figure inventory of chapter 1 is decisive

| figure | experiment | what it shows |
|---|---|---|
| 1.4, 1.5, 1.6 | Experiment 1 | genotypes, mutual information matrices, and the four detector features, for one individual and for the population |
| **1.7** | **Experiment 2, the ablation** | **fitness only. It is the only figure for the ablation.** |
| 1.8, 1.9 | Experiment 3, plants | fitness, phenotypic elements, genome size, operator usage |

### Companion, workshop, journal and retrospective versions, all checked

- `SRC-FOGA-2002`, the paper whose title most directly promises exploration-distribution measurement, has sections 2, 3, 4 and 6 and **no experiments, no simulation and no measured figure**. Pure derivation.
- `SRC-ARXIV-2002S` and its GECCO version: theory of crossover and entropy. No detector run.
- `SRC-NATCOMP-2003`, the Natural Computing journal extension of the CEC paper, is the single most likely place for an omitted measurement to surface. It contains two figures, one schematic and one analytical, and it **drops** the sphere experiment rather than extending it.
- `SRC-GECCO-PLANTS-2003` runs the same mechanism in a far larger world and reports fitness, phenotypic elements, genome size and operator usage. No detector. Its conclusion explicitly declines to show the ablated arm: "setting beta = 0 in our model corresponds to such a GA... **We do not need to present the results of such a trial, not much happens.**"
- `SRC-BIOSYS-2007`, the latest retrospective, contains no figures, no simulation and no detector term.
- `SRC-FOGA-2005`, `SRC-GECCOWS-2005`, `SRC-TCS-2006`, `SRC-TR-2006`, `SRC-ARXIV-2004`: the programme moves to compact codes and information geometry. No neutral degree, no modular degree.

### The surviving source code sharpens the claim rather than refuting it

The recovered driver `02-stringRuleJTB/main.cpp` shows the detector was **wired into the simulation loop**, not bolted onto one experiment. Its `monitor()` computes the spectrum for the best individual and then loops over the entire population, and `evolution.h` calls `monitor()` once per generation.

By contrast the recovered plants driver `02-plantEvo/main.cpp` has a `monitor()` that computes only fitness, elements, weight, operator usage and genome size, exactly matching the published plants figures.

So the instrumentation difference between the two systems is real and is visible in the code. **Within the string-rule system, the same instrumented binary plausibly produced detector output for both experiments, and only Experiment 1's output was ever plotted.** This is an inference about which build produced Figure 1.7, and it is tagged INFERRED, not verified. It cannot be verified, because the implementation headers containing `spectrum()` were never crawled by the archive and no run logs survive.

One further fact from the code: `spectrum()` also returns **`avgfit`, the mean fitness of the sampled offspring**, computed every generation for every individual. It appears in no figure of any recovered publication. That is a second, independent unreported measurement, and it is the most direct evolvability statistic in the whole programme.

---

## Part 2: bibliographic descendants

The citation graph was pulled from **OpenAlex**, for six seed works: the FOGA paper, the 2001 paper, the CEC and Natural Computing neutrality papers, the plants paper, the thesis and its book edition, and the 2006 Compression EDA paper. Semantic Scholar was tried first and returned HTTP 429.

**134 citing works, of which 117 are not Toussaint self-citations.** Full list preserved at `work/descendants_union.json`. The great majority are No-Free-Lunch theory, island models, coarse-graining, or applications, and are not candidates. Twenty were selected for full screening on the criterion that they plausibly measure variability or evolvability inside a representational manipulation.

Screening protocol, applied identically to each: does the work contain (A) a sampled offspring or exploration distribution, (B) measured longitudinally over generations during a run, (C) inside all arms of an ablation of a representational or variability mechanism, (D) related to subsequent acquisition?

### Slice A, complete

| work | A | B | C | D | verdict |
|---|---|---|---|---|---|
| Reisinger and Miikkulainen 2006, Selecting for Evolvable Representations | no | no | partial | no | not the composition |
| **Reisinger and Miikkulainen 2007, Acquiring Evolvability through Adaptive Representations** | **yes** | **no** | **yes** | no | **nearest miss** |
| Altenberg 2005, Evolvability Suppression to Stabilize Far-Sighted Adaptations | no | no | no | no | not the composition |
| Webb 2016, On Selection for Evolvability | unclear | unclear | no | partial | **cannot determine, access blocked** |
| Lehre and Haddow 2006, Phenotypic complexity and local variations in neutral degree | unclear | no | no | no | not the composition |
| **Seys and Beer 2007, Genotype Reuse More Important than Genotype Size** | **no** | yes | yes | yes | **second nearest miss** |
| Richter, Botsch and Menzel 2015, Evolvability of Representations, a survey | n/a | n/a | n/a | n/a | **reports no such study and gives no pointer to one** |

The two near misses fall on opposite sides of the same fault line, which is itself the finding of this slice. **Reisinger 2007 has the sampled-offspring detector and the representational arms, but runs the detector at exactly two time points, the first-generation champion and the final champion, rather than as a trajectory.** **Seys and Beer 2007 has the longitudinal measurement, a clean representational ablation with the size confound deliberately inverted, and a link to subsequent acquisition, but its measured quantity is realised population fitness, not a sampled offspring distribution.** The Seys thesis names the offspring-sampling family explicitly and sets it aside as "not widely used".

A lead surfaced by this slice, Reisinger, Stanley and Miikkulainen 2005, "Towards an Empirical Measure of Evolvability", GECCO 2005 Workshop Program pp. 257-264, was recovered in full and screened directly by this seat. It does **not** contain the composition: its measure is the average best fitness over the 100 generations following a target reset, and its "average of the local search space" is a developmental-variance noise mechanism inside fitness evaluation, not a recorded detector output.

### Slices B and C

Screening in flight at the time of writing. Slice B covers the Galvan-Lopez and Poli neutrality line including its 2011 review, the Downing binary-decision-diagram line, the Vanneschi neutrality studies and the Verel local-optima networks. Slice C covers the closest systems, namely grammar, L-system and developmental encodings with neutrality: Bornhofen and Lattaud, Luerssen and Powers, Matos and Suzuki, Hill and O'Riordan, Bercachi and Collard, Kouvaris and Clune and Watson, and Rieffel and Pollack.

### Documented access gaps, which are gaps and not negatives

- **Webb 2016 thesis, University of Manchester.** The full text is behind a Cloudflare challenge that refused four distinct retrieval routes. Its evolvability estimator is described as sampled and is used repeatedly during runs, but its manipulated mechanism is selection rather than representation, so on the stated criterion it fails element C regardless. Unresolved on A and B.
- **Lehre and Haddow 2006** is closed access with no repository copy. Ruled out on B, C and D from a complete abstract describing a static genospace survey; element A was not verified.

---

## Verdict

**Deferred until slices B and C report.** On the evidence in hand the in-corpus half of the claim is established beyond reasonable doubt and the descendants half is unrefuted, but a verdict of `MISSING_CELL_SUPPORTED` requires the complete search log, and this programme has already had one asserted negative refuted 0-3 by adversarial review precisely because it was asserted rather than documented.
