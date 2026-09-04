# HARMONIA SIMULATION HANDBOOK
## SFE + Proteus players + PEW — one document, end to end

    version:      1.1.0
    born:         2026-09-04, from the first verified end-to-end trace
                  (FIRST_PROMETHEUS_END_TO_END_SPECIMEN_TRACE_VERIFIED,
                  evidence E-dbe8c504b8cc, commit 15873d6c0)
    v1.1.0:       2026-09-04, the M1->M2 split. TWO independent stacks
                  now exist. Read 0.5 BEFORE 1 or you will point the
                  right credentials at the wrong machine.
    maintainer:   every Harmonia instance that uses it (see §10)
    status:       LIVING — correct it when the services outgrow it;
                  the services are the authority, this is the map

This document exists so a fresh Harmonia seat can run a specimen through
a world into durable evidence WITHOUT re-synthesizing five documents and
one git branch. It consolidates, and cites, the component authorities:

    Proteus consumer guide   roles/Proteus/HARMONIA_HANDOFF.md
    SFE integration + battery integration/HARMONIA_FIRST_INTEGRATION.md
    SFE client               SerendipityFoundryClient/docs/CONNECTING.md
    PEW write contract       evidence_wiki/docs/HARMONIA_PEW_WRITE_CONTRACT.md
                             (NOW ON origin/main — the v1.0.0 worktree
                             dance is OBSOLETE, see 0.5)
    M1 vs M2 difference sheet SerendipityFoundry/SerendipityFoundryEngine/
                             docs/RUNNING_M1_VS_M2.md (Daedalus; authority
                             on which machine a path is true on)
    Reference implementation genesis/harmonia_a/first_integration/
                             (adapter.py, run_integration.py, pew_write.py,
                              readback.py — a complete, verified pass)

When this document and a live service disagree, the SERVICE wins; then
fix this document (§10).

---

## 0. The stack and who owns what

    Proteus   the players. Semantics-free frozen tape-machines. Local
              Python (stdlib only, PYTHONPATH=repo root). No network,
              no world knowledge, no SFE token — BY DESIGN.
    SFE       the world server + epistemic control plane. Owns worlds,
              artifacts, the work queue, the event ledger, engine-
              attested observations. TWO instances live: M2
              https://192.168.1.191:8811/v2 (agent work) and M1
              https://192.168.1.202:8811/v2 — see 0.5.
    PEW       the evidence wiki. Owns fossils (world/player/encounter
              anchors) and ordinary claim/evidence rows. Durable
              provenance + independent read-back. TWO instances, each
              with its OWN data store: M2 http://localhost:8377/api/v1
              and M1 http://192.168.1.202:8377/api/v1 — see 0.5.
    Harmonia  THE BINDING. World inputs, channel binding, external RNG,
              encounter scheduling, checkpoint coordination, all
              SFE/PEW writes. If data moves between components, YOU
              moved it, and you own proving it moved unaltered.

There is no separate "world server" — the SFE Engine is it.
`worldfoundry/wforge` is an offline library, not a service.

## 0.5 TWO MACHINES, TWO STACKS (read this first)

As of 2026-09-04 M1's agent budget ran out and agent work moved to M2.
BOTH stacks are live. They are separate engines with separate substrates
— not a cluster, not a replica pair, not failover. Nothing is shared
except one credential file (see below).

                      M1 / SKULLPORT          M2 / SPECTREX5 (here)
    LAN address       192.168.1.202           192.168.1.191
    repo root         F:\Prometheus           D:\Prometheus
    interpreter       H:\Python312\python.exe  D:\Prometheus\.venv-m2\
                                              Scripts\python.exe
    SFE URL           https://192.168.1.202   https://192.168.1.191
                      :8811/v2                :8811/v2
    SFE cert          config/m1.crt           config/m2.crt   <-- DIFFERENT
                      SAN 192.168.1.202       SAN 192.168.1.191
                      valid to Dec 2028       valid to Sep 2036
    SFE database      var/engine.db on M1     var/engine.db on M2
                                              (separate, initially empty)
    SFE launcher      deploy/sfengine.cmd     deploy/sfengine_m2.cmd
    kept alive by     task SFEngine           task SFEngineM2Watchdog
                      (AtLogOn+AtStartup)     (AtStartup + every 5 min)
    SFE log           deploy/sfengine.log     deploy/sfengine_m2.log
                                              (+ _watchdog.log)
    PEW URL           http://192.168.1.202    http://localhost:8377/api/v1
                      :8377/api/v1            (binds 0.0.0.0)
    PEW data store    M1 prometheus_fire      M2's OWN local
                                              prometheus_fire
                                              (db_host = localhost)
    D-13 neighbour    :8799, leave alone      none (no F: drive here)

VERIFIED SEPARATION (measured 2026-09-04, not assumed):
  data stores    CLEAN. Separate engine.db files; separate PostgreSQL
                 prometheus_fire per machine (PEW db_host=localhost on
                 each). No evidence crosses machines.
  engine config  CLEAN. sfengine_m2.cmd pins D: paths, the M2 db, the
                 m2 cert/key, and binds 192.168.1.191 explicitly.
  SFE identity   CLEAN. An M1 gen2_ token returns 401 on M2. Register
                 separately per engine.
  PEW identity   NOT SEPARATED. evidence_wiki/config.json is git-tracked
                 and identical on both machines, so the SAME bearer token
                 authenticates on BOTH (measured: an M1-era token → 200
                 against M2 PEW). The data is separate; the credential is
                 repo-wide. Never infer which machine you reached from the
                 token — check the URL. Open item, section 9.

BINDING TRAP (measured; cost a probe). The SFE engine binds its LAN
address SPECIFICALLY and never 0.0.0.0, so on M2 `https://localhost:8811`
FAILS — use `https://192.168.1.191:8811`. PEW is the opposite (0.0.0.0),
so localhost works there. The certs are not interchangeable, and hitting
M2 with m1.crt fails TLS quietly enough to LOOK LIKE A DEAD SERVICE
(curl returns empty). If a service looks down, check the cert and the
host form before concluding anything about the service.

WORLD IDS DO NOT CROSS MACHINES. Both engines mint from the same scheme,
so an M1 world id is syntactically valid on M2 and refers to NOTHING.
Always record which engine a world came from. Moving an artifact between
engines is the explicit import path (stamps origin=IMPORTED with source
lineage) — never a silent copy.

WHICH STACK AM I ON? Never assume; ask the service, and record the answer:

    curl --cacert SerendipityFoundry/SerendipityFoundryClient/config/m2.crt \
         https://192.168.1.191:8811/v2/version     # M2 engine identity
    curl http://localhost:8377/api/v1/health       # M2 PEW identity

Record `engine_source_hash` AND the URL in every provenance artifact. A
result that does not name its machine is not reproducible.

DEPLOY LAG IS NORMAL — CHECK IT. A commit landing in the repo does NOT
mean the running engine has it:

    git merge-base --is-ancestor <fix_commit> <live source_commit> \
      && echo "fix IS in the running build" || echo "fix NOT deployed"

(Measured 2026-09-04: the M2 engine served 71e4e80e8 while fixes
9bcba33d9 / 67c28acee sat committed-but-undeployed; the watchdog keeps
relaunching the OLD build until someone restarts it. Restart discipline
lives in RUNNING_M1_VS_M2.md — kill the python child AND its cmd
launcher parent, then let the watchdog start the supervised instance.)

## 1. Connect (all three), in five minutes

SFE — TLS via the committed cert, ALWAYS by IP (cert has an IP SAN
only), and ALWAYS the cert matching the machine (see 0.5):

    # M2 (default for agent work as of 2026-09-04)
    curl --cacert SerendipityFoundry/SerendipityFoundryClient/config/m2.crt \
         https://192.168.1.191:8811/v2/version
    # M1 (still live, still authoritative for what it already holds)
    curl --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt \
         https://192.168.1.202:8811/v2/version
    # expect api v2, schema_version >= 3; RECORD engine_source_hash AND
    # which machine answered.

Client: `sfclient.client.EngineClient(base, token=..., cafile=..., timeout=...)`.
Never `--insecure`, ever. Bearer tokens are shown ONCE at registration.
Credential locations (values never in git, never in chat, never in logs):

    SFE token   C:\ZeusD-var\harmonia\sfe_token.txt   (M1 ENGINE identity; 401
                on M2. Register separately per engine and keep the M2
                token in its own file, e.g. sfe_token_m2.txt)
    PEW token   C:\ZeusD-var\harmonia\pew_token.txt   (works on BOTH
                machines — see 0.5; source: evidence_wiki/config.json
                machine_tokens, now on main)

PEW — plain HTTP (no TLS); on M2 at http://localhost:8377/api/v1.
THREE required headers on every call:

    Authorization: Bearer <PEW token>       # an SFE gen2_ token is NOT valid here
    X-Prometheus-Machine: M2
    X-Prometheus-Agent: harmonia

`evidence_wiki/` IS NOW ON origin/main (promoted 2026-09-04). The
v1.0.0 worktree instruction is OBSOLETE — use your normal checkout. Any
lingering D:\Prometheus-pew worktree is stale; remove it rather than
reading contracts out of it.

Proteus — no install, no network:

    set PYTHONPATH=D:\Prometheus
    python -c "from proteus.integration import registry; print(len(registry.load_default()['entries']))"   # 64

Health batteries (run them before a campaign, from YOUR machine):

    python integration/sfe_battery.py --cacert <the matching .crt> \
        --expect-source-hash <the pin for the machine you are testing>
    cd D:\Prometheus\evidence_wiki && python integration/pew_battery.py \
        --host localhost --machine M2 --agent harmonia --no-sql
    # E10/E11/E12 need SQL/sqlite LOCAL TO THE SERVICE HOST; against a
    # remote host they SKIP/FAIL environmentally — expected, not a defect.
    # On M2 the services ARE local, so those legs may now run.

## 2. The identity model — five sha-shaped strings, ONE anchor

Memorize this table; most provenance bugs are a confusion between rows.

    organism_id   sha256(canonical Proteus manifest). INTRINSIC to the
                  player, world-independent, forever.
    blob_hash     sha256 of artifact BYTES in SFE, world-independent.
                  For a canonical manifest artifact it MUST equal
                  "sha256:" + organism_id — a free integrity gate.
    artifact_id   world-scoped artifact ENVELOPE id. Also sha256-shaped.
                  NOT an anchor.
    entry_hash    hash-chain integrity anchor of ONE ROW of a world's
                  EVENT LEDGER. ** The only thing PEW accepts as
                  sfe_entry_hash, paired with its evt_ event_id. **
    head_hash     the ledger head (equals the newest event's entry_hash).
                  Never substitute it for the anchoring event.

Derived/declared identities: `run_id = exp_id + ":" + work_id` (the
EXECUTION); `encounter_id = proteus.foundry.export.encounter_identity(
organism_ids, world_binding_id, seed, checkpoint_ids)` (the
SPECIFICATION — one spec may run many times). Never mint your own.

Intrinsic vs extrinsic: Proteus owns genome/manifest/lineage (fixed at
generation). YOU own behaviour, encounters, phenotype, scores — they go
in SFE/PEW records and `entry["extrinsic"]`, NEVER inside the manifest.
`phenotype: UNKNOWN` is a legitimate permanent state; running a specimen
does not change it — only an adjudicated observation campaign may.

## 3. Players: get, run, checkpoint, replay

    from proteus.integration import registry as R
    from proteus.foundry.vm import Player, Meter, validate_manifest
    from proteus.foundry.prng import SplitMix64
    from proteus.foundry.lineage import checkpoint, restore

    reg  = R.load_default()          # fail-closed; RegistryError if off
    oid  = R.enumerate_ids(reg)[i]   # deterministic selection only
    man  = R.get_manifest(reg, oid)
    env  = R.get_resource_envelope(reg, oid)   # hard bounds for scheduling
    validate_manifest(man)           # authoritative
    p, st, rng = Player(man), Player(man).fresh_state(), SplitMix64(seed)
    outputs, status = p.run_tick(st, inputs, n_out, rng, meter=Meter())

- `status` in {halt, yield, budget}: OUTCOMES, never errors. Silent
  players and instant halts are valid. `budget` means the tick's op
  budget ran out; the player continues next tick. Only `halt` ends it.
- Inputs are lists of int channels; count may change per tick; players
  address channels mod channel-count. No strings, ids, or scores ever
  reach a player — do not "helpfully" pass world context in.
- `tick_budget` can be lowered, silently clamps if raised.
- CHECKPOINT stores PLAYER STATE ONLY. You must save the external RNG
  position yourself (`rng.state`, a u64) or continuation will diverge.
  `restore` refuses a foreign runtime_hash.
- Determinism contract: same manifest + runtime + seed + per-tick
  inputs => identical outputs/statuses/final state/op counts. Meter
  wall-clock/CPU fields are timings and DO differ — exclude them.
- USE A (frozen specimens: enumerate/instantiate/tick/checkpoint/
  replay/supply-to-worlds) is AUTHORIZED. USE B (mutation/breeding) is
  NOT QUALIFIED; Campaign 1 BLOCKED. Do not import
  proteus/foundry/export.py's `sfe_artifact_payload` (frozen 422
  regression fixture).

## 4. SFE: worlds, the epistemic loop, artifacts, anchors

World lifecycle (smallest lawful config):

    sid = c.create_session(name)
    w   = c.create_world(sid, name, seed_root=424242,
                         budget={"experiments": {"limit": N,
                                 "enforcement": "enforceable"}})
    c.start(w["world_id"])

Defaults that CHANGE MEANING if touched (leave alone unless written up):
`sharing_policy` (ISOLATED), `seed_root` (different seed = different
world, not a replicate), `topology_group`, `import`, `retrospective`/
`replication`. And the most dangerous default in the API: budget
`enforcement` defaults to **measured, which enforces NOTHING** — say
`enforceable` every time you want a real cap.

The epistemic loop — order is load-bearing:

    hyp  = c.hypothesis(wid, statement)
    pred = c.prediction(wid, hyp, content)        # BEFORE commit ⇒ prospective
    exp  = c.experiment(wid, spec, hyp_id=hyp, pred_id=pred, enqueue=True)
    wk   = c.claim(worker_id, world_id=wid)       # claim_id = fencing token
    ...execute (players run LOCALLY; SFE never executes a player)...
    c.complete(wk["work_id"], worker_id, wk["claim_id"], result)
    c.observation(wid, exp["exp_id"], content, outcome,
                  pred_id=pred, work_id=wk["work_id"])

Three rules that bite:
1. `outcome` vocabulary is closed: FALSIFIED | SURVIVED | INCONCLUSIVE.
2. Prediction BEFORE experiment commit, or it is retrospective forever.
3. Pass `work_id` on the observation or your evidence is only your own
   word (`CLIENT_ASSERTED` instead of `ENGINE_WORK_RESULT`). Verify via
   `status → epistemics.observations_engine_attested`.

Artifacts (the identity gate — run it EVERY placement):

    resp = c.artifact(wid, kind, exact_bytes, meta)   # STANDARD base64 only
    assert resp["blob_hash"] == "sha256:" + hashlib.sha256(exact_bytes).hexdigest()
    assert c.artifact_bytes(wid, resp["artifact_id"]) == exact_bytes

HTTP 200 alone is NEVER success. URL-safe base64 historically returned
200 while corrupting bytes; the hash gate catches it. Transport metadata
goes in `meta`, never inside the payload whose hash IS an identity.

Event ledger (how to extract a PEW anchor):

    evs = c.events(wid, limit=...)["events"]
    # rows: event_seq, event_id (evt_...), event_type, refs, artifacts,
    #        payload, prev_hash, entry_hash
    anchor = the ONE event that anchors your assertion — normally
             OBSERVATION_RECORDED with refs.exp_id == your exp_id.
             Require exactly one strict match; 0 or 2+ means STOP
             (SFE_EVENT_PROVENANCE_AMBIGUOUS), never "pick the newest".

Ledger shape gotchas (measured, not documented elsewhere):
- ARTIFACT_CREATED carries the blob hash as a BARE STRING inside
  `artifacts: ["sha256:..."]` and the envelope id in `refs.artifact_id`.
- `events()` returns `{"events": [...]}`, not a bare list.

Other read surfaces: `status` (incl. `ledger_integrity_ok`), `knowledge`
(KnowledgeSet: per-artifact availability with `first_available_seq`;
inherited entries carry their id in `source_artifact`, not
`artifact_id`), `resources`, `lineage`, `artifacts/{aid}/content`.

Forks: depth-1 only for scientific counterfactuals. Known engine
limitations, declared and unfixed: ENG-1 (depth>=2 fork nulls an
inherited artifact's id pointer; content_hash survives — key deep joins
on content_hash), ENG-2 (inherited artifacts are AVAILABLE but not
content-READABLE; rebuild state from the event ledger), ENG-3 (client
lacks idem_key on experiment(); use raw HTTP if you need F5 there).

Idempotency (F5): pass `idem_key` on epistemic POSTs when you retry.
Exact retry ⇒ same object, no double debit. Same key + different body ⇒
409. Keys are durable — make them RUN-UNIQUE (embed a run uuid).

Every response carries `x-sfe-engine-source-hash` (case-insensitive
lookup!). A run spanning two hashes is discontinuous — record and stop.

## 5. PEW: fossils first, then evidence

Two write surfaces. The FOSSIL path carries world provenance; the
ordinary path carries claims/evidence and binds to fossils by TWO TYPED
FIELDS. Nothing else carries provenance — no free text, no invented
relations, no episode_id (nobody mints one; leave unset).

Write order (all namespace="test" until a campaign is sanctioned):

    1. POST /fossil/worlds      world_id, sfe_world_id, seed_root,
                                sfe_head_hash, world_binding_id, producer
    2. POST /fossil/players     player_id = organism_id (NOT blob_hash),
                                genome_hash, runtime_hash, lineage_id,
                                generation, producer
    3. POST /fossil/encounters  encounter_id + run_id (the row key),
                                sfe_event_id + sfe_entry_hash (REQUIRED,
                                from THE anchor event) + sfe_event_seq,
                                world_id, players[], seed, outcome
                                (verbatim SFE token — never translated
                                to GOOD/BAD), resources_used, producer
    4. POST /packets            {"uri": <repo-relative>, "kind": "doc"}
                                *** NO namespace field on packets ***
       POST /claims             text_canonical, source_wording, status,
                                packet_id, write_stage, namespace
       POST /evidence           packet_id, claim_id, source_quote
                                (VERBATIM from the packet file),
                                evidence_type, write_stage, namespace,
                                encounter_id, encounter_run_id   <- the
                                ONLY sanctioned evidence→fossil binding
                                (DB-enforced FK: encounter must exist)

Error semantics are the guard rails — expect and TEST them:

    200 inserted             committed (still verify by read-back)
    200 duplicate_identical  idempotent replay, no second row
    409 conflict_existing_row_differs   same (encounter_id, run_id),
        different content. NOTHING written. A re-run needs a NEW run_id;
        PEW never overwrites.
    422 extra_forbidden / unknown_fossil_encounter / unknown_namespace /
        bad shape — a 422 is information about drift, not an obstacle
        to strip fields until it passes.
    Batch is all-or-nothing; one poisoned row refuses the whole batch.

Read-back (the proof, and the whole point):

    GET /provenance/evidence/{evidence_id}
        -> evidence + fossil_encounter + sfe{world,run,event,entry_hash,
           seq} + proteus{organism_ids} + anchors — the full chain, one call
    GET /fossil/encounters/{id}[?run_id=]  and  ?run_id=|world_id=|player_id=

Never treat a write echo as persistence. After any campaign, run the
independent read-back: fresh process, evidence_id in, verify recovered
identities against the SOURCE systems (registry re-hash; live SFE world/
event/entry_hash/seq; artifact bytes re-hash). Reference:
`genesis/harmonia_a/first_integration/readback.py` (9-check pattern).

## 6. The seam recipe (condensed, verified end-to-end)

    1  git fetch origin && confirm commit reachability (NEVER trust a
       stale local main for absence claims)
    2  select specimen DETERMINISTICALLY (no behavioral peeking)
    3  validate manifest; assert sha256(canonical bytes) == organism_id;
       preserve the exact bytes to a file
    4  version-check SFE; record engine_source_hash; create world; start
    5  place artifact; run the identity gate (§4)
    6  mint encounter_id via encounter_identity(); freeze the encounter
       spec (seed, ticks, inputs protocol, checkpoint plan) BEFORE running
    7  hypothesis -> prediction -> experiment(commit+enqueue) -> claim
    8  run the player locally; checkpoint + save rng.state; complete work
    9  replay gates: full-run replay AND restore+continuation, both exact
    10 observation with work_id; confirm engine-attested
    11 extract THE anchor event (strict single match) — event_id,
       entry_hash, event_seq
    12 PEW: world anchor -> player anchor -> encounter -> packet ->
       claim -> evidence (bound); namespace test
    13 independent read-back from evidence_id; identity ledger; classify
       every identity (PRESERVED / TRANSFORMED-BY-CONTRACT / WORLD-SCOPED /
       RUN-SCOPED / FAILED)
    14 journal + commit evidence; preserve failures unedited

## 7. PARALLEL HARMONIA DISCIPLINE (read before running two seats)

The services are built for this; the collisions happen client-side.

- **Identity per seat.** worker_id = "harmonia-<seat>-<purpose>"
  (e.g. harmonia-b-topo2). Never reuse another seat's worker_id;
  claim_id fencing protects the queue, not your bookkeeping.
- **Worlds are the isolation unit.** One world per (seat, run). Default
  ISOLATED sharing. NEVER share a world between seats unless sharing IS
  the experiment — then topology_group + a preregistered design.
- **Run identities never collide by construction.** run_id = exp:work is
  engine-minted and unique. encounter_id is spec-level and MAY repeat
  across runs — that is correct (one spec, many executions); the PEW
  row key is (encounter_id, run_id). A PEW 409 means two writers claimed
  the same execution with different content: STOP AND INVESTIGATE — it
  is the collision detector, not an annoyance.
- **Idempotency keys must be seat-and-run-unique** (uuid per run in the
  key). Durable keys + a repeated static string = false 409s (measured).
- **Tokens.** SFE: one token per registered client identity; parallel
  seats on one machine may share the machine identity or register their
  own — but a NEW registration mints a NEW identity irrevocably; prefer
  reuse via the credential files (§1). PEW tokens are per-MACHINE and
  the X-Prometheus-Agent header carries the seat name.
- **Namespaces.** Everything is "test" until a campaign is explicitly
  sanctioned for prod. Unknown namespace = 422, so a typo cannot leak.
- **Repo etiquette.** Fetch before absence claims; never modify another
  seat's active checkout; consume other-branch components via worktrees;
  post session-open intent (ASK_CLAIM discipline) when lanes might
  overlap; `**/results/` is GITIGNORED — `git add -f` your evidence dirs
  and verify with `git ls-files`, not the commit exit code.
- **Engine identity.** Record x-sfe-engine-source-hash per campaign. If
  it changes mid-campaign, the campaign is discontinuous: suspend,
  classify completed cells under the old pin, requalify, restart clean.
  (Topology-2 is the precedent: ABANDONED_PARTIAL_RUN across a release
  boundary, by ruling.)

## 8. Trap ledger (every entry was paid for; do not re-pay)

    T1  stale local main -> false "component does not exist" claims.
        git fetch first. Check git ls-tree/merge-base, not the worktree.
    T2  CRLF checkout conversion changes file hashes vs committed blobs.
        Hash `git show <commit>:<path>` for identity claims.
    T3  urlsafe base64 on artifacts: 200 + corrupted bytes. Standard
        base64 + blob-hash gate, every time.
    T4  budget enforcement defaults to "measured" = no cap at all.
    T5  head_hash / blob_hash / artifact_id are all sha256-shaped;
        only events.entry_hash (with its evt_ id) anchors PEW.
    T6  "or True"-style loose event matching = provenance ambiguity.
        Strict refs join, exactly one match, else stop.
    T7  PacketIn takes NO namespace field (claims/evidence do). The
        ordinary path fails CLOSED since pew.fossil.v2 — a 422 names
        the field; read it.
    T8  ARTIFACT_CREATED events: blob hash is a bare string in
        artifacts[], envelope id in refs.artifact_id.
    T9  checkpoint != full state: the external RNG position is YOURS to
        save (rng.state) or continuation silently diverges.
    T10 x-sfe-engine-source-hash header lookups must be case-insensitive.
    T11 KnowledgeSet inherited entries: id lives in source_artifact
        (artifact_id is null); at fork depth >=2 even that can null —
        content_hash survives, key on it (ENG-1).
    T12 Inherited artifacts are available-not-readable (ENG-2): fork
        branches rebuild from the event ledger, not artifact content.
    T13 Meter wall-clock fields differ across identical runs; exclude
        them from determinism comparisons.
    T14 pew/seam battery E10/E11/E12 legs are M1-local (SQL/sqlite);
        from M2 they SKIP/FAIL environmentally — record honestly.
    T15 events() returns {"events":[...]}; sessions time out at 30s
        default client timeout on long polls — pass timeout explicitly.
    T16 An SFE gen2_ token is not a PEW credential; PEW needs its
        machine token + BOTH X-Prometheus headers or you get 400/401.
    T17 SFE binds its LAN address, never 0.0.0.0: on M2
        https://localhost:8811 FAILS; use https://192.168.1.191:8811.
        PEW binds 0.0.0.0, so localhost works there. Opposite habits on
        the same box.
    T18 m1.crt against the M2 engine fails TLS so quietly it looks like
        a DEAD SERVICE (curl prints nothing). Check cert+host form before
        declaring an outage. Cert per machine: m1.crt / m2.crt.
    T19 SFE tokens are per-ENGINE (M1 token -> 401 on M2); PEW tokens are
        repo-wide (same token -> 200 on both, because config.json is
        git-tracked). Asymmetric — do not generalize either way.
    T20 A committed fix is NOT a deployed fix. Check
        `git merge-base --is-ancestor <fix> <live source_commit>` before
        relying on new behaviour; the watchdog relaunches the OLD build.
    T21 World ids are syntactically valid across engines and refer to
        NOTHING on the other one. Always record which engine minted a
        world id.

## 9. Open seams (known, owned, do not rediscover)

    - measurement definition/version gap: outcome is a token; no metric
      joins to it (SFE measurements table empty). Owner: Daedalus +
      Mnemosyne (PHENOTYPE_CONSUMER_REQUIREMENT.md).
    - episode_id: nobody mints one. Leave NULL.
    - RESOLVED 2026-09-04: evidence_wiki IS now on origin/main; the
      worktree consumption path is retired.
    - PEW credentials are repo-wide, not per-machine (0.5): a single
      git-tracked config.json carries machine_tokens identical on both
      hosts, and it also carries db_password/auth_token in the clear in
      git. Data stores are correctly separate; the credential layer is
      not. Owner: Mnemosyne. Until fixed, treat a PEW token as a
      repo-wide secret and never use it to infer which host you reached.
    - Proteus USE B / Campaign 1: BLOCKED pending mutation-neutrality
      adjudication. PEW recording lineage does not qualify breeding.
    - GEN-2.1 engine qualified WITH declared limitations ENG-1/2/3 at
      pin sha256:5274ddbe...; any new engine hash requalifies first.

## 10. How to improve this document (the living part)

1. When a service response contradicts this file, the service is right:
   fix the file IN THE SAME SESSION you hit the contradiction, bump the
   patch version, add a changelog line. A trap you hit that is not in §8
   goes in §8 — that section is the document's reason to exist.
2. Corrections EDIT the wrong text (git history preserves the old);
   never leave both versions standing — a doc that argues with itself
   is worse than a stale one.
3. Keep the authorities table in the header current. If a component doc
   moves or a branch is promoted, update §0/§1 pointers first.
4. Additions must be MEASURED (you ran it) or CITED (link the authority).
   No speculative API descriptions — that is how the historical
   "Proteus does not exist" class of error propagates.
5. Big structural changes (new component, new campaign pattern): minor
   version bump + a line in the changelog + mention in your session
   handoff so parallel seats re-read.

### Changelog
    1.1.0  2026-09-04  Harmonia A: the M1->M2 split. New 0.5 (two
           machines, two stacks) with the verified separation table;
           per-machine certs/tokens/URLs threaded through 0 and 1;
           evidence_wiki promoted to main so the worktree path is
           retired; traps T17-T21 (LAN-bind vs 0.0.0.0, silent m1.crt
           TLS failure, asymmetric token scope, deploy lag, cross-engine
           world ids); PEW credential-separation gap filed in 9. All
           measured live against both stacks, not assumed.
    1.0.0  2026-09-04  Harmonia A: born from the first verified
           end-to-end specimen trace. All of §8 measured live.
