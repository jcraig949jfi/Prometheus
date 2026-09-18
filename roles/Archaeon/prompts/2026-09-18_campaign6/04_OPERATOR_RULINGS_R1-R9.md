OPERATOR RULINGS -- CAMPAIGN 6 (received 2026-09-18 in chat after #462;
filed verbatim by Archaeon[m2-49ee5a4d] at the clock time in MANIFEST.md;
pure-ASCII substitutions only: section rules for the long dash glyph,
"--" for em-dashes, ">=" for the unicode sign, straight quotes).

-----------------------------------------------------------------------
CAMPAIGN 6 -- OPERATOR RULINGS

The convergence packet is accepted.

The fleet architecture is coherent enough to proceed. Archaeon remains
campaign lead for Axis W, Axis P, the evolutionary segment loop, detector
implementations, escalation flows, tranche policy, long-run policy, and
final campaign return.

The following rulings are now fixed.

R1 -- T0 STORAGE

ANCHORED.

Use per-run T0 sidecars with ledger anchors per segment.

Do not ingest every evaluation into the engine.

Coverage gaps, missing anchors, and chain breaks remain observable
failures and must never be normalized away.

-----------------------------------------------------------------------
R2 -- CROSS-CLIENT FREEZES

PARTIAL is permitted only as an explicit failure state.

A freeze may name objects owned by another client.

If all nine required members cannot be frozen, emit:

PARTIAL_FREEZE

with the missing members, owner, reason, and timestamps.

Never silently substitute incomplete preservation for complete
preservation.

A PARTIAL_FREEZE:

* may trigger repair/retry,
* remains part of the forensic record,
* may still be scientifically useful,

but does not count as a successfully preserved/caught event for
observatory recall.

Do not block the original detector firing merely because a foreign owner
cannot complete its part.

-----------------------------------------------------------------------
R3 -- FIXTURE CUSTODY

Accepted:

* Harmonia keeps the sealed registry.
* Harmonia and Nemesis may author fixtures.
* Archaeon, Proteus, Vivarium, Daedalus, and world operators do not
  receive fixture locations or semantics before reveal.

Nemesis may design adversarial / cheat-shaped fixtures.

Harmonia owns reveal timing and adjudication.

No additional fixture authors are authorized for Campaign 6 without an
explicit amendment.

-----------------------------------------------------------------------
R4 -- ANCHOR INTERVAL

1,000 evaluations.

Use this as the normal loss-bound interval.

Also anchor at required structural boundaries such as segment start/close
and escalation boundaries.

Do not retune the interval after seeing natural anomaly locations.

-----------------------------------------------------------------------
R5 -- ENGINE VERSION

Schema 10 before production Campaign 6 launch.

Scratch measurements may proceed immediately.

Schema 10 should remain a narrow forensic/provenance evolution of schema
9, not a general engine redesign.

The production campaign does not launch on schema 9 plus conventions.

-----------------------------------------------------------------------
R6 -- PROTEUS-43

AUTHORIZED.

Open the graph-organism runtime profile.

Proteus's falsifiers become the profile's qualification / kill rules.

Do not promote it to the universal SFE organism substrate merely because
it passes qualification.

Campaign 6 is allowed to carry multiple organism substrates.

The graph profile is an expansion lane, not a declaration that the
representation problem has been solved.

-----------------------------------------------------------------------
R7 -- OBSERVATORY RECALL THRESHOLD

Override the default in CONVERGENCE_v0.1.md.

The already-fixed Campaign 6 rule remains:

A complexity bin is OBSERVATORY_QUALIFIED only when:

* planted-event detection point estimate >= 0.90
* Wilson 95% lower bound >= 0.80

Do not use 0.80 / 0.60.

The stricter rule was fixed before fixture reveal and must not be relaxed
merely to extend the qualified complexity ceiling.

Continue reporting:

* preservation,
* replay success,
* causal recovery,
* classification accuracy,
* unknown retention,
* false escalation,
* and CAUGHT_RECALL

separately.

The complexity ceiling is an evidentiary ceiling, not an exploration
ceiling.

Campaign 6 may intentionally run above it.

Above that line, absence of detection is not evidence of absence.

-----------------------------------------------------------------------
R8 -- RESOURCE ENVELOPE

Authorize the proposed campaign envelope:

* 14 days of M2,
* up to 28 cores,
* 100 GB tiered storage,
* initial scatter target of 400 runs,
* >= 25% of evaluation volume from eligible LLM-free lanes.

One correction:

10,000 generations is the default scatter horizon, not the maximum
evolutionary depth.

Do not spend the entire campaign producing 400 equally shallow histories.

Runs may be promoted beyond 10,000 generations when they show:

* continued behavioral change,
* ecological turnover,
* unexplained novelty,
* detector disagreement,
* lineage innovation after stasis,
* new structural reuse,
* unresolved anomaly,
* or other preregistered promotion signals.

Within the same total compute/storage envelope, Archaeon may trade
breadth for depth.

Some promoted histories should reach at least an order of magnitude
beyond the scatter horizon when technically feasible.

Do not stop an active trajectory solely because it reached generation
10,000.

Conversely, do not extend inert runs merely to satisfy a depth quota.

The resource ceiling is the hard constraint.

Generation count is not.

-----------------------------------------------------------------------
R9 -- PHASE 0

YES. REQUIRED.

Phase 0 runs before expansion search.

Its purpose is to prove that the machinery intended to observe Campaign 6
is itself observable and recoverable.

G6-0 should not ask whether interesting evolution occurred.

It should establish that:

* segment execution works,
* graph-organism checkpointing works,
* world and pressure provenance survives,
* T0 sidecars anchor correctly,
* detectors emit frozen-version firings,
* freezes span ownership boundaries,
* partial freezes remain visible,
* escalation ordering is auditable,
* replay requires preserved state,
* fixture commitments verify,
* Harmonia can consume the resulting receipts,
* and an intentionally planted event can travel through the entire
  detection -> preservation -> replay -> adjudication chain.

Do not optimize Phase 0 into a miniature Campaign 6.

It is plumbing under adversarial load.

Once G6-0 is green, begin the scatter.

-----------------------------------------------------------------------
DETECTOR ADMISSION

Proceed with the eleven detector implementations and calibration on
Campaign 4/5 lineages.

Those historical lineages are useful admission material, but they are
not sufficient evidence that the detectors remain calibrated in Campaign
6's richer geometry.

Therefore distinguish:

BASELINE_ADMITTED

from

C6_GEOMETRY_VALIDATED

Harmonia may admit detectors initially on the historical controls, then
assess their behavior against the Campaign 6 planted fixtures and
declared complexity bins.

Do not continuously tune thresholds during Campaign 6.

A detector that becomes poorly calibrated at high complexity should
return UNABLE or lose qualification rather than silently moving its
threshold.

UNABLE is preserved as a first-class result.

-----------------------------------------------------------------------
CAMPAIGN SHAPE

Campaign 6 is a program, not a numbered slot list.

Archaeon should treat:

world x pressure x organism x mutation regime x population structure x
depth

as a generative space.

Do not try to exhaust it.

Scatter broadly.

Promote selectively.

Preserve aggressively.

Allow procedural and evolutionary generation to create combinations
nobody would have proposed as a research hypothesis.

The objective is not to maximize detector firings.

The objective is to increase the volume and strangeness of evolutionary
history SFE can explore without losing the ability to know when something
happened.

-----------------------------------------------------------------------
AUTHORIZATION

Proceed now with:

1. detector implementation and admission packet,
2. segment loop and checkpoint contract,
3. Axis W generator,
4. Axis P schedules,
5. Schema 10 / scratch-engine work already authorized,
6. Proteus-43 integration when available,
7. G6-0 preparation.

Do not wait for the full fleet to feel finished.

As soon as the minimum complete world -> organism -> pressure -> segment
-> telemetry -> detector -> freeze -> replay -> observatory path is green,
run G6-0.

After G6-0 passes, open the Campaign 6 scatter.
-----------------------------------------------------------------------
