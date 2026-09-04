# HARMONIA -> PEW WRITE CONTRACT (`pew.fossil.v2`)

The exact answer to one question:

> After I run a frozen Proteus organism in an SFE world and receive the SFE
> identities, what do I write to PEW so a future investigator can start from
> the resulting evidence and mechanically reconstruct which organism ran, in
> which world, in which SFE run, and which immutable SFE ledger event anchors
> that assertion?

Companion to `HARMONIA_FIRST_INTEGRATION_PEW.md` (connection, health, battery).
This document is the *provenance* half. Frozen 2026-09-03.

If this document and the service disagree, the service wins:
`GET /api/v1/fossil/contract` is the machine-readable authority.

---

## 0. Where PEW lives

    authoritative branch   origin/mnemosyne/evidence-wiki-v0
    NOT on                 origin/main -- `git checkout main` makes
                           evidence_wiki/ disappear entirely
    base URL               http://192.168.1.202:8377/api/v1   (M1, SKULLPORT)
    auth                   Authorization: Bearer <your M2 token>
                           X-Prometheus-Machine: M2
                           X-Prometheus-Agent: harmonia
                           (token is in evidence_wiki/config.json on the
                           branch; it is not reproduced in documentation)
    identity               schema_version 4, fossil_contract pew.fossil.v2

    git fetch origin mnemosyne/evidence-wiki-v0
    git checkout -b pew origin/mnemosyne/evidence-wiki-v0

## 1. The five identities, which are NOT synonyms

    Proteus  organism_id     sha256(canonical player manifest). INTRINSIC to
                             the player. World-independent. -> PEW players[]
    SFE      blob_hash       identity of artifact BYTES, world-independent.
                             For a Proteus manifest artifact it equals
                             sha256 of the same bytes as organism_id -- a free
                             cross-check, NOT a provenance anchor.
    SFE      artifact_id     identity of the artifact ENVELOPE, world-scoped.
                             ALSO "sha256:"-shaped. NOT an anchor.
    SFE      entry_hash      hash-chain integrity anchor of ONE ROW in the
                             EVENT LEDGER. ** THIS is sfe_entry_hash. **
    SFE      head_hash       a world ledger's head state. Always equal to some
                             event's entry_hash (it names the head event), so
                             it is NOT structurally distinguishable -- do not
                             substitute it for the anchoring event.
    PEW      (encounter_id, run_id)   fossil encounter identity

Never satisfy a required field by picking whichever sha256-looking string is
at hand. Three of the five above are sha256-shaped and only one is the anchor.

## 2. What `sfe_entry_hash` means, exactly

    sfe_entry_hash = SFE events.entry_hash of the event named by sfe_event_id

Shape `^sha256:[0-9a-f]{64}$`, enforced. Because head_hash cannot be excluded
by shape, the class is pinned by the REQUIRED companion field:

    sfe_event_id   = SFE events.event_id, shape ^evt_[0-9a-f]{16,32}$

An artifact blob_hash or artifact_id has no `evt_` id to pair with it, so a
substitution fails at the door. PEW holds no SFE client by design (you own
orchestration), so it validates CLASS and SHAPE, never ledger membership: the
auditable check is that the `(sfe_event_id, sfe_entry_hash)` pair exists in
SFE. That check passes 5452/5452 on PEW's historical rows.

Choose the event that actually anchors your assertion -- normally the
`ENGINE_WORK_RESULT` event for the run, from
`GET /v2/worlds/{wid}/events`.

## 3. Field mapping: Proteus + SFE -> PEW

    PEW field         comes from                          notes
    ---------------   ---------------------------------   --------------------
    world_id          SFE worlds.world_id (wld_<hex>)     also register a
                                                          world anchor row
    players[]         Proteus organism_id per player      NOT SFE blob_hash
    encounter_id      Proteus encounter_identity(         the SPECIFICATION;
                        organism_ids, world_binding_id,   one spec may be run
                        seed, checkpoint_ids)             many times
    run_id            SFE "exp_id:work_id"                the EXECUTION
                      (exp_<hex>:wrk_<hex>)
    sfe_event_id      SFE events.event_id                 REQUIRED
    sfe_entry_hash    SFE events.entry_hash of THAT event REQUIRED
    sfe_event_seq     SFE events.event_seq                producer order;
                                                          PEW's `revision` is
                                                          NOT producer order
    sfe_world_id      SFE world_id                        when it differs from
                                                          your world_id label
    seed              the encounter seed argument         world-level
                                                          seed_root goes on the
                                                          world anchor row
    outcome           SFE observations.outcome, or the    Proteus NEVER authors
                      work item's terminal status         an outcome
    failure_class     your world's failure taxonomy       optional
    resources_used    meters/cost                         optional jsonb
    occurred_ts       when it happened                    UTC ISO-8601 on read
    producer          {runtime_hash, grammar_hash,        optional jsonb
                       affordance_hash, spec_hash,
                       git_commit}
    episode_id        NOTHING mints one today             leave unset; PEW will
                                                          not invent it

## 4. The write sequence

**Step 1 -- world anchor** (once per world)

    POST /api/v1/fossil/worlds
    {"world_id":"wld_...", "sfe_world_id":"wld_...",
     "manifest_hash":"sha256:...", "world_binding_id":"...",
     "seed_root":"...", "sfe_head_hash":"sha256:...",
     "producer":{"component":"harmonia.adapter","version":"..."}}

**Step 2 -- player anchor** (once per organism)

    POST /api/v1/fossil/players
    {"player_id":"<Proteus organism_id>",
     "genome_hash":"sha256:<manifest hash>", "runtime_hash":"sha256:...",
     "lineage_id":"...", "generation":0,
     "producer":{"component":"proteus.foundry","version":"v0"}}

**Step 3 -- the encounter** (once per EXECUTION)

    POST /api/v1/fossil/encounters
    {"encounter_id":"<Proteus encounter_identity>",
     "run_id":"exp_<hex>:wrk_<hex>",
     "sfe_event_id":"evt_<hex>",
     "sfe_entry_hash":"sha256:<entry_hash of that event>",
     "sfe_event_seq":30835,
     "sfe_world_id":"wld_<hex>", "world_id":"wld_<hex>",
     "players":["<organism_id>"], "seed":"...",
     "outcome":"...", "resources_used":{...},
     "occurred_ts":"2026-09-03T00:00:00+00:00",
     "producer":{...}}
    -> {"encounter_id":..., "run_id":..., "inserted":true,
        "status":"inserted", "read_back":"/api/v1/fossil/encounters/<id>"}

**Step 4 -- ordinary evidence, BOUND to that encounter**

Evidence still needs its own source packet and verbatim quote (that rule is
unchanged). The binding is two typed fields:

    POST /api/v1/packets   {"uri":"<repo-relative path>","kind":"doc"}
    POST /api/v1/claims    {"text_canonical":"...","source_wording":"...",
                            "status":"OBSERVED","packet_id":"SP-...",
                            "write_stage":"SOURCE_BOUND"}
    POST /api/v1/evidence
    {"packet_id":"SP-...", "claim_id":"C-...",
     "source_quote":"<verbatim from the packet>",
     "evidence_type":"OBSERVATIONAL_ANALYSIS",
     "write_stage":"SOURCE_BOUND",
     "encounter_id":"<same encounter_id as step 3>",
     "encounter_run_id":"<same run_id as step 3>"}
    -> {"evidence_id":"E-...", "provenance":"/api/v1/provenance/evidence/E-..."}

That pair is the ONLY sanctioned evidence -> fossil binding. There is no
relation type, URI convention, or free-text field that carries it. The
binding is a foreign key: an encounter that does not exist is refused with
`422 unknown_fossil_encounter:<id>@<run>`, so **write the encounter first**.

## 5. Reading it back (both directions)

    GET /api/v1/provenance/evidence/{evidence_id}
      -> evidence, fossil_encounter, sfe{world_id,run_id,event_id,entry_hash,
         event_seq}, proteus{organism_ids}, world_anchor, player_anchors
      This is the whole chain in one call, and it is the traversal the success
      criterion names.

    GET /api/v1/fossil/encounters/{encounter_id}/evidence[?run_id=]
      -> every evidence record bound to that encounter (reverse direction)

    GET /api/v1/fossil/encounters/{encounter_id}[?run_id=]
    GET /api/v1/fossil/encounters?run_id=|world_id=|player_id=|episode_id=
    GET /api/v1/fossil/worlds/{world_id}   GET /api/v1/fossil/players/{id}

Never treat HTTP 200 as proof of persistence. The read-back is the proof.

## 6. Namespaces -- keep practice runs out of science

Fossil rows carry `namespace` ("prod" | "test" | "synthetic"); ordinary
claims/evidence/relations carry `namespace` ("prod" | "test" | "fixture").
Anything you write while practising must be `"namespace":"test"`.

`ew/fossil.py` analyses and the `ew.*_prod` views exclude test/fixture rows.
An unknown namespace is refused (`422 unknown_namespace:<x>`) so a typo cannot
silently leave a practice object in the scientific corpus.

## 7. Duplicate, conflict, and the 4xx you should expect

    200 status=inserted              committed and readable
    200 status=duplicate_identical   already present, byte-identical: a safe
                                     idempotent retry, no second row
    409 conflict_existing_row_differs:<fields>
                                     same (encounter_id, run_id) exists and
                                     DIFFERS. NOTHING written. Either your run
                                     identity is wrong (a re-run needs a new
                                     run_id) or the content changed. PEW never
                                     overwrites; correcting a record means a
                                     new identity, not a mutation.
    422 fossil_encounter_requires_sfe_entry_hash
    422 sfe_entry_hash_must_match_sha256_64hex:...
    422 sfe_event_id_required_and_must_be_evt_prefixed:...
    422 unknown_fossil_encounter:<id>@<run>     bind AFTER writing the encounter
    422 unknown_namespace:<x>
    422 extra_forbidden (field named)           unsupported field: your schema
                                                and PEW's have drifted. Nothing
                                                is ever silently dropped.
    400 missing X-Prometheus-Machine/Agent, or an unfiltered query
    401 bad token, or token/machine mismatch
    404 read-back of an unknown id

Batch (`POST /api/v1/fossil/encounters/batch`, field `encounters`) is
all-or-nothing: one conflicting or unprovenanced row refuses the whole batch,
so a 200 never means "some of your rows landed".

## 8. Proteus authorization boundary

Frozen Proteus specimens are AUTHORIZED for use: enumerate, fetch, validate,
instantiate, tick, checkpoint, restore, replay, supply to worlds.

Proteus breeding/mutation is NOT QUALIFIED
(`NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT`; operational significance
`NOT_YET_ADJUDICATED`; Campaign 1 BLOCKED). Nothing in this contract changes
that, and PEW recording a lineage_id does not qualify a bred organism.

Two SFE-side cautions Daedalus measured, repeated because they affect what you
anchor: use STANDARD base64 for `POST /v2/worlds/{wid}/artifacts` (URL-safe
base64 can return 200 while corrupting bytes) and verify the returned
`blob_hash` equals sha256 of the bytes you sent.

## 9. Known gaps (upstream, not PEW's to close)

1. Measurement definition + version for scores. SFE's `measurements` table
   holds 0 rows; `outcome` is a token and no metric is joinable yet.
   See `PHENOTYPE_CONSUMER_REQUIREMENT.md`.
2. `episode_id` is minted by nobody. Column exists, stays NULL.
3. Proteus's own claim/evidence path (`export.pew_rows`) has never been run
   against the service. Only the fossil + binding path in this document is
   qualified.
4. No PEW test has been executed FROM M2. Your first battery run is the real
   cross-host qualification.

## 10. Prove it yourself

    cd evidence_wiki
    python integration/pew_battery.py  --host 192.168.1.202 --machine M2 \
        --agent harmonia --no-sql
    python integration/seam_battery.py --host 192.168.1.202 --machine M2 \
        --agent harmonia --no-sql

`"all_pass": true` and exit 0 is the only PASS. `--no-sql` skips the legs that
require direct database access on M1; they report SKIP, never PASS.
