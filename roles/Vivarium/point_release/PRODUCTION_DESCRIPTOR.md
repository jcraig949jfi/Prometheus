# Production descriptor and credential bootstrap (point release, MUST/SHOULD)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design (operator s9, s10; campaign-1
ledger L-002 / L-003 / L-005, all dated 2026-09-17).

## 0. What already exists, and what is missing

    exists   SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOYED_BUILD_M2.json  (Daedalus): endpoint, engine_instance_id,
             schema_version, engine_source_hash, pinned_at/by, contract path. Declared PRODUCTION 2026-09-16T17:22Z.
    exists   archaeon/wse/engine_descriptor.py: the one reader every Archaeon consumer uses (L-002 closed on their side).
    exists   roles/Harmonia/contracts/sfe_contract.json: base_url + instance id the conformance gate pins.
    missing  the QUEUE/STORE half (which PostgreSQL cluster, which schema, which comms environment), the credential ROLE
             names per consumer, a HOLD field with an expiry, and one reader for Vivarium (vivarium/config.json still names
             M1 addresses; the M2 launcher overrides by environment -- L-002 open on my side).
    missing  per-machine credential bootstrap (L-005): the queue path stayed unexercised because a token file could not
             cross machines.

The ruling conflict (#301 vs #314/#315) is CLOSED by the operator's direction
of 2026-09-17: "Campaigns 1-3 established the M2 production ledger in actual
use." Production = eng_906356f7fb1da180131f9290 at https://192.168.1.191:8811.
This document does not re-decide it; it makes it a file consumers gate on.

## 1. The descriptor (one tracked file; proposed path: deploy/PRODUCTION.json at the repository root; owner Daedalus for
##    the engine block, Hermes/Archaeon for the store block, Vivarium for the consumer roles block; ONE file, three blocks)

    {
      "descriptor_version": "prometheus.production.v1",
      "ruled_by": "operator", "ruled_at": "2026-09-17T..Z", "ruling_ref": "roles/Vivarium/prompts/2026-09-16_m1_reboot/<file>",
      "hold": null | {"since": ts, "expires": ts, "reason": ..., "by": ...},
                                    a HOLD is a field with an expiry, not a chat message (L-003); consumers refuse to LAUNCH while a
                                    non-expired hold exists and say so
      "engine": {                    == DEPLOYED_BUILD_M2.json's fields, or a pointer to it; never a second copy that can drift:
        "descriptor_ref": "SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOYED_BUILD_M2.json",
        "endpoint": "https://192.168.1.191:8811", "engine_instance_id": "eng_906356f7fb1da180131f9290",
        "schema_floor": 8, "engine_source_hash": "sha256:4dbcd3fd...", "cacert": "SerendipityFoundry/SerendipityFoundryClient/config/m2.crt",
        "contract": "roles/Harmonia/contracts/sfe_contract.json"
      },
      "store": {                     the canonical PostgreSQL, by IDENTITY (comms/environments.json is the registry):
        "environment": "prometheus-canonical", "db_system_id": "7628127204585430828", "db_name": "prometheus_fire",
        "host_hint": "192.168.1.202", "schemas": {"queue": "viv", "comms": "comms", "ew": "ew"}
      },
      "pew": {"endpoint": "http://192.168.1.191:8377/api/v1", "namespace": "prod", "fossil_contract": "pew.fossil.v2"},
      "consumers": {                 credential ROLES, never values:
        "vivarium":  {"client_name": "vivarium",  "credential_file": "vivarium/config.local.json", "keys": ["sfe_token", "pew_token"],
                      "bootstrap": "viv.cli sfe-identity --ensure (registers on the engine named above if absent)"},
        "archaeon":  {"client_name": "cmp<N>-archaeon", "credential_file": "archaeon/campaign<N>/config.local.json", ...},
        "theophrastus": {...}
      },
      "machine": {"role": "sfe-ecosystem", "host": "SPECTREX5", "note": "Postgres/Redis shared on M1; every other service on M2"}
    }

Rules

    P1  a consumer that launches reads this file and REFUSES if: hold is live; engine.engine_instance_id != /v2/version's;
        store identity != the live connection's (my guard already does this half); the credential file for its role lacks a
        key. It prints which. (The dead-man's --expected-engine and prepare_m2.py's checks become reads of this file.)
    P2  the file is changed only by a commit that names the ruling; a change to engine.engine_instance_id is a
        "relocation" and requires the coordinated window (Amendment s11)
    P3  no secret, ever; the file names WHERE a secret lives and WHICH keys it must hold

## 2. Credential bootstrap (L-005; deterministic operational machinery)

    viv.cli sfe-identity --ensure   already exists: registers the durable client for the role if config.local.json lacks a
                                    token (identity.token_for(register_if_missing=True)). What is missing is the RULE for when
                                    it may run against production:
      - allowed when PRODUCTION.json names this machine as the engine's machine AND the engine answers with the descriptor's
        instance id AND no client of that name exists on this ledger for this role (the engine says; registration_open true)
      - refused when a client of that name already exists on this ledger (a second registration would be a second identity:
        the operator's "do not mint replacement identity" is honoured on the SAME ledger; on a DIFFERENT ledger there is
        nothing to replace -- which is the case today: eng_906356f7 has no vivarium client)
      - the receipt records client_id, engine_instance_id, registered_at; the token lands in config.local.json only
    prepare_m2.py                   gains: read PRODUCTION.json; run --ensure under the rule above when --bootstrap is passed;
                                    the "secrets ABSENT" precondition becomes "bootstrap the role" instead of "carry a file"
    PEW token                       Mnemosyne's route; the same shape (a per-machine writer registration) is requested in Stage 3

## 3. What changes in my prepared launch (not executed until the window)

    dead-man --expected-engine       -> read from PRODUCTION.json.engine.engine_instance_id (== eng_906356f7)
    launcher VIV_SFE_BASE_URL etc.   -> read from PRODUCTION.json (the launcher becomes a thin wrapper; the environment
                                        overrides remain for tests)
    B1 read scope                    -> re-issued on the M2 ledger for Archaeon's new client id (Daedalus #314 step; the grant
                                        tool is idempotent)
    the 5 held rows                  -> bind M1 worlds; Archaeon cancels/re-issues (Daedalus #314); I never cancel by inference
    the M1 corpus                    -> archive; UNKNOWN engine for any future join, said so in the envelope

## 4. Acceptance (Stage 4)

    positive   prepare_m2.py --bootstrap on a clean machine against a test engine registers the client once, records the
               receipt, and a second run is a no-op (client exists)
    negative   with hold live, every launch entry point refuses and prints the hold; with the descriptor's instance id != the
               engine's, refuses WRONG_ENGINE (the dead-man test today, re-pointed)
    cheat      a descriptor edited to a different engine id without the window's commit trailer fails a test that checks the
               file's last change names a ruling (repo-level; Archaeon/Hermes own the test)
