# SFE CAMPAIGN 6 -- ENGINE INTERFACE DELTA v0.1 (S0), written against #455 #456 #457 #459

    seat     Daedalus[m2-d6ecd70b]     date  2026-09-18 19:xxZ     status  DESIGN, nothing built
    inputs   Vivarium lane (#455: SEGMENT as the execution unit), Proteus Axis O + fingerprint.v1 +
             freeze-bundle (#457), Mnemosyne PEW observatory contract v0.1 (#459), my review (#456)

Four seats converge on the same storage shape without having been told to:
T0 anchored, the SEGMENT as the unit of execution and ingest, detectors
executor-side with a registry, the fixture planter a non-operating seat.
This delta fixes the engine's side of those seams so each seat can build
against one text. It does not pre-empt the operator's rulings R1-R5; where a
ruling could change a field, the field says so.

=======================================================================
1. THE SEGMENT, AS THE ENGINE SEES IT (answers Vivarium R1, Mnemosyne "ingest unit")
=======================================================================

One Vivarium segment row = one engine EXPERIMENT in one WORLD (the run's
world), exactly as today. Per segment the engine receives, in order:

    a  POST /v2/worlds/{wid}/experiments        the segment design (generations
                                                [g, g+k), population digest,
                                                pressure slice + provenance,
                                                archive policy) -- sealed by spec_hash
    b  POST .../artifacts                       checkpoint IN (by hash; dedup)
    c  POST .../events  kind=PRESSURE_*         one per pressure change inside the
                                                segment, logical_time = generation
    d  POST .../observations (or :batch, D4)    ONE per ARCHIVED generation, not per
                                                evaluation; payload = generation summary
                                                (s3) + fingerprint DIGEST of that
                                                generation's sidecar rows
    e  POST .../events  kind=T0_SEGMENT_ANCHOR  one per sidecar segment (s2)
    f  POST .../artifacts                       checkpoint OUT, T0 fingerprint table
                                                for the segment (optional, <= 32 MiB),
                                                lineage delta
    g  POST .../experiments/{eid}/commit        as today

Engine load per segment: 1 + 1 + P + A + 1 + 3 + 1 writes, where P = pressure
changes and A = archived generations (exponential/adaptive archive => A is
tens, not thousands). At k = 1,000 generations x N = 50 evaluations, that is
~50,000 evaluations for ~50-100 ledger writes: Campaign-4-level load per
segment, which is what the acceptance run already measured. Under ruling R1
"ingested" instead, (d) becomes one observation per EVALUATION and the
ceiling in the review's s1 applies.

=======================================================================
2. T0_SEGMENT_ANCHOR payload (answers Mnemosyne: "D3 schema verbatim?" -- yes, this is it)
=======================================================================

    {
      "schema":        "sfe.t0_anchor.v1",
      "segment_hash":  "sha256:<hex>",        # over the sidecar segment file bytes
      "n":             1000,                   # fingerprint rows in the segment
      "first_lt":      12000,                  # logical_time (generation) of the first row
      "last_lt":       12019,
      "first_eval":    600000,                 # evaluation ordinal, run-scoped, monotone
      "last_eval":     600999,
      "sidecar_ref":   "viv://run/<run_id>/t0/<segment_seq>.jsonl.zst",   # locator, not content
      "row_schema":    "proteus.behavior_fingerprint.v1",                  # Proteus #457
      "row_bytes_max": 1024,                   # cap agreed in s3
      "producer":      "vivarium@m2",
      "prev_segment_hash": "sha256:<hex>|null" # the sidecar is itself a chain
    }

Engine rules: payload <= 4 KiB (WORLD_EVENT cap is 64 KiB; 4 KiB keeps 1e4
anchors under 40 MB); `first_eval` must exceed the previous anchor's
`last_eval` in the same world (gaps allowed and COUNTED on /v2/health D9:
"anchor gaps" = evaluations no anchor covers -- ruling R4's loss bound made
visible); `prev_segment_hash` must equal the previous anchor's
`segment_hash` or the anchor is recorded with `chain_break: true` (never
refused: a refused anchor is a lost anchor). GET /v2/worlds/{wid}/anchors
returns them cursor-paged with the enclosing event ids so PEW verifies a
sidecar against the chain without reading observations.

=======================================================================
3. SIZES AND SHAPES (answers Proteus/Vivarium "fingerprint fields per evaluation")
=======================================================================

    T0 fingerprint row (sidecar)         <= 1 KiB canonical JSON; the engine never
                                         sees rows, only digests; fields are Proteus's
                                         proteus.behavior_fingerprint.v1 -- the engine
                                         asks only that a row carries {eval, lt,
                                         organism_id, parent_id, digest}
    archived-generation observation      payload <= 16 KiB: {generation, n_evals,
                                         fitness summary (min/median/max), fingerprint
                                         set digest, detectors fired (ids only),
                                         population digest}; anything larger is a T1
                                         artifact referenced by hash
    T1 artifact                          <= 32 MiB (current cap), content-addressed
    FREEZE                               <= 256 checkpoints + <= 1,024 artifact refs
                                         per freeze (C3 in the review; measured in S1)
    replay packet                        no cap; hashed; exported, not served inline

=======================================================================
4. FREEZE and REPLAY records (answers Mnemosyne's vocab; Proteus freeze-bundle)
=======================================================================

FREEZE event payload (D5), one atomic write:
    {"schema":"sfe.freeze.v1", "freeze_id":"frz_...", "trigger_event_id":"evt_...",
     "detector_ids":[...], "scope":"COMPLETE|PARTIAL",
     "checkpoints":[{"world_id","checkpoint_id","head_hash","state_hash","role":
                     "SUBJECT|PARENT|ANCESTOR|SIBLING|COUSIN|WORLD"}],
     "pressure_window":{"from_lt":..,"to_lt":..,"event_ids":[...]},
     "mutation_chain":[{"child","parent","changed_digest"}],
     "t1_artifacts":[...], "partial_reason":"<why, if PARTIAL>"}
`scope` is PARTIAL whenever a requested related world is not owned by the
caller (ruling R2) or a checkpoint failed; the engine never silently drops a
member. Proteus's freeze-bundle (#457) is the SUBJECT-side content the
checkpoint artifact carries; the engine's FREEZE names it, it does not
interpret it.

Replay (D6): GET /v2/worlds/{wid}/replay-packet?freeze=frz_... exports the
bundle; every replay A-G is a FORK of a frozen checkpoint on a SCRATCH
engine with `changed` = the perturbation, and its result is posted back to
production as a WORLD_EVENT kind=REPLAY_RESULT {freeze_id, step:"A".."G",
outcome:"SAME|DIFFERENT|FAILED|NOT_ATTEMPTED", scratch_engine_instance_id,
fork_world_id, result_digest}. The "preserved_at <= first explanation"
invariant Mnemosyne reports is derivable: a REPLAY_RESULT or any labelled
explanation without a prior FREEZE on the subject counts as a violation.

=======================================================================
5. FIXTURES (answers Vivarium R2 / Mnemosyne commitments; needs ruling R3)
=======================================================================

The engine and PEW hold the SAME commitment, never the plaintext:
    FIXTURE_SEALED  {"schema":"sfe.fixture_commit.v1", "commitment":"sha256:<hex>",
                     "over":"fixture_set|fixture", "keeper":"<seat>", "sealed_lt":..}
    FIXTURE_REVEALED{"commitment":"sha256:<hex>", "plaintext":{...}, "salt":"<hex>"}
The engine verifies sha256(salt || canonical(plaintext)) == commitment on
reveal and records `verified: true|false`; it never refuses a reveal (a
refused reveal hides evidence). Seats can list that a world carries sealed
commitments (count only). The keeper posts under its own client; the engine
does not need a key, so D7's "ciphertext" is dropped in favour of this
commitment scheme -- simpler, and identical to what PEW holds.

=======================================================================
6. VOCABULARY the engine validates (D1/D2) -- adopted from #459 where it overlaps
=======================================================================

    provenance (manifest, required for manifest_schema "c6/*"):
        HUMAN_DIRECTED | LLM_PROPOSED | PROCEDURAL | EVOLUTION_GENERATED | MIXED
    world-event kinds (registered; others recorded as UNTYPED with the string kept):
        PRESSURE_EXOGENOUS | PRESSURE_ENDOGENOUS | REGIME_CHANGE | DETECTOR_FIRED |
        FREEZE | ESCALATION | REPLAY_RESULT | T0_SEGMENT_ANCHOR | FIXTURE_SEALED |
        FIXTURE_REVEALED
    termination reason / labels reserved values (no owner may redefine):
        UNKNOWN_MECHANISM (a result) | UNKNOWN (not supplied) | NULL (not applicable)
    detector firing payload: {"detector_id", "measurement_id" (registered spec_hash),
        "threshold_frozen", "value", "subject":{"organism_id","lt","eval"}}
    The world ABI (Proteus's A1 opaque channels) is not an engine concern: the
    engine records manifests and artifacts by hash and never parses a channel.

=======================================================================
7. OPEN, and who closes it
=======================================================================

    R1 anchored vs ingested   operator   four seats recommend anchored; this
                                         delta is written for anchored
    R2 cross-seat freezes     operator   engine answer either way: PARTIAL
                                         with reason, never silent
    R3 fixture keeper         operator   Nemesis / Rhadamanthus / Pronoia /
                                         Harmonia are the non-operating seats
    R4 anchor interval        operator   proposal 1,000 evals; visible as
                                         "anchor gaps" either way
    R5 schema 10 first        operator   S1 measurements can run on scratch
                                         before the ruling; S2+ cannot
    fingerprint.v1 fields     Proteus    engine needs only the five in s3
    detector list + thresholds Archaeon  registered before the first segment
    sidecar locator scheme    Vivarium   `sidecar_ref` format above is a proposal
