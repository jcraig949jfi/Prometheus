# K. DESCENDANT SEARCH — forward from 2017

Directive §17: search direct descendants through the present; ask whether later work performed the
stronger experiment; **prefer the strongest already-built microscope.**

**This deliverable contains the most important finding of the pass, and it is the one that most
damages HC-T01.**

---

## 1. Method and counts

- **OpenAlex** (seed `W2578730668`): **106 citing records → 90 distinct works** after collapsing
  preprint/journal pairs. Raw JSON at `work/kouvaris_cited_by.json`.
- **Semantic Scholar** cross-check: 93 citing records, HTTP 200. ~12 genuinely additional works,
  two of which mattered.
- **Union: ~102 distinct works**, 2017–2026. Year histogram from OpenAlex: 2017:6, 2018:6, 2019:13,
  2020:15, 2021:13, 2022:11, 2023:15, 2024:13, 2025:11, 2026:3.
- **Self-citations** (Watson / Kouvaris / Kounios / Clune / Brede): 17 records, 12 distinct works.
  Watson on 15; Clune on 2; **Kounios 0, Brede 0**.
- **18 screened in full** against the four-element criterion. The rest triaged out as reviews and
  perspectives with no experiment (Uller 2018, Levis & Pfennig 2019, Feiner 2021 — explicitly
  labelled a perspective with hypothetical figures, Frank 2026 — *"This article generated no new data
  or computer code"*, Mitchell & Cheney 2025, Hartl & Levin 2025), philosophy-only (Lewens, Buskell,
  Steinhart, the Levin agential-materials cluster), or off-topic.

**Verification posture.** The enumeration and triage were done by a delegated search. The two works
that carry the conclusion — **Petak 2025** and **Tiso 2024** — I re-verified myself from primary
source, and the quoted sentences below are ones I read in the retrieved documents, not summaries.
Every other row is screening-level.

## 2. The screening table

| Work | A | B | C | D | Verdict |
|---|---|---|---|---|---|
| **Tiso 2024, thesis ch.3, Groningen** | **local** | **yes** | **mechanism** (not all arms) | **within-run, descriptive** | **HIT, qualified** |
| **Petak et al. 2025, PNAS** | **local** | **yes** | selection | arm-level | strictly stronger than the seed on A and B |
| Kounios et al. 2016, arXiv (sibling, not a citer) | global (basin size) | yes | **mechanism** (detector not in the null arm) | weak within-run | closest sibling |
| Moreno, Banzhaf & Ofria 2018, GECCO | local | **no** | mechanism | arm-level | detector ran in a *separate* experiment with different mutation rates |
| Ng & Kinjo 2023/2024 | population, generation 1 only | no | mechanism | arm-level | — |
| Kriegman et al. 2017, GECCO | global | no | mechanism | arm-level | "evolvability" never quantified as a distribution |
| Brun-Usan et al. 2020, PLOS CB | global (10⁵ random GRNs) | no | none | none | — |
| Szilágyi et al. 2020, PLOS CB | local, endpoint only | no | none | none | — |
| Tsuru & Furusawa 2025, Nat Commun | local (empirical MA lineages) | no | none | none | — |
| Geoffroy & André 2021, PRSB | none (backprop, no mutation) | yes | mostly selection | arm-level | — |
| Rago et al. 2019, PLOS CB | none | no | mixed | none | thesis ch.3 published |
| Shreesha & Levin 2023; Hartl/Risi/Levin 2024; Beaulieu 2018; Rappeport & Nitzan 2026; La Grove 2021; Vasylenko 2020 | none/global | no | mixed | none/arm | — |

## 3. Tiso 2024 — the nearest thing to HC-T01 that exists anywhere

*Tiso, thesis chapter 3, "The evolution of mutational transformers", University of Groningen,
defended 23 January 2024. Recovered as `original/tiso2024_thesis_groningen.pdf`, 182 pages, and
verified by me directly.*

- **A-local — verified, quoted from the retrieved PDF (p.67):** *"produced by 1000 different
  mutations at each locus of the best-performing GRN at a certain time point"*. Per-locus, one
  mutation at a time, from the actual current best individual.
- **B-within-run — verified, Fig 5C caption:** *"Distributions of the phenotypic effects of mutations
  at four different time points during the simulation. The first two time points are early in the
  simulation, shortly before … and after … an environmental change. The other time points are from a
  later stage."*
- **C-mechanism — verified:** the arms are GRN architecture crossed with transfer function (`1`,
  `1-1`, `10-2-1-1-1`, `5-5-5-1` × identity/sigmoidal), with environment and selection held fixed.
  This is a representational manipulation, not a selection one.
- **D-within-run — verified as descriptive:** the text links detector state to recovery speed at two
  stages of the same run — *"at the start of the simulation, the recovery of the population after an
  environmental change is slow and gradual … Towards the end of the simulation, when the population
  is able to recover rapidly from environmental change (i.e. the mutational transformer has evolved),
  we observe that the phenotype is highly sensitive to mutations at a particular, sensitive, locus."*

**Its three defects, which are what leave HC-T01 anything at all:**

1. **The detector is not run in all arms.** It is reported for the `1-1` linear and `1-1` sigmoidal
   arms and **not for the trivial `1` network — the negative-control arm**, the one where
   time-to-adaptation does not improve. A detector absent from the control arm cannot support a
   contrast. This is the same structural failure Herakles found in Toussaint, in a different place.
2. **The within-run link is descriptive, `n = 1`, unquantified.** Fig 5 is *"a representative
   simulation"*. There is no statistic relating detector state at generation `t` to
   time-to-adaptation at `t+n`. The only quantified comparison is arm-level over 7–10 replicates.
3. **It was never published.** No peer-reviewed version exists; it is a thesis chapter.

## 4. Petak et al. 2025 — the strongest *published* local longitudinal detector

*"The variability of evolvability: Properties of dynamic fitness landscapes determine how phenotypic
variation evolves", PNAS 2025, PMC12745803. Verified by me from the Europe PMC full-text XML.*

- **A-local, using the real operator — quoted:** *"Offspring were generated with the **same mutation
  operation used in the evolutionary runs**."* Plus *"2,500 clones"* for robustness and *"10,000
  mutated clones"* for phenotypic variability.
- **B-within-run — quoted:** the axes of Fig 4C are *"the slopes of the lines of best fit of the
  percentage of offspring with higher fitness than the parent **after each environmental change over
  time**"*.
- **Replication — quoted:** *"Error bars show 95% CIs among 15 replicates"*, over 15 fitness-landscape
  pairs.
- **C — selection-side:** static versus variable environment, switching every 300 generations.
- **D — arm-level:** the predictor relationship is a correlation across the 15 landscape pairs, not a
  within-run lead-lag.

Petak is therefore **strictly stronger than the specimen on A and B, and properly replicated**, while
sharing the specimen's selection-side intervention.

## 5. Kounios et al. 2016 — the sibling with the representational ablation

*arXiv 1612.05955. Not a citer (it predates the specimen by four months); same lineage and same GRN
model. Verified by me from the retrieved PDF.*

- **C-mechanism, and it is a real on/off:** a **one-to-one G→P map** against an **evolving GRN**, with
  the mutation operator on `G` identical in both (*"a single randomly chosen trait of G is mutated
  every evolutionary time-step by adding to it μ1, drawn from a uniform distribution in the range
  ±0.1"*). Turning the developmental map off is turning off the machinery that biases variation.
- **B-within-run with real statistics:** *"the median fitness of the phenotypes found at the end of
  every microevolutionary episode … over 30 replicates"*, with min/max bands and Mann–Whitney U
  p-values.
- **A — global.** Its genuine accessibility quantity is the **developmental basin of attraction**,
  defined as *"the number of G vectors that map into the concentric squares phenotype"*, tracked over
  1600 evolutionary episodes (Fig 8). That is a pre-image size over the whole `G`-space, not a
  one-step neighbourhood.
- **The composition still is not assembled**, for one specific reason: **the basin detector is
  measured in a single unablated condition** (Fig 8 clamps `G` to the target and evolves only `B`),
  not inside the one-to-one-vs-GRN arms. In the ablated arms the longitudinal quantity **is the
  outcome** — fitness found per episode — so detector and acquisition are the same measurement.

## 6. What this does to HC-T01, stated plainly

Herakles's defensible claim was that nobody had composed a one-step offspring distribution with an
on/off ablation of a variation mechanism and a within-run acquisition link. **After this search that
claim is no longer accurate as stated.**

- **Tiso 2024 has all four elements**, qualified by a missing control arm and a descriptive `n = 1`
  link, and unpublished.
- **Petak 2025 has A-local + B-within-run published, with 15 replicates and confidence intervals**,
  under a selection-side intervention.
- **Kounios 2016 has C-mechanism + B-within-run + 30 replicates**, with a global accessibility
  detector run outside the arms.

The three of them, plus the unreported `computeM.m`, hold every ingredient HC-T01 claims is missing.
No single one holds all of them **quantitatively, in every arm including the control, with run-level
uncertainty, under an operator on/off**. So the cell is not empty in the way Herakles described; it
is empty only in the way a *rigour* cell is empty.

**Recommendation, per directive §17's instruction to prefer the strongest already-built microscope:**

1. **HC-T01's justification document must be rewritten** before it runs. Its `MISSING_CELL_CONFIRMED`
   and `MISSING_CELL_SUPPORTED` verdicts were reached against Toussaint's corpus and its
   descendants, screened before Tiso, Petak and Kounios were known to it. The verdicts are not
   overturned — they were about Toussaint's own programme, and that finding stands — but the wider
   claim in `COMPOSITION_SEARCH_REPORT.md` needs the narrowing this deliverable supplies.
2. **Steal Petak's detector rather than re-deriving one.** Sampling offspring with *the same mutation
   operation used in the evolutionary runs*, reported as the fraction of offspring fitter than the
   parent after each environmental change, is exactly the local longitudinal statistic HC-T01 needs,
   is published, and comes with a replication and CI convention already worked out.
3. **Steal Tiso's per-locus decomposition.** Sampling mutations *at each locus separately* localises
   the change in the variation machine to a site, which a whole-genotype offspring cloud cannot do.
   For Toussaint's string genome this maps onto per-position sampling directly.
4. **Score HC-T01 against Kounios's replication standard**, not against Toussaint's. Thirty
   replicates with a non-parametric test and min/max bands is the bar this lineage set in 2016;
   HC-T01's preregistered 30 run pairs with paired permutation meets it, and should say that it is
   meeting a historical bar rather than inventing one.

## 7. Documented access gaps

- **Rappeport & Nitzan 2026** — read as arXiv v1, not the PRX Life version of record.
- **Geoffroy & André 2021** — read as the bioRxiv preprint; Europe PMC returned an empty full text.
- **La Grove et al. 2021, Artificial Life** — MIT Press HTTP 403; recovered from an institutional
  mirror.
- **Bernatskiy 2018 dissertation** — PDF not located. Triaged out because the published version of
  his evolvability measure is a rate of adaptation, not a sampled distribution. **This is the one
  item in the union that was not read in full**, and it is recorded as a gap rather than a negative.
- **Kounios et al. 1612.05955** — no published version located; it exists as a preprint and as
  chapter 5 of the Kounios MPhil thesis.
