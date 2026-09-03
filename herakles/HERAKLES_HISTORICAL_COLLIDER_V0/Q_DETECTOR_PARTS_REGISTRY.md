# Q. DETECTOR PARTS REGISTRY

**Authorised 2026-09-03** by ruling `roles/Herakles/prompts/RULING_V0_CONTINUE_HYPOTHESIS_DAMAGED_2026-09-03.txt` (sha256 `31816dc2…0811a`), authorisation 2: *"Add DETECTOR_PARTS_REGISTRY as a first-class artifact equal to the computational-parts registry."*

This extends the directive's A–P deliverable set with a seventeenth letter. It is not a subordinate index; it is the second half of parts archaeology.

---

## The two kinds of part

The V0 parts registry (`E_PARTS_REGISTRY.jsonl`) conflated two categories that need separating.

**Mechanism parts — things evolution uses.** Duplication, neutral traversal, modularity, hierarchy, robustness, developmental encoding, innovation protection, niche construction. These are candidate components of a synthetic reasoning or evolvability machine. They live in E.

**Detector parts — things scientists invented in order to see mechanism parts.** Price covariance measures, offspring-cloud diversity, neutral-network topology, mutation-effect distributions, line-of-descent reconstruction, evolutionary activity statistics, accessibility measures. They live here, in Q.

The operating insight behind this split, in the ruling's words:

> We entered thinking "perhaps nobody built the microscope." The evidence is already saying: lots of microscopes were built. They were pointed at different things, at different scales, in different disciplines, and rarely assembled into one instrument.

**Assembling proven detector parts is much easier than inventing every detector from scratch.** So the seat's job on this axis is recovery and composition, not invention. Standing consequence: **no Prometheus-native measure may be invented for a quantity until this registry records whether the field already has a better-developed one.**

---

## The D-ladder: the classification every detector part carries

The hypothesis that replaces the dead one, stated so it can die cleanly:

> Across historically important adaptive-computation experiments, how often was the local offspring / reachable distribution measured **repeatedly across population lineages**, in a way that permits changes in future accessibility to be reconstructed over evolutionary time?

| Level | Definition |
|---|---|
| **D0** | No accessibility measure. Only state variables: fitness, complexity, diversity. |
| **D1** | Accessibility measured for **selected individuals** only. |
| **D2** | Accessibility measured **population-wide**, at **snapshots**. |
| **D3** | **Longitudinal** population accessibility: measured repeatedly over evolutionary time, so change is reconstructable. |
| **D4** | Longitudinal accessibility **plus the subsequent acquisition outcome**: did the change predict what was later acquired? |
| **D5** | **Causal perturbation** showing that a change in accessibility altered future acquisition. |

The standing bet, recorded so it can be scored later: plenty of D1 and D2; possibly much more D3 than currently realised; very little clean D4 or D5.

**That is a bet, not a finding.** The prior that produced the dead hypothesis was badly calibrated, so this one is held loosely and is being actively attacked. A D-level survey is in flight; results land in this file, and no historical-blindness claim may be made until it completes (ruling authorisation 1).

---

## Registry entries

Each detector part carries: `detector_id`, historical name, inventor and date, **what quantity it computes**, what it can see, **what it cannot see**, D-level, substrate requirements, cost, composability notes, evidence tier, locators.

### det-part-01 — Price covariance decomposition of the offspring distribution

- **Origin:** Altenberg 1994, *Advances in Genetic Programming* ch.3, Theorems 3 and 4. Building on Price 1970.
- **Quantity:** Theorem 3 decomposes the probability that a population produces offspring fitter than any existing individual into a *search-bias* term (excess over random search) plus a *parent-offspring regression* term scaled by fitness variance. Theorem 4 gives a rate law: evolvability increases at a rate proportional to the variance in the constructional fitnesses of a program's blocks.
- **Sees:** the direction and rate of change of evolvability, as a function of representation and operator, analytically.
- **Cannot see:** anything empirical here. It is theory plus a deliberately simplified model (hill-climbing; blocks added but never deleted or disrupted; constructional fitness assumed constant). The search-bias term is defined against a random-search reference and is not directly computable for a real system. The rate constant decays as programs grow.
- **D-level:** the formalism *targets* D3–D5; the 1994 chapter itself performs **no measurement**, and Altenberg wrote that the quantity *"should be possible to measure in GP runs"* with tests *"currently under way"*.
- **Why it matters most:** this is simultaneously a detector part and a candidate **mechanism** part. See the crossover note below.
- **Evidence:** `PRIMARY_SOURCE_READ`, `dynamics.org/Altenberg/FILES/LeeEEGP.pdf`.

### det-part-02 — Offspring-cloud behavioural diversity

- **Origin:** Mengistu, Lehman & Clune, GECCO 2016 pp.141-148. Measure inherited from Lehman & Stanley 2011 and 2013, and Velez & Clune 2014.
- **Quantity:** generate 200 offspring of an individual, discard them, count how many are behaviourally distinct above a distance threshold of 0.01.
- **Sees:** the size of the one-step reachable behavioural neighbourhood, independent of fitness.
- **Cannot see:** the *shape* of the mutational-effect distribution (it is a scalar count at a threshold); anything beyond one mutation step; the difference between one far-wandering offspring and broad coverage, since the transfer metric is a union over the offspring cloud; and change over a lineage unless deliberately re-measured, which the paper does per treatment but not per lineage.
- **D-level:** **D2 by construction, D3 in one usage** (evolvability tracked every 100 generations across treatments). Not D4 or D5 on the lineage question.
- **Cost:** 200 extra evaluations per individual measured. This is the dominant cost and the reason it is not run population-wide every generation.
- **Evidence:** `PRIMARY_SOURCE_READ`, GECCO 2016 proceedings PDF.

### det-part-03 — Reachable-genome enumeration

- **Origin:** Lehman & Stanley 2013, PLoS ONE 8(4):e62186.
- **Quantity:** enumerate all genomes reachable by every possible single-connection mutation, then count the unique behavioural niches they encode.
- **Sees:** exact one-step reachability, without sampling error.
- **Cannot see:** anything beyond one step; anything in a representation where the one-step neighbourhood is too large to enumerate.
- **D-level:** D1–D2 depending on how many individuals are enumerated.
- **Composability note:** this is the exact-enumeration counterpart of det-part-02's sampling estimator. Where both are affordable, running them together calibrates the sampling error of the cheaper one. **That is a composition nobody appears to have needed, and it is nearly free.**
- **Evidence:** `PRIMARY_SOURCE_READ`.

### det-part-04 — Line-of-descent reconstruction

- **Origin:** Avida lineage tooling; Lenski, Ofria, Pennock & Adami 2003 and successors. Related: Burlacu, Kronberger & Affenzeller genealogy tools in genetic programming.
- **Quantity:** the complete mutational path from ancestor to a focal descendant, with fitness and phenotype at every step.
- **Sees:** everything that happened on the winning lineage, including deleterious steps later required.
- **Cannot see:** **the population that did not win.** This is the sharpest known blindness in the registry: it conditions on success, so it cannot supply the base rate of the same precursor arising and leading nowhere. Without that base rate, "stepping stone" is a survivorship description.
- **D-level:** D1 with respect to accessibility, even though the lineage itself is longitudinal. It records what *did* happen, not what *could* have.
- **Composability note:** line-of-descent plus mass replay from checkpoints converts D1 into D5. This is the single most valuable composition currently identified, and it is what the first archaeological experiment is designed to perform.
- **Evidence:** `MODEL_RECALL_UNVERIFIED` pending the Avida deep-dive.

### det-part-05 — Evolutionary activity statistics with a neutral shadow

- **Origin:** Bedau & Packard, roughly 1992-1998; Bedau, Snyder & Packard 1998 classification of long-term dynamics.
- **Quantity:** cumulative usage/persistence of components, compared against a neutral-model shadow population to subtract what drift alone would produce.
- **Sees:** whether adaptive novelty is being *retained* and accumulated, population-wide and longitudinally.
- **Cannot see:** **accessibility.** This is an activity and persistence measure, not a reachability measure. It answers "what has been used and survived", not "what could be reached from here".
- **D-level:** provisionally **D0 on the accessibility axis**, despite being longitudinal and population-wide on its own axis. **This is the classification most likely to be wrong** and is flagged for the survey in flight.
- **Why it is in the registry anyway:** the *neutral shadow* is a detector part in its own right and is separable from the activity statistic. A shadow population that isolates what drift alone produces is directly reusable as a null arm for any accessibility measure.
- **Evidence:** `MODEL_RECALL_UNVERIFIED`.

### det-part-06 — Neutral-network / genotype-network topology

- **Origin:** Schuster, Fontana, Stadler, Hofacker on RNA; A. Wagner on genotype networks; Hu, Banzhaf, Ochoa, Payne on phenotype networks in linear genetic programming.
- **Quantity:** the connectivity structure of the set of genotypes mapping to one phenotype, and the set of phenotypes accessible from its boundary.
- **Sees:** which innovations are adjacent to which neutral sets; a structural upper bound on what selection can ever reach.
- **Cannot see:** whether an *evolving population* actually occupies the parts of the network that matter, unless a population is tracked on it.
- **D-level:** typically D2 as usually reported, because it characterises a static structure rather than a population trajectory. Becomes D3 when a population's occupancy is tracked over time.
- **Evidence:** `MODEL_RECALL_UNVERIFIED` pending the survey.

### det-part-07 — Mutation-effect distribution

- **Origin:** distributed across population genetics and digital evolution; no single inventor.
- **Quantity:** the distribution of fitness or phenotype changes over sampled mutations of a genome.
- **Sees:** the full shape that det-part-02 compresses to a scalar.
- **Cannot see:** effects requiring more than the sampled number of steps; interactions between mutations unless multi-step sampling is added.
- **D-level:** anywhere from D1 to D3 depending on sampling design. **This is the quantity the seat was about to reinvent**, and the reason this registry exists.
- **Evidence:** `MODEL_RECALL_UNVERIFIED`.

### det-part-08 — Mass replay from checkpoints

- **Origin:** the biological long-term evolution experiment's frozen fossil record and the citrate replay experiments; conceptually available in any deterministic simulator with checkpointing.
- **Quantity:** the conditional probability of a subsequent innovation, estimated by re-running many times from a saved state.
- **Sees:** contingency directly. It is the only part in this registry that can reach **D5** on its own.
- **Cannot see:** anything, without checkpoints and a deterministic or seed-controlled substrate.
- **Historical availability:** economically impossible at scale for every specimen profiled so far, which is the seat's genuine leverage. Note this is a claim about *cost*, not about *conception*: the technique was understood.
- **Evidence:** `MODEL_RECALL_UNVERIFIED` on the specific historical instances.

---

## The crossover: when a detector part is also a mechanism part

`det-part-01` is the important case, and the ruling identifies it precisely.

Altenberg's constructional fitness describes subexpressions that proliferate **because of their propensity to produce beneficial variation**, not because of their current fitness contribution. Restated as causal computation:

```
structure X appears
  -> X changes the offspring distribution
    -> descendants have altered probability of useful variation
      -> X is selected BECAUSE of that second-order effect
```

That is candidate machinery for the evolution of evolvability: not reasoning, not intelligence, but plausibly one of the parts below the threshold this programme is hunting. It therefore has an entry in **both** registries: here as a measurement formalism, and in `E_PARTS_REGISTRY.jsonl` under `part-structural-duplication`, whose theoretical rate law it supplies.

The question the ruling directs at it, which becomes a specimen family rather than a single row:

> What exactly was Altenberg able to demonstrate theoretically, what was subsequently demonstrated empirically, and what portions of that mechanism have never been instrumented longitudinally?

---

## The positive-control insight

The ruling's sharpest instrument-design observation concerns Mengistu and colleagues, and it is recorded here because it determines how detector parts feed the prospective instrument.

**They reward evolvability directly. Prometheus ultimately must not.** The target is a world in which evolvability becomes advantageous through downstream consequences, with no evolvability term appearing anywhere in the world physics.

That makes their work two things at once: a historical detector, and a **positive control**. The resulting design, which belongs to Daedalus:

1. Build a treatment in which evolvability is deliberately rewarded, reproducing something of the 2016 shape.
2. Verify that Prometheus instruments detect the machinery that arises. A detector that misses it under direct reward is broken and must be fixed or killed before anything subtler is attempted.
3. Remove the direct reward and ask whether comparable machinery arises endogenously.

Step 2 is the calibration this seat owes the pantheon, and it is stronger than any of the calibration particles currently in `H_CALIBRATION_PARTICLES.md`, because the phenomenon is manufactured on demand rather than hoped for.

---

## Standing rules for this registry

1. **No invented measure before a recovery check.** Any Prometheus-native quantity must first be checked against this registry for a better-developed predecessor.
2. **Every entry states what it cannot see.** An entry without a blindness clause is incomplete.
3. **Every entry carries a D-level with its justification**, and the level is a claim about the *usage reported in the source*, not about what the measure could in principle support. Where those differ, say both.
4. **Composability is the point.** Record which parts calibrate, bound, or complete each other. The programme's bet is that the collider is assembled from existing detector parts, not invented.
