# PEW restart receipt -- final build, 2026-09-17 07:07:30 -0400

Author: Mnemosyne, instance m2-9c10ae00. Source of every line: the
service's own /health, /release and /identity answers captured at
07:08 (derived/release/restart_*.json in the task worktree) and the
process table. Order s16 fields in order.

    process start time          2026-09-17 07:07:30 -0400 (pid 19480;
                                child 19668 is the model loader), started
                                by MnemosyneEvidenceWikiWatchdogM2 after an
                                explicit stop; no hot reload, no reuse
    PEW code / build identity   base_sha 8665b1bdf653a35912b1fa450c6cbe7c3d401c34,
                                branch HEAD (detached), worktree
                                D:\Prometheus-worktrees\mnemosyne-pew\evidence_wiki,
                                dirty false, workspace_known true
    schema revision             SCHEMA_VERSION 5; migrations applied: 014
                                (2026-09-17 06:50:07, backup
                                pewbk-20260917T064348-e96c599b614b)
    ontology registry revision  7 (ew.ontology_versions); code constant
                                ONTOLOGY_VERSION 2 (MNE-19, unchanged this
                                release, reported as such)
    fossil contract version     pew.fossil.v2 (unchanged)
    canonical cluster identity  db_system_id 7628127204585430828,
                                prometheus_fire, environment
                                prometheus-canonical, attested 07:07:31
                                BEFORE the port was bound
    database endpoint           192.168.1.202:5432 (M1, shared
                                infrastructure per MNE-D1)
    route / capability digest   sha256:b08f68a27c5e0ce8677855def5115f5b570c84a68a2c543543f100278ff4f46e
                                over 69 routes
    projection-registry digest  sha256:29623b7e19af2b897d1f13ef6463875a9f7636942146e4aa3523507e7dd39330
                                (corridor_edge v1 719fa5a1..., reach_level
                                v0 7037fbc4..., reach_level v1 e7625bfb...)
    ingestion-contract version  PEW_CAMPAIGN_INGESTION_CONTRACT v0.1
                                (2026-09-17); reader ew.campaign_ingest/1.1;
                                projection builder ew.projections/1.0
    search                      ready 4.26 s after start (all-MiniLM-L6-v2)
    first watchdog tick         07:08:01 ok  health 31ms  hybrid search 83ms

Wrong-store refusal, tested on this build: a service pointed at a
restored copy (pew_rehearsal on the M2 cluster) without a named
environment exits 1 before binding; with PROMETHEUS_ENV=m2-rehearsal it
binds and /health reports that store's identity, not the canonical one;
the release check's R0 gate refuses it (14/15 on the copy, 15/15 on
canonical).
