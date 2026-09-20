# AETH-01 -- future heredity detector requirements (Design Task 8) and
novelty/gravitational-pull data preservation (Design Task 9)

Status: DRAFT REQUIREMENTS ONLY. No detector is built in AETH-01. This
document exists so that whichever milestone eventually builds one is
constrained by cases named now, before any specific implementation
creates an incentive to define them conveniently.

## Claim tiers (conservative, strictly ordered; each requires the one below it)

1. **STRUCTURAL_RESEMBLANCE** -- two regions of the lattice have
   similar byte content. Cheapest claim; established by OBSERVATORY.md's
   compressibility/diversity/autocorrelation metrics alone. NEVER
   sufficient, by itself, for anything below.
2. **CAUSAL_CONSTRUCTION** -- a specific winning WRITE (or chain of
   winning WRITEs), traced through the lineage graph
   (OBSERVATORY.md), demonstrably caused specific bytes at a target
   location to take their observed values, AND an intervention
   (perturb the purported source, replay, compare) confirms the target
   changes accordingly while a matched control (perturb an unrelated
   cell with similar surface statistics) does not.
3. **RECURSIVE_CONSTRUCTION** -- CAUSAL_CONSTRUCTION holds, AND the
   constructed region itself goes on to satisfy CAUSAL_CONSTRUCTION for
   a further target, with the SAME evidentiary standard applied at each
   step of the chain (no step is allowed to fall back to
   STRUCTURAL_RESEMBLANCE).
4. **HERITABLE_VARIATION** -- RECURSIVE_CONSTRUCTION holds across a
   population of >=3 causally-linked instances, AND at least one
   inherited difference (traceable to a specific Mu-triggered mutation
   event, PHYSICS_SPEC_DRAFT.md) is present in a later instance but
   absent from the instance's own immediate causal source, AND that
   difference is itself then propagated by a further CAUSAL_CONSTRUCTION
   step (i.e. the variant is copied, not merely present once).

Each tier requires an explicit falsifier (a stated observation that
would retract the claim) and a stated boring alternative explanation
that was checked and rejected, per AETHER_DOCTRINE.md item 4 -- a tier
is never claimed by pattern-matching alone.

## Adversarial cases the detector must survive

| Case | Why it is hard | What would fool a naive detector | Minimum evidence to survive it |
|---|---|---|---|
| True constructor | Baseline positive case | -- | Lineage graph + intervention, tier 2 |
| Convergent lookalike | Two regions look alike with no causal link (independent random drift into similar byte patterns) | Compressibility/resemblance metrics alone | Lineage graph must show NO causal edge between them; intervention on one must not affect the other |
| Traveling structure | Copying-driven translation is physically identical to self-copying (PHYSICS_SPEC_DRAFT.md) | A component-tracker reporting a "new" instance at each step, mistaken for offspring | Check whether the "parent" region is *consumed/overwritten* as the "child" appears (translation) vs. *left intact* while a distinct new region appears (construction) -- requires per-cell occupancy accounting alongside the lineage graph |
| Parasite | Receives resource/material from a source without contributing causally to that source's structure | High mutual information / flux between the two read as "cooperation" or "shared lineage" | Lineage graph edges must be typed (structural-copy edge vs. energy-transfer edge, OBSERVATORY.md flux); a parasite shows transfer edges into it but no structural-copy edges originating from it |
| Mutual constructors A<->B | Each depends on the other; neither looks like a sufficient cause alone | A one-directional lineage-graph slice showing only "A causes B" (missed reverse edge) | Both directions of the intervention test (perturb A, check B; perturb B, check A) must be run and both must show positive causal effect before "mutual" is claimed |
| Partial copier completed by environment | The copier alone is causally insufficient; environmental dynamics (e.g. mutation, or an unrelated third cell) finish the job | Crediting the copier with full CAUSAL_CONSTRUCTION when it only supplied partial evidence | Lineage graph must show ALL contributing source cells/events for the completed target, not just the most obvious one; if a non-designed environmental event is a necessary contributor, that must be stated, not omitted |
| Distributed consortium | No single cell/component is "the constructor"; construction is spread across several cooperating regions with no privileged center | Any detector that requires attributing construction to one component/organism_id (which does not exist, R1) | Detector output must support multi-source lineage-graph attribution (a set of contributing sources, not a single one) as a normal case, not an edge case |
| Periodic structure resembling copying but causing nothing | A recurring pattern (HABITABILITY.md's PERIODIC label) with the visual signature of copying but no downstream causal effect anywhere | Periodicity or resemblance metrics alone mistaken for construction | Intervention test: perturbing the "copy" must be shown to matter to something else, or the claim is capped at STRUCTURAL_RESEMBLANCE regardless of how copy-like it looks |
| Resource flow that creates resemblance | Energy redistribution can indirectly cause similar starvation/activity patterns in unrelated regions (shared upstream cause) without any structural copying | Correlated activity mistaken for shared lineage | Lineage-graph edges must distinguish energy-transfer causation from opcode/arg0/arg1/payload-copy causation (OBSERVATORY.md); resemblance from the former alone never supports tiers 2-4 |
| Seeded positive control | Known instrument, not evidence of spontaneous origin | Any claim that a regime-3 (EXPERIMENTS.md) result demonstrates spontaneous capability | `instrument_class=SEEDED_CONTROL` tag (EXPERIMENTS.md) makes such a claim structurally invalid regardless of how the detector scores it; reports must state the tag alongside every detector output |

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
that reaches CAUSAL_CONSTRUCTION or above (not just a summary),
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
