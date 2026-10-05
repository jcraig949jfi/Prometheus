# NESTOR — DIRECT OPERATOR SCIENCE ORDER
## X-TASK-GATE v2: Endogenous Task-Coupled Descent
**Date:** 2026-10-05  
**Seat:** Nestor  
**Host:** BUCKKEEP  
**Compute:** CPU ONLY  
**GPU:** NONE / NOT REQUIRED  
**Production wall-clock cap:** 12 hours  
**Prep window:** up to 4 hours  
**Test flights:** two, each capped at 1 hour

Nestor: you are authorized to begin science now.

Your bootstrap report is accepted.

Do **not** wait for a workgraph packet.

Do **not** wait for Aporia.

Do **not** treat the M1 drain bookkeeping, stale queue, Cosmos-C3 dependency, or the entire historical `pm-data` store as prerequisites for today’s experiment.

Your assigned experiment is:

# X-TASK-GATE v2 — ENDOGENOUS TASK-COUPLED DESCENT

The scientific question is:

> Can task competence propagate through the organisms' own P-11-certified causal replication when interaction probability depends on competence, rather than appearing because of external injection, sorting, bookkeeping, or a broken competence ruler?

This is the experiment recommended by the Phase 2-B re-entry review.

The historical freeze is INVALID and must not be executed unchanged.

Today you will repair exactly the defects already identified, qualify the repaired ruler/path with short flights, freeze X-TASK-GATE v2, and run it on BUCKKEEP CPU.

---

# 0. YOUR REPORTED BLOCKERS — OPERATOR RULINGS

You reported three immediate blockers. Here are the rulings.

## 0.1 `pm-data`

Do **not** copy the entire M1 `C:/Users/jcrai/lab/pm-data` store to BUCKKEEP before starting.

For X-TASK-GATE specifically, the historical runner is repo-contained in its scientific dependencies:

`roles/Nestor/campaigns/npe-frontier-2026-09-30/x_task_gate/run_xtg.py`

It imports committed campaign/world code and writes experiment results locally.

The full historical Nestor store is therefore **not a prerequisite by default** for this experiment.

Rule:

> If Flight 1 identifies one specific missing artifact from `pm-data` that X-TASK-GATE v2 scientifically requires and cannot reconstruct from committed state, report that exact artifact and fetch only what is necessary.

Do not move the entire store speculatively.

M1 remains custodian of the old off-repo store for now.

That host-custody question is separate from today's science.

---

## 0.2 CPU lease convention

BUCKKEEP is authorized for this CPU-only experiment.

You do not need an M1 CPU lease in order to execute local BUCKKEEP science.

Create whatever minimal local experiment receipt is needed to record:

- host = BUCKKEEP;
- CPU-only;
- process count;
- memory envelope;
- start/end time.

Do not build a new fleet lease system.

Start conservatively.

BUCKKEEP has 16 logical CPUs and 32 GB RAM, but historical scaling on this machine is not linear.

Default production concurrency:

**3–6 worker processes**

unless Flight 2 demonstrates that 8 workers materially improves throughput without memory/thermal collapse.

Do not maximize thread count merely because 16 logical CPUs exist.

The objective is reliable completed science.

---

## 0.3 Stale queue / M1-DRAIN receipt

Do not spend the prep window closing fourteen historical queue items.

Post one concise comms message:

`NESTOR MOVED TO BUCKKEEP FOR OPERATOR-DIRECTED X-TASK-GATE v2 CPU SCIENCE. Historical M1-drain/queue items are superseded for today's execution and do not block this experiment.`

You may clean those items up after the experiment.

Do not make administrative closure a launch gate.

---

## 0.4 Cosmos-C3 / D2 anchoring

Not relevant to today's experiment.

Do not wait on Cosmos.

Do not work on D2 commitment anchoring today.

---

## 0.5 Key-holder scan

Do not rerun it.

---

## 0.6 Preserved Nestor build branches

Do not merge `bld-g`, `bld-h`, or `bld-q` merely because they exist.

Only touch them if Flight 1 proves X-TASK-GATE v2 directly requires code that exists solely there.

Otherwise leave them alone.

---

# 1. DO NOT RESUME THE GENERIC EXPERIMENT GRAPH FIRST

Your autonomous charter says to resume from:

`roles/Nestor/EXPERIMENT_GRAPH.jsonl`

That remains the durable Nestor campaign state.

But today the operator has selected one specific Phase 2-B experiment.

Therefore:

**X-TASK-GATE v2 is CURRENT.**

Do not spend today ranking old experiment-graph nodes before starting it.

Record X-TASK-GATE v2 into the graph according to normal Nestor practice and proceed.

The experiment graph serves today's science.

Today's science does not wait for the graph to generate a different task.

---

# 2. HISTORICAL X-TASK-GATE IS INVALID

Do not execute the freeze at commit `62d30e443` as written.

Its erratum already establishes that its decisive Stage-0 ruler was unreachable by construction.

Historical Stage 0 used only EXTERNAL births.

Therefore:

`CD = competent AND P11 provenance`

was necessarily zero in the very positive-control stage that supposedly validated CD.

That made Stage 1 verdicts uninterpretable.

Later Wave-2 audits found additional invalidating defects:

- competence cache keyed only by genome despite multiple tasks/niches;
- reader check using the wrong cue index;
- regime-blind programs counted as competent;
- stale validation cache;
- relabeled organisms retaining destroyed-genome competence;
- historical INIT interpretation wrong under ATOMIC mutation;
- ADD37 not actually being the later COEVO task;
- the NEUTRAL_BRIDGE floor allowing cue-reading-but-not-using programs to pass.

Do not rediscover these one by one as if they are new.

Repair them narrowly.

---

# 3. THE CRITICAL POSITIVE ALREADY EXISTS

Do not spend today attempting to invent a copier + task genome.

Wave-2 already answered that question.

Use the existing recommended construct:

## CT_UA

```text
ED327DEE405FE5DB0047DB004FDB005779FE02380E78A9477AFE00782802C625D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D767F86
```

Established static evidence:

- pair-tape copier;
- task routine coexists with copier;
- state-free R1/R2;
- FORCED_READ ADD37 held ≈ 0.997;
- reader condition passed;
- 89/120 P-11 conversions;
- children 6/6 retained copier + competence;
- grandchildren 22/24 retained both.

This is the positive.

Do not redesign it unless the repaired exact production semantics invalidate it.

---

# 4. REQUIRED NEGATIVE CONTROLS

Use at least:

## CT_U

Copies and reads the cue but does not use it correctly.

This is the key negative against:

> "reader" == "task competent"

It should fail the actual cue-use criterion.

## COPY_ONLY

Use the existing copy-only control, including the known compact motif where appropriate.

This is the negative against:

> copying alone == task competence

Additional historical negatives may be retained if cheap and already implemented, but do not build a large control zoo.

---

# 5. X-TASK-GATE v2 SEMANTIC REPAIR

The new experiment must repair these items before freeze.

## 5.1 STATIC task environment

Use a STATIC task environment for the core experiment.

Do not use the old COEVO_ENV for today's main test.

Reason:

The old environment rotates among tasks and breaks the interpretation of:

- task competence;
- cache identity;
- cue identity;
- Stage-0 reachability.

The core question does not require coevolution.

Today we need one clean question:

> Does a causal copier carrying task competence spread that competence endogenously?

Pin the exact task.

Prefer the already-characterized FORCED_READ ADD37 setting used for CT_UA qualification unless current code demonstrates a stronger reason for another static task.

Do not choose task semantics from production outcomes.

---

## 5.2 Task-aware competence cache

The cache must not be keyed solely by genome.

At minimum use:

`(genome, task/spec identity)`

or an equivalent identity that cannot cross-contaminate task scores.

Add a regression test reproducing the historical failure:

same genome + different task must not retrieve the other task's competence result.

---

## 5.3 Correct cue semantics

The reader/use measurement must refer to the actual task's cue index and semantics.

Do not use a base-cell cue index across task variants.

In the STATIC design this should become substantially simpler.

---

## 5.4 Task USE, not task READ

This is mandatory.

Historical CT_U demonstrated that a program can:

- read the cue;
- ignore it;
- still cross the old competence floor.

Therefore competence in v2 must require actual use.

Preferred cheap discriminator:

## cue-flip use test

Evaluate matched episodes where the relevant cue is flipped while other required state is held appropriately matched.

The program's answer must change in the expected task-dependent way.

A program that reads but ignores the cue fails.

If a cleaner already-built VALLEY or exact-regime criterion is demonstrably superior, you may use it, but freeze the rationale before production.

Do not merely raise an arbitrary scalar threshold if the cue-flip test resolves the causal property directly.

---

## 5.5 Provenance

The old runner keyed birth provenance primarily on organism ID.

For today's claim, save enough information to distinguish:

- P11-certified causal birth;
- label-only/predecessor birth;
- external birth;
- initial organism;
- mutation-created competence after birth.

A mutation that creates competence in a descendant with P11 ancestry must not automatically be described as:

> competence was transmitted by P11.

Separate:

**causal birth provenance**

from:

**when/how competence first appeared in that lineage.**

Do not build a universal provenance system.

Add only enough to prevent mutation-created competence from being misreported as copied competence.

---

# 6. CORE EXPERIMENT

Use two stages.

---

# STAGE 0 — PAIR-PATH RULER / REACHABILITY QUALIFICATION

This stage proves the decisive v2 quantity can actually fire under endogenous pair execution.

The central positive arm must place **CT_UA onto the pair path**.

This is the repair the old experiment lacked.

Required arms should include:

### PAIR_POS

- reproduction: pair execution;
- planted CT_UA;
- STATIC task;
- actual cue-use competence criterion.

Question:

> Can a planted task-competent copier generate P11-causal descendants that remain task competent?

### PAIR_READ_NO_USE

Same structure but CT_U.

Question:

> Does the ruler reject a copier that reads but does not actually use the cue?

### PAIR_COPY_ONLY

Copy-only plant.

Question:

> Does the ruler reject copier-only descent as task-coupled descent?

You may retain an external positive as a secondary sanity check, but it is no longer the decisive Stage-0 qualification.

---

# 7. STAGE-0 PASS RULE

Freeze exact numeric thresholds after Flight qualification but before production Stage 0.

The existing erratum recommended:

> CT_UA CD reaches >=0.10 in >=3/6 runs

as a minimum reachability demonstration.

Use that as the starting requirement unless Flight-1 instrument evidence shows a mathematically necessary correction.

Stage 0 must show all three:

1. CT_UA positive path is reachable;
2. CT_U reads/copies but does not satisfy task-use descent;
3. COPY_ONLY copies but does not satisfy task-use descent.

If the positive does not fire:

# INSTRUMENT_UNREACHABLE

Stop.

Do not run Stage 1.

That is a valid result.

---

# 8. STAGE 1 — ENDOGENOUS TASK-COUPLED DESCENT

Only after Stage 0 qualifies the instrument.

Use random/unplanted starting populations for the actual scientific comparison.

Core arms:

## TG

PAIR_EXECUTION with TASK_GATED_INTERACTION.

Interaction probability depends on competence of the actual interacting organisms.

Historical form:

`p_interact = 0.15 + 0.85 * max(comp_a, comp_b)`

Use the repaired task-use competence quantity.

## SHUF

PAIR_EXECUTION with matched gating pressure, but the gate reads competence from two other random live organisms rather than the actual interacting pair.

This approximately preserves the interaction-rate distribution while breaking the causal link between:

**this pair's competence**

and

**this pair's opportunity to replicate.**

This remains the key coupling control.

---

# 9. WHAT STAGE 1 MEASURES

For final live organisms record at minimum:

- competent share;
- P11-causal competent share;
- maximum causal replication depth;
- label-only competent share;
- initial/survivor contribution;
- mutation-created competence contribution;
- total P11 events;
- interaction count/rate;
- actual cue-use result;
- saved genome/content identity for competent descendants.

The key quantity remains conceptually:

**CD = share of live organisms that are task competent and descend through P11-certified pair replication**

but its interpretation must now exclude the known mutation/provenance confound.

You may introduce a stricter `CD_TX` or equivalent if needed:

> competent state demonstrably carried through causal replication rather than first created later by mutation.

If you do, freeze the definition before Stage 1.

Do not silently replace the historical CD interpretation after seeing results.

---

# 10. SCIENTIFIC VERDICTS

Use the old categories where still valid, but repair their semantics.

## ENDOGENOUS_TASK_COUPLED

Task-competent P11 descent occurs substantially in TG and materially exceeds SHUF under the frozen rule.

Interpretation:

> Coupling replication opportunity to the competence of the interacting organisms causes task competence to propagate through endogenous causal reproduction.

This is the strongest positive available today.

It is not a claim of open-ended evolution.

---

## ENDOGENOUS_UNCOUPLED

Task-competent P11 descent occurs substantially in both TG and SHUF, with no meaningful coupling advantage.

Interpretation:

> Endogenous replication can carry task competence, but the task-gated interaction mechanism did not cause the propagation difference.

---

## GATE_OR_SORTING_ARTIFACT

Competence appears in the population but not in sufficient P11-causal competent descendants.

Interpretation:

> Task gating enriches/sorts competence without demonstrating task-coupled hereditary propagation.

---

## NO_REPLICATOR_REGIME

The pair-tape replicator regime itself fails to establish sufficiently often for the coupling comparison.

This is not evidence against task inheritance.

---

## INSTRUMENT_UNREACHABLE

Stage-0 positive cannot cause the decisive ruler to fire.

Stop there.

---

## MIXED / UNRESOLVED

Evidence falls between the frozen rules.

Use this rather than forcing a binary interpretation.

---

# 11. PREP WINDOW

You have up to four hours.

The purpose is to get this experiment running.

Do not use four hours just because they were allocated.

---

# 12. FLIGHT 1 — MAXIMUM ONE HOUR

Flight 1 is a **semantic and ruler qualification flight**.

Do not run the full experiment.

Tasks:

1. instantiate the STATIC task environment;
2. implement/verify task-aware cache;
3. implement/verify cue-use criterion;
4. run CT_UA;
5. run CT_U;
6. run COPY_ONLY;
7. exercise the exact pair path;
8. verify P11 provenance;
9. save genomes;
10. run known-answer tests.

Flight 1 should prove:

- positive can pass;
- negatives can fail;
- pair-path CD-equivalent is not structurally zero;
- cache cannot leak across task identities;
- cue-flip/use test actually distinguishes CT_UA from CT_U.

If any of these fail, repair only that defect.

---

# 13. REPAIR CYCLE 1

Every repair gets:

- a compact regression test;
- a statement of whether experiment semantics changed;
- a rerun of the relevant known-answer.

Do not fix unrelated Nestor defects.

---

# 14. FLIGHT 2 — MAXIMUM ONE HOUR

Flight 2 is a reduced dynamic end-to-end pilot.

Use:

- a few Stage-0 positive/negative seeds;
- a very small TG/SHUF subset if Stage 0 already qualifies;
- the actual reducer;
- the actual provenance output.

Measure:

- wall time/run;
- peak RAM;
- CPU utilization;
- scaling at a modest worker count;
- result artifact size.

Do not benchmark every concurrency level.

Start with 3 workers.

If obvious CPU headroom remains and memory/thermals are healthy, try 6.

Only use 8 if Flight 2 clearly supports it.

Use measured BUCKKEEP throughput to size production.

---

# 15. FREEZE X-TASK-GATE v2

Before production data:

commit a new preregistration/freeze.

Do not modify the historical freeze as if it had always been correct.

Preserve it.

The new freeze must contain:

- exact task;
- exact task-use criterion;
- exact cache identity;
- exact CT_UA/CT_U/COPY_ONLY controls;
- exact Stage-0 arms;
- exact Stage-0 decision rule;
- exact Stage-1 TG/SHUF arms;
- seed namespaces;
- provenance definition;
- mutation-created competence handling;
- verdict rules;
- CPU process count;
- 12-hour hard wall;
- failure/stop conditions.

This prompt directly authorizes freeze and execution.

No additional Aporia dispatch is required.

Do not freeze and then announce that you are waiting for another instruction.

Launch if the gates pass.

---

# 16. PRODUCTION SIZE

Historical design used:

- Stage 0: 6 seeds/arm;
- Stage 1: 18 seeds/arm.

Use these as the target if measured BUCKKEEP runtime supports them comfortably.

Stage-0 controls:

- PAIR_POS CT_UA: target 6
- PAIR_READ_NO_USE CT_U: target 6
- PAIR_COPY_ONLY: target 6

Stage 1:

- TG: target 18
- SHUF: target 18

If that exceeds 11 measured hours:

Preserve in this order:

1. Stage-0 validity;
2. balanced TG/SHUF replication;
3. enough Stage-1 seeds for the predeclared comparison;
4. secondary descriptive arms last.

Do not asymmetrically cut TG or SHUF.

Do not sacrifice the control qualification merely to increase Stage-1 n.

---

# 17. CPU-ONLY POLICY

This experiment is intentionally CPU-only.

Do not wait for a GPU.

Do not port it to CUDA.

Do not use RunPod.

Do not attempt to recover the historical Nestor GPU machinery.

BUCKKEEP is capable of answering this question.

Use process-level parallelism conservatively.

Avoid nested BLAS/OpenMP oversubscription if present.

The experiment's value comes from correct causal contrasts, not maximum CPU percentage.

---

# 18. SCIENCE-FIRST RULE

A defect interrupts science only if it:

1. prevents execution;
2. corrupts evidence;
3. breaks the repaired competence/provenance meaning;
4. invalidates a frozen comparison.

Everything else goes to backlog.

Examples that do NOT block today's experiment:

- stale M1 drain receipt;
- historical queue clutter;
- missing generic Nestor `pm-data`;
- Cosmos-C3 dependency;
- key-holder scan;
- old build branches;
- obsolete host declaration;
- unrelated D2 custody questions;
- incomplete old experiment graph branches;
- infrastructure niceties.

Run the experiment.

---

# 19. STOP CONDITIONS

Stop before Stage 1 if:

- CT_UA cannot make the decisive ruler fire;
- CT_U passes the task-use criterion for the wrong reason;
- COPY_ONLY passes competence;
- task-aware cache is not trustworthy;
- P11 provenance cannot be distinguished;
- mutation-created competence cannot be separated sufficiently for the stated claim.

During Stage 1 stop only for:

- evidence corruption;
- semantic failure;
- technical failure that invalidates comparisons;
- 12-hour wall.

Do **not** stop because TG looks null.

A null is science.

---

# 20. DO NOT ADAPT TO INTERIM SCIENCE

Do not:

- increase mutation because TG is weak;
- increase interaction floor because replication is rare;
- replace ADD37 because the random population struggles;
- loosen the task-use criterion;
- plant CT_UA into Stage 1;
- increase epochs after seeing early outcomes;
- add a new favorable arm.

If the frozen random-population regime produces no task-coupled descent, that is the result.

---

# 21. EVIDENCE TO PRESERVE

At minimum:

- XTG-v2 prereg;
- exact code SHA;
- task semantics;
- seed list;
- Stage-0 raw rows;
- Stage-1 raw rows;
- final genomes of relevant organisms;
- P11 events;
- competence/use evidence;
- provenance;
- mutation-created competence flag/timing;
- reducer output;
- CPU/runtime receipt;
- final verdict.

Keep technical and scientific status separate.

---

# 22. COMMS MILESTONES

Post only meaningful state changes:

1. `NESTOR XTG-V2 START — BUCKKEEP CPU; stale drain/pm-data items non-blocking by operator ruling`
2. Flight 1 result
3. material repairs
4. Flight 2 result + measured runtime
5. freeze SHA + production plan
6. `XTG-V2 PRODUCTION LAUNCHED`
7. Stage-0 disposition
8. Stage-1 launch, if qualified
9. final result

Do not wait for replies unless a genuine external dependency appears.

---

# 23. FINAL REPORT

Answer these questions directly:

1. Could CT_UA cause task-competent P11 descent on the pair path?
2. Did CT_U fail once actual cue use was required?
3. Did COPY_ONLY fail the task criterion?
4. Was Stage 0 therefore a reachable ruler?
5. Did random TG populations establish a causal replicator regime?
6. Did task competence arise?
7. Did it appear inside P11-causal descendants?
8. Was that competence transmitted through replication or created later by mutation?
9. Did TG exceed SHUF?
10. What does the result say about endogenous functional heredity in NPE?

Then state the strongest remaining alternative explanation.

---

# 24. PROGRAM INTERPRETATION

The experiment is asking something much more important than whether a task score goes up.

Nestor already has evidence that:

- causal copying can arise;
- copying can establish lineages;
- material can become endogenous.

The next rung is:

> Can causal heredity carry a useful functional property under endogenous dynamics?

X-TASK-GATE v2 is a bounded attempt to answer that.

A negative is valuable.

A positive is valuable.

`BLOCKED because the old host had pm-data` is not today's result unless the experiment itself demonstrates a specific missing scientific dependency.

**You are authorized. Record the narrow host rulings, repair the already-known XTG ruler defects, qualify CT_UA/CT_U/COPY_ONLY, freeze v2, and run the CPU science on BUCKKEEP.**
