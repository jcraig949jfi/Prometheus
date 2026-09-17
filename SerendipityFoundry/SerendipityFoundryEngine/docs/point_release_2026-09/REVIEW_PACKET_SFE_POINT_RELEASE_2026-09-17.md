=======================================================================
REVIEW PACKET -- SFE POINT RELEASE (schema 8 -> 9), 2026-09-17
=======================================================================
seat        Daedalus (maintainer of the Serendipity Foundry Engine)
instance    m2-d6ecd70b, on M2 / SPECTREX5 (192.168.1.191)
status      DEPLOYED and QUALIFIED on production at 10:51:30Z; one
            measurement (long-run load) still running at packet time
audience    an external reviewer with no repository access; every claim
            below names the file that carries its numbers
attack this the way you would attack a result: every "verified" line
            says HOW; anything said without a HOW is a claim, not a fact

-----------------------------------------------------------------------
0. BACKGROUND -- WHAT THE SFE ECOSYSTEM IS (for an external reader)
-----------------------------------------------------------------------

Prometheus is a research program whose question is whether an evolutionary
substrate can produce genuinely new computational capability, and -- more
to the point of this packet -- whether the INSTRUMENTS around it can tell a
real effect from an artifact of the instrument. It runs as a fleet of
role-bound agents ("seats"), each with a charter, a journal and a comms
inbox, on two machines: M1 hosts the shared Postgres/Redis; M2 hosts the
SFE ecosystem. Seats coordinate through a Postgres-backed message queue
("comms"); every claim ships with its raw rows in git.

The SFE ecosystem, four layers, four owners:

  SFE  (Serendipity Foundry Engine; seat Daedalus)
       The instrument. An HTTP/TLS service in front of one SQLite ledger.
       A "world" is an isolated experimental universe with a tamper-evident
       hash-chained event log; inside it a client registers experiments,
       commits them (an irreversible boundary), records observations,
       stores content-addressed artifacts, checkpoints, and forks children
       that share the parent's event prefix by reference. Multi-tenant:
       clients cannot see, mutate or starve each other's worlds even
       knowing their ids (an isolation battery proves it). The engine's
       standing order: RECORD THE WORLD FAITHFULLY, INTERPRET NOTHING.

  Archaeon  (scientific consumer)
       Designs and runs campaigns of preregistered experiments against
       the engine through a runner it built and refined over three
       campaigns; owns the scientific definitions (reachability levels,
       thresholds, corridor tables, dispositions).

  Vivarium  (durable execution)
       Queue/attempt/replay machinery; has NOT executed campaigns 1-3 (the
       runner did); is absorbing the runner's proven semantics.

  PEW / Mnemosyne  (evidence wiki)
       The empirical memory: immutable evidence, rebuildable projections.
       Holds zero campaign rows today; ingestion is its point release.

  Proteus  (organisms)  -- the players; untouched by this release.

What preceded this release: three campaigns (C1 2026-09-16, C2 09-17
00:21Z, C3 09-17 07:55Z) against this engine on this ledger. Engine
errors on attempts of record: 0, 0, 0. The engine-owned defects across
all three: a 422 on an extra field (strict bodies are by design), an
undocumented advisory-session read rule, no attempt tag, no artifact
listing route. Everything else the campaigns found was above the engine.
The operator then issued a backend point-release directive, an amendment
narrowing every seat's scope on the strength of the seats' read-only
reviews, and an implementation + deploy order once C3 closed.

-----------------------------------------------------------------------
1. THE RELEASE IN ONE PARAGRAPH
-----------------------------------------------------------------------

The engine gained the FACTS the science layer had to reconstruct from
prose and freeform rows -- when (a logical clock), why a run stopped, what
changed in the world and when, which world definition ran, which attempt
this world belongs to -- plus an artifact listing, cursor pagination on
every list, and a self-description route. Schema 8 -> 9 by six nullable
columns, no backfill. Four routes added, none changed, none removed. It
refused, mechanically, every interpretation: the words SHELF, SUMMIT,
CORRIDOR, TAKEOVER and GENERALIZATION do not occur in engine source, and a
test fails the build if they ever do.

-----------------------------------------------------------------------
2. WHAT SHIPPED (each: what it is / what it is NOT)
-----------------------------------------------------------------------

 D1 logical_time on observations      a non-negative integer the caller
                                       supplies; the UNIT is declared by the
                                       world's manifest (generation, tick,
                                       episode); NULL = not supplied, never
                                       0; sealed in the OBSERVATION_RECORDED
                                       event. NOT a generation counter the
                                       engine maintains.
 D2 typed termination                  POST .../terminate accepts an optional
                                       strict body {reason, logical_time,
                                       horizon, budget_consumed, reference,
                                       note}; `reason` is the STOP RULE that
                                       fired ("horizon", "stop_rule:first_
                                       solve"), in the caller's vocabulary.
                                       NOT an outcome; the engine never sets
                                       one. Why it matters: C3's "0 summits
                                       in 60 runs" is interpretable only if
                                       each run's horizon is on record.
 D3 sealed generic world events        POST .../events {kind, logical_time,
                                       payload, refs} -> ONE engine event
                                       type, WORLD_EVENT, chained and
                                       idempotent. Kinds are the caller's;
                                       a world may pin its own kinds via the
                                       manifest and undeclared ones are then
                                       refused. NOT an engine vocabulary of
                                       pressure/phase/intervention types.
                                       Why: C3 found import takeover is
                                       injection MECHANICS; the realized
                                       dose must be a recorded fact.
 D4 manifest envelope                  WorldCreate.manifest + manifest_schema
                                       -> engine computes manifest_hash,
                                       seals it in WORLD_CREATED, keeps it
                                       immutable, serves it back on GET
                                       .../manifest; fork children inherit or
                                       override. Validated for SHAPE and SIZE
                                       (<= 256 KiB) only. NOT understood.
 D5 GET /v2/worlds/{w}/artifacts       list, filters, cursor, no bytes.
                                       Closes C3's one PARTIAL readiness item.
 D6 fork changed-field diff            WORLD_FORKED.changed = {field:
                                       {parent, child}} over seed, policy,
                                       topology, manifest_hash, labels.
 D7 labels                             opaque str->str (<=16 x 64) on a world;
                                       ?label=k=v filter. The attempt id in it
                                       is minted ABOVE the engine (Vivarium /
                                       Archaeon); the engine carries it.
 D8 cursor pagination                  after_seq + limit on events,
                                       observations, experiments, artifacts,
                                       read/observations; ascending by the
                                       row's global sequence; next_after_seq
                                       null = end of stream; the historical
                                       unbounded answer is capped at 10,000
                                       with truncated=true. Ingestion
                                       checkpoint for PEW: save next_after_
                                       seq; a duplicate delivery re-reads the
                                       same rows with the same ids.
 D9 capabilities + read semantics      GET /v2/capabilities (no auth, no
                                       session): the engine's own vocabularies,
                                       limits, feature flags, checkpoint
                                       digest definition, and the advisory-
                                       session read rule (no key ADMITTED and
                                       audited; wrong key REFUSED) -- written
                                       into tests. Strict bodies stay strict;
                                       a test posts an unknown field to every
                                       mutating route and asserts 422 on all.
 D10 long-run measurement              tool + numbers (section 5); retention
                                       DECISION "none", with the numbers that
                                       would change it.
 D11 restart/duplicate/checkpoint      a standing fixture against a REAL
     fixture                           engine process: kill -9 mid-run,
                                       relaunch, identity/chain/cursor/anchor
                                       intact; 16/16 shapes; part of
                                       qualification.

 REFUSED  world objects (queues/locks/TTL stores) as engine services --
          they would make the engine the fitness landscape; a handoff note
          for a neutral world library is written instead.
 REFUSED  any universal level / threshold / corridor concept (order s4).
 DEFERRED QD projection route (library first); idempotency keys on the
          remaining 25 mutating routes (nobody has named them).
 SUPERSEDED a dedicated lineage-share table -- D3 carries the fact.
 ALREADY EXISTED (struck from the delta after surveying the deployed
          tree, not memory): parent_world_id, fork_point, checkpoint
          head_hash + state_hash, fork-by-reference, cost events, lineage,
          attestation, verify-anchor, idempotent posts on 9 routes.

-----------------------------------------------------------------------
3. HOW IT WAS DEPLOYED (order of operations, with the one refusal)
-----------------------------------------------------------------------

 tests            505 passed on the merged tree (483 -> 505)
 scope freeze     SFE_INTERFACE_DELTA.md committed BEFORE code; deviations
                  recorded as amendment lines A1-A3, never absorbed
 contract form    RESOLVED EMPIRICALLY: Harmonia's contract generator run
                  on two scratch engines of the candidate emits the
                  terminate route with required_body [] -> UNCHANGED; the
                  surface delta is exactly +4 routes. The generator REFUSES
                  a pre-deploy contract across a schema bump by design, so
                  the production contract is regenerated after the restart.
 preflight #1     REFUSED. 36 events in the prior 10 min, last one 16 s old:
 10:40:51Z        a 7-second burst from four throwaway clients (pewC4-...,
                  lineage-...) registered from this host by some seat's
                  fixture. "Campaign closed" != "nobody is writing". A
                  broadcast asked for quiet and for fixtures to use a
                  scratch engine.
 preflight #2     8/8 PASS: production ledger eng_906356f7 at schema 8; pin
 10:50:54Z        agrees with the running build; release commit resolves and
                  its tree hashes to a NEW build (bc8d3a0c); 0 events in
                  10 min; 0 work in flight; SQLite-API backup written and
                  re-opened (integrity ok, 10,995 events; identical sha256
                  to the refused run's backup -- nothing changed between)
 apply            pinned worktree advanced to 1b9286292; running process
 10:50:59Z        (child + launcher parent) killed; the pinned supervisor
                  started the new one; migration 8 -> 9 ran at first open.
                  Outage 20.3 s.
 identity check   12/12: process NEW (pid 8140 -> 5596; start 09-16 17:22Z
                  -> 09-17 10:51:30Z); engine instance UNCHANGED; source
                  hash == candidate; schema 9 live AND in the ledger; routes
                  68 -> 72; ledger path + bind unchanged; events 10,995 ==
                  10,995; capabilities advertises every feature. Descriptor
                  pin rewritten.
 contract         regenerated against live + a loopback scratch probe of
                  the same build; traps/bounds/policy byte-identical modulo
                  stamps; landed with a provenance block naming the
                  operator's order; gate 0 plain, 0 with Vivarium's 24 +
                  Archaeon's 1 declared routes; previous file kept beside
                  the receipts
 qualification    20/20 held on PRODUCTION (deploy/qualify_v9.py):
                  - 351 pre-v9 worlds read NULL manifest/labels/termination
                  - 1,622 pre-v9 observations read logical_time NULL
                  - head hashes of the 25 oldest worlds == the backup's
                  - event count up to the backup's last seq identical
                  - 20/20 pre-migration observation anchors verify
                  - capabilities; manifest round-trip; logical_time write/
                    read; events ordered + idempotent duplicate + undeclared
                    kind refused; pagination traversal == single page and
                    resume from a cursor exact; artifact list; checkpoint
                    digest + fork ancestry + changed diff; advisory read
                    semantics 200/403/422; typed termination + 409 after
                  - harness 12/12; isolation 7/7; contract gate 0
                  - D11 fixture in running-engine mode: 15/15
 rollback         written BEFORE deploy (R1-R6 in the migration receipt);
                  NOT exercised; the schema-8 build refuses a schema-9
                  ledger by design, so rollback = restore the verified
                  backup, never "old build on new ledger"

-----------------------------------------------------------------------
4. THE ARCHITECTURAL ACCEPTANCE TEST (order s12)
-----------------------------------------------------------------------

 tests/test_sfe_v9_campaign_fixture.py builds a Campaign-3-shaped run
 through the public routes: a manifest carrying the CALLER's thresholds
 ("SHELF_MIN": 0.45, "SUMMIT_MIN": 0.90); 100 generations with
 logical_time; a curriculum ladder as WORLD_EVENTs at generations 0/31/
 56/81; an import at generation 40 with INTENDED dose 4 and REALIZED dose
 3; dense probes; a checkpoint and a population artifact at 60; a
 counterfactual fork under a different schedule; termination at 99 of a
 declared horizon 120 (censoring-relevant). A downstream consumer that
 knows only the read routes and cursors rebuilds: the exact manifest and
 its hash, the generations, every pressure change with its time, the
 intended-vs-realized gap, ancestry (parent, fork_point, exactly which
 field changed), the horizon and that the run ended before it, the
 artifacts, the complete chained event history -- and applies ITS
 threshold to the engine's facts to find the first generation at or
 above 0.45. The engine's source contains none of the five words; the
 caller's words travel through it unchanged as opaque bytes. PASSES.

-----------------------------------------------------------------------
5. LONG-RUN MEASUREMENT (D10) -- PENDING AT PACKET TIME
-----------------------------------------------------------------------

 Shape: 20 worlds x 1,000 generations (1 experiment + commit +
 observation per generation, a WORLD_EVENT every 10, a checkpoint every
 50, an 8 KiB artifact every 100, a fork and a typed termination per
 world), 2 producer threads + 1 cursor-reader thread on one scratch
 engine of the shipped build, disposable ledger on the production volume
 class (D:). Then a full paginated event walk, kill -9 at full history,
 relaunch, anchor sample. Target ~20,000 observations / ~85,000 events:
 the size the previous production ledger reached in two weeks, and ~10x
 Campaign 3's per-run rows.

 Interim, at 11:06Z (30 min in): 12,327 observations, 50,955 events, DB
 ~50 MB, 0 HTTP 5xx, 0 stalls > 5 s in the producer thread logs.
 Throughput under 2 producers + a reader: ~300-400 observations/min
 (~130 ms per generation, i.e. three sequential POSTs at ~15-40 ms each
 through one SQLite writer). Small-scale run (2 x 60) for the route
 latency shape: POST observations p50 17 ms, p95 34 ms; checkpoint 5 ms;
 relaunch to /v2/version 0.5 s; identity same after restart; anchors
 50/50.

 The final table (per-route p50/p95/max by quarter of the run, DB bytes
 per 100K events, checkpoint latency, restart cost at full history,
 write_lock waits) is appended to SFE_LONG_RUN_REPORT.md when the run
 ends (~25 min) and the packet file is amended. Retention decision stated
 there from the numbers; today's prior: "forever" is fine at this scale
 and the ledger is tamper-evident, so retention would be a policy act.

-----------------------------------------------------------------------
6. WHAT WOULD FALSIFY THIS PACKET
-----------------------------------------------------------------------

 - Any consumer's conformance gate reading DRIFT against the landed
   contract (it reads 0; declared-route consumers read INCOMPLETE-covered
   on additions by Harmonia's #256 measurement).
 - A pre-v9 row reading a non-NULL v9 fact (351 worlds / 1,622
   observations checked; a backfill would be manufacturing facts).
 - A head hash of any pre-migration world differing from the backup's
   (25 checked; all 351 could be checked in seconds -- ask).
 - The long-run run showing a latency knee, a stall > 5 s, or a 5xx --
   then the retention/storage decision changes and section 5 says so.
 - The five-word grep failing on a future commit (it already caught my
   own docstring once; that is the point of it).
 - The one thing NOT independently verified: I wrote the tools that
   graded my own deploy (release_v9.py, qualify_v9.py). The shapes they
   assert are simple enough to re-derive from the JSON receipts by hand,
   and Harmonia's gate and the pre-existing harness/isolation batteries
   are not mine.

-----------------------------------------------------------------------
7. NOT SHOWN / LIMITS
-----------------------------------------------------------------------

 - POST scoping is not re-probed by the contract gate (its stated limit).
 - Stage 3 closed on the answers in hand: Mnemosyne and Vivarium
   answered; Proteus (not yet reviewed), Archaeon and Harmonia were
   resolved by the least-committal reversible default and recorded as
   such. The arbiter may overturn: unit-per-manifest and declared-kind
   strictness are both one-line reversals.
 - No consumer has yet written a v9 fact on production; the numbers above
   are the engine's own fixtures. The first real use is Campaign 4's.
 - Who owns the pewC4/lineage fixture that hit production is unknown to
   me; the broadcast asked, nobody has answered yet.

-----------------------------------------------------------------------
8. POINTERS (all under SerendipityFoundry/SerendipityFoundryEngine/)
-----------------------------------------------------------------------

 docs/point_release_2026-09/SFE_POINT_RELEASE_REVIEW.md    Stage 0-2
 docs/point_release_2026-09/SFE_INTERFACE_DELTA.md         frozen scope + A1-A3
 docs/point_release_2026-09/SFE_SCHEMA9_MIGRATION_RECEIPT.md  + rollback
 docs/point_release_2026-09/SFE_DEPLOYMENT_RECEIPT.md      before -> after
 docs/point_release_2026-09/SFE_RESTART_RECEIPT.md
 docs/point_release_2026-09/SFE_RELEASE_PACKET.md          every item classified
 docs/point_release_2026-09/WORLDLIB_INTERFACE_NOTE.md     the refused mechanics' handoff
 deploy/POINT_RELEASE_2026-09-17/{preflight,apply,qualify}.json, gate_*.txt,
     contract/, sfe_contract.PREVIOUS_schema8.json, longrun_restart_production.json
 deploy/release_v9.py, deploy/qualify_v9.py, deploy/longrun_load.py
 ../SerendipityFoundryClient/test_harness/longrun_restart.py
 tests/test_sfe_v9_facts.py, test_sfe_v9_read_surface.py, test_sfe_v9_campaign_fixture.py
 roles/Harmonia/contracts/sfe_contract.json (landed, provenance block `landed`)
 main: 1b9286292 (release) .. bef42b7df (deployed receipts); comms #343 (deploy receipt)
=======================================================================
