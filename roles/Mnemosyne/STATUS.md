# Mnemosyne / PEW - status

Currency: 2026-09-18 01:55 local (instance m2-9c10ae00; session closed; C4 gate items closed incl. G4 drained). Updated at least
every four hours of activity. The 2026-09-11 status is superseded where it
says the service runs on M1; everything else it recorded stands as history.

## What is running (asserting PRESENT, ACTIVE and PRODUCTIVE, measured)

    PEW service      http://127.0.0.1:8377 on M2 (SPECTREX5), bound 0.0.0.0
                     so M2 seats use 127.0.0.1 and LAN peers 192.168.1.191
                     schema 5 (migrations 014, 015, 2026-09-17), ontology 7 in
                     the registry (code constant still 2, MNE-19), contract
                     pew.fossil.v2, closure pew.closure.v0; the store is
                     ATTESTED before the port binds (health.store)
    serving from     the pinned worktree mnemosyne-pew (host convention
                     D:\Prometheus-worktrees\mnemosyne-pew\evidence_wiki)
                     detached at 438952e7b, clean; workspace_known true;
                     restarted 2026-09-17 15:22 (vivarium identity loaded)
    store            the CANONICAL store: PostgreSQL 17 prometheus_fire on
                     M1 (192.168.1.202), db_system_id 7628127204585430828,
                     attested by the service (S2) on every battery run
    engine           anchors verified against the M2 engine
                     https://192.168.1.191:8811/v2 (Daedalus, ledger
                     D:\Prometheus-data\sfe\engine.db) with a client token
                     minted for pew-m2-service, held only in the untracked
                     config.local.json
    scheduled        MnemosyneEvidenceWikiWatchdogM2 (5 min, property
                     probe, rule-10 bound 12, parks to Mnemosyne) from the
                     pinned worktree

## What is NOT running, or cannot be seen from here

    M1 PEW service   DORMANT since 2026-09-15 17:11:01 -0400 (last watchdog
                     search in ew.read_log). M1 8377 does not answer from
                     the LAN. M1 is Nestor's machine since 2026-09-15
                     (ccb26df01); nothing on it can be attested from M2.
    PEWBackupDaily   (M1) NOT RELIED ON since 2026-09-17; still UNLOCATED
    PEWRestoreVerify from M2. The backup of record is now on M2 (below).
    M2 fork store    untouched, quarantined, no reader since 2026-09-05;
                     no service fronts it.

## Backup of record (O2, ruling MNE-D1 2026-09-17)

    PEWBackupDailyM2          03:30 daily, M2, pinned worktree c46a882e9:
                              attested dump of the canonical cluster over
                              the LAN to D:\PrometheusBackups\pew, keep 14
    PEWRestoreVerifyWeeklyM2  Sun 04:30: restore into the M2 local cluster
                              (17.11, not canonical by identity) and
                              compare every table in every schema with live
    today                     2 backups (pewbk-20260917T055050-fea46038fa3c
                              hand-run; pewbk-20260917T055922-1b1967c7670a
                              by the task), 2 restore qualifications, both
                              RESTORE_VERIFIED: 164/164 tables, loss {},
                              chain identical, ~200 s each
    alarms                    failed job -> comms report; missed job -> the
                              M2 watchdog's stale check (36 h / 8 d), one
                              report per stale day (exercised)
    O3 conditions             1 backup cycles: 2 today (same day; nightly
                              cycles accrue); 2 independent restore: DONE;
                              3-7: open (consumer enumeration, reversible
                              connection changes, point-release integration
                              far enough, no active campaign, rollback
                              rehearsed); destination: M2 unless a
                              central-services host is imminent

## Last verified (2026-09-17 07:1x, from the task worktree, against the
## deployed service at 8665b1bdf)

    pew_battery 17/17, seam 12/12, closure 19/19, lineage 14/14 + 1 SKIP
    (no peer engine reachable), h0h5_refs 16/16, campaign release check
    15/15, ecology selector 7/7, minted player 7/7; projections
    rebuild-check equal x3; unit tests 30 passed 2 skipped, watchdog 9/9,
    base-role 11/11. Watchdog live tick: `ok  health 31ms  hybrid search
    83ms`. S2 cheat: naming the fork FAILS. Wrong-store startup: REFUSED
    (exit 1 before bind).

## Pre-Campaign-4 repair (2026-09-17 09:xx; order s4) -- FROZEN

    surface       docs/point_release/CAMPAIGN4_FROZEN_SURFACE.{md,json},
                  digest sha256:0ba00db3481f...; tests/test_frozen_surface.py
                  fails on any drift
    frozen ids    schema 5 (014+015); reader ew.campaign_ingest/1.4; builder
                  ew.projections/1.0; reach_level v1, corridor_edge v1 (v0
                  SUPERSEDED, kept); inbox pew.events.v1; thresholds 0.5 /
                  0.45 / 0.90 + held-out confirmation
    repairs       closure verify timeout 6 s -> 30 s + one retry (Daedalus
                  #345; a stall wrote UNVERIFIED silently); content-duplicate
                  sequences recorded (Vivarium #335, migration 015);
                  foundry_profile scheme tag (Proteus #339)
    acceptance    batteries green after restart; release check 16/16;
                  second ingest 0 new (C3/C2/C1); rebuild digests identical
                  to the point-release build; post-015 restore qualified
    receipt       docs/point_release/PEW_REPAIR_RECEIPT_2026-09-17.json;
                  dispositions PEW_STAGE3_DISPOSITIONS.md

## Point release (2026-09-17; docs/point_release/PEW_RELEASE_PACKET.md)

    ingested      campaigns 1-3 -> 26,636 campaign_observations (cmp3
                  19,436; cmp2 5,629; cmp1 1,352; other producers 219);
                  second pass 0 new; 278 checkpoints; 0 conflicts
    projections   reach_level v1 (agrees with producer 1265/1265),
                  reach_level v0 SUPERSEDED (156 rows differ; 126 = D3-006
                  class), corridor_edge v1; rebuild equal
    routes        campaign/observations, campaign/summary, projections,
                  ingestion/*, events (outbox inbox), release
    migration     014 at 06:50:07 against backup pewbk-20260917T064348;
                  post-migration backup pewbk-20260917T070006 restored
                  RESTORE_VERIFIED 171/171
    gate (s22)    PEW: deployed, restarted, qualified -- reported #33x

## Changed 2026-09-16

    guard       ew.workspace fails closed when git does not answer
    watchdog    one script, both machines; rule-10 bound enforced on M2;
                creates derived/; finds .venv-m2 via the common git dir
    tests       live-qualification scripts opt-in (Techne #194);
                derived/ ignored
    battery     S2 keyed by environment registry, not machine
    routes      GET /fossil/encounters?ecology=<json> (THEO-REQ-001)
    schema      migration 013: minted-player columns on fossil_players
    identity    Proteus read+write (R-5); tracker R-6 (Agora #258);
                vivarium read+write (R-7, 2026-09-17, C4 gate G4)
    client      fossil_encounters, register_fossil_player, get_fossil_player
    deps        evidence_wiki/requirements.txt

## Open, and on whom

    RULED     MNE-D1 (operator, 2026-09-17, verbatim in prompts/
              2026-09-17_point_release/02_OPERATOR_RULING_MNE-D1.md): O2
              approved and DONE today; O3 deferred behind seven
              conditions (MNE-46 tracks them); O4 rejected; M1 remains
              SHARED infrastructure, not handed over, while the canonical
              cluster serves both ecosystems.
    OPERATOR  MNE-D2 CONFIRMED in chat 2026-09-16 ("We are going to run
              the SFE ecosystem on M2 now"); residue: the fork database's
              disposition (keep quarantined / drop).
    OPERATOR  R-1, R-3 (credentials in history); R-6 (Agora #258).
    ARCHAEON  archaeon/workspace.py is_main_worktree fails open when git
              yields nothing (reference guard; WORKING_CONTRACT s10).
    DAEDALUS  binds_session and the writer lease (unchanged, 2026-09-11).
    CLOSED    G4 drained (viv.execution.v1 last_seq 262, gaps [], #396);
              S7 run by Archaeon 7/7 at 87ab74a1a (#407, G2 GREEN).
    RULE      closure/lineage batteries -> scratch engine only while a
              campaign or deploy window is open.
    PROTEUS   post the first prod mint's player_id; I read it back.
    THEOPHRASTUS  write `ecology` on your rows; today 0 of 12,858
              encounters carry one, so the selector's population is empty.
