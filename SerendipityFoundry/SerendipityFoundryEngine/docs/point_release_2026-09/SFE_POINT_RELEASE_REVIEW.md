# SFE POINT RELEASE -- REVIEW (Stage 0 evidence inventory, Stage 1 delta, Stage 2 self-critique)

    seat        Daedalus (maintainer, Serendipity Foundry Engine)
    instance    m2-d6ecd70b
    date        2026-09-17
    mode        READ-ONLY. Campaign 3 is active on the production substrate
                (eng_906356f7, https://192.168.1.191:8811, build 4dbcd3fd at
                dd10c9074). Nothing below is deployed; nothing touches the
                engine, its schema, its routes or its data.
    directive   roles/Mnemosyne/prompts/2026-09-17_point_release/
                  00_OPERATOR_DIRECTIVE.md   sha256:0c6ab59e0846fe09...
                  01_OPERATOR_AMENDMENT_1.md (verbatim, MANIFEST beside it)
                The amendment supersedes the directive where they conflict;
                amendment section 5 is the scope this review answers.
    engine      surveyed at dd10c9074 (the deployed tree): 68 routes, 24
                tables, schema 8. Every "exists today" claim below was read
                from that tree, not from memory.

Status vocabulary used throughout: CODE_FIXED != SERVICE_DEPLOYED !=
LIVE_VERIFIED != QUALIFIED. Everything in this document is at most a
proposal; nothing is CODE_FIXED.

=======================================================================
STAGE 0 -- EVIDENCE INVENTORY
=======================================================================

0.1  What the three campaigns said about the engine (measured)

    campaign  attempts of record  engine errors  worlds  reads across
                                                         sessions/campaigns
    C1        10 (14 attempts)    0 on record*   ~40     403 once (L-026)
    C2        10 (13 live)        0 in 13        18      worked (6/6 hash ok)
    C3        3 closed so far     0              1+      worked; 405 on a
                                                         route that does
                                                         not exist (#325)
    * C1 superseded attempts: SFE-01 a1 (422 extra field, L-006), SFE-07
      a1 (403 SESSION_MISMATCH, L-026). Neither reached the record.

    Source: archaeon/campaign1/CAMPAIGN_REPORT.md s5/s7/s13,
    archaeon/campaign2/CAMPAIGN_REPORT.md s10/s13,
    archaeon/campaign3/MACHINE_READINESS.md, JOURNAL.md, comms #325.

    Reading: the engine path was not the failure surface in any campaign.
    The directive's premise for SFE ("not a gratuitous rewrite") is
    measured, and the amendment's narrowing (s5) is the correct
    consequence. This review is therefore mostly INSTRUMENT and
    GENERALIZE, three FIXes, and a list of what already exists that the
    directive assumed was missing.

0.2  Engine-owned defects and requests, traced to ledger rows

    row     campaign  class      what                       recurrence  status today
    L-006   C1        BUG        422 on an extra field       0           strict bodies are BY
                                 ('evidence') on POST                    DESIGN (DFX-4); the
                                 /v2/worlds/{w}/failures                 client stopped
                                                                         forwarding it. Engine
                                                                         side: CONSISTENCY +
                                                                         DISCOVERY, not leniency
                                                                         (amendment 5C).
    L-026   C1        BUG        403 SESSION_MISMATCH on a   0           C2 reports cross-
                                 same-client, wrong-session             session and cross-
                                 read in ADVISORY mode; the             campaign reads worked.
                                 same read with NO key was              So the rule exists and
                                 admitted                                is UNDOCUMENTED in the
                                                                         contract. Amendment 5C.
    L-009   C1        FRICTION   digest form mismatch        1 (SFE-03)  client-side; Archaeon's
                                 (artifact id vs blob hash)              digest.py fixed it (C2).
                                                                         Engine: none.
    L-001   C1        FRICTION   no read wrappers            0           client; Archaeon added
                                                                         three (C3 group E).
    L-012   C1        MISSING_   rerun re-created all        3           Idempotency-Key exists
                      RECOVERY   engine objects                          on 9 of 34 mutating
                                                                         routes (A6 census
                                                                         2026-09-12); Archaeon's
                                                                         runner sends it since
                                                                         C2 (verified). Engine:
                                                                         none for this release.
    L-013   C1        OBSERV.    no attempt tag on world     1 (SFE-07)  worlds carry name +
                                 creation (14 cmp1-sfe01-*               seed_root only.
                                 worlds after two attempts)              Candidate: `attempt`
                                                                         label (amendment 5A,
                                                                         "if the ownership
                                                                         review agrees").
    L2-021  C2        BUG        resume replayed another     0           Archaeon runner (design-
                                 design's engine steps                   keyed keys). Vivarium
                                                                         absorbs (amendment 6B).
                                                                         Engine: none.
    L3-015  C3        BUG        import_fetch dst == src on  0           correct refusal by the
                                 an ISOLATED world -> 403                engine (a self-import is
                                 isolation_violation                     not an import); harness
                                                                         fixed. Engine: none.
    #325    C3        REQUEST    GET /v2/worlds/{wid}/       --          route absent (405).
                                 artifacts absent                        Amendment 5C, first
                                                                         item.

0.3  What the campaigns built ABOVE the engine (the empirical spec)

    mechanic (owner: Archaeon)              where                           campaigns   survived
    reachability table + levels             archaeon/wse/reachability.py    C2, C3      yes; levels
    FLOOR/SHELF/SUMMIT, first_*_gen,                                                    added C3 A,
    summit_censored, stopped_on_solve                                                   held-out rule
                                                                                        D3-006
    right-censored stopped runs             same, lookup(G) monotone        C3 B        yes
    corridor table                          archaeon/wse/corridor.py        C3 C        yes (73 rows
                                            campaign3/CORRIDOR.jsonl                    from C2)
    dense transition probes                 telemetry.probe_plan,           C3 D        yes
                                            transition_events
    inject + offspring cap + per-ask        wse/evolve.py                   C3 F        yes; caveat
    credit; origin shares per generation                                                (cap is on
                                                                                        descent)
    numbered attempts, design-keyed         campaign2/runner.py,            C2, C3      yes; the
    replay, receipt per step, ATTEMPTS.json ATTEMPTS.json                               thing
                                                                                        Vivarium
                                                                                        absorbs
    common random numbers, common fill,     wse/evolve.py                   C2, C3      yes
    gen0 provenance in the trace
    engine descriptor (base_url + cacert    archaeon/engine_descriptor.py   C2, C3      yes; reads
    from the deploy pin)                                                                DEPLOYED_
                                                                                        BUILD_M2.json
    typed failure states -> dispositions    c2base / c3base                 C2, C3      yes; L3-039
                                                                                        crash on
                                                                                        uninformative
                                                                                        rows

    Governing model (amendment s1): none of these is promoted into the
    engine by this release. The engine's job is to hold the FACTS these
    projections are built from, so that any of them can be rebuilt from
    the ledger without parsing freeform rows. Where a fact is missing
    today, that is an engine item (0.5).

0.4  What already exists in the engine that the directive assumed missing

    directive asked for                     exists today (dd10c9074)
    checkpoint identity                     POST /v2/worlds/{w}/checkpoint ->
                                            checkpoint_id, world_index,
                                            head_hash, state_hash (content
                                            hash of a state snapshot) +
                                            CHECKPOINT_CREATED event
    fork-from-state, immutable start,       POST /v2/worlds/{w}/fork: children
    explicit changed-condition metadata     share the parent's event prefix by
                                            reference; per-child seed_root,
                                            sharing_policy, topology_group;
                                            `interventions` recorded verbatim
                                            in WORLD_FORKED (never interpreted)
    parent_world, fork_point                worlds.parent_world_id,
                                            worlds.fork_point; on GET
                                            /v2/worlds/{w} and list_worlds
    immutable artifacts + provenance        artifacts: content-addressed,
                                            origin NATIVE|IMPORTED, source_
                                            world, source_artifact, import_seq
                                            (charter rule 4)
    costs explicit and observable           budgets, budget_reservations,
                                            cost_events, GET .../cost-report
    lineage                                 lineage_edges, GET .../lineage
    idempotent posts                        idempotency_keys on 9 mutating
                                            routes incl. observations,
                                            artifacts, failures
    measurements (declared value_path,      measurements table; /v2/read/
    direction, range; resolved server-      observations?measurement=...
    side)                                   resolves per row
    experiment identity beside observations spec_hash + committed_seq on
                                            /v2/read/observations (4dbcd3fd,
                                            2026-09-16, #223)
    attestation of what the ledger cannot   A6 intent journal, /v2/work/
    record                                  {id}/attestation, /v2/health
    tamper-evident event chain              events.head_hash, POST
                                            /v2/audit/verify-anchor
    lease/heartbeat on work                 work_items claim/heartbeat/
                                            complete/fail

    Consequence: amendment 5A's "parent_world, fork_point, checkpoint state
    digest" are DONE items, not delta. Listed so nobody re-implements them.

0.5  What is missing, as facts (not interpretations)

    fact                         today                                  who needs it
    logical time on an           inside freeform observation.content    reachability first_*_gen,
    observation (generation)     (runner's own keys); not a column,     censoring, transition
                                 not queryable                          probes, PEW projections
    typed world termination      terminate_world(): state -> TERMINATED, reachability (stopped_on_
    (reason, budget consumed,    event WORLD_TERMINATED, no payload      solve, right-censoring),
    horizon)                                                            PEW WORLD_TERMINATED
    stamped generic world        none. Fork `interventions` is the only  pressure/phase history
    events (phase change,        freeform-but-sealed slot; cost_events   (PEW raw events), the
    pressure applied/removed,    is cost-shaped                          runner's rung schedule
    intervention applied)
    world manifest envelope      WorldCreate = session_id, name,         manifest identity in
    (manifest, manifest_schema,  sharing_policy, topology_group,         every receipt; PEW
    manifest_hash)               budget, seed_root, require_attestation  identity envelope
    child-vs-parent changed-     WORLD_FORKED carries the child's         counterfactual replay
    field diff on fork           settings + interventions; the DIFF is   ("what changed")
                                 left to the reader
    artifact listing per world   POST + GET content by id only (#325)    harness verification
    supplied lineage-share       Archaeon computes origin_shares per     PEW LINEAGE_SHARE_
    observation                  generation into its trace rows; not     OBSERVED
                                 on the engine
    cursor pagination            GET .../events: limit only (default     any run beyond a few
                                 100, newest first); GET .../             thousand events per
                                 observations: NO limit (returns all);   world; PEW ingestion
                                 GET .../experiments: no limit;          checkpoints (amendment
                                 /v2/read/observations: limit only        7D)
    documented read/session      advisory mode: L-026 rejected one read   contract; every reader
    semantics                    and admitted the same read with no key
    capability/vocabulary        /v2/openapi.json + /v2/version;          consumers that today
    discovery                    vocabularies only via the contract       parse the contract
                                 generator's probe
    long-run storage facts       events 129K (M1 ledger, 09-12); M2       retention decision
                                 ledger young; NO measurement at 10x;    (amendment 5D)
                                 C9 burst stall was storage-bound (fixed
                                 by NVMe), never re-run at hour scale
    restart/reconnect/duplicate  harness 12 + isolation 7 are short       long-run confidence
    fixture                      probes; test_sfe_a6_wiring covers one   (amendment 5D)
                                 lock timeout; no restart-mid-run test

0.6  Manual decisions that can safely become deterministic (engine side)

    - "which build is production" -> the deploy pin + /v2/version (done;
      the C1 campaign spent half a decision on it, D-002).
    - "did the artifact I posted land" -> artifact listing (#325).
    - "what generation was this observation" -> a typed column, not a
      convention in content.
    - "why did this world stop" -> a typed reason, not the absence of
      further events.

0.7  Scientific discretion that MUST remain above the engine

    thresholds (0.45, 0.90, 0.5 foothold), level names, censoring rules
    (lookup(G) monotonicity), corridor definitions, ladder schedules,
    injection caps and dose choice, per-ask credit, dispositions
    (CAPABLE_NEGATIVE etc.), "generalization", "takeover", "forgetting".
    The engine must be able to STORE the facts each of these consumes and
    must never compute any of them. (Charter standing order 1; amendment s2.)

=======================================================================
STAGE 1 -- PROPOSED DELTA
=======================================================================

Every item: problem/evidence, change, owner, consumers, compatibility,
migration, science-validity risk, ops risk, cost, acceptance, rollback.
Classification per amendment s12. All routes additive; every schema change
is a nullable column or a new table; schema_version 8 -> 9 in ONE window.

-----------------------------------------------------------------------
D1  logical_time on observations and events                 MUST SHIP  INSTRUMENT
-----------------------------------------------------------------------
    evidence     0.5 row 1; reachability/censoring/transition probes all
                 key on generation, read today from runner-specific
                 content keys (campaign2/runner.py record()).
    change       observations.logical_time INTEGER NULL; ObservationCreate
                 gains optional `logical_time: int`; returned on both
                 observation read routes; world events gain an optional
                 `logical_time` in payload for D3 events. Unit is the
                 caller's (generation, tick, step) and is DECLARED in the
                 manifest (D4) -- the engine stores an integer, never a
                 meaning.
    owner        SFE (column); the meaning: manifest owner.
    consumers    Archaeon runner (writes), reachability (reads), PEW
                 ingestion (reads).
    compat       additive, nullable; old rows read NULL = NOT_SUPPLIED.
    migration    ALTER TABLE ADD COLUMN; reversible (column ignored by
                 the old build; schema 9 refuses to run under build 8 by
                 the existing have > SCHEMA_VERSION guard).
    sci risk     none if NULL is never read as 0. Acceptance test pins it.
    ops risk     negligible.
    cost         8 bytes/row.
    acceptance   unit: round-trip, NULL preserved, rejected if non-int;
                 read route returns it beside spec_hash/committed_seq.
    rollback     column stays, unread.

-----------------------------------------------------------------------
D2  typed world termination                                 MUST SHIP  INSTRUMENT
-----------------------------------------------------------------------
    evidence     0.5 row 2; C3 group B (right-censoring) reconstructs
                 "stopped on solve at G" from runner receipts because the
                 engine's WORLD_TERMINATED carries nothing.
    change       POST /v2/worlds/{w}/terminate accepts an OPTIONAL body
                 {reason: str (caller vocabulary, declared in manifest),
                 logical_time: int|null, budget_consumed: dict|null,
                 horizon: int|null, note: str|null}; recorded in the
                 WORLD_TERMINATED payload and on worlds.termination (JSON,
                 NULL for old rows). No enum in the engine: the vocabulary
                 is the manifest's; the engine validates shape only.
    owner        SFE (slot); vocabulary: manifest owner / Archaeon.
    consumers    reachability (censoring), PEW WORLD_TERMINATED, Vivarium
                 attempt terminal state.
    compat       the route today takes no body; a body-less call still
                 works (termination = NULL = NOT_SUPPLIED). Strict body
                 when present (DFX-4).
    migration    ADD COLUMN, reversible.
    sci risk     a caller writing reason="SUMMIT" would be smuggling an
                 interpretation; the engine cannot stop it and should not
                 try. Mitigation: the contract says `reason` is a fact
                 about the STOP RULE ("budget_exhausted", "stop_rule:
                 first_solve", "operator"), not about the outcome; PEW's
                 ingestion contract (Mnemosyne 7A) is where a reason
                 vocabulary gets pinned.
    ops risk     none.
    acceptance   unit + harness: terminate with and without body; event
                 payload carries it; old worlds read NULL.
    rollback     ignore the column.

-----------------------------------------------------------------------
D3  stamped generic world events                            MUST SHIP  GENERALIZE
-----------------------------------------------------------------------
    evidence     0.5 row 3; C2/C3 rung schedules, pressure ramps, inject()
                 timing and phase changes live only in trace rows; the
                 directive's PRESSURE_APPLIED / PHASE_CHANGED / INTERVENTION_
                 APPLIED families have no producer on the engine (amendment
                 7B: only families with a producer).
    change       POST /v2/worlds/{w}/events {kind: str, logical_time:
                 int|null, payload: dict, refs: dict|null, idem key}. The
                 engine appends event_type "WORLD_EVENT" with the caller's
                 `kind` inside the sealed payload (so the engine's own
                 event-type enum is untouched and old readers see one new
                 type, not N). `kind` must be one of the kinds the world's
                 manifest declares (D4) if a manifest is present; free
                 otherwise. Never interpreted.
    owner        SFE (the slot and its sealing); kinds: manifest owner.
    consumers    Archaeon (ladder/inject/phase), PEW raw events, Vivarium
                 (import realized-dose receipt, amendment 6G).
    compat       new route; new event_type value; readers that switch on
                 event_type must tolerate an unknown value (they already
                 must: CHECKPOINT_CREATED was added after the first
                 readers).
    migration    none (events table unchanged).
    sci risk     the classic one: a kind named "SHELF_REACHED" posted by a
                 harness becomes "evidence". Mitigation: the engine
                 records actor + client_id + logical_time and the
                 manifest's declared kinds; PEW classifies RAW vs
                 PROJECTION by producer, not by name (Mnemosyne 7B). The
                 engine does not police names.
    ops risk     a chatty caller could post per-organism-per-generation
                 events (amendment 7E warns against this at PEW). The
                 engine's answer is the existing budget/cost machinery
                 and pagination (D8), not a rate limit in this release.
    cost         one event row per post.
    acceptance   unit: sealed in the chain (verify-anchor sees it),
                 idempotent under a repeated key, refused when kind is not
                 declared by a present manifest, refused on a TERMINATED
                 world.
    rollback     route removed = contract DRIFT; so it ships in the window
                 with the contract regeneration, never alone.

-----------------------------------------------------------------------
D4  world manifest envelope                                 MUST SHIP  GENERALIZE
-----------------------------------------------------------------------
    evidence     0.5 row 4; every campaign world's definition lives in
                 Archaeon code; no receipt can name "which world
                 definition" except by campaign+cell name.
    change       WorldCreate gains optional `manifest: dict`,
                 `manifest_schema: str` (author's versioned name, e.g.
                 "archaeon.wse.world/3"); the engine computes
                 manifest_hash = content_hash(manifest) and stores all
                 three on the world row; manifest is IMMUTABLE after
                 creation; fork children inherit unless the child supplies
                 one (then the WORLD_FORKED payload carries both hashes --
                 that IS the changed-field diff for the manifest, D6).
                 The engine validates the ENVELOPE only: manifest is a
                 JSON object <= 256 KiB, manifest_schema is a non-empty
                 string, and OPTIONALLY the reserved key
                 `declared_event_kinds: [str]` (consumed by D3) and
                 `logical_time_unit: str` (documentation for D1). Nothing
                 else is read.
    owner        SFE (envelope); content: the manifest_schema's owner.
    consumers    Archaeon (writes), PEW identity envelope (manifest_hash
                 = "exact world" coordinate), Vivarium start bundle
                 (binds manifest_hash).
    compat       optional; old worlds have NULLs.
    migration    three ADD COLUMNs.
    sci risk     low; the engine understands nothing in it. The risk is
                 the reverse: a manifest that is decorative (posted but
                 not what the harness actually ran). Mitigation: Archaeon's
                 receipt should carry manifest_hash and the prereg seals
                 it; the engine can only guarantee immutability.
    ops risk     size bound stated.
    cost         <= 256 KiB per world.
    acceptance   unit: hash stable across key order; immutable (second
                 write refused); fork inheritance; oversize refused.
    rollback     columns unread.

-----------------------------------------------------------------------
D5  GET /v2/worlds/{wid}/artifacts                          MUST SHIP  FIX
-----------------------------------------------------------------------
    evidence     #325; C3 readiness group E PARTIAL.
    change       list artifacts of a world: artifact_id, kind, blob_hash,
                 origin, source_world, source_artifact, created_seq, meta
                 (no bytes); owner-scoped like the other world GETs;
                 `kind` and `origin` filters; cursor (D8).
    owner        SFE. consumers: Archaeon harness verification; Vivarium
                 artifact registry join.
    compat       additive route (+1 contract route; gates read added
                 routes as INCOMPLETE-covered, never DRIFT -- measured
                 #256 row C5).
    migration    none.  sci/ops risk  none.  cost  none.
    acceptance   harness: post 3, list 3, filter by kind, foreign world 403.
    rollback     n/a.

-----------------------------------------------------------------------
D6  fork: changed-field diff                                SHOULD SHIP IF CHEAP  INSTRUMENT
-----------------------------------------------------------------------
    evidence     0.4/0.5: WORLD_FORKED records the child's settings and
                 interventions verbatim; the reader computes the diff.
    change       WORLD_FORKED payload gains `changed: {field: {parent,
                 child}}` over seed_root, sharing_policy, topology_group,
                 manifest_hash, budget; `interventions` stays verbatim.
                 Payload-only; no schema change.
    risk         none; cost: payload bytes.
    acceptance   unit: fork with one change -> exactly one entry.
    why cheap    ~30 lines in fork(); ships with D4 or not at all.

-----------------------------------------------------------------------
D7  attempt label on world creation                         SHOULD SHIP IF CHEAP  INSTRUMENT
-----------------------------------------------------------------------
    evidence     L-013 (recurrence 1); amendment 5A "if the interface
                 ownership review agrees".
    change       WorldCreate gains optional `labels: dict[str,str]` (bounded:
                 <= 16 keys, <= 64 chars each) stored on the world row;
                 list_worlds filters by label. Named `labels`, not
                 `attempt`, because attempt identity is Vivarium's
                 (amendment 6B) and the engine should hold an opaque
                 coordinate, not own the hierarchy.
    ownership    to be settled in Stage 3 with Vivarium: if Vivarium's
                 attempt id is what goes in labels.attempt, the engine
                 never mints one. If the review says the engine should
                 not carry it at all, DROP.
    risk         a label used as a filter is not a scientific grouping;
                 the contract says so.
    acceptance   unit: round-trip, filter, bound refused.

-----------------------------------------------------------------------
D8  cursor pagination on list routes                        MUST SHIP  HARDEN
-----------------------------------------------------------------------
    evidence     0.5 row "cursor pagination": observations and experiments
                 lists are UNBOUNDED; events is newest-100-only. Amendment
                 5D first item; PEW ingestion checkpoints (7D) need a
                 monotone cursor.
    change       GET .../events, .../observations, .../experiments,
                 .../artifacts (D5), /v2/read/observations: `after_seq:
                 int` + `limit: int` (<= 1000), ascending by created_seq /
                 world_index; response gains `next_after_seq` (null at
                 end). Default behaviour UNCHANGED when neither param is
                 given (events keeps newest-100 DESC; observations keeps
                 all -- but with a stated ceiling of 10,000 and a `truncated:
                 true` flag beyond it, which is a behaviour change only
                 for worlds nobody has yet built).
    compat       optional params; response gains keys (readers ignore).
    sci risk     none. ops risk: none.
    acceptance   unit: 2,500 rows walked in 3 pages, no gap, no repeat;
                 ceiling flag.
    rollback     params ignored.

-----------------------------------------------------------------------
D9  documented read/session semantics + capability discovery  MUST SHIP  FIX / INSTRUMENT
-----------------------------------------------------------------------
    evidence     L-026 (advisory mode admitted a keyless read and refused
                 a wrong-keyed one); C1 rec. 9; amendment 5C items 2-4.
    change       (a) write the rule down in the engine (docs) and in the
                 contract generator's output as `session_affinity.reads`
                 = {no_key: ADMITTED, wrong_key: REFUSED_421, matching:
                 ADMITTED} per enforcement mode -- Harmonia's generator
                 already derives scoping by probe; this adds the READ
                 semantics as a derived row, not an assertion. (b) GET
                 /v2/capabilities: schema_version, session_enforcement,
                 science_profile, max_artifact_bytes, vocabularies the
                 engine OWNS (outcomes, evidence classes, sharing policies,
                 world states, event types incl. WORLD_EVENT), limits
                 (pagination ceiling, manifest size), and `features`
                 flags for D1-D8 so a client can negotiate. Strict bodies
                 stay strict (amendment 5C: do not loosen). (c) a
                 consistency test: every mutating route refuses an unknown
                 field with the SAME error type (L-006 was 422 on one
                 route; the test asserts all 34).
    compat       additive route; docs.
    acceptance   contract test: capabilities == what /v2/version +
                 openapi + probe derive; consistency test 34/34.

-----------------------------------------------------------------------
D10 long-run storage measurement and retention DECISION     MUST SHIP  INSTRUMENT (measure), DEFER (retention)
-----------------------------------------------------------------------
    evidence     amendment 5D; C9 (2026-09-11) measured a storage-bound
                 burst stall and fixed it by volume; nothing measured at
                 hour scale or at 10x rows. Events are append-only,
                 forever, and MUST stay so on the production ledger (the
                 chain is tamper-evident; retention = truncation of
                 evidence, which is a policy act, not an engineering one).
    change       a measurement, not a feature: deploy/longrun_load.py
                 drives a scratch engine (loopback, disposable ledger)
                 through an accelerated multi-hour-equivalent profile
                 (N worlds x G generations of observations + events +
                 artifacts + checkpoints + one fork; producer/reader
                 concurrency as in C9) and records: p95/max latency per
                 route vs row count, WAL size, DB size per 100K events,
                 read latency of paginated walks at 1M events, /v2/health
                 write_lock waits. Output: a table in
                 docs/point_release_2026-09/SFE_BENCHMARK_RECEIPT.md.
                 Retention: DECISION RECORDED as "none in this release;
                 revisit when the measurement shows a knee", with the
                 knee's numbers.
    risk         none (scratch only).
    acceptance   the table exists with real numbers and the knee (or its
                 absence) is stated.

-----------------------------------------------------------------------
D11 restart / reconnect / duplicate-post / checkpoint fixture  MUST SHIP  HARDEN
-----------------------------------------------------------------------
    evidence     amendment 5D items 4-5; today's battery is 12 + 7 short
                 probes; A6 covers one lock timeout; no test kills the
                 engine mid-run.
    change       test_harness/longrun_restart.py against a scratch engine:
                 (1) a producer mid-stream, engine process killed and
                 relaunched, producer reconnects, resumes with the same
                 idempotency keys -> no duplicate rows, chain verifies;
                 (2) the same POST sent twice and thrice concurrently ->
                 one row, same ids; (3) checkpoint at G, fork two children,
                 continue all three, verify-anchor on each; (4) a client
                 whose session lease expires mid-run (advisory today: the
                 test documents what happens, it does not assert a
                 policy). Runs on the M2 twin-style scratch, never on
                 production.
    acceptance   4/4 shapes recorded with counts; any failure is a FINDING
                 with a shape, not a red X.

-----------------------------------------------------------------------
D12 supplied lineage-share observations                     DEFER TO NEXT POINT RELEASE
-----------------------------------------------------------------------
    evidence     amendment 5E lists it; Archaeon computes origin_shares per
                 generation into trace rows (C3 F); nobody has asked the
                 engine to hold it.
    reasoning    D1 + D3 already give the slot: a WORLD_EVENT of kind
                 "lineage_share" with logical_time and a payload IS a
                 supplied observation, sealed and queryable by D8. A
                 dedicated column/table would be a second way to say the
                 same thing. Revisit if PEW's ingestion (Mnemosyne 7A)
                 needs it typed.

-----------------------------------------------------------------------
D13 world objects as engine services                        REJECT (accepted by amendment 5F)
-----------------------------------------------------------------------
    queues, locks, channels, TTL stores, buses: NOT engine services.
    sfclient/worldlib (a reviewed neutral location) owns experimental
    mechanics; the engine owns generic event (D3) and cost (existing)
    semantics. I will review worldlib's use of cost_events and WORLD_EVENT
    but not author the mechanics.

-----------------------------------------------------------------------
D14 QD / landscape projection route                         DEFER (accepted by amendment 5G)
-----------------------------------------------------------------------
    library/projection first over D1 + D8 + measurements; promote only on
    two independent consumers needing the identical server projection.

-----------------------------------------------------------------------
D15 universal FLOOR/SHELF/SUMMIT, thresholds, corridors     REJECT
-----------------------------------------------------------------------
    per amendment s2 and charter rule 1. Not in any route, column, enum or
    field name. The acceptance test for D2/D3/D4 includes a negative: the
    engine has no string "SHELF" or "SUMMIT" outside tests and docs.

-----------------------------------------------------------------------
D16 idempotency-key coverage on the remaining 25 mutating routes   DEFER
-----------------------------------------------------------------------
    A6 census 2026-09-12: 9 of 34 accept a key; the campaign runner sends
    keys on the routes that matter (observations, artifacts, failures).
    Widening is cheap but unasked; revisit when Vivarium's step
    idempotency (amendment 6B) names which routes it needs.

Summary table

    id   item                                   class        ship
    D1   logical_time                           INSTRUMENT   MUST
    D2   typed termination                      INSTRUMENT   MUST
    D3   stamped generic world events           GENERALIZE   MUST
    D4   manifest envelope                      GENERALIZE   MUST
    D5   GET artifacts list                     FIX          MUST
    D6   fork changed-field diff                INSTRUMENT   SHOULD IF CHEAP
    D7   world labels (attempt)                 INSTRUMENT   SHOULD IF CHEAP; ownership in Stage 3
    D8   cursor pagination                      HARDEN       MUST
    D9   read/session semantics + capabilities  FIX/INSTR.   MUST
    D10  long-run measurement; retention        INSTRUMENT   MUST (measure) / DEFER (retention)
    D11  restart/duplicate/checkpoint fixture   HARDEN       MUST
    D12  supplied lineage-share slot            --           DEFER (D3 covers it)
    D13  world objects in the engine            --           REJECT
    D14  QD projection route                    --           DEFER
    D15  universal levels/thresholds            --           REJECT
    D16  idempotency on all routes              --           DEFER

    Schema: 8 -> 9 (D1, D2, D4, D7: nullable columns only). Routes: +4
    (D3 POST events, D5 GET artifacts, D9 GET capabilities, D2 terminate
    body -- an existing route gaining an optional body is a contract
    "change" row in Harmonia's model; to be checked with her generator).
    One deploy window after Campaign 3 closes; one contract regeneration;
    consumers' gates read INCOMPLETE-covered, not DRIFT, on additions.
    Rough size: ~600 lines engine + ~900 lines tests/fixtures + docs.

=======================================================================
STAGE 2 -- SELF-CRITIQUE
=======================================================================

    question                                        verdict on the delta
    Does this encode the answer to a scientific     No item stores a level, threshold or
    question?                                       disposition. D2's `reason` is the closest
                                                    edge: KEEP with the contract wording
                                                    "reason describes the stop rule, not the
                                                    outcome"; MODIFY: add a negative test that
                                                    the engine never sets it.
    Does it turn an interpretation into fact?       D3 lets a caller name an event anything.
                                                    KEEP: the engine records provenance, PEW
                                                    classifies by producer. The alternative
                                                    (an engine-side allowlist of kinds) IS the
                                                    engine deciding what counts -- worse.
    Could it contaminate old results?               All columns nullable, all routes additive,
                                                    old rows read NOT_SUPPLIED. KEEP. MODIFY
                                                    D8: the observations ceiling (10,000 +
                                                    truncated flag) is the one behaviour change
                                                    for unbounded reads; state it in the
                                                    contract and test that no existing world
                                                    exceeds it at deploy time.
    Future-information leakage?                     D6's diff and D4's inheritance expose only
                                                    the parent's settings at fork time, which
                                                    the child already had. KEEP.
    New abstraction: more flexible or merely        D3 + D4 are two small generic slots replacing
    more complex?                                   N special cases (pressure, phase, inject,
                                                    ladder). D7 (labels) is the weakest: it is a
                                                    convenience for list_worlds. MODIFY: D7 ships
                                                    only if Stage 3 names a consumer that reads
                                                    it; otherwise DROP.
    Survives long runs, partial failures,           D8 + D11 exist to answer this rather than
    restarts, duplicated messages?                  assume it. D11 is the test; D10 the
                                                    measurement. KEEP both as MUST.
    State reconstructable after a crash?            Unchanged by this release (SQLite WAL, chain,
                                                    A6 journal). D11 case (1) verifies it.
    Expensive telemetry nobody will query?          D12 dropped for exactly this. D10 writes a
                                                    table once, not a stream. D9's capabilities
                                                    route is read by the contract generator on
                                                    every regeneration -- it has a consumer.
    Generic enough for worlds not yet imagined?     D3/D4 carry opaque payloads with declared
                                                    kinds; D1 is a unitless integer. The engine
                                                    learns nothing about worlds. KEEP.
    What did I leave out that the directive         Snapshot "replay eligibility": Vivarium's
    wanted and I should defend leaving out?         start bundle owns it (amendment 6C); the
                                                    engine exposes checkpoint head_hash +
                                                    state_hash and that is the coordinate.
                                                    ADD to D9's capabilities: `checkpoint.
                                                    state_hash_definition` so the bundle can
                                                    cite what the digest covers (today: counts
                                                    + head hash, NOT organism state -- the
                                                    engine never holds organism state).

    Result: KEEP D1-D5, D8-D11; MODIFY D2 (negative test), D7 (consumer
    named or drop), D8 (ceiling in contract + deploy-time check), D9
    (state_hash definition); DROP nothing further; ADD nothing further.

=======================================================================
STAGE 3 -- WHAT I NEED FROM THE OTHER SEATS (peer review inputs)
=======================================================================

    Vivarium    D7 ownership (does labels.attempt carry YOUR attempt id, or
                nothing); D2 termination shape vs your attempt terminal
                state; D3 as the realized-import receipt slot (6G); which
                routes your step idempotency needs keys on (D16).
    Mnemosyne   D3 event shape vs your RAW families (7B): is WORLD_EVENT
                with caller `kind` + logical_time + actor sufficient for
                RAW classification by producer; D8's after_seq as your
                ingestion checkpoint (7D); D4's manifest_hash and D2's
                termination as identity-envelope coordinates (7C).
    Proteus     nothing in this delta touches organisms; confirm that
                D4's manifest may reference a foundry profile id by value
                and that the engine should NOT validate it.
    Archaeon    (arbiter, s9) the D1 unit question -- generation vs tick
                -- is declared per manifest, not per engine; and whether
                D3's declared-kinds check (refuse undeclared kinds when a
                manifest is present) is a help or a nuisance to the runner.
    Harmonia    contract model: does an existing route gaining an OPTIONAL
                body (D2) read as "changed" in conformance_check? If yes,
                D2 ships as a new route (POST .../terminate-with) instead.

=======================================================================
NOT SHOWN / LIMITS
=======================================================================

    - No line of this is implemented; sizes are estimates.
    - The engine survey is of the deployed tree dd10c9074; the M1 archive
      ledger was not consulted (unreachable, and not production).
    - Campaign 3 is still running; its CAMPAIGN_REPORT.md, when it lands,
      is authoritative over the journal I read and may add rows to 0.2.
    - Proteus has not reviewed; Stage 3 cannot close without it.
