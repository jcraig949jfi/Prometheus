# ANANKE — DIRECT OPERATOR SCIENCE ORDER
## PTE-C2B: Search-Barrier Dissection / Gradient Creation
**Date:** 2026-10-05  
**Seat:** Ananke  
**Host:** M1 / SKULLPORT  
**GPU:** RTX 5060 Ti 16 GB  
**Authority:** direct operator order  
**Production wall-clock cap:** 12 hours  
**Target frozen projection:** <= 11 hours

Ananke: PTE-C2A is CLOSED.

Do not rerun it.

The result packet at:

`roles/Ananke/pte/c2a/RESULT_PTE_C2A.md`

is the starting scientific fact for this experiment.

You are authorized to proceed directly to:

# PTE-C2B — SEARCH-BARRIER DISSECTION

The question has changed.

C2A already established that, within the eight admitted cells tested:

- physics permits the tasks;
- valid solutions exist inside the searched genome space;
- the rulers recognize those solutions;
- cheap adversaries fail;
- selection retains the solutions;
- ordinary C1-style search almost never constructs them.

The remaining question is now:

> **Why can't search reach them?**

More specifically:

> Is the search barrier caused by inadequate budget, absence of useful stepping stones, or a locally disconnected/flat landscape around competent mechanisms?

This experiment should distinguish those explanations.

---

# 0. C2A RESULTS THAT ARE NOW FIXED INPUTS

Do not re-litigate these during C2B.

## Positive control

RELAY-1h:

- BASE 8/8;
- PSEED 2/2.

The search harness is alive.

## RELAY-mh

Four admitted cells:

- 0010
- 0019
- 0027
- 0032

C2A:

- BASE = 1/48;
- PSEED = 16/16;
- 4/4 S-LOCATED;
- family verdict = SEARCH_LIMIT_SUPPORTED.

## FLIP

Four admitted cells:

- 0000
- 0004
- 0099
- 0167

C2A:

- BASE = 0/48;
- PSEED = 16/16;
- 4/4 S-LOCATED;
- family verdict = SEARCH_LIMIT_SUPPORTED.

## W0

No rescue.

Do not rerun it.

## M32

No meaningful rescue.

Do not rerun it.

Increasing selector precision did not solve the problem.

## PSEED

32/32 retention across the core cells.

Selection is not the observed bottleneck.

Do not spend another large arm proving this again.

---

# 1. IMPORTANT C2A CORRECTION

The frozen C2A landscape label `RESPONSIVE` is not scientifically supported by actual repair behavior.

Post-hoc analysis showed:

- every apparent KSEED recovery began from an edit that was already competent;
- 15/15 apparent recoveries were neutral edits;
- genuinely broken starts recovered:

RELAY-mh:
- k=1: 0/9
- k=2: 0/14
- k=4: 0/16

FLIP:
- k=1: 0/11
- k=2: 0/15
- k=4: 0/16

Total:

**0/81 genuinely broken starts recovered.**

The frozen C2A verdict remains unchanged.

The KSEED landscape interpretation does not.

C2B repairs that experimental defect prospectively.

---

# 2. DO NOT EXPAND THE WORLD SAMPLE

Use the SAME eight admitted cells.

Do not perform a new 200-cell admission sweep.

Do not add XOR.

Do not add MAJ.

Do not build a new phase map.

The strength of C2B comes from keeping:

- physics;
- plants;
- rulers;
- genome space;
- held semantics;

fixed while manipulating the **search path**.

The same eight cells are already unusually well characterized.

Exploit that.

---

# 3. C2B HAS THREE PRIMARY ATTACKS

C2B should test three distinct explanations:

## A. BROKEN-START RECOVERY

Can evolution repair a solution that is close in genotype but genuinely noncompetent?

## B. B4X

Does simply giving ordinary search much more time solve the problem?

## C. STEP

Can a mechanistically meaningful stepping stone create a path that random search lacks?

These answer three different hypotheses.

Do not collapse them into one "better search" treatment.

---

# 4. ARM A — BROKEN-START RECOVERY

This is the most important repair to C2A.

Create:

## BRK1

A one-field perturbation of the plant that is **demonstrably noncompetent before search**.

## BRK2

A two-field perturbation of the plant that is **demonstrably noncompetent before search**.

Do not use k=4 in the primary design.

C2A already showed that k=4 almost always destroys competence completely. k=1 and k=2 are more informative about local topology.

---

# 5. BROKEN MEANS ACTUALLY BROKEN

Do not define BRK1/BRK2 merely by edit count.

A candidate start is admitted to the broken-start arm only if:

1. it contains exactly the required number of distinct GA-native field edits;
2. it reads FALSE under the frozen family competence ruler;
3. it is not merely INDETERMINATE;
4. qualification uses a fresh namespace disjoint from:
   - C2A admission;
   - C2A held;
   - C2B training;
   - C2B held.

Call this namespace something explicit such as:

`C2B_BROKEN_QUAL`

Do not qualify brokenness on the production held set.

That would contaminate the experiment.

---

# 6. DO NOT CHERRY-PICK THE BROKEN EDIT

Generate broken starts by a deterministic frozen procedure.

For example:

1. derive an edit RNG from:
   - cell ID;
   - arm;
   - search seed index;
   - dedicated C2B namespace;
2. draw using the GA's actual mutation-field distribution;
3. apply exactly k distinct edits;
4. score on BROKEN_QUAL;
5. if still competent, redraw;
6. accept the first FALSE start;
7. cap redraw attempts and report failures.

Do not choose the "most promising" broken mutant.

Do not choose the one closest to threshold after inspection.

First qualified broken draw wins.

Record the entire edit record.

---

# 7. LINEAGE ATTRIBUTION IS MANDATORY

A BRK search counts as **recovery** only if the competent organism descends from the injected broken start.

This is essential.

A rare competent organism discovered independently by the random background is not evidence that the broken genotype was repaired.

Record:

- injected broken genome ID;
- descendants;
- first competent descendant;
- generation of recovery;
- mutation/crossover path where practical;
- whether the final champion belongs to that lineage.

Separate:

`BROKEN_LINEAGE_RECOVERY`

from:

`BACKGROUND_SUCCESS`.

The latter remains scientifically interesting but answers a different question.

---

# 8. BRK SAMPLE SIZE

Default target per cell:

- BRK1: 8 seeds
- BRK2: 8 seeds

Across four cells per family this gives:

- 32 BRK1 trials/family;
- 32 BRK2 trials/family.

If measured throughput forces a reduction, preserve BRK1 before BRK2.

BRK1 is the highest-information arm because C2A already suggests one field is often enough to destroy competence.

---

# 9. BROKEN-START VERDICTS

Freeze numerical rules before production.

Use this conceptual ladder:

## LOCALLY_REPAIRABLE

Repeated lineage-attributed recovery from genuinely broken starts.

A good default criterion is:

- >= 4/32 lineage recoveries;
- represented in >= 2 of the 4 cells.

Do not let four recoveries from one unusually easy cell become a family-wide claim.

## SPARSE_REPAIR_PATH

1–3 lineage recoveries, or recovery concentrated in one cell.

## LOCALLY_FLAT_SUPPORTED

0/32 lineage recoveries at BRK1.

At n=32, zero already places a useful upper bound on repair probability.

Report the exact interval.

BRK2 strengthens but does not substitute for BRK1.

---

# 10. ARM B — B4X

C2A did not test whether the C1 search budget itself was simply too short.

Run:

## B4X

Same search as BASE except:

- generations = 144 instead of 36.

Do not alter:

- population size;
- mutation rates;
- crossover;
- shaping;
- M;
- genome specification;
- physics;
- rulers.

This isolates **time/budget**.

---

# 11. USE C2A BASE AS THE PREFIX CONTROL

Where possible, B4X should use the exact same search seeds as a declared subset of the C2A BASE runs.

The first 36 generations should reproduce the corresponding C2A BASE trajectory.

Add a prefix-identity gate:

> At generation 36, B4X state/curve/champion must reproduce the corresponding frozen C2A BASE search within exact established GPU semantics.

If it does not:

STOP that comparison.

A B4X result is only interpretable if it really is:

**the same search, allowed to continue.**

This gives us an unusually strong paired experiment without rerunning BASE.

---

# 12. B4X SAMPLE SIZE

Default:

- 8 B4X seeds per cell.

Prefer the C2A BASE seed indices 0–7 unless there is a predeclared technical reason otherwise.

Across each family:

32 B4X searches.

Record:

- whether competence appears by generation 36;
- whether it appears after generation 36;
- first competent generation;
- persistence thereafter.

The crucial quantity is:

`NEW_AFTER_36`

not simply final success.

---

# 13. B4X INTERPRETATION

## BUDGET_RESPONSIVE

Default criterion:

- >= 4/32 new post-generation-36 successes;
- in >= 2 cells.

Interpretation:

> The C1 budget was materially too short.

## WEAK_BUDGET_RESPONSE

1–3 late successes or concentration in one cell.

## NO_BUDGET_RESPONSE

0/32 new post-36 successes.

Do not equate this with proof that infinite search cannot work.

It means:

> Four times the C1 evolutionary horizon did not materially open the competence class.

---

# 14. ARM C — STEP

The third hypothesis is that the competence class is not locally climbable from random genomes but becomes accessible through an intermediate mechanism.

This is more scientifically interesting than merely adding compute.

Run a family-specific stepping-stone arm.

---

# 15. RELAY-mh STEPPING STONE

Use a **one-hop relay mechanism** that:

- performs real causal transport;
- is representable in the same genome space;
- fails the RELAY-mh competence ruler;
- is mechanistically upstream of multi-hop forwarding.

The stepping stone must be qualified before production as:

- functional at one-hop transport;
- FALSE on the multi-hop C2B competence criterion.

Do not use an already competent multi-hop plant.

The question is:

> Can evolution turn a useful one-hop relay into multi-hop forwarding?

---

# 16. FLIP STEPPING STONE

Use a predeclared copy/latch-like mechanism such as the existing RELAY_LATCH family only if it meets all qualifications:

1. inside the same genome space;
2. measurably performs a mechanistically relevant subfunction;
3. FALSE under the frozen FLIP B competence ruler;
4. not INDETERMINATE;
5. not an adversarial shortcut that already nearly passes on that cell.

Because FLIP-0184 demonstrated that copy behavior can approach the B boundary under some physics, qualify STEP separately on all four production cells.

If RELAY_LATCH is too close to the ruler boundary on any selected cell, do not tune it after seeing search.

Either:

- use a different predeclared stepping-stone family qualified everywhere;
- or mark STEP unavailable for that cell.

---

# 17. STEP LINEAGE ATTRIBUTION

As with BRK, a STEP success counts as stepping-stone conversion only if the successful organism descends from the injected stepping stone.

Separate:

`STEP_LINEAGE_SUCCESS`

from:

`BACKGROUND_SUCCESS`.

Without lineage attribution, STEP cannot tell us whether the stepping stone created the path.

---

# 18. STEP SAMPLE SIZE

Default:

- 8 STEP seeds per cell.

32 searches per family.

Use common random numbers against the corresponding C2A BASE indices where possible.

Only the seeded index-0 genome should differ at initialization.

---

# 19. STEP INTERPRETATION

## STEP_RESPONSIVE

Default:

- >= 4/32 lineage-attributed competence successes;
- represented in >= 2 cells.

Interpretation:

> The search space contains a useful intermediate route that ordinary random initialization rarely enters.

## WEAK_STEP_RESPONSE

1–3 successes or one-cell concentration.

## NO_STEP_RESPONSE

0/32 lineage-attributed successes.

---

# 20. FAMILY-LEVEL SEARCH-BARRIER CLASSIFICATION

At the end of C2B classify RELAY-mh and FLIP separately.

Possible outcomes:

## LOCAL_BASIN_BARRIER

BRK1 can recover, but BASE and B4X rarely find the mechanism.

Interpretation:

> A competent basin exists and has a local gradient, but random search almost never reaches that basin.

## BUDGET_LIMITED

B4X materially increases discovery.

Interpretation:

> The search process can reach competence under the existing operators, but C1's horizon was too small.

## STEPPING_STONE_LIMITED

STEP materially increases discovery while B4X does not.

Interpretation:

> Search lacks an accessible intermediate route from ordinary initialization.

This is particularly interesting for Prometheus.

## LANDSCAPE_BARRIER

All of the following:

- BRK1: no meaningful lineage recovery;
- B4X: no meaningful late success;
- STEP: no meaningful lineage success.

Interpretation:

> Under the tested operators, nearby broken states, extra search time, and the selected mechanistic stepping stone all fail to create an accessible path.

Call this a measured **landscape barrier**.

Do not call the mechanism globally unreachable.

## MIXED

Different cells or interventions disagree.

Report the heterogeneity.

Do not force both families into the same story merely because C2A looked similar.

---

# 21. WHY B4X AND STEP BOTH MATTER

Do not choose one and discard the other merely to simplify the story.

They separate two important hypotheses:

### B4X succeeds

The mechanism was rare but reachable under ordinary search.

### STEP succeeds while B4X fails

The problem was not simply compute.

The problem was **path structure**.

That is a much more interesting result for Prometheus.

### Neither succeeds

Then the C2A search failure becomes substantially stronger:

the mechanism is representable and selectable, but the current genetic operators do not expose a useful path toward it.

---

# 22. DO NOT RERUN W0 OR M32

C2A already measured them.

RELAY-mh:

- W0 = 0/32 against BASE 1/32 balanced subset;
- M32 = 1/32 against BASE 1/32.

FLIP:

- W0 = 0/32;
- M32 = 0/32.

Their bounded effects are already small.

The next experiment is about:

- local repair;
- time;
- stepping stones.

Stay on the new question.

---

# 23. USE THE EXISTING C2A INSTRUMENT

Reuse:

- same eight cells;
- same canonical plants;
- same competence rulers;
- same adversaries;
- same engine semantics;
- same held design pattern;
- same GPU execution path;
- same population saving;
- same evidence format where possible.

Build C2B as an additive experiment.

Do not modify C2A artifacts.

C2A is historical evidence now.

---

# 24. PRE-FREEZE REPAIR: KSEED DEFECT

Prospectively repair the specific C2A design defect:

> Seeded near-plant arms must condition on the **starting genotype actually being broken**.

Add known-answer tests proving:

- competent neutral edit is rejected from BRK arm;
- FALSE edit is accepted;
- INDETERMINATE edit is not treated as broken;
- qualification namespace is distinct from training/held;
- edit record regenerates exactly;
- lineage attribution distinguishes injected-descendant success from background success.

Do not generalize this into a new search framework.

---

# 25. SAME-AUTHOR THREAT

C2A's result packet correctly records:

> One seat wrote plants, rulers, adversaries and verdict code.

For C2B, prepare a compact freeze/review packet and post it to comms for read-only adversarial review by an appropriate independent seat.

The review should target:

- broken-start conditioning;
- lineage attribution;
- STEP qualification;
- B4X prefix identity;
- verdict reachability.

Do not let review become a week-long gate.

If an independent reviewer returns a fatal validity defect before production launch, repair it and re-freeze.

If no review returns within the bounded preparation window, proceed and record:

`EXTERNAL REVIEW PENDING AT LAUNCH`.

Science should continue.

---

# 26. FLIGHT 1 — BROKEN / STEP QUALIFICATION

Maximum approximately one hour.

Do not run production science.

Qualify:

- BRK1 generation;
- BRK2 generation;
- brokenness test;
- lineage tracking;
- RELAY step;
- FLIP step;
- B4X prefix replay on at least one cell.

Known answers:

- exact plant starts competent;
- BRK candidate starts FALSE;
- STEP starts FALSE under final competence;
- lineage marker survives ordinary mutation/crossover bookkeeping;
- B4X reproduces its C2A BASE prefix.

Repair only demonstrated blockers.

---

# 27. FLIGHT 2 — END-TO-END MINIATURE

Maximum approximately one hour.

Use:

- one RELAY cell;
- one FLIP cell.

Run at least one seed each of:

- BRK1;
- BRK2;
- B4X;
- STEP.

Exercise the actual reducer.

Measure:

- seconds/36-generation search;
- seconds/144-generation B4X;
- VRAM;
- GPU utilization;
- result volume;
- lineage overhead.

Use actual 5060 Ti throughput.

---

# 28. PRODUCTION FREEZE

Before production commit:

`PREREG_PTE_C2B.md`

with:

- exact C2A input SHA;
- exact eight cells;
- exact plants;
- exact BRK construction;
- qualification namespaces;
- exact STEP genomes/mechanisms;
- B4X seed mapping;
- lineage attribution definition;
- arm sizes;
- decision rules;
- wall-clock projection;
- censoring behavior;
- stop conditions.

This prompt authorizes freeze and execution.

No additional activation from Aporia is needed.

---

# 29. TIME ENVELOPE

Hard production wall:

**12 hours**

Target projection:

**<= 11 hours**

If full default C2B exceeds that envelope, reduce in this order:

1. preserve BRK1;
2. preserve B4X;
3. preserve STEP;
4. reduce BRK2;
5. only then reduce per-arm replication.

Do not reduce both families to one unless absolutely necessary.

We want to know whether RELAY-mh and FLIP truly share the same landscape problem.

---

# 30. GPU

M1's RTX 5060 Ti is authorized for PTE-C2B.

Acquire/renew the normal GPU lease.

Use the proven 3-worker configuration unless Flight 2 shows a reason to change it.

Do not send this experiment to RunPod.

The validated local GPU path is sufficient.

---

# 31. STOP CONDITIONS

Stop scientific interpretation for a cell/arm if:

- frozen plant no longer passes;
- ruler changes meaning;
- STEP starts competent;
- BRK starts competent;
- BRK qualification touched production held data;
- lineage attribution fails;
- B4X prefix diverges from C2A BASE unexpectedly;
- held/train namespaces overlap;
- CPU/GPU threshold-relevant disagreement appears;
- evidence cannot reconstruct edit/lineage/search state.

Do not patch a semantic defect into the same production run.

Freeze again.

---

# 32. DO NOT ADAPT TO RESULTS

Once production begins:

Do not:

- choose nicer broken edits;
- alter STEP;
- increase generations beyond 144;
- change mutation rate;
- change crossover;
- loosen competence rulers;
- add new stepping stones;
- remove hard cells;
- expand population;
- change thresholds.

If all three interventions fail, that is an important result.

---

# 33. WHAT A STRONG NEGATIVE WOULD MEAN

Suppose C2B finds:

- BRK1 = 0/32 recovery;
- BRK2 = 0/32;
- B4X = 0 meaningful late successes;
- STEP = 0/32 lineage successes;

for one or both families.

Then the result becomes:

> A valid solution exists and is retainable, but the C1 genetic operators expose neither a local repair gradient, a longer-budget route, nor a route through the selected mechanistic stepping stone.

That is much stronger than:

> search failed.

It begins to characterize the **geometry of reachability** itself.

That is highly relevant to Prometheus.

---

# 34. WHAT A STRONG POSITIVE WOULD MEAN

If STEP succeeds where B4X and broken-start repair fail:

that is potentially more important than C2A.

It would show:

> search reachability depends on the existence of intermediate mechanisms rather than raw compute.

That connects directly to:

- reachability deserts;
- curriculum;
- mechanism composition;
- evolutionary stepping stones;
- open-ended architecture search.

Treat such a result carefully.

Attack it before generalizing.

---

# 35. FINAL REPORT

Answer:

1. Can a genuinely broken one-edit plant recover?
2. Can a genuinely broken two-edit plant recover?
3. Are recoveries descendants of the broken seed or independent discoveries?
4. Does 4× search horizon create new competent lineages?
5. At what generation do they appear?
6. Does a one-hop RELAY stepping stone enable multi-hop RELAY?
7. Does the FLIP stepping stone enable genuine FLIP competence?
8. Are STEP successes lineage-attributable?
9. Which family is:
   - locally repairable;
   - budget limited;
   - stepping-stone limited;
   - landscape-barrier limited?
10. Do RELAY-mh and FLIP still appear to share the same search pathology?
11. What search/operator change is now justified?
12. What C1/PTE conclusions change?

And state the strongest alternative explanation.

---

# 36. PROGRAM DIRECTION

C2A answered:

> Is the failure physics or search?

For these admitted cells:

**search.**

C2B now asks the more interesting question:

> **What kind of search barrier is it?**

Do not return to broad parameter maps until we understand that.

**Keep the eight validated worlds fixed. Force near-solutions to be genuinely broken. Give ordinary search more time. Give it a mechanistic stepping stone. Then determine whether the missing ingredient is gradient, budget, or path.**
