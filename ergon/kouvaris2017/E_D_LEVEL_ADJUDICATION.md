# E. D-LEVEL ADJUDICATION — Kouvaris et al. 2017

**VERDICT (directive §0, exactly one): `KOUVARIS_STRONGER_BUT_DIFFERENT`**

Stated precisely, because the label alone is too blunt:

> Kouvaris 2017 reaches **D3 outright and D4 at arm level**, which is higher than anything in
> Herakles's Toussaint corpus. It does **not** reach D5. It is a **stronger experiment than HC-T01
> proposes on three axes** — its intervention is not tautological, it has a real train/test split
> over environments, and its acquisition outcome includes unreachability rather than only speed —
> and a **weaker one on statistical discipline**, since it reports no replication and no uncertainty
> on any longitudinal figure. It is **a different experiment** from HC-T01 on all three of the
> refinements that define HC-T01: the detector is global rather than one-step-local, the
> intervention is on selection rather than on the variation operator, and the acquisition link is
> made at arm level after evolution rather than within runs.
>
> `HC_T01_HISTORICALLY_REDUNDANT` is **refused**, and §5 below lists the FIVE ways this pass
> nonetheless damages HC-T01 — the fifth added 2026-09-03 after another seat caught an error in my
> own genealogy, and it is the most damaging of the five.

---

## 1. Why not each of the other five verdicts

| Verdict | Why refused |
|---|---|
| `HC_T01_HISTORICALLY_REDUNDANT` | Kouvaris satisfies **none** of A-local, C-mechanism, D-within-run. Directive §7 asks whether the paper "actually satisfies" the one-step / operator-ablation / within-run statement. It satisfies no clause of it. |
| `KOUVARIS_NOT_D4_D5` | Half-wrong, and I will not sign a half-wrong label. D4 as the directive defines it — *"longitudinal accessibility plus subsequent acquisition outcome"* — **is** met: Fig 3 is the longitudinal accessibility trajectory, Fig 5 is the subsequent acquisition outcome, and both are present per arm. Only D5 fails. |
| `KOUVARIS_COMPLEMENTARY` | True but weaker than the evidence supports, and it buries the finding that matters. Complementarity is a *consequence* (recorded in `M_CANDIDATE_COMPUTATIONAL_PARTS.jsonl` and §19 of the review packet), not the headline. The headline is that on the axes the two experiments share, the 2017 design is the better one, and HC-T01 has to be re-justified against it. |
| `MORE_ARCHAEOLOGY_REQUIRED` | Refused **for the specimen**, on evidence: its article, its complete supporting information, the preprint, the author's PhD thesis and **the author's own source code** were all recovered and hashed. The one access gap (Watson 2014) is not load-bearing. **But note what §5 item 5 records: more archaeology WAS required on an ANCESTOR, I did not do it, and another seat caught it.** That does not change a cell of the specimen's matrix; it changed a genealogy claim and it sharpened the HC-T01 conclusion. |
| `SPECIMEN_NOT_RECONSTRUCTABLE` | Refused. The developmental equations, class construction, training set, fitness form, all four intervention values and the detector are exact. Seven ambiguities exist (`C_HISTORICAL_PHYSICS_SPEC.md` §10) and three are code-versus-paper contradictions, but a reconstruction can enumerate them; none blocks a rebuild. |

## 2. A noun problem that has to be fixed before the ladder is applied

The D-ladder says "population-wide" at D2 and "population" at D3. **This specimen has no population.**
It is a single genotype `[G, B]` under strong-selection-weak-mutation, explicitly chosen so the
result *"does not require lineage-level selection"*. There is no standing variation, so there is
nothing population-wide to measure.

I therefore read the ladder's intent — *how much of the accessible set is being characterised, and
when* — rather than its letter, and say so rather than quietly awarding a rung. Under that reading
the specimen's detector is **broader than population-wide**: it samples the entire embryonic
genotype space, not the states a population actually occupies. That is a different failure mode from
D1's "selected individuals only", and it is worth naming: **the detector over-covers**. It measures
what the map *can* express from anywhere, including regions the lineage will never visit.

## 3. The ladder, mapped to explicit evidence

| Rung | Criterion | Verdict | Evidence, and what it does not support |
|---|---|---|---|
| **D0** | no accessibility measure | **exceeded** | An accessibility measure exists and is the centre of the paper. |
| **D1** | selected individuals only | **exceeded** | The measure is not confined to the evolved genotype; it is over sampled genotype space. |
| **D2** | population-wide snapshot accessibility | **ACHIEVED**, with the noun corrected | Methods, *Estimating the empirical distributions*: 5000 Sobol points uniform in `[−1,1]^16`, each developed through the current `B`, binned by sign, counted. Fig 2 shows the snapshot per arm. |
| **D3** | longitudinal population accessibility | **ACHIEVED** | Fig 3, training and test χ² error against evolutionary time, one panel per arm. S1 Fig B, the pictorial distribution across epochs. S1 Fig D, Shannon entropy against time (16 → 4 bits). Code: `findErrors.m` loops over the stored `outB` trajectory. **Qualified:** no replication and no uncertainty are reported for any of these, and `GRN.m` contains no replicate loop. The trajectory is a trajectory; it is not an estimate with an interval. |
| **D4** | longitudinal accessibility **plus** subsequent acquisition outcome | **ACHIEVED AT ARM LEVEL** | Fig 5: evolved `B` frozen, `G` re-randomised, `G` evolved 2500 generations, generations-to-target recorded, 1000 runs per environment per arm, all 8 class members including the 5 never selected. Both objects exist, in the same paper, over the same four arms. **Qualified:** the pairing is arm-to-arm, endpoint-to-endpoint. No point on the Fig 3 trajectory is ever related to an acquisition measurement taken later in the same run. |
| **D5** | causal intervention demonstrating that an accessibility **change** alters subsequent acquisition | **NOT ACHIEVED** | Three independent reasons, below. |

## 4. Why D5 fails — three reasons, each sufficient

**(a) No mediation is identified.** The interventions (`K`, `κ`, `λ_L1`, `λ_L2`) change the fitness
function or the environment. Those change `B`. Both the accessibility measure and the acquisition
measure are then read off `B`. The design supports `intervention → B → {accessibility, acquisition}`
and nothing more. It cannot separate "the accessibility change caused the acquisition change" from
"the change in `B` caused both". No arm holds accessibility fixed while varying something else, and
no arm perturbs accessibility directly.

**(b) The two readouts are functionals of the same frozen object, so the link is close to
definitional.** Given a frozen `B`, the detector is the push-forward of the uniform measure on
`G`-space through `develop(·, B)`; the acquisition assay is a hill-climb over the same `G`-space
through the same `develop(·, B)`. If `B` cannot express phenotype `s` from anywhere, hill-climbing
under `B` will not reach `s` either — the censored outliers in Fig 5 are exactly the phenotypes
missing from the Fig 2 distributions, and the paper says so: *"The outliers … indicate the inability
of the developmental system to express the target phenotypic pattern … This corresponds to the
missing phenotype from the class we saw above in the evolved phenotypic distributions."* That
sentence is the paper correctly noticing that its two measurements agree; it is not evidence that one
caused the other. **This is the same hazard Herakles preregistered as TRAP 2 for Toussaint. Finding
it here as well means it is a property of this whole experimental family, not a Toussaint defect.**

**(c) There is no run-level uncertainty to support a causal claim.** With the number of evolutionary
replicates unstated and the code showing no replicate loop, the between-arm difference in the
longitudinal detector has no error term. A causal claim needs one.

## 5. What this pass does to HC-T01 — five ways it is damaged, stated without hedging

The directive said not to protect HC-T01. These are the findings that count against it.

1. **Kouvaris's intervention is non-tautological and HC-T01's is not.** All four Kouvaris knobs act
   on the fitness function and never touch the variation operator, so 100% of the detector's
   movement is an evolved response. HC-T01's `β` *is* the rate of second-type mutations, i.e. a
   parameter of the operator that induces the exploration distribution, which Herakles's own
   preregistration declares makes "the arms differ on the detector" **true by construction** and
   forces a mechanical-effect null. On the cleanliness of the intervention, the 2017 design is
   simply better, and HC-T01 cannot claim otherwise.
2. **An `A-local` detector already existed in this lineage's code and was never reported.**
   `computeM.m` (300 single mutations per individual, population-wide, mutation draws frozen and
   shared across replicates) computes mutational variance and correlations from one-step mutants of
   real individuals. It appears in **no** publication and **zero** times in 159 thesis pages. So the
   one-step offspring detector is not an instrument the field lacked the capability to build. HC-T01's
   novelty is a **reporting and composition** novelty, not an instrument novelty, and it should stop
   being described as the latter.
3. **HC-T01 has no held-out environment set.** Kouvaris has a genuine train/test split defined by
   construction (3 training targets, 8-member structural class) and can therefore say what
   "generalisation" means without argument. Toussaint's Experiment 2 acquires a single structured
   target. On the acquisition construct, the 2017 design is again the stronger one.
4. **A sibling paper in the same lineage is closer to HC-T01 than the specimen is, and HC-T01 was
   never justified against it.** Kounios et al. (arXiv 1612.05955) ablate the **representation
   itself** — a one-to-one G→P map against an evolving GRN, with the mutation operator on `G` held
   identical — measure the outcome longitudinally **within runs** across both arms, over **30
   replicates** with min/max bands and Mann–Whitney U tests, and separately track a genuine
   accessibility quantity over evolutionary time (**the developmental basin of attraction**, the
   number of `G` vectors mapping to a target phenotype, Fig 8). That is `C-mechanism` = YES,
   `B-within-run` = YES, `D-within-run` = YES, and it is properly replicated. **HC-T01's missing-cell
   argument was built against Toussaint's corpus and its descendants; it has not been tested against
   this.** See `K_DESCENDANT_SEARCH.md` for the full scoring and for what Kounios still lacks.

5. **The specimen's own direct ancestor had a LOCAL accessibility detector, published, in all arms,
   with standard errors — nine years earlier — and the 2017 paper replaced it with a global sample.**
   Added 2026-09-03 after Elenchus recovered Parter et al. 2008's Text S1, which this pass had failed
   to fetch. Text S1 defines neutrality as *"the fraction of 1-mutant circuits that compute the same
   Boolean function as the wild-type"*, over a 104-bit genome, so the one-mutant neighbourhood is
   enumerated **exhaustively** rather than sampled; it also reports *"Maximal fitness (mean ± SE) for
   G2 in the phenotypic neighborhood of evolved logic circuits"* and the modularity of neighbouring
   circuits, across **all three** arms (FG / MVG / NBVG), *"Mean ± SE … for each scenario"*, over 30
   simulations. Its arms are still goal schedules, so `C-mechanism` remains absent. But on **detector
   locality** and on **statistical discipline** the lineage did not stall between 2008 and 2017 — **it
   regressed**, and it regressed while citing the earlier paper.
   Consequence: `A-local` is not merely buildable-but-unreported, as `computeM.m` showed. It was
   **built, published, run in every arm, and reported with error bars in 2008**. HC-T01's residual
   novelty shrinks accordingly, to `C-mechanism` plus a quantified within-run acquisition link, and
   nothing else. Full detail and a recorded disagreement with Elenchus about whether the 2008
   measurement was longitudinal: `J_DETECTOR_GENEALOGY.md` §4.

## 6. What survives for HC-T01

After all four, the cell HC-T01 targets is still empty, and the reason is narrow and specific:

- Kouvaris 2017 measures accessibility longitudinally in all arms but **globally**, under a
  **selection-side** intervention, with acquisition **at arm level**.
- Kounios 2016 has the **representational ablation**, **within-run** longitudinal outcome and proper
  replication, but its longitudinal quantity in the ablated arms **is the outcome itself**, and its
  one genuine accessibility detector (basin size) is **global** and is run in **one unablated
  condition only**, not inside the arms.
- The unreported `computeM.m` has the **local** detector, population-wide and same-probe, but it is
  **endpoint-only**, never longitudinal, and never inside an operator ablation.

- **Parter et al. 2008** has the **local, exhaustive** detector, **in all arms, with SE over 30
  replicates** — but its arms are goal schedules, not a mechanism ablation, and on the evidence I
  verified its neighbourhood measures are endpoint-per-arm.

So the surviving gap is now only this: a **local** accessibility detector, run **inside all arms of a
MECHANISM ablation** (not a goal schedule), related to acquisition **within runs and quantitatively**.
Every other ingredient has been built, and most of them published. That is far narrower than "nobody
has measured accessibility longitudinally under an intervention", and narrower than Herakles's own
statement, which did not know about Kounios 2016, `computeM.m`, Petak 2025, Tiso 2024, or Parter 2008's
Text S1.

## 7. The honest answer to directive §25

> *If Prometheus had existed in April 2017 and had been handed the complete Kouvaris experiment,
> what important question about changes in future computational accessibility would still have
> remained unanswered?*

Not `NONE`. Specifically, and in the order that matters:

1. **Does the change in what is reachable *from where the lineage actually stands* track the change
   in what the map can express from anywhere?** Kouvaris measures only the second. In this very
   model the one-step neighbourhood of `G` is a perturbation of ≤0.1 on one of sixteen coordinates —
   a vanishing fraction of the cube the detector samples. The two can move independently and the
   paper contains nothing that would detect it if they did.
2. **Is the accessibility change a cause of the acquisition change, or a co-symptom of the same
   change in `B`?** The design cannot tell, and both readouts are functionals of the same frozen
   matrix.
3. **Does any of it exceed the noise of a single run?** No replication was reported, so the size of
   the effect relative to run-to-run variation is unknown.

Question 2 is the one Prometheus most wants answered and is the hardest; question 1 is the one HC-T01
actually proposes to answer; question 3 is cheap and is the one a reconstruction settles first.
