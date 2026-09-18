# SFE CAMPAIGN 6 -- THE ENGINE AS OBSERVATORY: REVIEW, ENVELOPE, DELTA

    seat      Daedalus[m2-d6ecd70b]          date  2026-09-18 18:4xZ
    against   directive "SFE CAMPAIGN 6 -- CAMBRIAN EXPANSION / OBSERVATORY STRESS"
    engine    9.0.1 (699ca0f9 at b0d752183), schema 9, production on M2 NVMe
    status    REVIEW (Stage 0-2, read-only). Nothing built, nothing deployed.
              Campaign 5 is CLOSED (#451); no campaign is running.

The directive's own success condition is the engine's job description:
"It fails if increasing generative complexity makes SFE scientifically
blind." The engine does not evolve anything. It is the place where a
world, an organism history, a pressure history and a detector firing
become an immutable, hash-chained, replayable FACT that a seat which did
not run the experiment can re-derive. Everything in this review is the
question: at Campaign 6 volumes, does that remain true?

=======================================================================
0. WHAT THE ENGINE HOLDS TODAY, MAPPED ONTO THE FOUR AXES
=======================================================================

The organisms, worlds, mutations and pressure schedules of axes W/O/P are
Proteus's substrate and Archaeon's search. The engine's obligation on each
axis is a RECORD obligation, and schema 9 already carries most of it:

    axis W  "complete generative provenance of every world"
            -> world manifest envelope (manifest + manifest_schema + manifest_hash,
               <= 256 KiB, sealed at creation); labels; fork `changed` diff.
            GAP: no vocabulary for "who chose this world" (the five provenance
            classes) -- today that is a caller convention inside the manifest.
    axis O  "a child must retain enough ancestry metadata to reconstruct
             exactly what changed"
            -> the engine can guarantee this only for what it is GIVEN: a
               fork records parent, fork_point and the changed fields; an
               organism's genotype diff is an artifact Proteus writes. The
               engine anchors it by hash; it cannot verify the diff is complete.
    axis P  "preserve the exact pressure history for every lineage;
             EXOGENOUS vs ENDOGENOUS"
            -> WORLD_EVENT (v9): caller-described, sealed in the chain, with
               logical_time. A pressure schedule is a sequence of these.
            GAP: no typed kind vocabulary; EXOGENOUS/ENDOGENOUS is a caller
               string today. Cheap to make a validated enum in `kind`.
    axis T  fingerprints, tiers, detectors, freezes, replay packets
            -> observations (payload, logical_time, measured-by), artifacts
               (<= 32 MiB, content-addressed), checkpoints (head/state hash),
               measurements registry (POST /v2/measurements: a detector IS a
               registered measurement with a spec_hash), typed termination,
               labels, forks for counterfactuals.
            GAPS: see s2. The big one is not a feature; it is VOLUME (s1).

=======================================================================
1. THE ENVELOPE, FROM MEASUREMENT (not from hope)
=======================================================================

Everything below is from deploy/LONG_RUN_2026-09-17/ on the shipped build,
ledger on the NVMe:

    write lock            one writer at a time; 5.7 ms max wait at 2 gen/s
    saturating throughput 100-240 generations/s (R1-R3), ~4 events/generation
                          -> ~400-900 ledger events/s ceiling, single process
    bytes                 ~1.07 KB of ledger per event (127 MB / 123,990 events);
                          blobs beside it (175 MB for 300 artifacts in R0N)
    WAL/checkpoint        bounded at campaign rate on NVMe (1.9 MB); on the
                          SMR HDD it was the thing that failed -- C6 does not
                          go back to D:
    restart               2 s; anchors verify; identity stable through kills
    read side             cursor pages, 10,000-row cap; a full event walk of
                          124K events took 3.7 s

Now the directive's shape. Campaign 4 wrote ~1,152 observations in a
rehearsal and ~6,000 rows in the whole campaign. Campaign 6 asks for "a
compact behavioral fingerprint for EVERY evaluated organism", long runs,
"archive densely around events". Three honest scenarios, per run:

    scenario   evals/run   T0/eval into the LEDGER as one observation each
    C6-small   1e5         1e5 obs = ~4e5 events = ~430 MB, ~7 min at 240/s;
                           fine, ~10 min per run at the saturating rate
    C6-mid     1e6         4e6 events = ~4.3 GB, ~1.2-2.8 h per run at
                           saturation -- the ledger is the bottleneck of
                           evolution, not the VM; five runs = a day and 21 GB
    C6-long    1e7+        43 GB per run, ~12-28 h of pure ledger writing;
                           SQLite holds it, but every full walk, backup,
                           contract regeneration and restart cost scales
                           with it (restart cost already scaled with WAL)

Conclusion that decides the design: T0 per evaluation CANNOT be one ledger
write per evaluation at C6-mid and above. The ledger is a single-writer
hash chain; that property is exactly what makes it trustworthy and exactly
why it must not be the T0 firehose. The observatory has to be TIERED IN
STORAGE, not only in richness:

    T0  streams to a sidecar (append-only per-run fingerprint files, one
        row per evaluation, content-hashed in fixed-size segments) and the
        LEDGER holds the anchors: one WORLD_EVENT per segment carrying the
        segment hash, count, first/last logical_time. Nothing is lost,
        everything is verifiable, and the ledger write rate becomes
        1 per segment (e.g. per 1,000 evals) instead of 1 per evaluation.
    T1  ARTIFACTS, content-addressed, attached to the world and referenced
        from the escalation event (the richer trace around an unusual event)
    T2  the existing fork + checkpoint + labels + typed termination, plus
        the parent/ancestor/sibling worlds' checkpoints -- the FREEZE is a
        set of checkpoints and a FREEZE world event that names them
    T3  a replay packet = a fork of the frozen checkpoint with `changed`
        naming the perturbation (exact replay: changed = {}; rollback:
        changed = {mutation: ...}; ablation; pressure perturbation); the
        engine already records the diff, so "what was perturbed" is a fact

With that split the engine's C6 budget is: escalations x (T1 artifact
bytes) + segments x 1 event + the normal experiment/observation traffic of
the seats' science rows -- which is Campaign-4 shaped and measured.

=======================================================================
2. ENGINE DELTA FOR CAMPAIGN 6 (proposed; needs the operator's order)
=======================================================================

Schema-additive, nullable, same shape as the schema-9 release; every item
has a test grep for the forbidden-narrative words rule (no
SHELF/SUMMIT/... in engine source) and nothing here names a phenomenon.

    D1  provenance class on the manifest envelope: `provenance` in
        {HUMAN_DIRECTED, LLM_PROPOSED, PROCEDURAL, EVOLUTION_GENERATED, MIXED},
        validated, filterable on list_worlds, REQUIRED when manifest_schema
        starts with "c6/". The 25% LLM-free floor becomes a census query on
        the ledger, not a claim in a report.
    D2  world-event kind vocabulary (validated, extensible by registration):
        PRESSURE_EXOGENOUS, PRESSURE_ENDOGENOUS, REGIME_CHANGE, DETECTOR_FIRED,
        FREEZE, ESCALATION, T0_SEGMENT_ANCHOR, FIXTURE_SEALED, FIXTURE_REVEALED.
        A caller may still post an unregistered kind; it is recorded as
        kind=UNTYPED with the string preserved (unknown stays a valid value).
    D3  T0 segment anchor: a WORLD_EVENT payload schema {segment_hash, n,
        first_lt, last_lt, sidecar_ref} plus GET /v2/worlds/{wid}/anchors
        (cursor-paged) so a third party can verify a sidecar file against
        the chain without reading observations.
    D4  batch observations: POST /v2/worlds/{wid}/observations:batch, up to
        N rows in ONE transaction and one event per row -- the write lock is
        taken once per batch; measured single-row cost is dominated by lock
        + fsync, so this is the cheapest 10x available. Keyed per batch.
    D5  freeze as a first-class act: POST /v2/worlds/{wid}/freeze -> takes a
        checkpoint of THIS world and, given a list of related world ids the
        caller owns (parent, ancestors, siblings), checkpoints those too in
        one transaction and writes one FREEZE event naming every checkpoint
        hash, the triggering DETECTOR_FIRED event id and the recent pressure
        events. It is the escalation protocol's steps 1-8 as one atomic
        engine fact, so "explain before preservation is complete" cannot
        happen by accident: the freeze id is required by the replay routes.
    D6  replay packet: GET /v2/worlds/{wid}/replay-packet?freeze=<id> ->
        one content-addressed bundle (manifest, lineage to root with every
        `changed` diff, pressure events, checkpoints, referenced artifacts
        by hash, T0 anchors in the window). Exported once, hashed, importable
        on a scratch engine (the existing keyed import) -- replay A-G run on
        a scratch engine from the packet, never on production.
    D7  sealed fixtures: FIXTURE_SEALED events whose payload is stored
        ENCRYPTED to a keeper key the engine does not hold (the engine stores
        ciphertext + hash; reveal = the keeper posts FIXTURE_REVEALED with
        the plaintext, the engine verifies the hash). The campaign seats can
        list that a sealed fixture exists in a world (so the census is
        honest) but cannot read what it is. Ownership model unchanged.
    D8  retention: an engine-side archive policy for T1/T2 material by
        world -- nothing deleted, but artifacts older than a window and not
        referenced by any FREEZE move to cold blob storage with the hash
        staying in the chain. Needed for C6-long; not for C6-small.
    D9  observatory health on /v2/health: sidecar anchor lag, escalations
        open, freeze count, blob bytes, oldest unreferenced artifact --
        "scaling health" as a readable number, not a feeling.

NOT in the engine: detectors (they are measurements registered by the seat
that runs them, with a spec_hash; the engine records firings and never
scores "interestingness"); organism structure (Proteus); the sidecar
writer itself (the evaluator's side, with a shared segment format we agree
in the interface delta); world generators.

=======================================================================
3. HOW MUCH STRANGER CAN SFE SAFELY BECOME -- the engine's half of the answer
=======================================================================

The engine cannot tell you when the SCIENCE goes blind; it can tell you
exactly when the RECORD does, and those are the ceilings to pre-register:

    C1  ledger events per second: ~400-900 sustained, single writer. Above
        it, the queue backs up, latency climbs, and (measured, 9.0) the
        request path starts timing out. Everything per-evaluation goes to
        the sidecar or it does not fit.
    C2  ledger size: full walks, backups and contract regeneration are
        linear in it; restart cost was linear in WAL. Pre-register a size
        at which a run's material is exported (D6) and the run's world
        terminated, e.g. 20 GB per engine, and measure the walk time at
        each doubling rather than assuming.
    C3  artifact bytes per escalation: 32 MiB cap per artifact today; a T2
        freeze of a deep lineage with dense neighborhoods can be hundreds
        of artifacts. Cap per freeze in the interface delta and measure.
    C4  detector fan-out: 11 detectors x every evaluation cannot each post
        an event; they post only firings above a FROZEN threshold, and the
        threshold is registered (measurement spec_hash) before the run.
        Detector disagreement is a firing of a 12th detector, not a query.
    C5  the reader: a paced cursor reader at 0.5 s/page cost nothing at 2
        gen/s (R0N); at C6-mid a seat re-reading a 4e6-event world through
        10,000-row pages is 400 requests per pass. Fine. Ten seats doing it
        during a saturating writer is not measured; measure it before
        launch (the C4 rule: acceptance at the campaign's real rate, longer
        than any prior defect's onset).

The engine's recommendation for the FIRST complexity ceiling: C6-small
shapes (1e5 evals per run, T0 to sidecar with 1,000-eval anchors, T1/T2 in
the ledger) on the current engine plus D1-D6, with a measured acceptance
run at 3x the planned rate before launch. Raise to C6-mid only after the
observatory recall fixtures have been scored once at C6-small: "a planted
event that is missed is more important than a natural anomaly that is
found" applies to the ledger too -- a missed anchor is a blind spot.

=======================================================================
4. PUSH-BACK AND RULINGS I NEED (each one changes what gets built)
=======================================================================

    R1  T0 placement. If the operator wants every fingerprint IN the ledger
        (not anchored), the ceiling is C6-small and the campaign is ledger-
        bound. My recommendation is the sidecar + anchor design (s1). Rule.
    R2  Freeze scope crosses ownership. "Freeze the parent, ancestors,
        siblings" is one client's worlds today (a campaign seat owns its
        lineage). If lineages span seats, D5 needs a grant-like consent or
        the freeze is partial and says so. Rule whether cross-seat freezes
        exist in C6.
    R3  Fixture keeper. D7 needs a seat that plants fixtures, holds the key
        and is NOT Archaeon/Proteus/Vivarium. Nemesis (cheat-control lane) or
        Harmonia fit. Rule who.
    R4  Sidecar custody. T0 files are evaluator-side; if the evaluator host
        dies, unanchored segments are lost. The anchor interval is the
        loss bound; 1,000 evals is my proposal. Rule the bound.
    R5  Freeze before the campaign: this is a schema bump (10) and a point
        release with the same discipline as schema 9 (preflight, backup,
        qualification, long-run at C6 rate, contract regeneration,
        Harmonia's promotion). Campaign 6 cannot start on 9.0.1 + conventions
        without giving up D3/D5/D6/D7 -- the parts that make recall and
        forensics machine-checkable. Rule: build first, or run C6 on
        conventions and accept the blind spots as named.

=======================================================================
5. WHAT I WILL DO ON AN ORDER (stages, each with a receipt)
=======================================================================

    S0  this review; interface delta with Proteus (sidecar segment format,
        fingerprint size cap), Archaeon (freeze/replay flows), Harmonia
        (contract), Mnemosyne (PEW reads anchors, not fingerprints),
        Vivarium (batch route, freeze in the consumer's retry model)
    S1  measure before building: T0 ingest shapes on a scratch engine
        (single-row vs batch vs anchor-only) at 1e5 and 1e6 evals; the
        numbers in s1 become measured, not projected
    S2  schema 10 in the worktree, tests, NOT deployed
    S3  point release with the schema-9 discipline; acceptance long run at
        the C6 rate (>= 3x planned, >= 4 h, on the NVMe)
    S4  observatory recall dry run: a keeper plants three sealed fixtures on
        a scratch engine, the freeze/replay routes are driven end to end,
        and the recovery matrix is produced by a seat that did not plant
    S5  freeze pin; Campaign 6 launch gate item "engine" GREEN by evidence

Nothing above is started. The engine stays 699ca0f9 until ordered.
