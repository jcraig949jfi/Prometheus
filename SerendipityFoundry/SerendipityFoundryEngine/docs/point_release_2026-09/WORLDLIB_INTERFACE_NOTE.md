# WORLDLIB -- interface note (handoff, not scope; operator order s11)

    from   Daedalus (engine maintainer)        date  2026-09-17
    to     whoever builds the neutral shared world library (proposed home:
           SerendipityFoundry/SerendipityFoundryClient/sfclient/worldlib/;
           owner to be settled in the joint review -- Archaeon prototypes,
           the library absorbs what repeats, per amendment s1)
    status this is what the ENGINE offers and requires; it builds nothing.

WHY A LIBRARY AND NOT THE ENGINE. Queues, locks, channels, TTL stores,
resource pools, caches and buses are WORLD MECHANICS: their discipline
(FIFO vs LIFO, expiry, contention rule) is an experimental variable. Inside
the engine that variable becomes a hidden fitness landscape shared by
every world (charter standing order 1; amendment 5F accepted the
rejection). Inside a library it is code a world composes, versioned in the
world's manifest, and the engine only ever sees its FACTS.

=======================================================================
1. WHAT THE ENGINE EXPOSES TO A WORLD PRIMITIVE (schema 9)
=======================================================================

    need                          engine surface                                what it is / is not
    identity of the definition    WorldCreate.manifest + manifest_schema ->     the manifest is where a world says
                                  manifest_hash (sealed; GET .../manifest)      "queue Q: bounded 64, FIFO, expiry
                                                                                8 ticks, worldlib.queue/2". The
                                                                                engine hashes it; never reads it.
    a clock                       observations.logical_time; WORLD_EVENT.       unitless int; the manifest declares
                                  logical_time; termination.logical_time        the unit (logical_time_unit).
    factual world changes         POST .../events {kind, logical_time,          the ONLY generic write slot; kinds
                                  payload, refs} -> WORLD_EVENT, chained,       are the caller's; a manifest may pin
                                  idempotent under Idempotency-Key              them (declared_event_kinds).
    costs                         POST .../cost-events; budgets + reservations; the ledger of what was paid, in the
                                  GET .../cost-report                           world's declared units; the engine
                                                                                enforces limits, assigns no meaning.
    persistence of world objects  artifacts (content-addressed, origin,         a primitive's STATE that must outlive
                                  source lineage); checkpoints (head_hash +     a process goes here as an artifact
                                  state_hash); fork by reference                referenced from a WORLD_EVENT, never
                                                                                as engine tables.
    termination                   POST .../terminate {reason, logical_time,     the stop rule that fired, in the
                                  horizon, budget_consumed, reference}          world's vocabulary.
    reading it back               cursor pagination (after_seq) on events/      a consumer rebuilds any projection
                                  observations/experiments/artifacts;           from these without private client
                                  GET /v2/capabilities for limits + vocab       knowledge.

=======================================================================
2. WHAT A WORLDLIB PRIMITIVE MUST REPORT (the contract the engine can hold)
=======================================================================

    - Its definition in the manifest under a versioned key, e.g.
        "worldlib": {"queue.Q": {"impl": "worldlib.queue/2", "capacity": 64,
                                 "discipline": "FIFO", "ttl": 8}}
      so manifest_hash changes when the primitive's semantics change.
    - Every state transition that a downstream projection could need, as a
      WORLD_EVENT with a kind namespaced by the primitive
      ("queue.Q.enqueue", "queue.Q.expire", "lock.L.contend", ...), with
      logical_time and a payload of FACTS (counts, ids, sizes), never a
      verdict. Batch at the world's clock granularity when per-item events
      would flood (amendment 7E; the engine does not rate-limit).
    - Every cost it charges through cost-events in units the manifest
      declares ("messages", "bytes", "ticks_held"); a primitive that charges
      nothing must say so in its manifest entry (a free queue is a design
      choice, not an omission).
    - Its own state at checkpoint time as an artifact (kind
      "worldlib.state", meta {primitive, logical_time}) referenced from a
      WORLD_EVENT "checkpoint.state", so a fork can restore it. The engine's
      checkpoint state_hash covers row COUNTS + head hash, NOT primitive
      state; the library must not pretend otherwise.
    - Determinism: any randomness drawn from the world's seed_root through
      a declared derivation ("rng": "sha256(seed_root, primitive, tick)"),
      written in the manifest.

=======================================================================
3. WHAT STAYS OUTSIDE THE ENGINE, PERMANENTLY
=======================================================================

    - The mechanics themselves (data structures, discipline, expiry).
    - Any judgement about them (contention "high", queue "saturated").
    - Any coupling to organisms (what a message means to a genotype).
    - Scheduling: the engine's work queue is for engine-executed work
      items, not for a world's internal queue.

=======================================================================
4. HOW ITS VERSION / MANIFEST IDENTITY BECOMES REPRODUCIBLE
=======================================================================

    - The library ships a `describe()` per primitive that returns exactly
      the manifest entry it will honour, including its code version
      ("worldlib.queue/2" = a git-tracked implementation whose hash the
      library records in the entry as "impl_hash"). Two worlds with equal
      manifest_hash ran the same primitives at the same versions.
    - Vivarium's start bundle binds manifest_hash (its contract v0.1 row
      "world_version"); PEW's identity envelope carries it (7C). A
      counterfactual fork that changes a primitive's parameter changes the
      child's manifest_hash and appears in WORLD_FORKED.changed.

=======================================================================
5. SMALLEST FIRST STEP (if someone builds it)
=======================================================================

    One primitive, `worldlib.queue/1` (bounded FIFO with TTL), with:
    describe(), enqueue/dequeue/expire that emit WORLD_EVENTs and cost
    events through sfclient, snapshot()/restore() via an artifact, and a
    test that two worlds with the same manifest + seed produce
    byte-identical event payloads. Then measure whether Campaign 4 wants a
    second one before writing it.
