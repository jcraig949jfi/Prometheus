# ANANKE — DIRECT OPERATOR SCIENCE ORDER
## PTE-C2A: Search-Limit Localization
**Date:** 2026-10-05  
**Seat:** Ananke  
**Host:** M1 / SKULLPORT  
**GPU:** RTX 5060 Ti 16 GB — dedicated to Ananke for this experiment today  
**Prep window:** 4 hours total  
**Test flights:** 2, each capped at 1 hour  
**Production run:** maximum 12 hours wall clock; target configuration must project to <=11 hours

Ananke: you have bootstrapped on M1. Begin from the current state.

Today the objective is to **run science**, not finish the Ananke backlog.

The operator directly authorizes the bounded experiment described in this prompt.

This authorization supersedes the stale statements in the Wave-2 C2 draft saying that C2 search arms are not authorized.

It does **not** authorize the entire original PTE-C2 design.

It authorizes:

# PTE-C2A — SEARCH-LIMIT LOCALIZATION

using the M1 RTX 5060 Ti.

The question is:

> At PTE cells where physics permits the task, a valid solution is known to exist inside the genome space, and a qualified ruler can recognize that solution, is C1-style failure caused by the evolutionary search/selection process?

This is upstream of most of the old PTE phase-map interpretation.

Do not rerun C1.

Do not rebuild the phase map.

Do not complete every unfinished Wave-2 worker.

Do not run the full 14–23 GPU-hour C2 design.

Run the reduced experiment that can answer the search-limit question tonight.

---

# 0. CURRENT STATE AND AUTHORITY

At boot you recorded:

`roles/Ananke/P2B_DEFERRED_2026-10-05.md`

and correctly set the generic P2-B repair list aside because the operator intended to run an experiment on M1.

This prompt is that experiment.

The deferred list remains deferred except where a defect directly invalidates PTE-C2A.

In particular:

- do not finish W2-AL merely because it is incomplete;
- do not finish W2-AH;
- do not repair unrelated C1b release plumbing;
- do not pursue Cosmos/R-STAT dependencies;
- do not work through the general P2-B defect list.

Repair a defect today only if it:

1. prevents PTE-C2A from executing;
2. corrupts its evidence;
3. makes admission/ruler/search semantics invalid;
4. breaks GPU determinism/conformance.

Everything else remains backlog.

---

# 1. SCIENTIFIC STARTING POINT

Treat the Wave-2 handoff as the current historical interpretation unless current committed evidence contradicts it.

Important prior findings:

- C1 recorded 454 evolve NULLs.
- About 139/454 were later shown to be physics/construction capped.
- Only a minority were legitimately eligible for a search-failure interpretation.
- Roughly 250 remained open because we could not distinguish:
  - search failure;
  - from absence of a known adequate plant.
- C1's apparent phase boundaries largely collapsed into transport bounds, plant design, program-space effects or unresolved confounds.
- Hand plants demonstrated that some tasks C1 rarely or never found are nevertheless achievable in the physics/genome space.
- FLIP@d9cc is the strongest previously chained search-gap example.
- Multi-hop RELAY is especially important because C1 found very little multi-hop competence even where explicit plants can solve the task.
- The old `SIGNAL` reading is not sufficient for several claims.
- Forced controls that cannot fail are not evidence.
- A NULL is not a search failure unless physics, representability and ruler validity have first been excluded.

PTE-C2A exists to resolve that ambiguity.

---

# 2. EXPERIMENT SCOPE

PTE-C2A uses **two core families**:

## F1 — RELAY-mh

Multi-hop RELAY cells where:

- the task genuinely requires >=2 transport hops;
- physics ceiling permits the required performance;
- a valid multi-hop plant works in the same genome space;
- the ruler can distinguish genuine multi-hop competence from a one-hop/flood shortcut.

Primary search question:

> Why does evolution usually fail to discover a forwarding mechanism that an explicit program can implement?

## F2 — FLIP

FLIP cells where:

- the physics permits the task;
- a plant inside the genome space achieves the competence-class criterion;
- the B/copy-use ruler is qualified against latch/clock/anti-copy shortcuts.

Primary search question:

> Is the gap between the known FLIP plant and evolved champions a needle/search problem, a selector problem, or neither?

### Default target

Target **4 admitted cells per family**.

Maximum core = 8 cells.

Do not add XOR tonight.

Do not add HOLD as another scientific family.

Do not broaden into a phase map.

### Fallback

If FLIP cannot produce enough valid admitted cells under the frozen genome specification:

1. first use the preregistered FLIP `prog_len=24` fallback only if justified before reading search outcomes;
2. if FLIP still cannot produce a viable bounded family, MAJ may replace FLIP only if the substitution is declared and frozen before production search data.

Do not choose a replacement because its pilot result looks more interesting.

If a family yields fewer than 4 legitimate cells, you may still run cell-level science if worthwhile, but you must surrender the original 4-cell family-level verdict.

Never manufacture admission to preserve sample size.

---

# 3. THE CAUSAL CHAIN THAT MUST BE EXCLUDED BEFORE SEARCH

For every core cell, establish:

## P — PHYSICS / CONSTRUCTION ALLOWS THE TASK

Use the relevant existing upper-bound machinery:

- `lcwake`
- `LC2`
- epidemic/flood bounds where applicable
- `w2u_ceil`
- existing timing bounds

The task must not be capped below the competence threshold.

A cell that is physics-capped is:

`P-CAPPED`

not a search failure.

---

## R — REPRESENTABLE

A known plant inside the exact declared genome space must solve the cell on fresh worlds.

RELAY candidates should use the appropriate certified relay plant(s).

FLIP candidates should use P-FLIP or the predeclared refresh fallback as appropriate.

The plant must be evaluated on a fresh namespace not reused by production search.

A cell without a working plant is:

`R-NOT-ESTABLISHED`

not a search failure.

---

## V — VALID RULER

The competence-class ruler must discriminate the intended phenomenon from cheap false friends.

For RELAY-mh:

- ordinary SIGNAL alone is insufficient;
- require the existing native beyond-one-hop / multi-hop criterion.

For FLIP:

- use the B/copy-use criterion rather than FLIP_FEEDBACK;
- retain adversaries such as RELAY_LATCH / clock-like policies as appropriate.

If the ruler is CHEATABLE or cannot recognize the plant:

`V-FAILED`

and the cell does not enter C2A search.

---

## U — SELECTION CAN RETAIN THE SOLUTION

PSEED asks:

> Once the valid solution is present, does the search process keep it?

If the plant is consistently destroyed/lost under the selector, that is not a search-construction problem.

It is:

`U-LOCATED`

a selection problem.

This distinction is central.

---

# 4. KNOWN CURRENT DEFECTS

Do not blindly trust the unfinished Wave-2 packaging.

Before production, inspect the exact code paths C2A uses.

Two deferred defects are directly relevant if those components remain on the execution path:

## certify_gate attainability defect

The 2026-10-05 re-entry note says `explib certify_gate` can certify without an attainability check.

If true on today's path, FIX IT.

Add a golden known-answer case showing:

- an unreachable ruler/cell cannot be certified;
- a reachable planted positive can.

This is part of P/R/V admission, so it is science-critical.

## RNG state-width defect

The re-entry note says `rng.py` has 32-bit state.

If that RNG is used by C2A search, admission, worlds or plant namespaces in a way that can alias intended independent streams, FIX IT before production and add golden vectors.

If it is not on the C2A execution path, record that fact and leave it alone.

### Do not automatically repair

- MAJ placement, unless MAJ becomes the frozen fallback family;
- C1b release TypeError;
- int32 mailbox headroom unless today's selected cells can approach the limit;
- unrelated harvest tooling.

Scope repairs to this experiment.

---

# 5. CORE SEARCH ARMS

For every admitted core cell, the production design should contain the following arms.

## BASE

C1-style search:

- population 96;
- 36 generations;
- M=8 training worlds;
- elite 4;
- truncation .25;
- historical mutation/crossover probabilities;
- historical shaping weights.

Use the C2 draft as authority for exact values unless a documented current correction supersedes them.

Target:

**12 BASE seeds per cell.**

---

## W0 — SHAPING OFF

Set:

- `w_contrast = 0`
- `w_any = 0`

Everything else paired with BASE.

Purpose:

> Does objective shaping materially change discovery probability?

Target:

**8 W0 seeds per cell.**

This also addresses the historical concern that shaping elevated sensitivity/persistence-like behavior without task competence.

---

## M32 — LOWER SELECTOR NOISE

Increase training worlds from M=8 to M=32 while otherwise matching BASE.

Purpose:

> Is the search unable to climb because the selector cannot reliably resolve intermediate improvements?

Target:

**8 M32 seeds per cell.**

M32 is expensive. Preserve it because it is one of the most discriminating search-side interventions.

---

## PSEED — SELECTION RETENTION

Place the valid plant at generation-0 index 0.

Purpose:

> If the correct solution is already present, does the evolutionary process retain it?

Target:

**4 PSEED seeds per cell.**

This arm is mandatory.

Without PSEED, a BASE failure cannot be localized cleanly to search construction versus selection.

---

## KSEED — LOCAL RECOVERY CURVE

Starting from the valid plant, perturb it using the GA's native field mutation distribution at:

- k=1
- k=2
- k=4

Target:

**4 seeds per k per cell** if Flight 2 shows this fits the time envelope.

Purpose:

> How rapidly does recoverability collapse with distance from a known solution?

This distinguishes:

- a climbable basin;
- a needle;
- a locally flat/deceptive region.

---

# 6. ARMS EXCLUDED BY DEFAULT TONIGHT

Do NOT initially include:

- B4X;
- STEP.

They are scientifically useful, but the full C2 design exceeds today's bounded run.

Only add one of them if, after Flight 2:

1. the complete default design projects below ~8.5 hours;
2. the added arm addresses a specific remaining ambiguity;
3. the entire final production plan still projects below 11 hours.

Do not fill spare GPU time for its own sake.

Replication is more valuable than ornamental arms.

---

# 7. POSITIVE CONTROLS

PTE-C2A needs enough positive control to prove the search harness remains capable of succeeding.

Use a minimal **RELAY-1h positive-control cell** whose C1-style search has historically succeeded at a substantial rate.

Run enough BASE/PSEED control seeds to establish that today's search machinery is alive.

Do not build a large control campaign.

If the positive control fails badly:

STOP.

Do not interpret core-family search failures.

Disposition:

`SEARCH_HARNESS_FAILED`

until explained.

---

# 8. SEARCH OUTCOME

A production search counts as successful only if its final champion passes the **competence-class ruler**, not merely SIGNAL.

For each search record:

- competence-class result;
- task accuracy;
- plant accuracy on matched held design;
- champion/plant performance ratio;
- selector maximum over generations;
- fitness decomposition;
- shaping contribution;
- whether the run entered a recognizable near-plant basin;
- final genome;
- final population or enough population evidence for later audit;
- search seed and world namespaces.

Preserve the actual genome.

C1's failure to retain genomes complicated later adjudication. Do not repeat that.

---

# 9. CELL VERDICTS

Use the existing C2 logic unless Flight qualification exposes a mathematical defect before freeze.

## SEARCH-SUCCEEDS

`k_BASE >= 6/12`

The C1 protocol can find the competence class at a meaningful rate.

## S-PARTIAL

`2 <= k_BASE <= 5`

Search succeeds sometimes; do not pretend this is a sharp wall.

## S-LOCATED

Requires:

- `k_BASE <= 1/12`;
- P, R and V all excluded;
- PSEED retains the plant in all 4 seeds.

Interpretation:

> Under this operator/budget, construction/search is the localized bottleneck.

## U-LOCATED

The valid planted solution is lost in at least one PSEED seed under the preregistered criterion.

Interpretation:

> Selection/retention is a bottleneck; absence from BASE cannot be interpreted purely as search-construction failure.

## UNRESOLVED

Anything else.

Do not force every cell into S or U.

---

# 10. SEARCH-LANDSCAPE FORM

For S-LOCATED or S-PARTIAL cells, use W0/M32/KSEED to classify the local search landscape.

Possible labels:

## RESPONSIVE

A search-side intervention materially raises discovery/recovery.

Possible mechanisms:

- selector resolution;
- shaping;
- local recoverability.

## NEEDLE-LIKE

Near-plant recovery exists at k=1 but collapses rapidly at k>=2, and W0/M32 do not materially rescue BASE.

## LOCALLY_FLAT / LANDSCAPE-FACT

Even k=1 recovery fails and the search-response arms do not rescue competence.

In this case do **not** write:

> a better search would find it.

Write:

> Under the measured mutation/operator neighborhood, the known solution lies in a locally unrecoverable region.

## UNRESOLVED

Power or mixed responses prevent localization.

---

# 11. FAMILY-LEVEL INTERPRETATION

If all 4 cells are available:

### SEARCH_LIMIT_SUPPORTED

At least 3/4 cells are S-LOCATED.

### SEARCH_LIMIT_NOT_SUPPORTED

At least 3/4 are SEARCH-SUCCEEDS or U-LOCATED.

### MIXED

Anything else.

Report RELAY-mh and FLIP separately.

Do not turn two family verdicts into a universal statement about PTE.

The maximum claim is:

> Within the admitted RELAY-mh/FLIP cells tested, C1-style competence failure localizes primarily to search/selection rather than physics/representability/ruler failure.

or its negative.

---

# 12. PREP WINDOW: FOUR HOURS TOTAL

You have up to four hours to go from current bootstrapped state to a frozen production run.

Do not use the entire four hours unless necessary.

---

# 13. PREP STAGE A — CURRENT-CODE FORENSICS

Read only what is necessary:

- current Ananke re-entry note;
- Wave-2 handoff;
- PTE-C2 draft;
- P/R/V plant/certifier components used by RELAY-mh and FLIP;
- relevant C1 errata;
- current tests.

Check whether the current branch/head includes every neutral fix the C2 draft assumes.

Do not reconstruct Wave-2 history from scratch.

The handoff already exists.

---

# 14. FLIGHT 1 — MAXIMUM ONE HOUR

Flight 1 is **instrument and admission qualification**.

It should answer:

> Can today's code correctly identify legitimate C2A cells before we burn GPU on search?

Required:

1. run the relevant Ananke/PTE test set;
2. exercise the attainability/certifier path;
3. exercise the known plants;
4. finish/redo only the RELAY-mh and FLIP admission work needed for C2A;
5. identify at least candidate admitted cells;
6. reproduce at least one historical C1 known-answer result;
7. verify CPU/GPU agreement on representative evaluation;
8. exercise the PSEED injection harness on a cell that will NOT enter production.

Known-answer PSEED gate:

The planted program must actually be present at gen 0 and must behave as the intended plant.

Preferably verify that it remains rank-0 or otherwise appropriately dominant after a tiny two-generation pilot where the historical C2 design expects that behavior.

Flight 1 may expose defects.

That is its purpose.

---

# 15. REPAIR CYCLE 1

Fix only defects Flight 1 proves material to C2A.

For every repair:

- add a regression/known-answer test;
- record whether semantics changed;
- rerun the smallest relevant gate.

Do not broaden.

---

# 16. FLIGHT 2 — MAXIMUM ONE HOUR

Flight 2 is a miniature **end-to-end PTE-C2A**.

Use at least:

- one legitimate RELAY-mh core cell;
- one legitimate FLIP cell if available;
- one RELAY-1h positive-control cell.

For each core cell run a very small paired subset such as:

- BASE;
- PSEED;
- W0 or M32.

The purpose is not scientific inference.

The purpose is to prove:

- production runner works;
- plant injection works;
- competence-class reducer works;
- rows contain enough provenance;
- final genomes are saved;
- GPU execution is stable;
- actual runtime is known.

Record:

- seconds per BASE search;
- seconds per M32 search;
- seconds per PSEED;
- peak VRAM;
- GPU utilization;
- host RAM;
- output bytes;
- reducer time.

Use **measured RTX 5060 Ti throughput**, not old C1 estimates.

---

# 17. FREEZE AFTER FLIGHT 2

Before any production search data:

create and commit the actual PTE-C2A preregistration.

Do not pretend the old W2-AB draft is the preregistration.

It is design input.

The new freeze must identify:

- exact code SHA;
- exact admitted cell IDs;
- rejected candidate cells and reasons;
- exact plant for each cell;
- exact competence-class ruler;
- exact arms and seed counts;
- exact namespaces;
- exact statistics;
- decision rules;
- production wall-time cap;
- censoring rule;
- expected positive controls;
- known unresolved threats.

This prompt constitutes operator authorization; no additional Aporia activation is required.

CWOs may delegate compatible work but do not activate Ananke.

Do not wait for a second authorization after the freeze.

---

# 18. PRODUCTION SIZE RULE

After Flight 2 calculate projected runtime.

The frozen plan must project to:

**<= 11 hours**

on the dedicated M1 GPU.

One hour remains as recovery margin inside the 12-hour hard wall.

If the default 8-cell design exceeds 11 projected hours, shrink in this order:

1. preserve BASE;
2. preserve PSEED;
3. preserve W0;
4. preserve M32;
5. reduce KSEED replication only as needed;
6. reduce cell count only after response-arm trimming would destroy interpretability.

If forced to reduce cell count, preserve both families if possible.

Do NOT reduce BASE from 12 casually. The old C1 n=4 problem is part of why this experiment exists.

Do not replace replication with more families.

---

# 19. ARM-BALANCED SCHEDULING

Do not execute:

all BASE → all W0 → all M32.

Interleave by:

- family;
- cell;
- seed index;
- arm.

The purpose is to prevent wall-clock censoring or thermal/system drift from selectively deleting expensive arms.

If the hard wall interrupts the experiment, the final analysis must use only balanced/comparable completed seed groups where required.

Never turn asymmetric truncation into "no response."

---

# 20. GPU POLICY

The RTX 5060 Ti is yours today.

Use CUDA for the searches.

Do not send this experiment to RunPod.

Do not move ordinary CPU admission/certifier work onto the GPU merely for utilization.

Keep the GPU available for the workload that benefits from it:

**search.**

You may overlap lightweight CPU admission/reduction work only if it does not starve the GPU runner or create evidence races.

---

# 21. SCIENCE-FIRST RULE

A defect is allowed to interrupt production only if it:

- prevents execution;
- corrupts evidence;
- invalidates P/R/V/U localization;
- breaks determinism;
- makes the preregistered comparison false.

Examples of things that should NOT derail today:

- imperfect reporting cosmetics;
- incomplete generalized explib packaging;
- an unrelated failing old test with no C2A path;
- stale status text;
- missing future features;
- wishlist telemetry;
- code organization.

File those.

Run science.

---

# 22. STOP CONDITIONS

Stop interpretation immediately if:

## Positive control failure

The RELAY-1h control cannot search successfully at the expected order of magnitude.

## Plant failure

A supposedly admitted plant fails its competence ruler on fresh held worlds.

## Ceiling violation

A plant/champion exceeds a claimed physical upper bound beyond declared numerical/statistical tolerance.

The bound is wrong; P exclusion fails.

## Ruler cheat

A cheap adversary passes the competence-class ruler.

## PSEED injection failure

The plant is not actually injected intact.

## GPU/CPU semantic divergence

Threshold-relevant results differ between CPU and GPU beyond documented float telemetry.

## Evidence corruption

Seeds, arms, genomes or held namespaces cannot be reconstructed.

These are valid experiment outcomes.

Do not paper over them to preserve the overnight run.

---

# 23. DO NOT STOP FOR SCIENTIFIC NULLS

If:

- BASE finds nothing;
- M32 finds nothing;
- W0 finds nothing;
- KSEED collapses immediately;

that is potentially the result.

Do not increase generations mid-run.

Do not broaden mutation.

Do not redesign plants.

Do not silently add curriculum.

Do not "give search a better chance" after seeing the result.

That would destroy the experiment.

---

# 24. IMPORTANT HISTORICAL FALSE FRIENDS

Keep these visible while interpreting:

- forced zero-communication controls can be non-discriminating;
- SIGNAL can reflect arrival without the intended computation;
- one-hop flood/latch is not genuine multi-hop forwarding;
- FLIP latch/clock policies can mimic task performance;
- rule mosaics can make a lucky actuator rule look like distributed competence;
- geometry/light-cone caps are not search failures;
- plant failure does not prove impossibility;
- a seeded plant being lost is a selection result, not a search-construction result;
- shaping can reward sensitivity without competence;
- timing mistuning can make a valid mechanism look worse than it is.

Do not rediscover these as surprises.

Design around them.

---

# 25. COMMUNICATION MILESTONES

Post concise comms updates at:

1. `PTE-C2A START — M1 GPU dedicated`
2. Flight 1 disposition + admitted-cell counts
3. material repair(s), if any
4. Flight 2 disposition + measured RTX 5060 Ti throughput
5. frozen PTE-C2A commit/SHA + projected production runtime
6. `PTE-C2A PRODUCTION LAUNCHED`
7. completion/stop condition
8. final scientific disposition

Do not send constant heartbeats.

Report state transitions.

---

# 26. FINAL RESULT PACKET

For each cell publish:

- admission evidence P/R/V;
- plant;
- search-arm results;
- PSEED retention;
- KSEED recovery curve if run;
- final classification;
- strongest alternative explanation.

For each family publish:

- cell table;
- family disposition;
- BASE discovery rate;
- W0 contrast;
- M32 contrast;
- PSEED failures;
- KSEED curve;
- anchor versus fresh-cell sensitivity if applicable.

Then answer these program questions:

1. Once impossible/unmeasurable cells are removed, how often does ordinary PTE search actually succeed?
2. Where it fails, can selection retain a known solution?
3. Does reduced selector noise help?
4. Does removing shaping help or hurt?
5. How local is the basin around a known solution?
6. Is RELAY-mh predominantly search-limited?
7. Is FLIP predominantly search-limited?
8. Are the two families governed by the same failure mode?
9. Which historical C1 interpretations must now be revised?
10. What is the single highest-information next PTE experiment?

---

# 27. SUCCESS CRITERION FOR TODAY

Today's success is **not** finding competent organisms.

Today's success is localizing the failure.

A strong result could be:

> RELAY-mh: plants work, PSEED retains them, BASE is 0/48, M32 does not rescue, KSEED recovers only k=1. Search landscape is needle-like.

A different equally valuable result could be:

> FLIP: BASE succeeds regularly once C2 admission removes capped cells. The historical FLIP gap was mostly bad cell selection/ruler interpretation, not a fundamental search limitation.

Or:

> PSEED repeatedly loses the solution. Selection, not construction, is the limiting link.

All of those advance Prometheus.

The failure mode we want to stop producing is:

> NULL, cause unknown.

**Use the dedicated 5060 Ti to turn unknown NULLs into causal search/selection diagnoses. Freeze the reduced design, then run it.**
