# Alien lenses: bounded probes

Aporia inference harvest, 2026-09-30. No fleet authority. These are candidate probes
only. None is assigned, and none asks for a new engine. Under CWO-2026-09-30C, any of
them becomes work only if the operator or an owning seat takes it up through normal
dispatch.

Every probe uses existing engines or archived logs. Each has a frozen falsifier and a
guard against relabeling, meaning a guard against calling a known thing new.

Each lens lists:
- **Attacks:** the blind spot it targets (see CONVERGENT_BLIND_SPOTS.md);
- **Cannot see now:** what current systems cannot see;
- **Probe:** a minimal probe;
- **Falsifier;**
- **Relabeling guard:** how a genuinely new signal is told apart from a relabeled one.

---

## L1. Memorylessness: the accumulation null

**Attacks.** B3 and assumptions A1/A2. Tests rival ontology O1.

**Cannot see now.** Whether search history carries any advantage.

**Probe.** Uses existing run logs only: NPE soups, Archaeon SFE, PTE GA, BEE multi-day,
Tyche.
1. Extract time-to-first-competence (or first-event) per run, under a single frozen
   competence definition for each engine.
2. Fit geometric vs increasing-hazard models.
3. Compute the conditional hazard given "was within 1 edit / 0.1 score of competence at
   time t" vs not.
4. Separately, where logs allow, compare against the neutral-walk arm at the same
   mutation operator (NPE pilot data exists).

**Falsifier (of O1).** An increasing hazard, or a conditional-hazard ratio > 1 with a
bootstrap CI excluding 1, in at least 2 engines, means something accumulates.

**Relabeling guard.**
- Competence definitions are frozen before extraction.
- Runs are censored at budget, not dropped.
- A "near-competence" covariate that is itself the definition of competence at a lower
  threshold is excluded. The C3 failure mode is restating the definition.

**Cost.** Hours of CPU, no new runs.

---

## L2. Fixed-point census of the rewrite map

**Attacks.** B5 and A3. Tests O2.

**Cannot see now.** Whether "replicators" and painters are properties of the physics,
independent of selection and history.

**Probe.**
1. For 3 NPE/BEE cells, run the world's write physics and mutation on 1,000 random
   tapes with selection and fitness off, at the same budget.
2. Cluster the end-state contents by exact content classes: homopolymer, period-k, and
   tapes containing the known copy cores.
3. Compare the class inventory and frequencies with the evolved runs.

**Falsifier (of O2).** Evolved classes absent from the census, or more than 10x
enriched over it, in 2 of 3 cells means selection builds structure the map alone does
not.

**Relabeling guard.**
- Classes are defined by content, not by lineage label.
- The census uses the identical physics hash.

---

## L3. Graded withdrawal vs abrupt gating (support migration)

Adapted from the replacement dissent's probes 1 and 2. Tests O3's core bet.

**Attacks.** A5 and B1.

**Cannot see now.** Whether scaffold removal schedules move capability inward.

**Probe.** Two sites, which can share one preregistration.
- **(a) C9-H1R configuration.** Three arms at matched budget:
  - the existing read gate (abrupt);
  - no gate;
  - one generic linear ramp that flattens the answer distribution's skew over the same
    epochs.

  Readout: the share of competence carried by input-conditional outputs (readers).
- **(b) A published soup with reset-supplied self-location.** Three arms: constant
  resets, abrupt removal, and a geometric ramp. Readout: the existing true-locator test.

**Falsifier.** Ramp reader or locator share no greater than max(abrupt, none), within
the 95% CI. That kills O3's distinctive prediction.

**Relabeling guard.**
- One ramp shape for every source, with no tuning.
- The capability must persist once support reaches zero.
- It must also be restorable in a fresh world with no ramp history, via the handle test.
  This separates "grown" from "scaffolded".

---

## L3b. Write-graph motifs vs genome features

**Attacks.** B5. Tests O5.

**Probe.** From existing BEE and NPE logs that record who wrote whom:
1. Build per-run interaction graphs.
2. Define a small motif set before looking: 2-cycles, hub degree, triangle counts.
3. Predict which regions persist to the end with (i) genome features and (ii) motif
   features, on held-out runs.

**Falsifier (of O5).** Genome features at least as good as motif features (AUC
difference <= 0).

**Relabeling guard.** Motifs are frozen before fitting. Held-out runs come from different
seeds.

---

## L4. Reader-first evolution

**Attacks.** B11 and B1. Tests O4.

**Cannot see now.** Whether the frontier is reader-limited.

**Probe.** In PTE, take cells with documented present-but-unused carriers. Run two arms
at matched budget:
- freeze the writer genome and evolve only readout/reader parameters;
- freeze the reader and evolve the writer.

Measure new counterfactual consultation edges: a site whose later state depends on the
carrier.

**Falsifier (of O4).** Writer-first produces edges at least as fast.

**Relabeling guard.**
- A planted-carrier positive control shows the edge detector can fire.
- Edges are counted by counterfactual swap, not by correlation.

---

## L5. Re-origination rate instead of end-state

**Attacks.** B4.

**Probe.** On the REPL-01 logs and the Z80 flag logs, count independent appearances of
a content class per 1,000 ticks, against a time-shuffled null. Then compare which arms
differ under a rate readout vs the end-state readout.

**Falsifier.** Rate and end-state rank the arms identically. The lens then adds nothing.

**Relabeling guard.** "Independent" means no write-path from a prior instance: the taint
ancestor is absent.

---

## L6. Subtraction dose-response

**Attacks.** A9. The cross-engine "clearing helps" cluster.

**Probe.** In 3 engines (NPE, Archaeon Proteus, graph-world), apply random state
clearing at doses of 0, 1, 3, 10 and 30% of mutable state per epoch. Include a
sham-matched perturbation of equal magnitude that rewrites rather than clears. Measure
competence and persistence.

**Falsifier.** Monotone harm with dose in every engine, or clearing indistinguishable
from the sham rewrite.

**Relabeling guard.** The sham must match perturbation energy, so that "any disturbance
helps" is separated from "clearing specifically helps".

---

## L7. Variation-operator swap on frozen stuck frontiers

**Attacks.** B2 and A6.

**Probe.** Take two frozen stuck frontiers: the CW01 cycle-8 plateau (a 4-edit valley)
and BEE LADDER2 (0/960). Replace point mutation with duplication-and-divergence of
executed segments, holding world, budget and selection fixed.

**Falsifier.** No crossing in either frontier at matched budget.

**Relabeling guard.**
- The new operator may not insert hand-written segments. It may only copy existing
  executed code.
- The witness-seeded arm stays out of the comparison.

---

## L8. Consequence-defined novelty

**Attacks.** B8 and A8.

**Probe.**
1. For Theseus M000617 and M000946, and for a matched set of library mechanisms, compute
   a consequence signature: the vector of outcome changes when each is inserted into
   each of the 12 known families' worlds.
2. Ask whether the candidates' signatures lie in the span, or convex hull, of library
   signatures.

**Falsifier.** Both candidates are inside the library span within noise.

**Relabeling guard.**
- The library gets an equal insertion budget.
- Signatures come from held-out worlds, not from the worlds used to select the
  candidates.

---

## L9. Exceedance triage: lucky draw, leak, or discovery

**Attacks.** A2 and B11.

**Probe.** Scan existing results for any score that exceeds the instrument's own
information ceiling, or improves when the supposed carrier is removed. Known cases:
- Hecate W6: 0.7823 against a ceiling of 0.4576, already explained in place as
  selection on lucky reservoir draws;
- blind deletion improving raw score;
- decoding improving without recurrence.

Classify each by re-evaluating the elites on fresh draws. A drop to the ceiling means
selection on luck. Surviving with a code-level leak means a leak. Surviving with no leak
means the organism uses a channel the instrument does not model.

**Falsifier.** Every exceedance is luck or a leak.

**Relabeling guard.** Fresh draws must be disjoint from the selection draws.

**Note.** The first case already resolved as luck, which supports A2.

---

## L10. Substrate fingerprinting as a standing control

**Attacks.** B9 and the C3 failure mode.

**Probe.** For any claimed cross-substrate regularity, report how well substrate family
can be predicted from the same features. C3 reached .77 vs chance .33.

**Falsifier (of the lens's usefulness).** Family identifiability is always near chance
for claims that later fail, so it predicts nothing.

**Relabeling guard.** Features are frozen before the fingerprint test is run.

---

## If only three are run

1. **L1 memorylessness.** It uses no new runs, and it tests the most dangerous hidden
   assumption across five engines.
2. **L3 graded withdrawal.** It is the only probe that can promote a genuinely different
   mechanism of accumulation (support migration), and its falsifier is directional.
3. **L2 fixed-point census.** It is cheap, and it tells us whether the organism/descent
   ontology is carrying real weight or only redescribing basins of the physics.
