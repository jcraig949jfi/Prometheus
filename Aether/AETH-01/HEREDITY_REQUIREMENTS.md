# AETH-01 -- future heredity detector requirements (Design Task 8) and
novelty/gravitational-pull data preservation (Design Task 9)

Status: DRAFT REQUIREMENTS ONLY. No detector is built in AETH-01. This
document exists so that whichever milestone eventually builds one is
constrained by cases named now, before any specific implementation
creates an incentive to define them conveniently.

## Claim tiers (conservative, strictly ordered; each requires the one below it)

**[REPAIRED per ASTRA_REVIEW_01.md S04, ACCEPT, see REPAIR_LEDGER_01.md.
The reviewed tier ladder let a preconfigured A->B->C forwarding relay
satisfy RECURSIVE_CONSTRUCTION, because it only ever tested whether a
target's VALUE was caused, never whether the target's own CAPACITY to
act was caused. This repair separates value-transport from
capacity-construction as distinct evidence axes and requires the
latter, not the former, for tier 3+.]**

### Separated evidence axes (not a single ladder)

Before the tiers: the following properties are logically INDEPENDENT
and must be evaluated and reported SEPARATELY, never collapsed into one
score: (1) **resemblance** (byte content similarity); (2) **byte/value
transport** (a specific WRITE caused a specific target BYTE VALUE to
take its observed value); (3) **causal influence** (an intervention on
a purported source changes a purported effect, vs. a matched control);
(4) **construction of enabling capacity** (the TARGET'S OWN
opcode/arg0/arg1 fields -- i.e. whether and where IT can act -- were
themselves caused to change by the alleged constructor, not merely its
payload/content); (5) **recurrence of capacity** (a target whose
capacity was constructed goes on to itself construct a further
target's capacity, with the same standard applied); (6) **origin of
variation** (a difference is traceable to a specific Mu-triggered
event, PHYSICS_SPEC_DRAFT.md); (7) **transmission of variation** (an
originated difference is itself then copied onward by a further
value-transport event, independent of whether it originated recently or
is standing variation); (8) **environmental/scaffold contribution**
(what pre-existing, non-constructed machinery the process depended on,
named explicitly, never left implicit); (9) **resource contribution**
(energy-transfer edges are typed separately from structural-copy edges
and MAY carry heredity-relevant patterning -- not excluded by field
type, correcting the reviewed draft's blanket resource-flow exclusion);
(10) **individuality/segmentation hypothesis** (any claimed
"individual" boundary is stated as a hypothesis with its own evidence,
never assumed from component tracking alone, and a distributed
consortium with no privileged center remains a normal, not degenerate,
case).

1. **STRUCTURAL_RESEMBLANCE** -- two regions of the lattice have
   similar byte content (axis 1 alone). Cheapest claim; established by
   OBSERVATORY.md's compressibility/diversity/autocorrelation metrics
   alone. NEVER sufficient, by itself, for anything below. Neither
   necessary nor sufficient for causal construction (a dissimilar
   A->B->A construction is not excluded by requiring resemblance first).
2. **CAUSAL_VALUE_CONSTRUCTION** -- a specific winning WRITE (or chain
   of winning WRITEs), traced through the lineage graph (OBSERVATORY.md,
   preserving ALL contenders per contest, not only winners), demonstrably
   caused specific bytes at a target location to take their observed
   VALUES, AND a content-only intervention (perturb the purported
   source's payload, replay, compare) confirms the target's value
   changes accordingly while a matched control (perturb an unrelated
   cell with similar surface statistics AND comparable causal
   opportunity) does not. This is axes 2+3 together. **This tier alone
   is what a preconfigured forwarding relay (K3 relay fixture, below)
   can satisfy -- it is renamed from the reviewed draft's
   "CAUSAL_CONSTRUCTION" specifically to make clear it certifies VALUE
   transport only, nothing about the target's own capability.**
3. **CONSTRUCTED_CAPACITY** -- CAUSAL_VALUE_CONSTRUCTION holds, AND an
   ENABLING-STATE intervention (perturb/block the purported source's
   write to the TARGET'S opcode/arg0/arg1 fields specifically -- the
   fields that determine WHETHER and WHERE the target can subsequently
   act -- replay, compare) confirms the target's OWN capacity to act
   changes accordingly (e.g. it never becomes WRITE-active, or never
   targets where it otherwise would have), while the matched control
   does not. This is axis 4, and is the tier the reviewed ladder was
   missing entirely. **This is what the K3 constructed-capacity fixture
   (below) is designed to satisfy and the relay fixture is designed NOT
   to satisfy.**

   **[NEW, closure-patch addendum]** `CONSTRUCTED_CAPACITY` is not one
   uniform claim -- two sub-cases pass this tier's test but carry
   different scientific weight, and MUST be reported separately, never
   merged into a single "tier 3, PASS" line:
   - **ACTIVATION_OF_PRECONFIGURED_MACHINERY** -- the source's write
     touches ONLY the target's `opcode` field (WHETHER it acts); the
     target's `arg0`/`arg1`/`payload` (WHERE/WHAT it acts) were already
     present at initialization, untouched by the source. The source
     switched existing machinery on; it did not design that machinery.
     This is what the current K3 constructed-capacity fixture (below,
     fixture 2) demonstrates.
   - **CONSTRUCTION** -- the source's write touches the target's
     `opcode` field AND at least one of `arg0`/`arg1` (i.e. the source
     determines not just whether the target acts, but where/what it
     does) -- a strictly stronger claim. Its ablation battery must be
     finer-grained than the activation case's single on/off test: each
     field the source writes (opcode, routing/`arg0`, targeting-field/
     `arg1`) must be ablated INDEPENDENTLY, since a detector that only
     tests the opcode field cannot tell "source built the target's
     behavior" from "source merely flipped a switch on a coincidentally
     pre-wired target." Fixture 3 (below) is the minimal case that
     forces this distinction to matter.
   - **PAYLOAD_RELAY** is not a `CONSTRUCTED_CAPACITY` sub-case at all
     -- it is the tier-2-only relay fixture (fixture 1, below), named
     here only so all four labels appear together as one taxonomy: a
     detector's report must state which of PAYLOAD_RELAY /
     ACTIVATION_OF_PRECONFIGURED_MACHINERY / CONSTRUCTION /
     RECURSIVE_CONSTRUCTION (tier 4, below) applies, never just a bare
     tier number.
4. **RECURSIVE_CONSTRUCTION** -- CONSTRUCTED_CAPACITY holds, AND the
   region whose capacity was constructed itself goes on to satisfy
   CONSTRUCTED_CAPACITY for a further target's enabling state (axis 5),
   with the SAME evidentiary standard applied at each step (no step
   allowed to fall back to STRUCTURAL_RESEMBLANCE or to
   CAUSAL_VALUE_CONSTRUCTION alone).
5. **HERITABLE_VARIATION** -- RECURSIVE_CONSTRUCTION holds across a
   population of >=3 causally-linked instances, AND at least one
   difference is present in a later instance but absent from the
   instance's own immediate causal source (axis 6 -- origin, via a
   traceable Mu-triggered event OR standing/spatial/energy-pattern
   variation, no longer restricted to Mu-origin only, correcting the
   reviewed draft's exclusion of standing variation), AND that
   difference is itself then propagated by a further
   CAUSAL_VALUE_CONSTRUCTION step (axis 7 -- transmission, evaluated
   separately from origin).

Each tier requires an explicit falsifier (a stated observation that
would retract the claim) and a stated boring alternative explanation
that was checked and rejected, per AETHER_DOCTRINE.md item 4 -- a tier
is never claimed by pattern-matching alone. "Parent-intact vs.
parent-consumed" is DROPPED as a required universal movement/
reproduction discriminator (it is a real observable in SOME cases, not
a universal law, per REPAIR_LEDGER_01.md B02); instead, whether a
successor's construction CONSUMED a predecessor's capacity is tested
directly as its own observable, never assumed.

## Adversarial cases the detector must survive

| Case | Why it is hard | What would fool a naive detector | Minimum evidence to survive it |
|---|---|---|---|
| True constructor | Baseline positive case | -- | Lineage graph + intervention, tier 2 |
| Convergent lookalike | Two regions look alike with no causal link (independent random drift into similar byte patterns) | Compressibility/resemblance metrics alone | Lineage graph must show NO causal edge between them; intervention on one must not affect the other |
| Traveling structure | Copying-driven translation is physically identical to self-copying (PHYSICS_SPEC_DRAFT.md) | A component-tracker reporting a "new" instance at each step, mistaken for offspring | Check whether the "parent" region is *consumed/overwritten* as the "child" appears (translation) vs. *left intact* while a distinct new region appears (construction) -- requires per-cell occupancy accounting alongside the lineage graph |
| Parasite | Receives resource/material from a source without contributing causally to that source's structure | High mutual information / flux between the two read as "cooperation" or "shared lineage" | Lineage graph edges must be typed (structural-copy edge vs. energy-transfer edge, OBSERVATORY.md flux); a parasite shows transfer edges into it but no structural-copy edges originating from it |
| Mutual constructors A<->B | Each depends on the other; neither looks like a sufficient cause alone | A one-directional lineage-graph slice showing only "A causes B" (missed reverse edge) | Both directions of the intervention test (perturb A, check B; perturb B, check A) must be run and both must show positive causal effect before "mutual" is claimed |
| Partial copier completed by environment | The copier alone is causally insufficient; environmental dynamics (e.g. mutation, or an unrelated third cell) finish the job | Crediting the copier with full CONSTRUCTED_CAPACITY when it only supplied partial (e.g. CAUSAL_VALUE_CONSTRUCTION-level) evidence | Lineage graph must show ALL contributing source cells/events for the completed target, not just the most obvious one; if a non-designed environmental event is a necessary contributor, that must be stated, not omitted |
| Distributed consortium | No single cell/component is "the constructor"; construction is spread across several cooperating regions with no privileged center | Any detector that requires attributing construction to one component/organism_id (which does not exist, R1) | Detector output must support multi-source lineage-graph attribution (a set of contributing sources, not a single one) as a normal case, not an edge case |
| Periodic structure resembling copying but causing nothing | A recurring pattern (HABITABILITY.md's PERIODIC label) with the visual signature of copying but no downstream causal effect anywhere | Periodicity or resemblance metrics alone mistaken for construction | Intervention test: perturbing the "copy" must be shown to matter to something else, or the claim is capped at STRUCTURAL_RESEMBLANCE regardless of how copy-like it looks |
| Resource flow that creates resemblance | Energy redistribution can indirectly cause similar starvation/activity patterns in unrelated regions (shared upstream cause) without any structural copying | Correlated activity mistaken for shared lineage | Lineage-graph edges must distinguish energy-transfer causation from opcode/arg0/arg1/payload-copy causation (OBSERVATORY.md); resemblance from the former alone never supports tiers 2-4 |
| Seeded positive control | Known instrument, not evidence of spontaneous origin | Any claim that a regime-3 (EXPERIMENTS.md) result demonstrates spontaneous capability | `instrument_class=SEEDED_CONTROL` tag (EXPERIMENTS.md) makes such a claim structurally invalid regardless of how the detector scores it; reports must state the tag alongside every detector output |
| **[NEW, S04 repair]** Preconfigured forwarding relay | A genuine, verifiable causal chain of VALUE changes exists (A really does change B really does change C) using machinery that was never built by anything | Any claim standard that only checks value-transport (old "CAUSAL_CONSTRUCTION") certifies this as recursive construction | Must be capped at CAUSAL_VALUE_CONSTRUCTION; fails CONSTRUCTED_CAPACITY because an enabling-state intervention on A does not change B's own opcode/arg0/arg1 (B's capacity pre-existed A) -- see K3 relay fixture, `KILL_GATES_01.md` |

## K3 fixtures (relay negative and constructed-capacity positive)

**[NEW per ASTRA_REVIEW_01.md S04/K3, see REPAIR_LEDGER_01.md and
`KILL_GATES_01.md` for the adjudicated outcome.]** These are the two
minimal, hand-specified byte configurations the repaired tier ladder
above must discriminate. Both use a 1-row, 3-cell segment `A,B,C` (a
1xW torus with W>=3, so A/B/C have distinct, non-aliased von-Neumann
neighbors; direction encodings below assume `arg0 mod 4` selects "right
neighbor" via a fixed convention, consistent with PHYSICS_SPEC_DRAFT.md).

1. **Relay negative.** Initial state: `A = (WRITE, right, field=3,
   payload=p_A, energy>=WRITE_COST)`; `B = (WRITE, right, field=3,
   payload=<anything>, energy>=WRITE_COST)`; `C` = anything
   non-interfering. Every tick, A overwrites B's PAYLOAD with `p_A`
   (field 3 only); B, independently and UNCONDITIONALLY of what A did
   (B's own opcode/arg0/arg1 were never touched by A), overwrites C's
   payload with B's current payload. Ablation test: remove A (or block
   its proposal) -- B's opcode/arg0/arg1 are completely unaffected (A
   never wrote fields 0-2 of B), so B keeps writing to C every tick
   exactly as before, just with stale/different payload content.
   Verdict under the repaired ladder: A->B and B->C each qualify for
   CAUSAL_VALUE_CONSTRUCTION (A's payload changes verifiably propagate
   to B then to C); NEITHER qualifies for CONSTRUCTED_CAPACITY, because
   ablating A does not change B's capacity to act at all.
2. **Constructed-capacity positive.** Initial state: `A = (WRITE, right,
   field=0, payload=WRITE_opcode_byte, energy>=WRITE_COST)`; `B`'s
   opcode starts at `RESERVED_INERT` (a non-WRITE byte, e.g. `0x00`),
   but B's `arg0/arg1/payload` are PRE-SET at initialization to
   `(right, field=3, some payload)` -- i.e. B's "wiring" exists but is
   switched off because its opcode is inert; `C` = anything
   non-interfering. Tick 1: A's WRITE targets B's OPCODE field and
   writes the WRITE opcode byte into it -- B flips from inert to
   active. From tick 2 onward, B (now WRITE-active, using its
   pre-existing arg0/arg1/payload) writes to C every tick. Ablation
   test: remove A (or block its proposal) -- B's opcode NEVER becomes
   WRITE, so B NEVER writes to C, at any tick, for the entire run.
   Verdict under the repaired ladder: A->B qualifies for
   CONSTRUCTED_CAPACITY (the enabling-state intervention -- removing
   A's specific opcode-field write -- changes B's own capacity to act,
   confirmed by ablation, with a matched control of perturbing an
   unrelated inert cell showing no effect on B). Whether B->C also
   constructs C's CAPACITY (as opposed to only C's value) depends on
   C's own configuration, which this minimal fixture leaves passive
   (C is a value-transport target only) -- this fixture demonstrates
   the A->B discrimination, not a full RECURSIVE_CONSTRUCTION chain,
   and does not claim to.

Per operator instruction, if these two fixtures received the SAME
verdict under the repaired ladder, this would mean the claim standard
is unusable and must be reported as `INFERENCE_CONTRACT_UNRESOLVED`.
They do not: see `KILL_GATES_01.md` K3 for the adjudicated disposition.

3. **[NEW, closure-patch addendum] Construction fixture (stronger than
   fixture 2, with per-field ablations).** Initial state: `A = (WRITE,
   right, field=0, payload=WRITE_opcode_byte, energy>=WRITE_COST)` on
   tick 1, THEN (tick 2 onward) `A`'s own payload/arg1 are such that it
   writes `field=1` (`arg0`, i.e. B's routing byte) with a fixed
   direction value into B; `B`'s opcode starts INERT and its `arg0`/
   `arg1`/`payload` start at all-zero (no pre-existing wiring at all,
   unlike fixture 2's B); `C`, `D` = non-interfering targets at two
   different relative positions, chosen so that B's stored `arg0`
   value determines WHICH of C/D receives B's writes once active. Four
   INDEPENDENT ablations (never collapsed into one on/off test):
     - **(a) opcode-only ablation** (block only A's tick-1 write to
       B's opcode): B never activates at all -- reproduces fixture 2's
       result, confirms `CONSTRUCTED_CAPACITY` holds for the
       WHETHER-axis alone.
     - **(b) routing-only ablation** (leave A's opcode write intact,
       block only A's tick-2+ write to B's `arg0`): B activates (still
       WRITE-active) but its `arg0` stays at its inert-initialized
       value (0 = a fixed default direction) instead of A's intended
       direction -- B still writes SOMEWHERE, but not to the target A
       "intended," confirmed by comparing which of C/D receives B's
       output with vs. without this specific ablation. This is the
       case fixture 2 cannot produce (its B had no `arg0` construction
       to ablate at all) and is what distinguishes CONSTRUCTION from
       ACTIVATION_OF_PRECONFIGURED_MACHINERY: the target's BEHAVIOR,
       not just its on/off state, is shown to have been built.
     - **(c) matched control** (perturb an unrelated inert cell E with
       similar surface statistics, e.g. `(0, 5, 5, 5, 0)`, instead of
       A): neither B's opcode nor B's `arg0` changes -- confirms the
       effect in (a)/(b) is specific to A, not an artifact of
       perturbing any cell in the lattice.
     - **(d) inherited-scaffold check** (axis 8, never left implicit):
       B's `payload`/target-field selection beyond `arg0`-routing (i.e.
       WHAT value gets written, as opposed to WHERE) is still whatever
       A itself supplies each tick as the winning proposal's value --
       so unlike fixture 2, this fixture has NO leftover
       "pre-existing, non-constructed machinery" credited silently to
       B; the scaffold contribution here is named as "none beyond A's
       own repeated writes," explicitly, not assumed.
4. **[NEW, closure-patch addendum] Recursive construction fixture
   (A constructs B's capacity; B, once capable, constructs C's
   capacity).** 1-row, 5-cell segment `A,B,C,D,E` (`E` = unrelated
   inert control, `D` = C's non-interfering write target). Initial
   state: `A = (WRITE, right, field=0, payload=WRITE_opcode_byte,
   energy>=WRITE_COST)` targets B's opcode; `B`'s opcode starts INERT,
   but `B`'s `arg0/arg1/payload` are PRE-SET to `(right, field=0,
   WRITE_opcode_byte)` -- i.e. once active, B's own wiring makes IT
   write the WRITE opcode into C's opcode field (this fixture composes
   ACTIVATION_OF_PRECONFIGURED_MACHINERY at both steps, deliberately
   minimal, to isolate the RECURSIVE property itself rather than
   re-testing CONSTRUCTION's per-field ablations a second time); `C`'s
   opcode starts INERT, `arg0/arg1/payload` PRE-SET to `(right, field=3,
   value=99)` targeting `D`'s payload. Tick 1: A activates B. Tick 2:
   B (now active) activates C. Tick 3 onward: C writes 99 into D.
   Ablation test (single lever: remove/block A only): B's opcode NEVER
   changes -> B NEVER writes to C -> C's opcode NEVER changes -> C
   NEVER writes to D, for the entire run -- a single upstream ablation
   propagates through BOTH construction steps, which is exactly the
   signature `RECURSIVE_CONSTRUCTION` (tier 4) requires: CONSTRUCTED_
   CAPACITY holds at A->B, AND B itself goes on to satisfy
   CONSTRUCTED_CAPACITY for a further target (C), by the same standard,
   with no step falling back to a weaker tier. Matched control:
   perturbing E affects neither B nor C at any tick.

## What data must be preserved NOW so this remains possible later

The lineage graph and intervention evidence above require: (a) the full
`proposal_emitted`/`proposal_won`/`stored_bits_changed` trace
(AETHER_SPEC.md, already required), (b) AETH-01's extended energy-event
trace (PHYSICS_SPEC_DRAFT.md Instrumentation), (c) OBSERVATORY.md's
promoted forensic buffers around any anomaly, and (d) the ability to
fork a replay from an exact `S[t]` and re-run with one field perturbed
(requires exact checkpointing, REQUIREMENTS.md). None of this is built
in AETH-01; the requirement is that AETH-01's engineering (checkpoint
format, trace schema, replay-fork capability) not foreclose it.

## Novelty / "gravitational-pull" observatory -- future requirement (Design Task 9)

Not part of AETH-01 physics or observatory v0. If a mechanism ever
survives the tiers above, a LATER milestone may ask disguised frontier
models "what familiar human mechanism best explains this specimen?"
Requirements on that future assay (not built now):

- mechanism names, source engine identity, and provenance must be
  hidden from the model at query time;
- causal traces (the lineage graph and intervention results, not just a
  visual/summary rendering) must be what is shown, since resemblance
  alone is exactly what tier 1 already warns against;
- multiple models queried independently, without letting them see each
  other's answers first;
- literature-retrieval-assisted answers and pure-parametric-memory
  answers must be kept as separate conditions, not blended;
- a model reporting "I don't recognize this" is NOT itself a novelty
  claim (absence of recognition is weak evidence, easily produced by a
  bad description, not just by genuine novelty);
- calibration set: known, disguised, FAMILIAR mechanisms (e.g. a
  hand-seeded copier from EXPERIMENTS.md regime 3, described the same
  way) must be run through the identical pipeline to measure the
  models' baseline recognition rate on things that are NOT novel,
  before any AETH-01 specimen's "low recognition" score means anything.

**What AETH-01 must preserve now, specifically for this future use**:
the full lineage graph and intervention-result set for any specimen
that reaches CAUSAL_VALUE_CONSTRUCTION or above (not just a summary),
`instrument_class` provenance (so a seeded calibration case is never
confused with a candidate novel case), and enough of the raw trace to
reconstruct a mechanism description that does not itself leak
Aether-specific terminology (opcode/WRITE/etc.) into the disguised
query -- i.e. an abstraction layer between raw trace and any future
natural-language description is a requirement on the eventual query
pipeline, not something AETH-01 needs to build, but AETH-01's trace
must contain enough structure (typed lineage edges, intervention
deltas) that such an abstraction is possible later without re-running
the original world.

## Explicitly not done in AETH-01

No detector code, no claim pipeline, no LLM assay, no lineage-graph
implementation. This document is requirements only.
