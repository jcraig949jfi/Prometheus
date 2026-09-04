# DESCENDANTS SCREENING LOG

Companion to `COMPOSITION_SEARCH_REPORT.md`. This file exists because a negative verdict is only admissible if it lists what was checked and what each check returned. Screening date 2026-09-03.

## Population screened

Citation graph pulled from OpenAlex for six seed works: the FOGA 2002 exploration-distributions paper, the 2001 arXiv paper, the CEC 2002 and Natural Computing 2003 neutrality papers, the GECCO 2003 plants paper, the 2003 thesis and its 2004 book edition, and the 2006 Compression EDA paper. Semantic Scholar was attempted first and returned HTTP 429.

**134 citing works; 117 after removing Toussaint self-citations.** Full record: `work/descendants_union.json`.

Of these, twenty-four were selected for full screening on the criterion that they plausibly measure variability or evolvability inside a representational manipulation. The remainder are No-Free-Lunch theory, island models, coarse-graining, metaheuristic applications, or reviews of unrelated topics.

## Screening criterion, applied identically

- **A** a detector: an estimate, by sampling offspring or variants, of the distribution of phenotypes reachable in one variation step
- **B** applied longitudinally, repeatedly over generations during a run
- **C** measured inside all arms of an ablation of a representational or variability mechanism
- **D** with the detector trajectory related to subsequent adaptive acquisition

A measurement made once, at the end, or by static enumeration of a landscape does not satisfy B. A comparison of final fitness across encodings does not satisfy A.

---

## Results

| work | A | B | C | D | verdict |
|---|---|---|---|---|---|
| Reisinger and Miikkulainen 2006, Selecting for Evolvable Representations | no | no | partial | no | not the composition |
| **Reisinger and Miikkulainen 2007, Acquiring Evolvability through Adaptive Representations** | yes | **no** | yes | no | near miss |
| Reisinger, Stanley and Miikkulainen 2005, Towards an Empirical Measure of Evolvability | no | no | yes | no | not the composition |
| Altenberg 2005, Evolvability Suppression to Stabilize Far-Sighted Adaptations | no | no | no | no | not the composition |
| Webb 2016, On Selection for Evolvability | unclear | unclear | no | partial | **cannot determine, access blocked** |
| Lehre and Haddow 2006, Phenotypic complexity and local variations in neutral degree | unclear | no | no | no | not the composition |
| **Seys and Beer 2007, Genotype Reuse More Important than Genotype Size** | **no** | yes | yes | yes | near miss |
| Richter, Botsch and Menzel 2015, Evolvability of Representations, a survey | n/a | n/a | n/a | n/a | reports no such study, gives no pointer |
| **Kouvaris, Clune, Kounios, Brede and Watson 2017, How evolution learns to generalise** | **qualified** | yes | yes | yes | **closest of all** |
| Bornhofen and Lattaud 2008, On hopeful monsters, neutral networks and junk code in evolving L-systems | unclear | unclear | partial | unclear | **cannot determine, access blocked** |
| Luerssen and Powers 2007, Evolvability and Redundancy in Shared Grammar Evolution | no | no | no | no | not the composition |
| Luerssen 2005, Phenotype Diversity Objectives for Graph Grammar Evolution | no | no | no | no | not the composition |
| Matos, Suzuki and Arita 2009, Heterochrony and Artificial Embryogeny | unclear | no | no | no | **cannot determine on A, ruled out on B, C, D** |
| Hill and O'Riordan 2011, non-trivial fixed genotype-phenotype mapping | no | yes | yes | no | not the composition |
| Hill and O'Riordan 2015, Impact of Neutral Theory on GA Population Evolution | weakened | weakened | yes | no | not the composition |
| Bercachi, Collard, Clergue and Verel 2008, Effects of Dual Coding | unclear | unclear | unclear | unclear | **cannot determine, access blocked** |
| Bercachi, Collard, Clergue and Verel 2009, Do not Choose Representation just Change | partial | no | no | no | not the composition |
| Rieffel and Pollack 2004, Emergence of Ontogenic Scaffolding | no | no | no | no | not the composition |

### Slice B, the neutrality-measurement line

| work | A | B | C | D | verdict |
|---|---|---|---|---|---|
| Galvan-Lopez and Poli 2006, Some Steps Towards Understanding How Neutrality Affects Evolutionary Search | no | partial | no | no | not the composition |
| Poli and Galvan-Lopez 2007 and 2012, Effects of Bit-Wise Neutrality on Phenotypic Mutation Rates | partial | **no** | no | partial | not the composition |
| Galvan-Lopez and Poli 2011, Neutrality in Evolutionary Algorithms, What do we know? | n/a | n/a | n/a | n/a | **review: reports no instance, and does not ask for one** |
| **Downing 2006, 2007 and 2008 thesis, BDD evolvability in neutral spaces** | **no** | yes | partial | partial | **closest in slice B** |
| Vanneschi et al. 2006 and 2012, Neutrality of Boolean function landscapes in GP | partial | **no** | partial | partial | not the composition |
| Verel, Ochoa and Tomassini 2010 and 2011, Local Optima Networks of NK Landscapes with Neutrality | no | no | partial | no | not the composition |

Slice B's failure mode is the sharpest of the three and it is consistent. **Where a sampled variation detector exists, it is applied once to a static landscape or a static encoding, outside any run.** Vanneschi samples neighbourhoods by Metropolis-Hastings over the search space, not over an evolving population. Poli and Galvan-Lopez estimate a phenotypic mutation rate from 10,000 mutants of a uniform random population, once, per encoding. **Where a per-generation series inside a manipulation exists, the tracked quantity is a structural genotype statistic or a realised, selection-filtered population flow, never a sampled offspring distribution.** Downing's pleiotropic utility is computed deterministically over a genotype's edges; his implied solution complexity is a property of the variable ordering; Galvan-Lopez and Poli's family trees count realised parent-to-offspring transitions after selection.

Downing's 2008 thesis is the closest artifact in this slice, and the only one that puts a per-generation variational measure inside both arms of a representation contrast and reads it against fitness gain. It fails element A.

---

## The three near misses, stated precisely

**Kouvaris, Clune, Kounios, Brede and Watson 2017, PLOS Computational Biology 13(4):e1005358. This is the closest work found anywhere.** It satisfies B, C and D outright. It generates 5000 embryonic phenotypes uniformly at random, develops each through the evolved gene-regulatory network, and re-estimates the resulting phenotype distribution over evolutionary time in all four arms, scoring it as a chi-squared training and test error. It then relates arm to adaptation rate, measured as generations to target on novel environments with the regulatory interactions frozen.

Its A is **qualified, not absent**: the sample is drawn uniformly over the whole genotype hypercube as an explicit approximation to drift, not from the one-mutation-step neighbourhood of a parent. Its manipulated mechanism is the selective pressure that shapes the genotype-phenotype map, not an on-or-off switch on a variation operator. And its acquisition link is arm-level on frozen endpoint architectures, not a within-run relation between a detector trajectory and subsequent gain.

**This narrows the missing-cell claim and must be reported as narrowing it.** The honest statement is not "nobody composed a longitudinal accessibility detector with an intervention". It is that nobody did so with a **one-variation-step offspring distribution** inside an **on/off ablation of a variation operator**, related to acquisition **within runs**.

**Reisinger and Miikkulainen 2007** has the sampled-offspring detector and the representational arms, but runs the detector at exactly two time points, the first-generation champion and the final champion. It fails B by a narrow and specific margin.

**Seys and Beer 2007** has longitudinal measurement, an unusually clean representational ablation with the genotype-size confound deliberately inverted, and a link to subsequent acquisition, but its measured quantity is realised population fitness rather than a sampled offspring distribution. The Seys thesis names the offspring-sampling family explicitly and sets it aside as "not widely used", which is itself evidence about why this composition is rare.

---

## Documented access gaps

These are gaps, not negatives, and they are the honest limit of this search.

0. **Two Downing conference papers and one Vanneschi conference paper** were paywalled, but each is superseded by a full text that WAS read: Downing 2006 and 2007 are chapters 7 and 9 of the 2008 thesis by its own account, and Vanneschi 2006 is extended by the 2012 journal version. **These gaps are not load-bearing.**
1. **Webb 2016 thesis, University of Manchester.** Cloudflare challenge defeated four retrieval routes. Its estimator is described as sampled and used repeatedly during runs, but its manipulated mechanism is selection rather than representation, so it fails element C on the stated criterion regardless of what the full text says about A and B. The EGS chapter was never published separately.
2. **Bornhofen and Lattaud 2008.** Closed access, no repository copy, no author copy. Its system, evolving L-systems with neutral networks and junk code, is the closest *system* to Toussaint's in the whole descendant set, and the abstract names no sampled offspring distribution. **This is the most material gap.**
3. **Bercachi et al. 2008 book chapter.** Closed access, nothing beyond the title recoverable.
4. **Matos, Suzuki and Arita 2009.** Closed access. Ruled out on B, C and D from a complete abstract; element A unverified.
5. **Lehre and Haddow 2006.** Closed access. Ruled out on B, C and D from a complete abstract describing a static genospace survey; element A unverified.

## The field's own admission, which is the strongest documented negative found

Poli and Galvan-Lopez computed the static distribution of phenotypic mutation rates across the strings of a neutral encoding, anticipated exactly the composition sought here, and stated in print that it was not done:

> "To some extent, we would expect evolution to exploit these differences... However, at this stage, we do not know how important this effect is in a mutation-based EA."

And the 2011 review of the whole neutrality literature reports no instance of the composition and, in its own Open Issues section, asks for new encodings, mathematical frameworks and predictive tools rather than for longitudinal exploration-distribution measurement inside an ablation.

An assertion that nobody did something is weak. A leading practitioner writing that they did not do it, and a field review not even listing it as an open problem, is strong.

## Retrieval methods that worked, recorded for reuse

- OpenAlex `filter=cites:<id>` for citation graphs, and OpenAlex abstract inversion for closed-access abstracts.
- NCBI E-utilities `efetch` to obtain complete abstracts when PubMed's own page is behind a cookie wall.
- DSpace REST traversal, from handle to item UUID to bundles to bitstreams, to reach green open-access copies that the repository's own single-page interface will not serve.
- Author personal pages and doctoral theses as substitutes for closed conference papers, where the thesis reproduces the paper.
