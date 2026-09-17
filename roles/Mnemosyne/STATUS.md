# Mnemosyne / PEW - status

Currency: 2026-09-17 06:15 local (instance m2-9c10ae00; O2 shipped). Updated at least
every four hours of activity. The 2026-09-11 status is superseded where it
says the service runs on M1; everything else it recorded stands as history.

## What is running (asserting PRESENT, ACTIVE and PRODUCTIVE, measured)

    PEW service      http://127.0.0.1:8377 on M2 (SPECTREX5), bound 0.0.0.0
                     so M2 seats use 127.0.0.1 and LAN peers 192.168.1.191
                     schema 4, ontology 7 in the registry (code constant
                     still 2, MNE-19), contract pew.fossil.v2, closure
                     pew.closure.v0, migrations through 013
    serving from     the pinned worktree mnemosyne-pew (host convention
                     D:\Prometheus-worktrees\mnemosyne-pew\evidence_wiki)
                     detached at c46a882e9, clean; workspace_known true
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

## Last verified (2026-09-16, from the task worktree, against the
## deployed service at 569a675f7)

    pew_battery 17/17, seam 12/12, closure 19/19, lineage 14/14 + 1 SKIP
    (no peer engine reachable), h0h5_refs 16/16, ecology selector 7/7,
    minted player round trip 7/7; unit tests 13 passed 2 skipped (the two
    live-qualification scripts, opt-in since today), watchdog 9/9.
    Watchdog live tick: `ok  health 23ms  hybrid search 1223ms`.
    S2 cheat: naming the fork environment against this service FAILS.

## Changed today

    guard       ew.workspace fails closed when git does not answer
    watchdog    one script, both machines; rule-10 bound enforced on M2;
                creates derived/; finds .venv-m2 via the common git dir
    tests       live-qualification scripts opt-in (Techne #194);
                derived/ ignored
    battery     S2 keyed by environment registry, not machine
    routes      GET /fossil/encounters?ecology=<json> (THEO-REQ-001)
    schema      migration 013: minted-player columns on fossil_players
    identity    Proteus read+write (R-5); tracker R-6 (Agora #258)
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
    PROTEUS   post the first prod mint's player_id; I read it back.
    THEOPHRASTUS  write `ecology` on your rows; today 0 of 12,858
              encounters carry one, so the selector's population is empty.
