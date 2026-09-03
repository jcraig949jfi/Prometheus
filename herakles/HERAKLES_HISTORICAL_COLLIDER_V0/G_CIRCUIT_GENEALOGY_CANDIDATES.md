# G. CIRCUIT-GENEALOGY CANDIDATES

Historical sequences where earlier machinery appears necessary for later machinery. Each link is answered against the §11 questions with an evidence class. **Every entry below is `MODEL_RECALL_UNVERIFIED`.** No dependency claim here is established; each is a hypothesis with a stated test.

Evidence classes: `assoc` observed association · `seq` historical sequence · `pert` perturbation · `abl` ablation · `repl` replication · `mech` mechanistic proof.

---

## gen-01 — Duplication → neutral divergence → memory depth (Lindgren IPD)

```
genome doubling (neutral at creation)
  --seq--> redundant memory positions drift
    --?--> longer-memory strategy becomes one mutation away
      --?--> new dominant strategy era
```

- **Did later capability require earlier structure?** Unknown. The claim that memory-3 strategies are unreachable without a prior duplication is testable by forbidding duplication in a matched arm.
- **Was it useful when it appeared?** Believed no: duplication is phenotype-neutral at creation. This is the attraction.
- **Did it alter subsequent accessible mutations?** The central question. Measure the mutation-effect distribution of duplicated vs non-duplicated lineages at matched fitness.
- **Could later machinery arise without it?** Testable by the no-duplication arm.
- **Kill:** matched non-duplicated lineages reach the same strategy sophistication at the same rate.
- **Strength today:** `seq` at best. Nothing measured.

## gen-02 — Alignment → survivable duplication → complexification (NEAT)

```
historical markings (origin ids)
  --abl--> crossover stops destroying novel structure
    --assoc--> add-node/add-connection changes persist
      --assoc--> speciation shields them for k generations
        --?--> larger topologies become reachable
```

- **Required?** NEAT's own ablations (as recalled) show removing markings or speciation degrades performance. That is a contemporaneous-fitness claim, not a reachability claim.
- **Blindness:** no evolvability measurement; no measurement of whether protected structures changed the *descendant* acquisition rate.
- **Kill:** protection changes final fitness but not time-to-adaptation after an environment shift.

## gen-03 — Neutral drift → position on network → innovation (RNA relay series)

```
population diffuses on a neutral set (phenotype constant)
  --pert--> boundary of the neutral set contacts a new shape
    --repl--> transition occurs; new shape fixes
```

- **Required?** The relay-series construction (as recalled) shows the transition occurs from specific positions. Whether drift is *necessary* rather than incidental needs a control that pins the population to its entry point.
- **Distinguishing feature:** this is the cleanest historical instance of the §14 shape (performance flat, accessibility changed).
- **Kill:** transition probability independent of position on the neutral set.

## gen-04 — Reward scaffold → deleterious intermediate → complex feature (Avida EQU)

```
environment rewards sub-functions
  --abl--> intermediate structures retained
    --abl--> a deleterious mutation places the lineage one step from EQU
      --abl--> EQU appears
```

- **Status:** the strongest historical genealogy recalled, because the original team ran the ablations (reward removal; mutation reversion).
- **Use:** CALIBRATION, not excavation. If a Prometheus detector cannot flag the deleterious intermediate *before* EQU appears, without being told the outcome, the detector fails.
- **Risk:** the reward scaffold is designer-imposed; the genealogy may be a property of the experimenter, not of evolution.

## gen-05 — Environment coevolution → transfer → unreachable region (POET)

```
environments mutate alongside agents
  --pert--> a niche appears that is easy from a current agent
    --abl--> transfer moves that agent into it
      --pert--> a region direct optimisation fails to reach
```

- **Required?** The authors report direct optimisation failing on the same environments. Verify compute matching, n, and whether a curriculum baseline was run.
- **Kill:** matched-compute curriculum reaches the same regions.

---

## What is missing from all five

None of these genealogies has, as recalled:
1. a measurement of the descendant mutation-effect distribution before and after the precursor;
2. mass replay from the generation preceding the precursor;
3. a null arm that perturbs the same axis the statistic varies on;
4. an SE beside the dependency claim.

Those four absences are exactly the Herakles instrument. They are also the reason no row here may be promoted without SFE work.
