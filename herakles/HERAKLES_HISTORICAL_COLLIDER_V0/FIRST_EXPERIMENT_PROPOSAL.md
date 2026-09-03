# THE FIRST ARCHAEOLOGICAL EXPERIMENT — recommendation

**Recommended specimen: `spec-evca-density` — GA-evolved one-dimensional cellular automata for density classification (EvCA, Santa Fe Institute, 1993-1999; Mitchell, Crutchfield, Das, Hraber, Hordijk).**

Status: recommendation only. Nothing has been run, no source recovered, no primary source read. Every factual claim below is `MODEL_RECALL_UNVERIFIED` and must be verified before a line of code is written.

---

## Why this one, against the §28 preferences

| §28 preference | EvCA | Runner-up: Lindgren IPD | Runner-up: RNA relay |
|---|---|---|---|
| small physics | 128-bit rule table, 149-cell ring, ~300 steps. Smaller than almost anything else in the registry | smaller still | small but needs a folding library |
| surviving source | rule tables published in hex; EvCA package believed to have existed (VERIFY) | believed none | ViennaRNA survives, era parameters may not |
| surviving experimental description | GA parameters, lattice size, IC distribution all believed published | fully specified in print | protocol published |
| known lineage phenomenon | epochs of innovation; rare transition to particle-based strategies | duplication then divergence | relay series (explicitly a lineage) |
| affordable massive replication | 1e4-1e5 runs per CPU-day | even cheaper | cheap |
| meaningful detector blindness | six of eight blind-spot rows blind (see M) | six of six blind | **weak: the original detector was good** |
| causal counterfactual opportunity | mass replay from pre-epoch checkpoints; rule-bit ablation | no-duplication arm | position-pinning control |

EvCA wins on the combination of published artifacts to check a reconstruction against, and blindness on exactly the rows Prometheus cares about. Lindgren is cheaper and has the cleaner mechanism but no artifact to validate the rebuild. RNA is deliberately kept as runner-up because its strong original detector makes it the best place to discover that we add nothing.

**Anti-fame check (§18):** this is not the famous choice. Tierra and Avida are more cited. EvCA is chosen because its physics fits in a page and its interesting event is rare and seed-dependent, which is precisely what 1e4 replicates converts from anecdote to distribution.

---

## The three-stage shape (§19)

**Stage 1 — faithful physics, observation only.** Reimplement the GA and the CA exactly as specified. Pin seeds. Run 1e4 times. Single question: *does the transition to particle-based strategies recur, and at what rate with a confidence interval?* Compare against the originally reported rate. If the reconstruction cannot reproduce the original's reported outcome distribution, stop and report a reconstruction failure. That is a valid and useful ending.

**Stage 2 — add resolution, do not touch physics.** Emit into SFE: every genome every generation (not just elites), full lineage DAG, per-initial-condition failure classes, neutral-variant occupancy around the elite, first-divergence points between forks, content-addressed rule tables.

**Stage 3 — the question they could not afford.** Mass replay: fork 1e3 times from the generation immediately preceding each detected transition, and 1e3 times from a fitness-matched control generation with no subsequent transition. Measure the conditional probability of transition from each. Then ablate individual rule-table bits of the pre-transition elite and measure which ones the transition required.

**The Stage 3 question in one sentence:** was the pre-transition rule table *already special* in a way that changed what was reachable, or was the transition a coin flip that happened to land?

That question is answerable now for a few CPU-days and was economically impossible in 1996. It is also exactly the §1 primary question, instantiated on real historical physics.

---

## Pre-registered outcomes

Registered before any code exists, so that neither outcome can be rescued later:

- **HISTORICAL_PHENOMENON_RECURS** — transition rate in faithful reconstruction is within CI of the reported rate.
- **RECONSTRUCTION_FAILS** — it is not; the physics is underdetermined or our rebuild is wrong. Report which unspecified parameter is responsible.
- **CONTINGENT** — replay from pre-transition checkpoints yields a significantly higher transition rate than from fitness-matched controls. The precursor was special.
- **NOT_CONTINGENT** — the two replay sets are indistinguishable. The transition is a coin flip and `bump-evca-transition` dies.
- **NO_PARTICLE_STRATEGIES** — the transition does not occur at all in 1e4 runs. Either the reconstruction is wrong or the original result does not replicate; both need saying out loud.

The gate line for CONTINGENT will be computed from the SE of the replay-set difference **before** the replay runs, per standing Prometheus rule, and the attainable range checked so the gate can actually fire.

---

## The sixteen §25 answers

1. **What did the original researchers want to measure?** Whether a GA discovers CA rules that perform a global computation, and what computational strategy those rules embody.
2. **What did their experiment actually measure?** Best-of-generation fitness on sampled initial conditions, final rule tables, and hand computational-mechanics analysis of a few selected rules.
3. **What information did it discard?** Non-elite genomes, neutral variants, extinct lineages, per-initial-condition failures, seeds, and (believed) the trajectories of runs that never reached particle strategies.
4. **What phenomenon are we interested in that they were not measuring?** Whether the pre-transition rule table changed what was reachable, i.e. a change in the descendant search distribution rather than in fitness.
5. **What evidence suggests it may nevertheless have occurred?** The transition is reported as rare, seed-dependent and epochal, and three independent search physics (GA, GP, coevolution) reportedly found the same particle motif. Rare + epochal + convergent is the signature a contingent precursor would leave. TO VERIFY.
6. **What alternative mundane explanation exists?** The transition is a low-probability mutation with no precursor structure; epochs are drift; convergence across search methods reflects the task, not a reachability structure.
7. **Does original data survive?** Rule tables believed published. Run logs, populations and seeds: believed lost. TO VERIFY.
8. **Does source code survive?** An EvCA package is believed to have existed. TO VERIFY — this is the single highest-value unknown, because it decides REIMPLEMENTATION versus APPROXIMATE_RECONSTRUCTION.
9. **Can the physics be reconstructed?** Yes. The CA is unambiguous. The GA has parameters that may be underdetermined; each will be enumerated and given variants.
10. **What would SFE record that the original system did not?** Full population per generation, lineage DAG, neutral occupancy, per-initial-condition failure classes, fork divergence points, ablation results, content-addressed rule identity.
11. **What would 10,000x replication buy?** Transition rate with a CI instead of an anecdote; seed-versus-initialisation variance decomposition; the conditional probability of transition given ancestral structure; the false-positive rate of epoch-like fitness jumps with no strategy change.
12. **What counterfactual becomes possible now?** Blount-style mass replay from pre-transition checkpoints against fitness-matched controls.
13. **What ablation would most strongly test it?** Bit-level ablation of the pre-transition elite rule table, measuring which entries the subsequent transition required.
14. **Which recovered part does this specimen contain?** `part-particle-computation`, `part-epochal-innovation`; candidate presence of `part-neutral-drift-precursor`.
15. **What other historical part might compose with it?** `part-cross-context-transfer` (comp-05: do particle rules transfer to a second task?), and `part-innovation-protection` (would protection raise the transition rate?).
16. **What observation would kill our interest immediately?** Replay from pre-transition checkpoints is statistically indistinguishable from fitness-matched controls. The precursor is then not special, and the specimen drops out of the programme.

---

## What must happen before any code is written

1. Read the primary sources and fix the GA parameters, initial-condition distribution, run count and reported transition rate.
2. Hunt for the EvCA source and any surviving rule tables; hash whatever is recovered into manifest J.
3. Write the physics sheet with every unspecified parameter enumerated; fix the provenance class.
4. Compute the SE and attainable range for the CONTINGENT gate.
5. Send the SFE world proposal to Daedalus, and the pre-registration to Elenchus for an independent failure mode.
