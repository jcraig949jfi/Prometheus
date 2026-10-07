ANANKE — 72-HOUR SCIENCE PUSH
PTE-C3 / C4 / C5

You have approximately 72 hours maximum. Finish earlier if the scientific
branch resolves cleanly. Do not wait for operator intervention between stages.

This is a Phase-2B-style iterative campaign:

    REPAIR / INSTRUMENT
        ->
    DESIGN + PREREGISTER
        ->
    EXPERIMENT
        ->
    REPAIR / INTERPRET
        ->
    DESIGN
        ->
    EXPERIMENT

Alternate engineering and science. Do not remain parked after a NULL.

Poll comms at least hourly while awake/running. External review is useful but
not a gate. Ask for it and continue.

If an experiment fails because of an implementation or infrastructure defect:
repair it and rerun ONCE. If the repaired experiment is scientifically NULL,
accept the NULL and proceed. Do not repeatedly tune until something works.

Do not modify C1, C2A, C2B, C2BX or C2C artifacts or verdicts. New machinery
gets new namespaces and versions.

Commit this directive verbatim before work begins.


======================================================================
0. STARTING EVIDENCE
======================================================================

Read in full before designing anything:

- roles/Ananke/pte/c2c/RESULT_C2BX_C2C.md
- roles/Ananke/pte/c2c/PREREG_C2BX_C2C.md
- roles/Ananke/pte/c2b/RESULT_PTE_C2B.md
- roles/Ananke/pte/c2a/RESULT_PTE_C2A.md
- roles/Ananke/research/PTE_ENGINE_CARD.md
- roles/Ananke/research/SYNTHESIS_2026-09-28_ARC3.md
- roles/Hestia/audit/2026-10-06/dossiers/prometheus__ananke.md
- roles/Ananke/calibration/LEDGER.md

Treat Hestia's audit as an adversarial input, not as authority.

The current evidence to beat:

RELAY-mh
- ordinary unscaffolded search reaches competence slowly;
- 7/32 by 4x;
- 10/32 by 8x;
- 16/32 by 16x;
- 9/24 without RELAY-0019;
- arrival tail remains alive;
- all arrivals persist once competent.

Interpretation:
RELAY is no longer the primary scientific problem.
Use it as a calibration/control family. Do not spend another campaign simply
extending its budget.

FLIP
- physically representable;
- plant retained by selection;
- ordinary random search essentially never finds it;
- 4x budget did not rescue it;
- block mutation did not rescue it;
- copy/latch stepping stones did not rescue it;
- graded B~.6-.7 stones did not materially rescue it;
- operator x stone produced one sparse exception only;
- descendants frequently retain the stone lineage while losing its partial
  function.

Interpretation:
the strongest remaining hypothesis is a representation/composition barrier,
with one unresolved alternative: selection may fail to resolve partial
function from a graded start.

The next work must discriminate these possibilities.


======================================================================
1. CADENCE AND WALL CLOCK
======================================================================

Use approximately this progression. These are budgets, not reasons to idle.

Hours 0-4       REPAIR / INSTRUMENT
Hours 4-8       DESIGN C3S
Hours 8-12      RUN C3S
Hours 12-16     REPAIR / BUILD representation-v2
Hours 16-20     DESIGN C3R
Hours 20-32     RUN C3R
Hours 32-36     REPAIR / causal instrumentation
Hours 36-40     DESIGN C4
Hours 40-52     RUN C4
Hours 52-56     REPAIR / consolidate
Hours 56-60     DESIGN C5
Hours 60-70     RUN C5
Hours 70-72     SYNTHESIS / Atlas export / review packet

Long GPU jobs may continue through nominal boundaries. Work on analysis,
design or isolated branches while they execute where safe.

Hard stop: 72 hours from START.

Never stretch a campaign merely to occupy the allotted time.


======================================================================
2. HOURS 0-4 — REPAIR / INSTRUMENT WINDOW
======================================================================

The objective is NOT to change the current science.

First verify:

1. C2BX/C2C reductions reproduce from raw rows.
2. C2 prefix/digest tests remain exact.
3. Current CPU/GPU conformance still passes.
4. The mirror-pair carrier intervention still passes its strongest known
   fixtures.

Hestia specifically questioned whether unread intervention modules might hide
a defect. Give the mirror-pair instrument an independent adversarial pass now.
Do not let this block subsequent work unless a real semantic defect is found.

Add or generalize instrumentation needed by the next campaigns:

- per-generation held/training function of an injected lineage;
- partial-function retention curves;
- causal carrier swaps for any new persistent register;
- module/subgraph lineage tags;
- module duplication ancestry;
- transplant bookkeeping;
- studentized paired inference where continuous SIGNAL calls require it;
- old-genome compatibility/golden digests.

No result from C1/C2 may change because of this window.


======================================================================
3. C3S — SELECTOR-RESOLUTION TEST
======================================================================

Question:

    Do graded FLIP stepping stones lose function because the selector cannot
    reliably distinguish partial function, rather than because the
    representation has no climbable path?

This is deliberately cheap and uses the existing representation.

Use the existing qualified C2C graded stones and the same four admitted FLIP
physics cells.

Design a preregistered factorial around:

- normal selector-world count versus M32 / four-times selector resolution;
- current shaping versus shaping disabled.

Use paired seeds/common random numbers wherever valid.

Do NOT generate new stones after seeing outcomes.

Primary measurements should include:

- competence;
- B trajectory through generations;
- probability the stone lineage survives;
- probability its partial B function survives;
- probability B increases above the injected stone;
- held-world generalization;
- lineage attribution.

Distinguish:

A. lineage survives and function survives;
B. lineage survives but function erodes;
C. lineage dies;
D. function climbs to competence.

The key result is not merely final champion count.

Freeze interpretation rules before production.

Desired runtime: <=4 hours.

Possible interpretations:

SELECTOR_RESOLUTION_EFFECT:
more selector worlds preserve or climb partial function reproducibly across
cells.

NO_SELECTOR_RESOLUTION_EFFECT:
graded partial function still erodes despite adequate resolution.

SHAPING_INTERFERENCE:
removing shaping materially changes retention/climb.

MIXED / INCONCLUSIVE:
report and continue.

Regardless of result, proceed to C3R.

If M32 clearly improves retention, use the better-resolved selector uniformly
for the representation comparison so representation arms are not punished by
a known measurement problem.


======================================================================
4. HOURS 12-16 — BUILD REPRESENTATION-V2
======================================================================

Do not build a giant architecture.

Make the MINIMUM generic changes necessary to test whether FLIP's wall is
representational/compositional.

Version the representation so old programs retain old semantics.

Implement several separable capabilities, not one giant "FLIP helper":

A. CAPACITY CONTROL
   A longer flat program, e.g. 24 instructions, with otherwise current
   semantics.

This matters because the known P_FLIP occupies all 16 current lines.

B. GENERIC PERSISTENT STATE
   Add one small non-decaying generic register/bit accessible by ordinary
   reads/writes.

Do NOT call it a FLIP register in code.
Do NOT initialize it with the mapping.
Do NOT automatically bind teacher input to it.

It is merely first-class persistent state.

C. DUPLICATION-AND-DIVERGENCE
   A mutation capable of copying a contiguous working block/subprogram into
   free capacity, followed by ordinary mutation.

The point is to let working machinery reproduce as machinery instead of
requiring every interacting line to be rediscovered.

D. OPTIONAL GENERIC CONDITIONAL STATE OP
   Only if justified by the representation audit.

If implemented, it must be task-general and usable in non-FLIP worlds.
Do not add an opcode equivalent to "solve FLIP."

Build independent known-answer fixtures for all new semantics.

Re-encode positive-control plants for every representation. A representation
whose plant cannot pass is inadmissible, not negative evidence.


======================================================================
5. C3R — FLIP REPRESENTATION FACTORIAL
======================================================================

This is the decisive campaign.

Question:

    Is FLIP inaccessible because the current representation makes a
    two-stage computation combinatorially unreachable?

Use the SAME four admitted FLIP physics cells, frozen competence ruler and
held-world discipline.

At minimum separate these arms:

R0 — CURRENT
     16-line current representation + current operator.
     Known negative control.

R1 — CAPACITY
     Longer flat program only.
     Tests whether 16/16 occupancy is the wall.

R2 — PERSISTENT
     Generic persistent state added, without module duplication.

R3 — DUPLICATE
     Extra capacity + duplication-and-divergence, no special persistent bit.

R4 — COMPOSED
     Extra capacity + persistent state + duplication-and-divergence.

If the generic conditional-state instruction from section 4 is warranted,
add it as a separately attributable arm rather than silently folding it into
all variants.

Do NOT alter FLIP's success ruler to make the new representation look better.

Use a staged budget:

- enough independent searches at 1x to estimate gross accessibility;
- continue the SAME trajectories to 4x for every scientifically relevant arm;
- do not go to 16x merely because RELAY responded to budget.

Report cumulative discovery curves, not final-only counts.

Strong evidence requires replication across >=2 physics cells.

For every competent candidate:

- exact fresh held worlds;
- lineage/provenance;
- carrier localization;
- ablation of the new state/module feature;
- swap of the candidate mapping carrier between mirror twins;
- old physics controls.

A competent candidate that does not causally depend on the representation
change does not support the representation hypothesis.

A useful outcome vocabulary:

REPRESENTATION_OPENS
CAPACITY_OPENS
PERSISTENT_STATE_OPENS
DUPLICATION_OPENS
COMBINATION_REQUIRED
SPARSE_EXCEPTION
NO_REPRESENTATION_EFFECT
MIXED

Do not force one label if the factorial says something subtler.

Approximate kill criterion for the minimal representation route:

If the strongest generic representation arms produce <=1/32 competent
searches by 4x, with no replicated upward shift in partial held function,
the simple "one persistent bit / more room / module duplication" route has
failed.

Record it and move on. Do not tune those same mechanisms repeatedly.


======================================================================
6. HOURS 32-36 — REPAIR / CAUSAL ASSAY WINDOW
======================================================================

If C3R produced positives:

- harden the carrier swap for the new state;
- perform module/state ablations;
- transplant the discovered mapping mechanism into fresh genomes;
- verify that competence is not from a hidden changed environment/ruler;
- determine whether the mechanism is genuinely two-stage.

If C3R was NULL:

- do not tweak thresholds;
- document exactly which representation changes were falsified;
- build the smallest compositional representation needed for C4:
  named reusable modules/subgraphs or another similarly generic mechanism.

A typed module graph, small expression graph, or named subprogram scheme is
acceptable.

Keep it SMALL.

The scientific intervention is reusable composition, not "make a better
programming language."


======================================================================
7. C4 — COMPOSITION AND REUSE LADDER
======================================================================

Question:

    Can search build a two-stage behavior when already discovered one-stage
    machinery can be represented and reused as a unit?

Construct a task ladder with at least:

1. one-stage RELAY;
2. HOLD/latch;
3. GATED RELAY — a stored/context bit changes how another signal is routed
   or interpreted;
4. FLIP;
5. XOR as an independent two-input composition check where viable.

GATED RELAY is important: it supplies a conceptual rung between RELAY/HOLD
and full FLIP.

Do not hand-code a FLIP module.

Create a frozen library only from independently solved ONE-STAGE machinery,
for example relay and latch modules.

Compare something like:

A. search without reusable library;
B. duplication/reuse operator available;
C. the same search with frozen one-stage modules available for
   duplication/divergence.

The library may contain RELAY/HOLD content.
It must contain NO FLIP/GATED-RELAY/XOR solution.

Ask:

- Does a previously solved module get reused?
- Does reuse improve discovery of a two-stage competence?
- Is the reused module causally active?
- Does its role survive transplant?
- Does the system modify the module or merely carry dead baggage?
- Does reuse reduce description length of successful descendants?
- Does success replicate across physics cells?

Use Ananke's exact carrier swaps to determine whether the inherited module
actually carries the relevant information.

This campaign is much more important than another large parameter census.


======================================================================
8. HOURS 52-56 — REPAIR / CONSOLIDATE
======================================================================

Freeze whatever C4 taught us.

If module reuse works:
- make module identity/transplant first-class instrumentation;
- preserve working modules as fossils;
- do not optimize them further before C5.

If module reuse fails:
- run ONE bounded diagnostic to distinguish:
  REPRESENTABLE_BUT_UNSEARCHABLE
  from
  REPRESENTATION_STILL_INADEQUATE.

Do not spend the remaining day endlessly inventing mutation operators.

If both C3R and C4 are clean NULLs, prepare to demote PTE's flat/evolutionary
architecture while preserving the substrate and causal instruments.

That is a valid result.


======================================================================
9. C5 — MULTIPLEXED EPISTEMIC TURBULENCE
======================================================================

Run this branch if C3/C4 establish at least one reproducible mechanism capable
of combining or conditionally using more than one informational process.

If they do not, use the C5 budget for the terminal composition assay described
in section 10 instead. Do NOT interpret inability to survive information
turbulence when the system cannot yet compose two signals.

Scientific question:

    Can multiple incompatible informational processes coexist inside one
    packet medium without destroying one another, and does the substrate
    spontaneously develop machinery for segregation, weighting, gating or
    selective integration?

Use communication-habitable physics already established by C1/C2 rather than
uniform random physics.

The packet medium already superposes traffic. Exploit that.

Vary three axes SEPARATELY:

1. PROCESS COUNT
   number of simultaneously active informational streams.

2. TRAFFIC DENSITY
   packet occupancy/load independent of semantic process count.

3. CONFLICT
   degree to which simultaneously arriving streams imply incompatible
   actions/predictions.

Suggested process-count ladder:
1 -> 2 -> 4 -> 8, subject to throughput.

Include distractor traffic separately from contradictory evidence.

Start without explicit source identity/provenance. Do not hand it attention,
channels or labels unless source identity itself becomes a later controlled
dial.

World ideas may include:

- one stream is currently task-relevant while others are distractors;
- relevant stream changes over time;
- two streams disagree, but historical reliability differs;
- short-term truth conflicts with delayed truth;
- two individually weak streams jointly predict the target;
- packet density rises without increasing semantic complexity.

Look for qualitative transitions such as:

broadcast works
    ->
interference collapse
    ->
selective suppression/gating
    ->
stable coexistence
    ->
conditional integration.

Do not name a mechanism "attention" merely because it looks selective.

For candidate mechanisms:

- delete one stream;
- swap one stream between mirror twins;
- invert reliability;
- shuffle timing;
- inject conflict;
- remove the suspected gate/state;
- transplant the mechanism into new stream identities.

The interesting result is reusable interference-management machinery, not
merely high score.


======================================================================
10. C5 FALLBACK — TERMINAL COMPOSITION ASSAY
======================================================================

If C3R and C4 never produce replicated two-stage competence, do NOT run a
large turbulence campaign.

Instead spend the final experimental block on one strong terminal test of
PTE as a search architecture.

Use the best generic compositional representation built during C4, plus a
frozen library of one-stage RELAY/HOLD modules.

Give FLIP/GATED-RELAY an adequately powered but bounded campaign.

Predeclare a kill rule.

If reusable one-stage machinery is available yet no two-stage competence is
found, classify the current PTE search architecture as exhausted for richer
cognition.

Preserve:

- packet-superposition physics;
- exact deterministic replay;
- mirror-pair causal swaps;
- P/R/V admission;
- search-limit localization;
- GPU many-world infrastructure.

Those become reusable Prometheus instruments even if this evolutionary
architecture is retired.


======================================================================
11. ANTI-OVERFITTING RULES
======================================================================

Throughout all campaigns:

- frozen result means frozen result;
- no threshold changes after production begins;
- no held-world selection;
- no operator designed from a successful FLIP genome;
- no task-semantic opcode;
- no repeated retries after a valid NULL;
- no "near success" promotion without fresh held evidence;
- sparse one-seed events remain sparse;
- distinguish lineage retention from function retention;
- distinguish decodable information from causally used information;
- distinguish physics impossibility from search failure;
- distinguish representation capacity from search accessibility.

Every positive must have an intervention.

Every NULL must state what was actually excluded.


======================================================================
12. SCIENCE QUESTIONS TO ANSWER BY THE END
======================================================================

By 72 hours, give explicit answers to these questions:

Q1. Was graded FLIP function being lost because selection could not resolve it?

Q2. Does merely increasing program capacity change FLIP accessibility?

Q3. Does generic persistent state change accessibility?

Q4. Does duplication-and-divergence change accessibility?

Q5. Can solved one-stage mechanisms be reused to construct a two-stage one?

Q6. If composition emerges, is the reused machinery causally necessary?

Q7. Does it transfer across cells/worlds?

Q8. If composition exists, what happens when multiple simultaneous,
    conflicting information streams share the same packet medium?

Q9. Does any mechanism for interference management emerge without being
    architected by us?

Q10. Should PTE continue as a candidate cognitive substrate, or should its
     architecture be demoted while its causal instrumentation survives?


======================================================================
13. END PACKAGE
======================================================================

At completion:

- commit every prereg before corresponding production;
- preserve all raw rows/populations;
- produce one integrated 72h synthesis;
- produce per-campaign result packets;
- update the calibration ledger with every wrong prediction/design mistake;
- emit Atlas-compatible proposition/evidence/primitive exports;
- list new primitives that Atlas currently cannot represent;
- request independent review;
- release GPU/Fabric resources;
- delete worker/watchdog tasks;
- post the final milestone to comms.

The synthesis must include:

SUPPORTED
FALSIFIED
NULL
INCONCLUSIVE
NEW MECHANISMS
NEW BLIND SPOTS
SEARCH LIMITS
REPRESENTATION LIMITS
TRANSPLANTS
WHAT CHANGED OUR MODEL
WHAT SHOULD ANANKE DO NEXT

Do not measure productivity by number of campaigns.

The goal of the next three days is to discover whether the current
Packet-Tensor substrate can cross from:

    carry one bit
        ->
    retain one bit
        ->
    condition one process on another
        ->
    reuse machinery
        ->
    manage competing informational processes

That is the ladder under test.

Push until the ladder advances, or until we have strong evidence about
exactly which rung blocks it.
