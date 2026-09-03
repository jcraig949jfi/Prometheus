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
  population and simply never reported it.

## 3. What the ancestors did *not* have

Checked against the same four-element criterion, so the genealogy answers the redundancy question
backwards in time as well as forwards.

| Ancestor | A | B | C | D | Note |
|---|---|---|---|---|---|
| **Watson et al. 2014** [25] | its measured object is the evolved correlation structure of `B` and its recall behaviour, not a sampled offspring distribution | no longitudinal sampled distribution reported | environment structure, **selection-side** | developmental memory / recall | **ACCESS_BLOCKED** at Wiley; scored from its abstract and from the specimen's description of it, and tagged as such. It fails `C-mechanism` regardless of access, because its manipulation is the environment. |
| **Parter et al. 2008** [34] | recovered in full (PDF + XML). Its evolvability measure is the **adaptation-rate assay** — generations to reach new goals — not a sampled variation distribution | no | modularly varying vs fixed environment: **selection-side** | yes, this is where the assay comes from | Supplies D, not A. |
| **Kashtan & Alon 2005 / 2007 / 2009** | no sampled offspring distribution | no | environment structure and cost: **selection-side** | speed-up of evolution | Supplies the environment construction and the fitness form. |
| **Clune et al. 2013** [27] | no | no | connection cost: **selection-side** (a cost term in fitness) | modularity as outcome | Supplies the cost mechanism. |

**Not one direct ancestor manipulates a variation operator, and not one measures a one-step offspring
distribution longitudinally.** So the backward search does not fill HC-T01's cell either. The
`C-mechanism` element is absent from the entire ancestral line, which is consistent with the field
having inherited its interventions from the Kashtan/Alon modularly-varying-environments tradition,
where the environment is always the knob.

## 4. One correction to the programme's own record

Herakles's `DESCENDANTS_SCREENING_LOG.md` describes the specimen's sample as drawn *"uniformly over
the whole genotype hypercube as a drift approximation"* and its manipulation as *"selective pressure
rather than an operator switch"*. **Both are confirmed exactly**, from the Methods and from
`findErrors.m`. Herakles's screening of this paper was correct on the two facts that mattered, and
this pass upgrades them from screening-level to source-level with the code as an additional witness.

What Herakles's log did **not** have, and what changes the picture, is: the unreported `computeM.m`
local detector; the sibling Kounios paper with a representational ablation and 30 replicates; and the
two post-2017 descendants (Petak 2025, Tiso 2024) that between them hold every element HC-T01 claims
is missing. Those are in `K_DESCENDANT_SEARCH.md`.
