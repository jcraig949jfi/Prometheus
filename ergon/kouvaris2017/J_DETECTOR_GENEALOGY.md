# J. DETECTOR GENEALOGY — where the 2017 microscope came from

Directive §16: trace only the *direct* ancestors of the mechanism and detector. No general
literature review. Every attribution below is from the specimen's own reference list (article XML,
71 references) or from an explicit statement in its text.

**Headline: the "2017 microscope" is an assembly, and two of its three main parts are not from
evolutionary biology at all.**

---

## 1. The assembly

| Component | Taken from | Evidence |
|---|---|---|
| **The GRN model itself** — `P(t+1) = P(t) + τ1·σ(B·P(t)) − τ2·P(t)`, `B` evolving slowly relative to `G`, Hebbian character of the evolved `B` | **Watson, Wagner, Pavlicev, Weinreich & Mills 2014**, *The Evolution of Phenotypic Correlations and "Developmental Memory"*, Evolution 68(4) — ref [25] | S1: *"Following previous work [2]"* citing Watson 2014; the specimen cites [25] for the model, the fitness benefit form, and the combinatorial-recall interpretation |
| **The question** — can selection in varying environments produce a map that helps in *unseen* environments | **Parter, Kashtan & Alon 2008**, *Facilitated variation: how evolution learns from past environments to generalize to new environments*, PLOS Comput Biol — ref [34] | The specimen's framing question is Parter's title. Its class of *"modularly varying"* targets is Kashtan & Alon's construction |
| **The adaptation-rate assay** — freeze the evolved structure, re-evolve from random starts, count generations to target | **Parter et al. 2008** — ref [34] | The specimen says so explicitly: *"evolve a population to new selective environments and evaluate the evolved predisposition of the development system to produce suitable phenotypes for those environments (as per [34])"* |
| **Modularly varying environments** | **Kashtan & Alon 2005** [35]; **Kashtan, Noor & Alon 2007**, *Varying environments can speed up evolution* [36] | cited for the time-scale dependence of evolvability under environmental switching |
| **Benefit-minus-cost fitness** | **Kashtan, Mayo, Kalisky & Alon 2009**, *An analytically solvable model for rapid evolution of modular structure* — ref [64] | *"Following the framework used in [64], we define the fitness … as a benefit minus cost function"* |
| **Connection cost as a driver of modularity** | **Clune, Mouret & Lipson 2013**, *The evolutionary origins of modularity* — ref [27]; also [65]–[67] | the cost term on `b_ij` and its biological justification |
| **The L1/L2 regularisation analogy** | **Russell & Norvig** — ref [68] | the only source cited for the regularisation framing; a general AI textbook, not a biology paper |
| **THE ESTIMATOR** — "Classify and Count" | **Forman 2008**, *Quantifying counts and costs via classification*, Data Mining and Knowledge Discovery — ref [69] | Methods: *"we follow the Classify and Count (CC) approach [69]"*. This is a **machine-learning quantification** method, imported wholesale |
| **THE SAMPLER** — scrambled low-discrepancy sequences | **Galanti & Jung 1997** (Sobol, in a *finance* journal) — ref [70]; **Matoušek 1999**, *Geometric discrepancy* — ref [71] | Methods: *"low discrepancy quasi-random sequences (Sobol sequences; [70]) with Matousek's linear random scramble [71] were used to reduce the stochastic effects of the sampling process"*. Confirmed in code: `sobolset(M,'Skip',500,'Leap',0)` with `'MatousekAffineOwen'` |
| **The learning-theory framing** | **Watson et al. 2016**, *Evolutionary Connectionism* (recovered); Watson & Szathmáry's evolution-as-learning line | conceptual ancestor of the whole Table 1 mapping |

## 2. What this genealogy actually shows

**The detector's two hardest parts are borrowed from outside evolutionary biology.** The estimator is
Forman's classify-and-count from data mining; the sampler is Sobol quasi-random sequences with a
Matoušek affine-Owen scramble, cited from a derivatives-pricing paper and a discrepancy-theory
monograph. The evolutionary-biology ancestors supply the *model* (Watson 2014) and the *question and
assay* (Parter 2008) — not the measurement.

That is a genuinely useful observation for the Historical Collider. It means:

- the microscope was not incrementally refined over many evolutionary experiments; it was
  **assembled in one step by importing a variance-reduced quantification method** into a model
  inherited from a single direct ancestor;
- the reason nobody in this lineage built a *local* detector is not that the tooling was hard. The
  hard part — an unbiased, variance-reduced estimator of a phenotype distribution — was solved by
  import. Redirecting the same estimator at the one-step offspring cloud is a change of *where the
  sample comes from*, not a change of instrument;
- therefore **the missing composition is a design choice, not a capability gap** — which is exactly
  what `computeM.m` independently proves, since the same author did later point a local sampler at a
  population and simply never reported it. **And §4 makes this much stronger than a design choice:
  the direct ancestor had already built and PUBLISHED a local exhaustive detector in 2008, and the
  2017 paper replaced it with a global sample.**

## 3. What the ancestors did *not* have

Checked against the same four-element criterion, so the genealogy answers the redundancy question
backwards in time as well as forwards.

| Ancestor | A | B | C | D | Note |
|---|---|---|---|---|---|
| **Watson et al. 2014** [25] | its measured object is the evolved correlation structure of `B` and its recall behaviour, not a sampled offspring distribution | no longitudinal sampled distribution reported | environment structure, **selection-side** | developmental memory / recall | **ACCESS_BLOCKED** at Wiley; scored from its abstract and from the specimen's description of it, and tagged as such. It fails `C-mechanism` regardless of access, because its manipulation is the environment. |
| **Parter et al. 2008** [34] | **CORRECTED 2026-09-03 — see §4. It has an `A-local` detector: the fraction of `1-mutant` circuits preserving the wild-type phenotype, plus the modularity and the maximal G2 fitness of the `1-mutant` phenotypic neighbourhood. Genome is 104 bits, so the neighbourhood is enumerated EXHAUSTIVELY, not sampled.** It also has the adaptation-rate assay | see §4 — endpoint per arm on the evidence I verified; asserted longitudinal by Elenchus | FG / MVG / NBVG goal schedules: **selection-side** | yes, this is where the assay comes from | Supplies **both A-local and D**. My original row said it supplied D and not A. That was wrong. |
| **Kashtan & Alon 2005 / 2007 / 2009** | no sampled offspring distribution | no | environment structure and cost: **selection-side** | speed-up of evolution | Supplies the environment construction and the fitness form. |
| **Clune et al. 2013** [27] | no | no | connection cost: **selection-side** (a cost term in fitness) | modularity as outcome | Supplies the cost mechanism. |

**CORRECTION, 2026-09-03.** The sentence that stood here was wrong and is retracted. It read: *"Not
one direct ancestor manipulates a variation operator, and not one measures a one-step offspring
distribution longitudinally."* The first clause survives. **The second clause is false**, and §4
below records what actually happened and how the error was caught.

What survives: **not one direct ancestor manipulates a variation operator.** FG / MVG / NBVG are goal
schedules; connection cost is a fitness term; environmental switching is a schedule. `C-mechanism` is
absent from the entire ancestral line, which is consistent with the field having inherited its
interventions from the Kashtan/Alon modularly-varying-environments tradition, where the environment is
always the knob.

---

## 4. CORRECTION — the direct ancestor DID measure the one-step neighbourhood, and I missed its supplement

**How the error was caught.** By another seat, independently. Elenchus's Kashtan/Alon deep-dive
(`elenchus/kashtan-alon-mvg/`, commit `397dc307f`) recovered **Text S1 of Parter et al. 2008**, a
3,024,384-byte Word supplement with eleven sections, and reported that the 2008 paper measured the
adjacent possible. My pass recovered Parter 2008's article PDF and XML and **never fetched its
supporting information**, then asserted in this document that it had no `A` element. That assertion
was an inference from an incomplete recovery, which is exactly the failure this seat's own ledger is
supposed to prevent.

**Independently verified before accepting it.** I fetched Text S1 myself from the publisher
(`.s001`, `type=supplementary`) and my sha256 is `9fe6a4bab6718f799db1b315…`, which matches the hash
in Elenchus's ledger byte for byte. Two seats, two retrievals, one file. The quotes below are from
that file.

**What Parter et al. 2008 actually measured:**

- **`A-local`, and EXHAUSTIVE rather than sampled.** Text S1: *"Neutrality was defined as the fraction
  of 1-mutant circuits that compute the same Boolean function as the wild-type (G1)."* The logic-circuit
  genome is `B = 104` bits, so the one-mutant neighbourhood is 104 circuits and can be enumerated
  completely. There is no Monte-Carlo error at all. In the RNA model the same family of measures is
  tabulated: *"Fraction of 1-mutant neighborhood that preserves the wild-type phenotype / No. of
  different structures in 1-mutant neighborhood / Average structural distance in the 1-mutant
  neighborhood."*
- **More than one statistic over that neighbourhood.** *"Maximal fitness (mean ± SE) for G2 in the
  phenotypic neighborhood of evolved logic circuits"*; *"Averaged modularity (Qm) of genetic
  neighboring circuits"*; *"Number of modular and non-modular goals in the phenotypic neighborhood of
  evolved circuits."*
- **Population-level.** Genomes are *"sampled from the G1 neutral network"*; for the varying-goal arms,
  *"genomes are from the end of the last G1-epoch populations."*
- **In every arm, with uncertainty.** All three scenarios FG, MVG and NBVG, *"Mean ± SE is presented
  for each scenario"*, over *"30 simulations"* per scenario in the circuit model and 20 in the RNA
  model. **This is better statistical practice than either Toussaint or Kouvaris 2017 manages.**
- **`C-mechanism` still absent.** FG / MVG / NBVG differ in the *goal schedule*. The variation operator
  (`Pc`, `Pm = PT/B`) is held fixed across arms.

**Longitudinality: I record a disagreement rather than adopt a reading.** Elenchus's packet states the
measurement was made *"longitudinally"* and scores the paper `D4 (weak form)`. The sentences I read say
the opposite for the neighbourhood measures specifically — repeatedly, *"genomes from the end of the
last G1-epoch population were analyzed"*, which is an endpoint per arm. Text S1 does contain a section
titled *"8.2 Evolution of facilitated variation on a neutral network"* and a panel *"Evolution of
genetic triggers in NBVG evolution"*, so a longitudinal reading may rest on those; I have not verified
that either is the 1-mutant neighbourhood measure rather than a different quantity. **Unresolved, and
owed back to Elenchus** rather than settled here.

**What this does to HC-T01, and it is worse than anything else in this pass.** The specimen's own
direct ancestor, published in the same journal nine years earlier, had a **local, exhaustive,
population-level accessibility detector, run in all three arms, with standard errors over thirty
replicates.** Kouvaris 2017 then **replaced it with a uniform global sample**. On detector locality and
on statistical discipline the lineage did not merely fail to advance between 2008 and 2017 — **it
regressed**, and the regression is visible in the citation from the later paper to the earlier one.

The consequence for HC-T01's novelty claim is direct: the `A-local` element is not merely
buildable-but-unreported (as `computeM.m` showed); it was **built, published, run in all arms, and
reported with error bars, in 2008, by the specimen's own ancestor.** HC-T01's residual cell shrinks to
`C-mechanism` plus quantified `D-within-run`, and nothing else.

---

## 5. One correction to the programme's own record

Herakles's `DESCENDANTS_SCREENING_LOG.md` describes the specimen's sample as drawn *"uniformly over
the whole genotype hypercube as a drift approximation"* and its manipulation as *"selective pressure
rather than an operator switch"*. **Both are confirmed exactly**, from the Methods and from
`findErrors.m`. Herakles's screening of this paper was correct on the two facts that mattered, and
this pass upgrades them from screening-level to source-level with the code as an additional witness.

What Herakles's log did **not** have, and what changes the picture, is: the unreported `computeM.m`
local detector; the sibling Kounios paper with a representational ablation and 30 replicates; and the
two post-2017 descendants (Petak 2025, Tiso 2024) that between them hold every element HC-T01 claims
is missing. Those are in `K_DESCENDANT_SEARCH.md`.
