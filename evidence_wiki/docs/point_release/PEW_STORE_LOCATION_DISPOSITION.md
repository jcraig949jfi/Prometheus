# PEW store-location risk disposition (amendment 1 section 7G; release-blocking)

Author: Mnemosyne, instance m2-9c10ae00, 2026-09-17. Status: RULED the same
day (section 8 below); O2 executed. Read-only pass: every number below was
measured today; nothing was changed. Inherits roles/base-role/
RESPONSIBILITIES.md and WORKING_CONTRACT.md.

## 1. The question, in one sentence

The store PEW writes to is a PostgreSQL 17.9 cluster on M1 (SKULLPORT,
192.168.1.202), a machine that since 2026-09-15 belongs to a different
ecosystem; its nightly backup and weekly restore-verify run on that
machine, onto that machine's disk, under a scheduled task nobody in this
ecosystem can observe; and the amendment forbids productionising campaign
ingestion until canonical host, backup ownership/location, restore
procedure and migration/deploy authority are resolved.

## 2. Measured state (2026-09-17)

    cluster            PostgreSQL 17.9 (Windows), db prometheus_fire,
                       db_system_id 7628127204585430828
    size               2,861 MB total; ew is 21 MB of it. The bulk is
                       other seats' schemas: zeros 1,303 MB (2 tables),
                       charon_duckdb 867 MB, xref 493 MB, agora 62 MB,
                       viv 47 MB, noesis 10 MB, ludus_atlas 8 MB,
                       archaeon 4.6 MB, sigma 2 MB, comms 1.7 MB (6
                       tables) + others
    who uses it        comms: 22 registered agent instances on SPECTREX5
                       (M2), 14 on SKULLPORT (M1); senders in the last
                       3 days include Nestor and Agora (M1 ecosystem)
                       and Archaeon, Harmonia, Vivarium, Daedalus,
                       Proteus, Herakles, Techne, Mnemosyne (M2). The
                       store is SHARED INFRASTRUCTURE for both
                       ecosystems today, not a PEW-private asset.
    PEW service        on M2 since 2026-09-16 08:10 (pinned worktree,
                       fronting this cluster over the LAN; hybrid search
                       1.2 s; batteries green)
    backup             PEWBackupDaily 03:30 on M1, pg_dump -Fc of the
                       WHOLE database to F:\PrometheusBackups\pew on M1's
                       own disk, retention 14; PEWRestoreVerifyWeekly
                       Sun 04:30 on M1 into a scratch database. Last
                       evidence: restore receipt 2026-09-13 04:30
                       (committed 985a3f760). Whether the 09-14..09-17
                       nightly dumps ran: UNKNOWN from M2 (no share, no
                       shell, 8377/8811 do not answer; 5432 does).
    off-host copy      none (MNE-18 open; Techne #231: the intended
                       share is unreachable from M1)
    M2 local cluster   PostgreSQL 17.11, prometheus_fire, 21 MB, schemas
                       ew + public only -- the 2026-09-04 fork,
                       quarantined, no reader since 09-05. Same major
                       version as canonical: a pg_dump/pg_restore of the
                       canonical cluster onto M2 is version-compatible.
    LAN exposure       5432 on M1 accepts the committed credentials from
                       any LAN peer (B2, open since 09-04)

## 3. Risks, each with the measurement that makes it real

    R-A  UNOBSERVABLE BACKUP. The only evidence the canonical store is
         restorable is four days old and cannot be refreshed from this
         ecosystem. A dead disk on M1 tonight loses ew, comms (both
         ecosystems' inbox), viv, archaeon and the rest, with no copy
         anywhere else. Severity: data-loss class. This is the one that
         is release-blocking on its own.
    R-B  OWNERSHIP WITHOUT OPERATION. This ecosystem's evidence layer
         depends on a scheduled task, a disk and a Postgres service
         administered by nobody in it. "Silence is not health"
         (MONITORS rows 16-17 are UNLOCATED, not ACTIVE).
    R-C  SHARED STORE, DIVERGENT AUTHORITY. Two ecosystems now write
         comms to one cluster; a migration by one strands the other.
         Any move is therefore a program decision, not a PEW decision.
    R-D  CREDENTIALS. The committed defaults authenticate from any LAN
         host (R-1); a store on a machine outside this ecosystem widens
         who can reach it. Rotation is already the operator's (R-1).
    R-E  LATENCY/AVAILABILITY. Not a risk today: search 1.2 s, batteries
         green over the LAN. Becomes one only if M1 is powered down or
         re-imaged for the other ecosystem without notice.

## 4. Options

    O1  STATUS QUO + ATTESTATION. Store stays on M1. Someone with a
        shell on M1 (Nestor's operator session) confirms the backup
        task fires and exports the latest dump + manifest to a location
        M2 can read; MONITORS rows 16-17 move from UNLOCATED to
        ATTESTED-BY-<who>-<date>. Cost: minutes, on M1. Closes R-A
        partially (a copy exists), R-B not at all.
    O2  M2-OWNED BACKUP OF THE M1 STORE. Register PEWBackupDaily on M2
        running pg_dump over the LAN against 192.168.1.202 (the script
        already takes db_host from config; only PEW_BACKUP_DIR changes)
        and PEWRestoreVerifyWeekly on M2 into the M2 local cluster (17.11
        can restore a 17.9 dump). ~2.9 GB nightly over the LAN, of which
        ew is 21 MB; retention 14 = ~40 GB on M2. Closes R-A and R-B
        without moving the store or touching M1. Requires nothing from
        the other ecosystem. This is a deploy-window item on M2 only.
    O3  MIGRATE THE CLUSTER TO M2. pg_dump/pg_restore prometheus_fire
        (2.9 GB) onto M2's 17.11, re-point every client's EW_DB_HOST
        (both ecosystems' comms, PEW, viv, archaeon), update
        comms/environments.json (the M2 cluster gets the canonical
        role; db_system_id changes, so every store-identity guard
        re-keys), rotate credentials in the same window (R-1). Closes
        R-A..R-E. Cost: one coordinated window of an hour or two, a
        re-key of environments.json, and Nestor's ecosystem re-pointing
        to M2 for comms -- which inverts today's dependency rather than
        removing it.
    O4  SPLIT: ew + this ecosystem's schemas to M2, comms stays on M1
        (or is duplicated). REJECT: two canonical stores with one comms
        is the 09-04 fork again, and "comms in my Postgres" is a
        registered fact in my inventory that would become false in a
        way every seat's guard is built to refuse.

## 5. Recommendation (my lean; the operator decides)

    NOW (no deploy window needed on the production substrate; M2 only):
      O2. An M2-owned nightly dump of the canonical cluster and a weekly
      restore into the M2 local cluster. It is additive, it touches
      nothing on M1, it makes the backup observable from this ecosystem
      within 24 h, and it produces the dump O3 would start from. Until
      it has run once, campaign ingestion stays a reader over committed
      files (which are themselves durable in git) and writes nothing
      that only the store holds -- that is the release-blocking gate
      restated as a mechanism.
    THEN, as a planned cutover with a date, not as a side effect:
      O3 if M1 is to remain the other ecosystem's machine for months;
      O1+O2 permanently if M1 comes back to this ecosystem. The decision
      hinges on one operator fact I do not have: how long M1 stays
      handed over.
    ALSO, orthogonal and already the operator's: R-1 rotation in the
      same window as any O3.

## 6. What "resolved" means, so the gate can be checked and not asserted

    canonical host            comms/environments.json names it; every
                              guard keys on its db_system_id; PEW's
                              STATUS says which; MONITORS rows agree
    backup ownership/location a MONITORS row on the OWNING machine with
                              a freshness source readable from this
                              ecosystem (a manifest file with sha256 and
                              a restore verdict, dated within 36 h)
    restore procedure         docs/BACKUP_AND_RESTORE.md rewritten for
                              the chosen host, and one restore receipt
                              produced by the M2-side job (not the 09-13
                              M1 receipt)
    migration/deploy authority a DECISIONS.md row (Archaeon) naming who
                              may run a migration against the canonical
                              cluster and in which windows (amendment
                              section 11 made the freeze a rule; this
                              names the hand)

## 7. What I will not do without the ruling

    - restore anything into the M2 local cluster that could be mistaken
      for canonical (the store-identity guard would refuse it anyway,
      and that refusal is the point);
    - re-point any client's EW_DB_HOST;
    - register the M2 backup task before the deploy window opens, even
      though it is M2-only (amendment section 3: "production mutation is
      not [allowed]"; a task that reads production is a grey area and I
      am reading it strictly).

## 8. Ruling and execution (addendum, 2026-09-17)

The operator ruled the same day (verbatim: roles/Mnemosyne/prompts/
2026-09-17_point_release/02_OPERATOR_RULING_MNE-D1.md): O2 approved now;
O3 deferred behind seven explicit conditions; O4 rejected; O1 alone
insufficient; M1 remains SHARED infrastructure, not handed over, while
the canonical cluster serves both ecosystems; backup ownership and
database ownership are separate questions.

O2 executed 2026-09-17 (commit 67b6f7323; pin c46a882e9):

    backup 1   pewbk-20260917T055050-fea46038fa3c  1,095,684,908 B  153 s
               (hand-run from the task worktree; source identity attested
               7628127204585430828; cheat: the M2 fork named as source
               was REFUSED with 0 files written)
    restore 1  into 127.0.0.1 (M2, PG 17.11), rc 0, 199 s, 164/164 tables,
               5,765,459 / 5,765,473 rows (14 = live drift), loss {},
               chain identical -> RESTORE_VERIFIED
    backup 2   pewbk-20260917T055922-1b1967c7670a  1,095,689,332 B  234 s
               by the scheduled task PEWBackupDailyM2 itself (S4U, pinned
               worktree)
    restore 2  by PEWRestoreVerifyWeeklyM2 itself: rc 0, 206 s, 164/164,
               5,765,480 / 5,765,491 (11 = drift), loss {}, chain identical
               -> RESTORE_VERIFIED
    alarms     failed job -> comms; missed job -> the M2 watchdog's stale
               check (36 h / 8 d), exercised: one report per stale day
    receipts   D:\PrometheusBackups\pew\*.manifest.json,
               restore_verify_*.json; committed copy
               evidence_wiki/ops/restore_verification.json

Section 6's "resolved" test, re-read against this: canonical host --
unchanged, M1, named in environments.json; backup ownership/location --
NOW Mnemosyne on M2, MONITORS rows PEWBackupDailyM2 /
PEWRestoreVerifyWeeklyM2 with readable freshness; restore procedure --
docs/BACKUP_AND_RESTORE.md rewritten, two M2-side receipts exist;
migration/deploy authority -- still the open item (a DECISIONS row,
Archaeon). O3 readiness is tracked as MNE-46.
