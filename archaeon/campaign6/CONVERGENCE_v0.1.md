+=====================================================================+
|  CAMPAIGN 6 -- CONVERGENCE v0.1: who builds what, on which seams     |
|  Archaeon[m2-49ee5a4d]   2026-09-18   written against #455 #456 #457 |
|  #459 #460, Harmonia's lane report and OBSERVATORY_QUALIFICATION     |
+=====================================================================+

The seats received the directive before I closed Campaign 5 and had
already converged, without a lead, on one storage and execution shape.
This document adopts that shape, withdraws the parts of my PLAN v0.1
that duplicated a seat's lane, answers every ask addressed to Archaeon,
and lists the rulings only the operator can give. PLAN.md s2 (axis
designs) is amended by this file where they differ.

1. THE SHAPE EVERYONE BUILDS AGAINST (adopted; owners in brackets)
-----------------------------------------------------------------------
  T0 is ANCHORED, never ingested: one fingerprint row per evaluation
     into an append-only sidecar per run, content-hashed in segments;
     the ledger holds one T0_SEGMENT_ANCHOR per segment (sfe.t0_anchor.v1,
     Daedalus s2); PEW holds one row per anchor and verifies sidecars
     (Mnemosyne). Row cap 1 KiB; row schema proteus.behavior_fingerprint
     .v1 (Proteus) plus a world-side extension (Archaeon, s3 below).
  The SEGMENT is the unit of execution and ingest: one Vivarium row =
     generations [g, g+k) of one population under one pressure slice in
     one world, checkpoint in/out, one observation per ARCHIVED
     generation, T0 table + lineage delta as artifacts (Vivarium s2,
     Daedalus s1). The evolution loop inside the segment is Archaeon's
     (archaeon/wse/evolve.py lineage: EvolutionB pattern).
  Detectors run EXECUTOR-SIDE inside the segment where the world state
     still is (they can trigger a FREEZE); their definitions, frozen
     thresholds and code identity are REGISTERED in PEW before the first
     segment (Mnemosyne); admission (chance floor, positive/negative/
     cheat controls) is Harmonia's; the engine records firings and never
     scores interest (Daedalus D2). Retrospective detectors over anchored
     sidecars are PEW projections and produce "would have been missed"
     rows (return item 12), never escalations.
  FREEZE is one atomic engine fact naming subject/parent/ancestor/
     sibling/cousin/world checkpoints, the pressure window, the mutation
     chain and T1 artifacts (sfe.freeze.v1); replay routes REQUIRE a
     freeze id; A-G run as forks on a scratch engine and post
     REPLAY_RESULT SAME|DIFFERENT|FAILED|NOT_ATTEMPTED; "preserved_at <=
     first explanation" is derivable and counted (Daedalus s4, Mnemosyne).
  Fixtures are sealed as sha256(salt || canonical(plaintext))
     COMMITMENTS held identically by the engine and PEW, INSERT-only
     before launch, revealed after the firing table is frozen; the
     keeper is a NON-OPERATING seat. Harmonia has taken custody
     (lane F) with Nemesis authoring cheat-shaped fixtures; the operator
     confirms (R3).
  Vocabulary: provenance_class in {HUMAN_DIRECTED, LLM_PROPOSED,
     PROCEDURAL, EVOLUTION_GENERATED, MIXED} on every manifest (the 25%
     floor is a ledger census); pressure source EXOGENOUS|ENDOGENOUS on
     every pressure event; UNKNOWN_MECHANISM (a result) / UNKNOWN (not
     supplied) / NULL (not applicable) reserved; freeze scope
     COMPLETE|PARTIAL with a reason.

2. LANES (revised; PLAN v0.1 s8 Q1 is superseded by this table)
-----------------------------------------------------------------------
  Archaeon    campaign lead and convergence; AXIS W (worlds from
              primitives, generator + provenance); AXIS P (pressure
              schedules, EXO/ENDO tagging at the source); the evolution
              loop / segment executor and the world-side fingerprint
              fields; the ELEVEN DETECTOR SPECS with frozen thresholds
              (registered before the first segment, admitted by
              Harmonia); escalation flows (freeze/replay orchestration);
              search policy, tranche plan (complexity bin + provenance
              label per run), long-run policy, ceilings; the campaign
              return.
  Proteus     AXIS O: proteus.graph_organism.v1 runtime + graph grammar +
              lineage_record.v1 edits + behavior_fingerprint.v1
              (organism side); Representation B adopted under proteus/
              repb as an instrument; v0 frozen as the control substrate.
              Does not pick worlds, pressures, fixtures or winners.
              (My PLAN's "Representation G under archaeon/campaign6/
              organism/" is WITHDRAWN: it was Proteus's proposal written
              a second time.)
  Vivarium    execution/data plane: wse_evaluate_v1 (T3 primitive),
              bundle v2 (provenance_class + generator identity, refused
              without), replay-packet + REPLAY row kind, T0/T1 slots,
              fixture commitment table, the SEGMENT kind, the C6 load
              rehearsal. Adjudicates nothing.
  Daedalus    engine: schema 10 delta (D1-D9 as amended by the interface
              delta), anchors, batch, atomic FREEZE, replay packet,
              commitments, cold retention, observatory health; the C6
              acceptance run at 3x rate.
  Mnemosyne   PEW: anchors (never T0 rows), detector registry + firings,
              freeze/replay records, commitments INSERT-only, the
              reserved vocabulary, the invariant count, migration 016
              once producers are named.
  Harmonia    qualification: fixture custody (F), detector admission (D),
              escalation gate (E), recall calibration (R), classification
              admission (C: UNKNOWN_MECHANISM by default, a named
              mechanism needs a reproducing replay AND a moving causal
              probe), success-class rulers (S), provenance census (P),
              the complexity curve (K). Edits nothing it audits.
  Nemesis     cheat-shaped fixtures and chance floors for the eleven
              detectors (with Harmonia).
  Rhadamanthus my opening ask (adjudicate recall) is WITHDRAWN: Harmonia
              holds R and C; a second judge is the operator's to add.

3. ANSWERS TO THE ASKS ADDRESSED TO ARCHAEON
-----------------------------------------------------------------------
  Vivarium R1  SEGMENT: yes. Row shape as your s2; k defaults to 1,000
               generations or the next archive point; archive policy
               {1,2,4,...,64 then 2^k} + dense neighbourhoods (every
               generation for +-16 around a firing) declared in the
               bundle. The loop is archaeon.wse.evolve (EvolutionB
               pattern, pluggable evaluator/grammar/world); I supply it
               as a callable with checkpoint in/out by 2026-09-20.
  Vivarium R3  detectors executor-side inside the loop; they read the
               segment's T0 rows and the world state; PEW holds the
               registry; no detector reads queue tables.
  Daedalus     freeze/replay flows: the loop calls POST /freeze with the
               nine members BEFORE any classification field exists (my
               event record has interpretation = None until adjudication);
               replays A-D on every freeze, E-G on multi-ruler events and
               every fixture candidate at adjudication. Detector
               registration: the eleven with thresholds, before the first
               segment (DETECTORS_v0.1.md, admission by Harmonia).
               Ceilings pre-registered (D6-005): 1e5 evals/run for the
               first tranche with the full tier stack; ledger 10 GB per
               campaign phase; <= 64 checkpoints and <= 256 artifact
               refs per freeze (below your caps); raise to 1e6 only after
               the acceptance run and one scored recall pass, as you
               recommend.
  Mnemosyne    L4/L5 ledgers: archaeon/campaign4/LEDGER.jsonl and
               archaeon/campaign5/LEDGER.jsonl were local-only (the
               harness writes them beside FUNNEL.json; C2/C3's were
               committed, C4/C5's were not) -- committed in the commit
               that carries this file; reader 1.6 may add them. Detector
               list + thresholds: DETECTORS_v0.1.md, thresholds frozen at
               G6-0 with the digest posted; classification adjudication:
               Harmonia (lane C), UNKNOWN_MECHANISM default.
  Proteus      world ABI stays A1 opaque channels: yes. Axis W adds
               channels, not a protocol: K action channels are K output
               channel indices, resources/objects/hidden state are input
               channel indices with world-defined encodings the organism
               never sees the meaning of; no v0 world changes. PROTEUS-43
               (open one new runtime profile) is the operator's; my
               recommendation is yes, with your s7 falsifiers as the
               profile's own kill rules.
  Harmonia     tranche plan with complexity bin + provenance label per
               run: TRANCHES_v0.1.md at G6-1 (bins = feature count of
               the world x organism profile x schedule class); detector
               specs for admission: DETECTORS_v0.1.md; escalation
               receipts in c6_observatory's shape (freezes, replays A-C,
               causal probes D-G, classification, preserved_at,
               classified_at): adopted as the receipt schema for my
               escalation flows; firing-table digest at close: yes.

4. RULINGS ONLY THE OPERATOR CAN GIVE (consolidated; defaults in brackets)
-----------------------------------------------------------------------
  R1  T0 anchored vs ingested                 [anchored; all seats]
  R2  cross-seat freezes (a freeze naming worlds another client owns)
                                              [PARTIAL with reason]
  R3  fixture keeper and who may author fixtures
                                              [Harmonia keeps; Harmonia +
                                              Nemesis author; Archaeon,
                                              Proteus, Vivarium never]
  R4  anchor interval = the loss bound       [1,000 evaluations]
  R5  schema 10 built before launch, or run on conventions naming the
      blind spots                             [schema 10 first; S1
                                              measurements on scratch now]
  R6  PROTEUS-43: open ONE new runtime profile (graph_organism.v1)
                                              [yes]
  R7  the recall threshold for the complexity ceiling, fixed before the
      reveal (Harmonia's ask)                 [planted detection >= .80
                                              with Wilson lower >= .60
                                              per complexity bin]
  R8  the resource ceiling (PLAN Q2)          [14 d / 28 cores / 100 GB /
                                              10,000 generations / 400
                                              scatter runs / >= 25%
                                              LLM-free by evaluations]
  R9  Phase 0 before any expansion search    [yes]

5. WHAT ARCHAEON BUILDS NEXT, IN ORDER (no ruling blocks 1-3)
-----------------------------------------------------------------------
  1  DETECTORS_v0.1.md -> code with UNABLE as first-class, calibration
     on C4/C5 lineages, thresholds frozen, admission packet to Harmonia
  2  the segment loop (EvolutionB generalized: pluggable world/organism
     profile/pressure schedule; checkpoint in/out; T0 rows; executor-
     side detector calls; freeze orchestration stub)
  3  AXIS W generator v0.1 (feature modules + procedural sampler +
     provenance) and AXIS P schedules v0.1, each with fixtures
  4  G6-0 receipt (observatory calibrated on the old substrate)
  5  TRANCHES_v0.1 (complexity bins, lanes, volumes) -> G6-1 with
     Proteus's profile and Vivarium's segment kind
+=====================================================================+
