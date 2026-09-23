# AETH-01 -- configuration-transmission detector requirements (legacy path HEREDITY_REQUIREMENTS.md; Design Task 8) and
novelty/gravitational-pull data preservation (Design Task 9)

Status: DRAFT REQUIREMENTS ONLY. No detector is built in AETH-01. This
document exists so that whichever milestone eventually builds one is
constrained by cases named now, before any specific implementation
creates an incentive to define them conveniently.

## Five-tier claim ladder (ordered claim strength, separate evidence axes)

The formal tiers are exactly STRUCTURAL_RESEMBLANCE /
CAUSAL_VALUE_CONSTRUCTION / CONSTRUCTED_CAPACITY /
RECURSIVE_CONSTRUCTION / TRANSMITTED_VARIATION. Tiers 3-5 require the
causal evidence of the preceding causal tier; resemblance (tier 1)
is NOT a prerequisite for tier 2 or above. Mechanism labels below are
qualifiers, not extra tiers. Missing evidence is unresolved, not an
automatic resemblance finding or a negative result.

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
and MAY carry configuration transmission-relevant patterning -- not excluded by field
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
   of winning WRITEs), traced through the causal provenance graph (OBSERVATORY.md,
   preserving ALL contenders per contest, not only winners), demonstrably
   caused specific bytes at a target location to take their observed
   VALUES, AND a content-only intervention (perturb the purported
   source's payload, replay, compare) confirms the target's value
   changes accordingly while a matched control (perturb an unrelated
   site with similar surface statistics AND comparable causal
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
   - **CONSTRUCTION** -- an attributed source SET supplies the target's
     `opcode` field AND at least one of `arg0`/`arg1`, with observed
     effects on whether and where/which field the target writes. A
     stored-byte difference alone is insufficient: `arg0=1` and
     `arg0=5` both route EAST. This is a stronger configuration claim
     than activation alone, not an additional tier. Its battery must be
     finer-grained than the activation case's single on/off test: each
     field the source writes (opcode, routing/`arg0`, targeting-field/
     `arg1`) must be ablated INDEPENDENTLY, since a detector that only
     tests the opcode field cannot tell "source built the target's
     behavior" from "source merely flipped a switch on a coincidentally
     pre-wired target." Fixture 3 attributes opcode and routing to
     DISTINCT sources `A_opcode` and `A_arg0`, not a lone A. It is
     DISTRIBUTED_CONSTRUCTION with remaining initialized scaffold,
     not a complete machine built from an unwired target.
   - **PAYLOAD_RELAY** is not a `CONSTRUCTED_CAPACITY` sub-case at all
     -- it is the tier-2-only relay fixture (fixture 1, below), named
     here as a mechanism label. Reports give BOTH a formal tier and
     the observed mechanism, contributing source set, initialized
     scaffold, provenance and tested horizon, never a bare tier number.
4. **RECURSIVE_CONSTRUCTION** -- CONSTRUCTED_CAPACITY holds, AND the
   region whose capacity was constructed itself goes on to satisfy
   CONSTRUCTED_CAPACITY for a further target's enabling state (axis 5),
   with the SAME evidentiary standard applied at each step (no step
   allowed to fall back to STRUCTURAL_RESEMBLANCE or to
   CAUSAL_VALUE_CONSTRUCTION alone). Fixture 4 satisfies this formal
   capacity-recursion criterion via
   RECURSIVE_ACTIVATION_OF_PRECONFIGURED_MACHINERY: only opcodes are
   supplied at each step. It does NOT demonstrate recursive configuration
   construction. That stronger mechanism claim needs routing/field
   construction and independent field ablations at each generation.
5. **TRANSMITTED_VARIATION** (frozen ladder alias: `HEREDITY_VARIATION`) -- RECURSIVE_CONSTRUCTION holds across a
   ensemble of >=3 causally-linked instances, AND an identified
   difference has separately supported provenance (axis 6: a traceable
   Mu-triggered event OR standing/spatial/energy-pattern variation), AND
   that difference is itself propagated by a further
   CAUSAL_VALUE_CONSTRUCTION step (axis 7 -- transmission, evaluated
   separately from origin). Only a NEW perturbation-origin claim requires
   absence from its immediate source; standing variation need not be
   newly created during the observed chain. None of the four K3 fixtures
   supplies a ensemble-level variation-transmission assay.

Each tier requires an explicit falsifier (a stated observation that
would retract the claim) and a stated boring alternative explanation
that was checked and rejected, per AETHER_DOCTRINE.md item 4 -- a tier
is never claimed by pattern-matching alone. "Parent-intact vs.
parent-consumed" is DROPPED as a required universal movement/
recursive construction discriminator (it is a real observable in SOME cases, not
a universal law, per REPAIR_LEDGER_01.md B02); instead, whether a
successor's construction CONSUMED a predecessor's capacity is tested
directly as its own observable, never assumed.

## Adversarial cases the detector must persist

| Case | Why it is hard | What would fool a naive detector | Minimum evidence to persist it |
|---|---|---|---|
| Value-transport source | Baseline tier-2 positive case, not necessarily a capacity constructor | Confusing caused content with caused behavior | Winning-value provenance + content intervention and controls; capacity claims additionally require tier 3 evidence |
| Convergent lookalike | Two regions look alike with no causal link (independent random drift into similar byte patterns) | Compressibility/resemblance metrics alone | Causal provenance graph must show NO causal edge between them; intervention on one must not affect the other |
| Traveling structure | Copying-driven translation and recursive state copying share physical primitives | A component-tracker reporting a "new" instance at each step, mistaken for successor | Test construction and recurrence of capacity directly; record predecessor-capacity consumption separately. Parent-intact vs. consumed is not a universal movement/recursive construction discriminator |
| Resource asymmetry (measured, not labeled "asymmetric-resource-dependence case") | A site receives resource/material from a source without contributing causally to that source's structure | High mutual information / flux between the two read as "cooperation" or "shared causal provenance"; OR treating passive receipt alone (transfer edges in, no structural-copy edges out) as sufficient to certify exploitation, ignoring that donor debit means the source -- not the recipient -- pays for the transfer (ASTRA_CLOSURE_REVIEW_02.md M03) | Causal provenance graph edges must be typed (structural-copy edge vs. energy-transfer edge, OBSERVATORY.md flux) and reported with measured benefit/contribution per site (energy received, energy spent, source of each credit); an asymmetric flow pattern (transfer edges in, no structural-copy edges out) is evidence to report, not by itself a "asymmetric-resource-dependence case" verdict -- that requires the same behavior/outcome evidence (donor-reconfiguration cost, recipient's own downstream contribution or lack thereof) as any other resource-mediated case, never edge-type presence alone |
| Mutual constructors A<->B | Each depends on the other; neither looks like a sufficient cause alone | A one-directional causal provenance-graph slice showing only "A causes B" (missed reverse edge) | Both directions of the intervention test (perturb A, check B; perturb B, check A) must be run and both must show positive causal effect before "mutual" is claimed |
| Partial state copier completed by environment | The state copier alone is causally insufficient; environmental dynamics (e.g. perturbation, or an unrelated third site) finish the job | Crediting the state copier with full CONSTRUCTED_CAPACITY when it only supplied partial (e.g. CAUSAL_VALUE_CONSTRUCTION-level) evidence | Causal provenance graph must show ALL contributing source sites/events for the completed target, not just the most obvious one; if a non-designed environmental event is a necessary contributor, that must be stated, not omitted |
| Distributed consortium | No single site/component is "the constructor"; construction is spread across several cooperating regions with no privileged center | Any detector that requires attributing construction to one component/assembly_id (which does not exist, R1) | Detector output must support multi-source causal provenance-graph attribution (a set of contributing sources, not a single one) as a normal case, not an edge case |
| Periodic structure resembling copying but causing nothing | A recurring pattern (HABITABILITY.md's PERIODIC label) with the visual signature of copying but no downstream causal effect anywhere | Periodicity or resemblance metrics alone mistaken for construction | Intervention test: perturbing the "copy" must be shown to matter to something else, or the claim is capped at STRUCTURAL_RESEMBLANCE regardless of how copy-like it looks |
| Resource flow that creates resemblance | Energy redistribution can indirectly cause similar starvation/activity patterns in unrelated regions (shared upstream cause) without any structural copying | Correlated activity mistaken for shared causal provenance | Type energy-transfer edges separately and test interventions/transmission; correlation alone is insufficient, but resource-mediated causal evidence is not categorically excluded from tiers 2-5 |
| Seeded positive control | Known instrument, not evidence of spontaneous origin | Any claim that a regime-3 (EXPERIMENTS.md) result demonstrates spontaneous capability | `instrument_class=SEEDED_CONTROL` tag (EXPERIMENTS.md) makes such a claim structurally invalid regardless of how the detector scores it; reports must state the tag alongside every detector output |
| **[NEW, S04 repair]** Preconfigured forwarding relay | A genuine, verifiable causal chain of VALUE changes exists (A really does change B really does change C) using machinery that was never built by anything | Any claim standard that only checks value-transport (old "CAUSAL_CONSTRUCTION") certifies this as recursive construction | Must be capped at CAUSAL_VALUE_CONSTRUCTION; fails CONSTRUCTED_CAPACITY because an enabling-state intervention on A does not change B's own opcode/arg0/arg1 (B's capacity pre-existed A) -- see K3 relay fixture, `KILL_GATES_01.md` |

## K3 fixtures (relay negative and constructed-capacity positive)

**[NEW per ASTRA_REVIEW_01.md S04/K3, see REPAIR_LEDGER_01.md and
`KILL_GATES_01.md` for the adjudicated outcome.]** These are the two
minimal, hand-specified byte configurations the repaired tier ladder
above must discriminate. Both use a 1-row segment `A,B,C` on a 1x4
torus with a fourth control site; EAST/WEST neighbors are distinct but
NORTH/SOUTH self-alias. Direction encodings select the right neighbor
with `arg0 mod 4 = 1` (EAST), consistent with PHYSICS_SPEC_DRAFT.md.

1. **Relay negative.** Initial state: `A = (WRITE, right, field=3,
   payload=p_A, energy>=WRITE_COST)`; `B = (WRITE, right, field=3,
   payload=<anything>, energy>=WRITE_COST)`; `C` = anything
   non-interfering. Every tick, A overwrites B's PAYLOAD with `p_A`
   (field 3 only); B, independently and UNCONDITIONALLY of what A did
   (B's own opcode/arg0/arg1 were never touched by A), overwrites C's
   payload with B's current payload. Ablation test: remove A (or block
   its proposal) -- B's opcode/arg0/arg1 are completely unaffected (A
   never wrote fields 0-2 of B), so B keeps writing to C every tick
   while its finite energy budget lasts, with stale/different payload content.
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
   pre-existing arg0/arg1/payload) writes to C while funded. Ablation
   test: remove A (or block its proposal) -- B's opcode NEVER becomes
   WRITE, so B NEVER writes to C, at any tick, for the entire run.
   Verdict under the repaired ladder: A->B qualifies for
   CONSTRUCTED_CAPACITY (the enabling-state intervention -- removing
   A's specific opcode-field write -- changes B's own capacity to act,
   confirmed by ablation, with a matched control of perturbing an
   unrelated inert site showing no effect on B). Whether B->C also
   constructs C's CAPACITY (as opposed to only C's value) depends on
   C's own configuration, which this minimal fixture leaves passive
   (C is a value-transport target only) -- this fixture demonstrates
   the A->B discrimination, not a full RECURSIVE_CONSTRUCTION chain,
   and does not claim to.

Per operator instruction, if these two fixtures received the SAME
verdict under the repaired ladder, this would mean the claim standard
is unusable and must be reported as `INFERENCE_CONTRACT_UNRESOLVED`.
They do not: see `KILL_GATES_01.md` K3 for the adjudicated disposition.

3. **Distributed construction fixture (stronger than fixture 2, with
   per-source/per-field ablations).** The executable 3x3 torus has
   B at `(1,1)`, initialized as `(0, SOUTH=2, field=3, payload=77,
   energy=10)`. `A_opcode` at `(0,1)` is `(WRITE, SOUTH, field=0,
   payload=1, energy=10)`; `A_arg0` at `(1,0)` is `(WRITE, EAST,
   field=1, payload=1, energy=10)`. BOTH write into B in the first
   tick, to different fields, without contention. B acts only on the
   NEXT tick, routing EAST to C at `(1,2)`, not SOUTH to F at `(2,1)`.
   Control is at `(0,0)`; other sites start zero. WRITE_COST=1,
   maintenance/replenishment/perturbation=0, seed=31.
     - Disable only `A_opcode`: B stays inert; neither C nor F gets 77.
     - Disable only `A_arg0`: B activates but routes SOUTH; F gets 77,
       C does not. Disable both: B stays inert with default SOUTH routing.
     - Perturb each donor's PAYLOAD independently while preserving its
       emission path; winning-event and target-state checks attribute
       opcode ONLY to `A_opcode`, routing ONLY to `A_arg0`. Neither
       source alone built both fields. The attribution unit is the SET.
     - Perturb the inert control instead of merely checking it stays
       untouched. Also use an active control with the same cost/energy,
       writing payload NORTH outside the focal mechanism, and perturb
       its content. Focal trajectories must be unchanged. This matches
       emission opportunity, not every environmental/positional factor.
     - B's `arg1=3`, `payload=77`, energy=10, and the constructors'
       wiring/energy are initialized scaffold, NOT constructed by this
       source set. Changing B's arg1 changes its output field; changing
       payload changes its output value; removing energy stops emission
       despite successful opcode/routing writes. These are explicit
       scaffold-dependence regressions, not "no scaffold" claims.
   Verdict: CONSTRUCTED_CAPACITY / DISTRIBUTED_CONSTRUCTION, limited to
   opcode and routing construction. No recursive or variation claim.
4. **Recursive activation of preconfigured machinery fixture.**
   Formal tier RECURSIVE_CONSTRUCTION, NOT evidence of recursive
   configuration construction. 1-row, 5-site segment `A,B,C,D,E` (`E` = unrelated
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
   Upstream ablation (remove/block A): B's opcode NEVER
   changes -> B NEVER writes to C -> C's opcode NEVER changes -> C
   NEVER writes to D, for the entire run -- a single upstream ablation
   propagates through both activation steps. This alone is insufficient
   edge-specific evidence: independently change A's opcode-writing
   payload and B's opcode-writing payload. Blocking B->C must leave
   A->B functional while preventing C's action. With A absent, externally
   rescuing B's opcode restores B->C->D; rescuing C alone restores C->D.
   These are interventions, not endogenous construction claims. Trace
   timing must show A->B before B->C before C->D. B/C routing, field
   selection and payload remain byte-identical to initialization.
   Perturbing E (including an active, emitting control) changes neither
   focal capacity nor output. Thus both edges support the formal tier's
   capacity criterion, but ONLY the recursive-activation mechanism.
   Changing B's initialized arg1 from opcode to payload preserves A->B
   and B->C value transport but eliminates C's activation and D's output:
   the second edge then supports only CAUSAL_VALUE_CONSTRUCTION.

All four are SEEDED_CONTROL fixtures, checked over four transitions by
the revised tests (execution status is recorded in KILL_GATES_01.md).
The no-activation consequences in these isolated, no-inflow/no-perturbation
worlds also follow from the law, but finite tests are not unbounded
campaign observations. Shared builders are in
`test/reference/scientific_aeth01.py`; the falsification gate suite tests byte,
winner, behavior and intervention evidence rather than hard-coded verdict
booleans. Differential tests reuse inputs, not transition implementations.
These regressions are fixture-local calibration, not a general detector;
K7 trace qualification and ensemble-level configuration transmission work remain deferred.

## What data must be preserved NOW so this remains possible later

The causal provenance graph and intervention evidence above require: (a) the full
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
persists the tiers above, a LATER milestone may ask disguised frontier
models "what familiar human mechanism best explains this observed instance?"
Requirements on that future assay (not built now):

- mechanism names, source engine identity, and provenance must be
  hidden from the model at query time;
- causal traces (the causal provenance graph and intervention results, not just a
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
  hand-seeded state copier from EXPERIMENTS.md regime 3, described the same
  way) must be run through the identical pipeline to measure the
  models' baseline recognition rate on things that are NOT novel,
  before any AETH-01 observed instance's "low recognition" score means anything.

**What AETH-01 must preserve now, specifically for this future use**:
the full causal provenance graph and intervention-result set for any observed instance
that reaches CAUSAL_VALUE_CONSTRUCTION or above (not just a summary),
`instrument_class` provenance (so a seeded calibration case is never
confused with a candidate novel case), and enough of the raw trace to
reconstruct a mechanism description that does not itself leak
Aether-specific terminology (opcode/WRITE/etc.) into the disguised
query -- i.e. an abstraction layer between raw trace and any future
natural-language description is a requirement on the eventual query
pipeline, not something AETH-01 needs to build, but AETH-01's trace
must contain enough structure (typed causal provenance edges, intervention
deltas) that such an abstraction is possible later without re-running
the original world.

## Explicitly not done in AETH-01

No detector code, no claim pipeline, no LLM assay, no causal provenance-graph
implementation. This document is requirements only.
