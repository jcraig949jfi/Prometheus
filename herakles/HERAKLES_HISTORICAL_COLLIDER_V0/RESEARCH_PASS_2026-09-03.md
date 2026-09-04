# RESEARCH PASS 1 — 2026-09-03 — primary-source verification of the V0 seed

Method: multi-agent deep-research fan-out (107 agents, 25 sources, 3-vote adversarial verification per claim, 2/3 refutes to kill). 17 findings survived; 6 claims were refuted. Full run digest retained at run id `wf_5bd85206-7a3`.

**This pass changes the seat's disposition.** The specimen parameters verify almost exactly as recalled. The seat's own opening hypothesis does not survive in its stated form.

---

## 1. THE HEADLINE: the blind-spot hypothesis is partly dead

The V0 lead (`M_BLIND_SPOT_MATRIX.md`) said historical instruments measured state and almost never measured change in what is reachable. Two counterexamples were found, both unanimous at 3-0, and both were on the seat's own list of places to look.

**Altenberg 1994**, "The Evolution of Evolvability in Genetic Programming", chapter 3 of Kinnear ed., *Advances in Genetic Programming*, MIT Press. Author-hosted PDF at `dynamics.org/Altenberg/FILES/LeeEEGP.pdf`, 29 pages extracted and read.
- **Theorem 3 (Evolvability)** decomposes the probability that a population produces individuals fitter than any existing one into a search-bias term (excess over random search) plus a parent-offspring regression term scaled by fitness variance, derived via Price's Covariance and Selection Theorem. Altenberg proposes it explicitly as a replacement for the Schema Theorem.
- **Theorem 4 (Evolution of Evolvability)** is a rate law for the change in reachability: evolvability, defined as the probability that a duplicated random block of code increases fitness, increases at a rate proportional to the variance in the constructional fitnesses of its blocks. Verbatim: *"This result is Fisher's fundamental theorem of Natural Selection, but applied not to the fitness of the evolving programs, but to their evolvability."*
- So the formalism for reachability change existed in 1994, thirty-two years ago, and it couples structural duplication directly to evolvability change.

**Mengistu, Lehman and Clune 2016**, "Evolvability Search", GECCO 2016 pp.141-148. This is a measurement, not only a formalism: the offspring-effect distribution *is* the fitness function. Evolvability is estimated by generating 200 simulated offspring, discarding them, and counting behaviourally distinct ones at a 0.01 threshold. They then run an explicit reachability-transfer test, moving the most evolvable organism into an unseen 450x450 maze and measuring the fraction of grid cells its offspring cloud reaches, beating novelty search and objective search at p<0.001.

**Dating correction that weakens the seat further.** The 2016 measure is inherited, not invented. Lehman and Stanley 2013 (PLoS ONE 8(4):e62186) enumerate the genomes reachable by all possible single-connection mutations and count unique behavioural niches, which is literal reachable-neighbourhood measurement, with precedent cited to Lehman and Stanley 2011 and Reisinger and Miikkulainen 2006. **The anchor date is 2011 or earlier, not 2016.**

### What survives, precisely

The strong claim is dead. The residue is narrower and must be stated as such:

> The formalism for reachability change was available from 1994 and neighbourhood-diversity measurement from 2011 or earlier, but population-wide measurement of reachability change over a lineage was not performed in the specimens profiled. Altenberg himself wrote that the offspring-effect quantity *"should be possible to measure in GP runs"* and reported no such measurement in that chapter.

Even this residue is fragile. Two qualifications from the verifiers:
- The 2016 statistic is a scalar count at a threshold, not the full distribution of mutational effects, and it is a snapshot of neighbourhood size at a point rather than a lineage-level measure of change. That snapshot-versus-change distinction is where the remaining hypothesis lives.
- **Only two of the eight candidates the seat itself named were actually checked, and both were genuine counterexamples.** A 2/2 hit rate on a self-selected list is weak evidence about a base rate, but it should shift the prior sharply toward "the gap is smaller than hypothesised" before more effort is committed.

**Disposition:** `M_BLIND_SPOT_MATRIX.md` is amended, not deleted. The hypothesis is downgraded from "opening thesis" to "narrow residual claim, actively being disconfirmed". The six unchecked candidates (Wagner and Altenberg 1996; Hu and Banzhaf on accessibility in linear genetic programming; Dolson and Ofria's MODES toolbox; Toussaint on neutral traits shaping the exploration distribution; Andreas Wagner; Draghi; Hordijk and Stadler; Bedau and Packard evolutionary activity) must be cleared before the residue is quoted anywhere.

---

## 2. EvCA specimen: parameters VERIFIED, and one correction that improves the experiment

Promoted to `PRIMARY_SOURCE_READ`. Sources: Mitchell, Crutchfield and Hraber, *Physica D* 75 (1994) 361-391 (SFI WP 93-11-071), and Das, Mitchell and Crutchfield, PPSN III 1994 pp.344-353 (SFI WP 94-03-015), both read as author-hosted PDFs at `csc.ucdavis.edu/~evca/Papers/`.

Confirmed verbatim: k=2, r=3 with periodic boundaries, rule-table chromosome 2^(2r+1)=128 bits over a 2^128 space, lattice N=149, population P=100, elite E=20 (generation gap 0.8, top 20% copied unmodified), remaining offspring by single-point crossover between elite parents chosen **with replacement**, exactly m=2 point mutations per offspring, I=100 initial conditions per evaluation **regenerated fresh every generation including for the elite**, relaxation time M drawn per simulation from a Poisson with mean 320 (about 2.15N). Generations G=100 in the Physica D experiment, G=50 (100 in some runs) in PPSN III. An earlier companion paper in *Complex Systems* 7(2) used I=300.

### The correction that matters most

**The transition frequency is two different numbers from two different experiments, and V0 conflated them.**

| Experiment | Runs | Outcome |
|---|---|---|
| Physica D 1994 | 50 GA runs with crossover | **Zero** particle-based strategies. 46/50 showed the same four-epoch best-fitness signature; epochs 3 and 4 are block-expanding. 4/50 never exceeded fitness 0.5. |
| PPSN III 1994 | 300 runs, one seed each | Particle-based computation on exactly **7 runs = 2.3%**. Most runs evolved one of the two block-expanding strategies. |

A verifier grepped the Physica D text: the word "particle" occurs zero times in part 2, and in part 1 only in analysis of the hand-designed GKL rule. So a reconstruction targeting the Physica D configuration would be targeting a configuration in which the phenomenon of interest **never occurred**. This alone would have wasted the first experiment.

"Epochs of innovation" is the papers' own phrase, from the Figure 3 caption: *"each corresponding to the discovery of a new, fitter strategy"*.

### A load-bearing confound the seat must carry

Initial conditions were sampled uniformly over density in [0,1], exactly half either side of the critical density, **not** from the unbiased binomial over configurations. The authors say the bias was necessary for early progress and, verbatim, that it *"turns out to impede the GA in later generations because, as increasingly fitter rules are evolved, the IC sample becomes less and less challenging"*. The initial population was likewise seeded uniformly over the fraction of 1s in the chromosome, not per bit.

This is the fitness measure F_I, and it is distinct from the unbiased reporting measure. **Quoting a single accuracy without naming the distribution is an error**: GKL scores 0.972 on the density-uniform measure at N=149 and 0.816 on the unbiased measure.

### Measured accuracies (unbiased P over 10^4 ICs, N=149/599/999)

| Rule | N=149 | N=599 | N=999 |
|---|---|---|---|
| majority | 0.000 | 0.000 | 0.000 |
| block-expanding (GA) | 0.652 | 0.515 | 0.503 |
| particle (GA, best of three) | 0.769 | 0.725 | 0.714 |
| GKL (hand-designed) | 0.816 | 0.766 | 0.757 |

Standard deviation of the N=149 measure is about 0.004. The F_100 fitness measure has a noise floor of about 0.02, which the authors identify as the impediment preventing the GA from resolving GKL-quality rules.

**Scope trap flagged by a verifier:** "the GA never matched GKL" is true of the EvCA runs only. Andre, Bennett and Koza (GP-96) and Juille and Pollack report evolved rules at or above GKL on the unbiased measure.

### Two things V0 got wrong or would have got wrong

1. **The impossibility bound is on perfect classification, not an accuracy ceiling**, and the 1994 PPSN paper does **not** cite Land and Belew, which postdates it (published 19 June 1995). It attributes the argument to *"C. Moore. Personal communication."* Land and Belew appears in the 1996 review. Further, the review's paraphrase is **weaker than the actual theorem**: impossibility bites at each fixed sufficiently large ring size, not only under quantification over all sizes. Capcarrere, Sipper and Tomassini 1996 and Fuks 1997 circumvent it under changed output specifications.
2. **"No artifact survives" for EvCA is NOT established.** The negative inventory claim was refuted 0-3. No verifier found source code either. The question is open in both directions and must be re-run as a dedicated artifact hunt, not recorded as a negative finding. Evolved rule tables **are** printed as hexadecimal in the 1996 review's Table 1, but a specific transcription of the digits was refuted 0-3, so the digits and the neighbourhood-ordering convention must be re-read from source before any reimplementation.

---

## 3. Lindgren specimen: encoding and duplication VERIFIED, with a load-bearing scope correction

Promoted to `PRIMARY_SOURCE_READ` for the ECAL93 paper only. Source: Lindgren and Nordahl, "Evolutionary dynamics of spatial games", ECAL93 pp.604-616, at `alife.org/wp-content/uploads/2013/08/collections_ECAL93-0604-0616-Lindgren.pdf`.

**Custody note, unusual and important:** that PDF is an image-only scan with no text layer. Verifiers extracted the page images and read them visually. Two independent verifiers produced matching transcriptions, which is why confidence is high, but every quote below is a **transcription**, not machine-extracted text. Any digit that becomes load-bearing must be re-checked. The paper is internally inconsistent between `p_dupl` on p.606 and `p_dbl` on p.608 for the same operator.

Verified: a memory-m strategy is a binary string of length 2^m indexed by history bits. Three mutation operators: point mutation at rate p_mut; **gene duplication** at rate p_dupl raising m to m+1 by doubling the genome (1011 becomes 10111011); and split at rate p_split, halving and keeping one random half.

The duplication operator's neutrality is confirmed **in the paper's own words**, which is stronger than the seat claimed:

> *"Gene duplication is a neutral mutation, which increases the size of the evolutionary search space without immediately affecting the phenotype. Additional point mutations can then give rise to new strategies without shorter memory equivalents."*

This is a structural fact of the encoding, not an empirical assertion: the doubled string ignores the new most-significant bit.

### The scope correction

**The verified source is the spatial lattice model with Nordahl, not the 1991 replicator model.** In ECAL93 each site holds one strategy, plays the infinitely iterated game against four nearest neighbours, and deterministically adopts the highest-scoring strategy in the von Neumann neighbourhood, ties broken by tiny noise, updates simultaneous. The paper states its genetic representation is identical to Lindgren 1991 and that the 1991 model *"could be viewed as a mean-field approximation to the present model"*.

Published ECAL93 parameters: (R,S,T,P)=(1,0,5/3,1/3), p_err=0.01, p_mut=0.002, p_dbl=p_split=0.001, initial state one of the four memory-1 strategies per site with equal probability, main run 3000 generations.

**Two qualifications that must travel with those numbers:** the 5-run 100x100 phase-diagram figures had duplication and split **disabled**, so p_dbl and p_split must not be carried into them; and the 10^5-generation stability statement is scoped to memory-5 mutants only.

**Still unanswered for the 1991 model:** replicator-ODE versus finite population, run counts and lengths, the extinction frequency cutoff, and the paper's actual wording on punctuated stasis and extinction events. There is also a citation-year discrepancy to resolve, since ECAL93 cites it as 1991 while it is commonly cited as 1992 (Artificial Life II). No claim about code survival was submitted for either model.

---

## 4. What this pass did NOT answer

Recorded as gaps in the research, **not** as findings.

- **RQ4, Avida, entirely unanswered.** Zero claims survived on the population-wide base rate of deleterious intermediates that led nowhere, on Covert et al. 2013, or on the archival status of the 2003 configurations, genomes and line-of-descent data. The fan-out did reach relevant sources without producing surviving claims, including a Dryad dataset, the archived Lenski-lab supplementary page, and a PMC article. **This is the highest-value remaining target**, because a clean "not measured" there is the single strongest licence for the seat's programme, and it now looks more valuable than before precisely because the blind-spot thesis weakened.
- **RQ5, composition cells, largely unanswered.** The NEAT ablation endpoint question was not checked, despite the fan-out reaching Stanley's 2002 paper and 2004 thesis. Island models versus speciation was not checked. For robustness versus duplication, only the duplication half is touched, by Altenberg's Theorem 4.
- **Six of eight RQ3 counterexample candidates unchecked**, with three verifiers reporting the search budget exhausted at 200/200 before an adversarial sweep could run.

---

## 5. Effect on the first experiment: it survives, better specified

The recommendation stands, with the target configuration changed from the Physica D setup to the **PPSN III 300-run configuration**, which is the only one in which particle strategies appeared.

The pre-registered outcomes are now quantitative rather than aspirational, and the gate is computable in advance as the standing rule requires.

Original rate: 7/300 = 0.0233. Wilson 95% interval [0.0113, 0.0474]; normal-approximation SE 0.0087.

| Replication | Expected transitions | SE | 95% half-width |
|---|---|---|---|
| n = 1,000 | 23 | 0.0048 | 0.0094 |
| n = 10,000 | 233 | 0.0015 | 0.0030 |

So `HISTORICAL_PHENOMENON_RECURS` fires if the reconstruction rate lands inside the Wilson interval of the original, and `RECONSTRUCTION_FAILS` becomes a sharp call rather than a judgement, because at n=10^4 our own interval is about fifteen times tighter than the historical one.

**The CONTINGENT gate, computed before the replay is designed and shown reachable.** Comparing conditional transition probability between 1,000 forks from a pre-transition checkpoint and 1,000 from a fitness-matched control:

- minimum detectable precursor rate at 2 sigma, control at 0.023: **0.0381**, a 1.7x enrichment
- at 3,000 forks per arm: 0.0312, a 1.4x enrichment

The attainable range of the difference is 0 to 1 and the gate sits at 0.015 above control, so the gate can fire on real inputs. This closes the defect that produced two earlier Prometheus failures.

---

## 6. Promotions and demotions applied to the registries

| Row | Was | Now | Basis |
|---|---|---|---|
| `spec-evca-density` parameters | MODEL_RECALL_UNVERIFIED | PRIMARY_SOURCE_READ | Physica D and PPSN III PDFs |
| `spec-evca-density` transition rate | recalled as "rare" | PRIMARY_SOURCE_READ, 7/300 in PPSN III, 0/50 in Physica D | both papers |
| `spec-evca-density` artifact status | "source REPORTED" | **UNKNOWN, open in both directions** | negative inventory refuted 0-3 |
| `spec-lindgren-ipd` encoding + duplication | MODEL_RECALL_UNVERIFIED | PRIMARY_SOURCE_READ (ECAL93 only) | page-image transcription, 2 independent verifiers |
| `spec-lindgren-ipd` population dynamics | recalled | **still UNVERIFIED**, wrong paper | scope correction |
| `part-structural-duplication` neutrality | observed_association | historical_sequence with a primary quotation | Lindgren's own words |
| `part-structural-duplication` -> evolvability | speculative | **theoretical rate law exists** (Altenberg Thm 4) | primary source |
| M blind-spot hypothesis | opening thesis | **downgraded to narrow residual claim** | two counterexamples |
| `bump-evca-transition` | pool entry | pool entry with a real denominator | 7/300 |

No row was promoted to `ARTIFACT_IN_HAND`. Manifest J remains empty: this pass read papers, it did not recover code or data.
