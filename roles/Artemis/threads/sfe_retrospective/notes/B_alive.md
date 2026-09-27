# Spike B -- what is actually ALIVE (SFE ecosystem and neighbours)

Author: research assistant for seat Artemis (ubu002). Measured 2026-09-27 ~15:05-15:25 UTC.
Mode: READ-ONLY. No commits, no DB writes (psycopg2 conn.set_session(readonly=True); verified
transaction_read_only = on). Repo: /home/jcraig/Prometheus-worktrees/artemis-base-role at f287a4fdb
(origin/main tip 2026-09-27). No `git fetch`/`pull` was run; remote refs are as last fetched
(newest remote ref dated 2026-09-27).

Store: prometheus_fire at 192.168.1.202 (inet_server_addr 192.168.1.202, system_identifier
7628127204585430828 = the CANONICAL M1 cluster per MONITORS.md row PEWBackupDailyM2). DB clock at
query time: 2026-09-27 11:20:42 -04:00.

Host naming used below: M1 = SKULLPORT (192.168.1.202), M2 = SPECTREX5 (192.168.1.191), M4 = harry1.

Base-role rule 8 is applied throughout: a heartbeat, watchdog tick or scheduled no-op is NOT
progress. Three levels are kept separate: CODE (implemented), USE (exercised by a client), DOMAIN
OUTPUT (rows/experiments/claims that advance science).

---------------------------------------------------------------------------------------------------

## 0. Status table

| # | Component | Classification (2026-09-27) | Last domain output | Last sign of process life | Key evidence |
|---|---|---|---|---|---|
| 1 | SFE engine (SerendipityFoundryEngine, Daedalus; M2 https://192.168.1.191:8811, 9.0.1, schema 9, SQLite ledger eng_906356f7) | IMPLEMENTED; RECENTLY USED (to 2026-09-18); now NOT SERVING as of last host evidence 2026-09-25 -> effectively IDLE/DOWN. Current state UNKNOWN / NEEDS HOST EVIDENCE (M2) | 2026-09-18 (Campaign 4/5 runs; atlas last_seen 2026-09-18 11:07) | pid 19464 listening but HUNG 2026-09-24 21:24Z (#563); "actively refused" 2026-09-25 11:40Z (#573); "nothing on :8811" 2026-09-25 18:1xZ (#586) | comms #563 #573 #586; atlas.engine_instance; last code commit 9cfcd3779 2026-09-18 |
| 1a | SFE on M1 (eng_8a37a5d3, schema 8) | SUPERSEDED / HISTORICAL (archive ledger) | 2026-09-14/15 | M1 8811 closed from ubu002 today | Daedalus STATUS "SFE on M1 RETIRED"; MONITORS SFEngine row |
| 1b | SFEngineM2Watchdog | DEAD/DISABLED as of 2026-09-24 (state Disabled, last result 2) | n/a | last run 2026-09-24 05:25 local | comms #563 |
| 1c | SFE Postgres-ledger migration (operator ruling 2026-09-18, Harmonia #448) | NOT IMPLEMENTED (design/ruling only) | none | none | no `sfe` schema in prometheus_fire; no postgres/psycopg in SerendipityFoundryEngine/sfe |
| 2 | SFE clients (sfclient; archaeon campaign1-6, vivarium/viv, genesis/harmonia_*) | IMPLEMENTED; RECENTLY USED to 2026-09-18; campaign6 design-only; genesis clients HISTORICAL (2026-09-04/05) | 2026-09-18 | n/a | git log per dir (s.2) |
| 3 | Vivarium consumer vivarium@m2 + viv queue | IMPLEMENTED, QUALIFIED; last domain execution 2026-09-17 20:20; MAINTAINED BUT IDLE then DOWN (parked 09-19 idle bound; dead-man PARKED 2026-09-25 11:40Z on SFE UNREACHABLE) | 2026-09-17 20:20:26 (viv.execution_attempt / events) | viv.worker_heartbeat last_seen 2026-09-25 07:24:39 -04 (no work) | viv tables (s.3), comms #563 #573 |
| 3a | Vivarium consumer on M1 (vivarium@m1) | SUPERSEDED / HISTORICAL | 2026-09-14 19:27 | heartbeat 2026-09-14 19:53 | viv.worker_heartbeat |
| 3b | VivariumOutboxDelivererM2 | IDLE (outbox 262/262 DELIVERED, last delivery 2026-09-17 20:24) | 2026-09-17 | idle ticks to 2026-09-24 21:20Z (#563) | viv.pew_outbox |
| 4 | PEW service (evidence_wiki, M2 :8377, canonical store) | IMPLEMENTED; last substantive writes 2026-09-18; service HUNG 2026-09-24; watchdog PARKED 2026-09-23 08:35. MAINTAINED BUT IDLE -> DOWN; current state UNKNOWN / NEEDS HOST EVIDENCE | ew.write_log 2026-09-18 14:30:16; claims 2026-09-17 09:51 | ew.read_log last watchdog search 2026-09-23 07:32:06 -04 | ew tables (s.4), comms #542 #563 |
| 4a | PEW on M1 (:8377) | SUPERSEDED (DORMANT since 2026-09-15 17:11) | 2026-09-15 | M1 8377 closed from ubu002 today | MONITORS row MnemosyneEvidenceWikiWatchdog |
| 4b | PEW backups PEWBackupDailyM2 / RestoreVerifyWeeklyM2 | UNCLEAR / NEEDS HOST EVIDENCE (last recorded ACTIVE 2026-09-17; artifacts live on M2 D:) | n/a | 2026-09-17 in MONITORS | MONITORS rows 18-19 |
| 4c | PEW backups on M1 (PEWBackupDaily, RestoreVerifyWeekly) | SUPERSEDED ("NOT RELIED ON since 2026-09-17") | 2026-09-13 restore receipt | unknown | MONITORS rows 16-17 |
| 5 | Archaeon producer/tick (ArchaeonTick, archaeon/producer, created_by=archaeon queue rows) | IMPLEMENTED; HISTORICAL for the SFE path. Last archaeon rows to viv queue 2026-09-17 19:59 (C4 rehearsal); last cadence_log 2026-09-17 19:22; archaeon/producer code last touched 2026-09-17. ArchaeonTick on M1 UNKNOWN since 2026-09-15 20:57 | 2026-09-17 | 5 archaeon rows still `queued` since 2026-09-14/15 (M1 era) | viv queue, archaeon.cadence_log (s.5) |
| 5a | archaeon.experiment_queue (own queue) | HISTORICAL (1 row, QUEUED since 2026-09-05, never claimed) | 2026-09-05 | none | s.5 |
| 5b | Archaeon's non-SFE work (envgate2, frontier, z80atlas, lineage) | ACTIVELY/RECENTLY USED (not SFE) -- ENVGATE-02 verdict 2026-09-26; frontier events to 2026-09-22; commits 2026-09-26/27 | 2026-09-26 | comms Archaeon last post 2026-09-26 20:27 | comms #593 #676 #710 #736 #741 |
| 6 | Daedalus-owned engine components (SFE engine, serve.py, watchdog, deploy/relocate, contract) | IMPLEMENTED; last commit 2026-09-18; seat last active in comms 2026-09-18 16:07 -> MAINTAINED BUT IDLE (no owner activity for 9 days while engine hung/down) | 2026-09-18 | Daedalus comms.agents last_active 2026-09-18 16:07:03 | s.6 |
| 7 | REST 8811 SFE | see #1: UNKNOWN / NEEDS HOST EVIDENCE (last host evidence: down 2026-09-25) | | | |
| 8 | REST 8377 PEW | see #4: UNKNOWN / NEEDS HOST EVIDENCE (last host evidence: hung 2026-09-24) | | | |
| 9 | comms (schema comms: messages, task_queue, receipts) | ACTIVELY USED (messages today 2026-09-27 11:18; task_queue last update 2026-09-26 10:14) -- coordination substrate, not domain output | n/a | 2026-09-27 11:18:51 | s.7 |
| 10 | agora (machine_probes, intelligence_outputs, heartbeats) | ACTIVELY USED but only by M4 (MachineProbe-M4, HealthCheck-M4, Pronoia brief cycle). M1/M2 probes absent in last 14 days. Scheduled activity, not domain output (rule 8). Research_queue/clio tables HISTORICAL (May 2026) | Pronoia cycle 2026-09-27 08:15 | 2026-09-27 11:15:58 | s.7 |
| 11 | Atlas (schema atlas) | RECENTLY USED; seat PARKED for loop since 2026-09-19; one-off harvests 2026-09-24..26 on operator instruction; experiment coverage lags (newest modelled activity 2026-09-22) | harvest_run 2026-09-26 09:49 | same | s.8 |
| 12 | ew claims/evidence provenance pathway | RECENTLY USED to 2026-09-17/18, then no writes; claims 147 (last 2026-09-17), evidence 133 (last 2026-09-17) | 2026-09-18 | | s.4 |

Bottom line: after 2026-09-18 the SFE -> Vivarium -> PEW pipeline produced ZERO domain rows
(no viv executions, no ew writes, no new claims/evidence). The live science on
2026-09-19..27 happened OUTSIDE it (Archaeon envgate/frontier, Bellerophon z80atlas coupling,
Nestor NPE, Cosmos, Ensorain, Aether), recorded in git and comms rather than viv/ew. Cyclops
#586 (2026-09-25): "SFE is not currently usable as producer infrastructure".

---------------------------------------------------------------------------------------------------

## 1. Method and exact commands

### 1.1 Git (repo worktree above)

    git log -1 --format='%h %ad %an %s' --date=iso -- <path>
    git log --oneline --since=<YYYY-MM>-01 --until=<next month>-01 -- <path> | wc -l   (2026-06..09)
    weekly: --since=2026-09-{01,08,15,22} windows of 7 days
    git log --remotes -1 --format='%h %ad %s' --date=iso -- <path>   (all seat branches)
    git log --reverse ... | head   (first commit per path)

Repository is NOT shallow (git rev-parse --is-shallow-repository = false; oldest commit 2026-03-22).

Results (last commit on origin/main; monthly counts Jun/Jul/Aug/Sep; weekly counts for Sep weeks
starting 01/08/15/22):

| path | last commit | Jun | Jul | Aug | Sep | wk01 | wk08 | wk15 | wk22 |
|---|---|---|---|---|---|---|---|---|---|
| SerendipityFoundry | 9cfcd3779 2026-09-18 16:06 -0400 Daedalus: Campaign 6 engine interface delta v0.1 | 0 | 0 | 0 | 116 | 39 | 29 | 48 | 0 |
| SerendipityFoundry/SerendipityFoundryEngine | 9cfcd3779 2026-09-18 (same) | 0 | 0 | 0 | 98 | | | | |
| SerendipityFoundry/SerendipityFoundryClient | 9739cc0ca 2026-09-17 10:32 (merge) | 0 | 0 | 0 | 18 | | | | |
| vivarium | 1db58c264 2026-09-17 19:40 Vivarium: canary run 11 OK 35/35 | 0 | 0 | 0 | 77 | 10 | 27 | 40 | 0 |
| evidence_wiki | 0d448387e 2026-09-18 14:35 Mnemosyne: C6 PEW observatory-storage contract v0.1 (design only) | 0 | 0 | 0 | 70 | 37 | 10 | 23 | 0 |
| archaeon (whole) | 0a5c0895d 2026-09-27 14:30 +0000 Artemis: C-001/E-002 | 0 | 0 | 0 | 285 | | | | |
| archaeon/producer | 7017dc79e 2026-09-17 21:48 Archaeon: HARM-13 table | 0 | 0 | 0 | 49 | 9 | 38 | 2 | 0 |
| atlas | 7190591f4 2026-09-26 09:51 Atlas: ATLAS-37 Cosmos adapter | 0 | 0 | 0 | 15 | | | | |
| comms | 8216dd3de 2026-09-17 06:43 Mnemosyne PEW point release | 0 | 0 | 0 | 7 | | | | |
| agora | 6be994430 2026-09-17 21:25 M4 probe cadence | 0 | 0 | 0 | 1 | | | | |
| genesis (SFE precursor/harmonia clients) | f2e3148e3 2026-09-05 | 0 | 0 | 56 | 46 | | | | |
| roles/Daedalus | 3ddbf5b6a 2026-09-17 23:32 STATUS: C4 engine readiness complete | 0 | 0 | 0 | 87 | | | | |
| roles/Vivarium | 8c5a1a23b 2026-09-24 17:40 INCIDENT M2 host at 98% commit | 0 | 0 | 0 | 95 | | | | |
| roles/Mnemosyne | 8915b660f 2026-09-18 14:36 STATUS pin e8f90c04d | 0 | 0 | 0 | 48 | | | | |
| roles/Archaeon | ca189b020 2026-09-27 10:16 E-002 dispatched | 0 | 0 | 0 | 217 | | | | |
| roles/Nestor | 11e0665c3 2026-09-26 09:32 | 0 | 0 | 0 | 697 | | | | |
| roles/Bellerophon | 98a28dd39 2026-09-25 15:43 | 0 | 0 | 0 | 142 | | | | |
| roles/Atlas | 7190591f4 2026-09-26 09:51 | 0 | 0 | 0 | 28 | | | | |

First commits: SFE engine d332658cf 2026-09-01; Vivarium 8b940a165 2026-09-05; evidence_wiki
c711c5bf6 2026-09-01. So SFE/Viv/PEW are September-only systems: born 09-01..05, heavy commit
activity 09-01..18, zero commits in the week of 2026-09-22 on any of the three code trees.
Across ALL remote refs (`git log --remotes -1`) the newest commit touching SerendipityFoundry,
vivarium, evidence_wiki, archaeon/producer, roles/Daedalus, roles/Mnemosyne is the same as on
main (2026-09-17/18); roles/Vivarium newest is the 2026-09-24 incident receipt.

### 1.2 Database (read-only) -- helper scripts

Connection: `export EW_DB_HOST=192.168.1.202`; params from evidence_wiki/ew/db.py load_config();
`conn.set_session(readonly=True, autocommit=True)`; `SET statement_timeout='60s'`.
Freshness script: for every base table in a schema, count(*) (or reltuples if > 3M) and max() of up
to three timestamp columns, filtered `<= now() + 1 day`.

Schemas present (base-table counts): agora 13, analysis 1, archaeon 4, atlas 35, bus 6,
charon_duckdb 14, comms 6, ew 44, kill 2, ludus_atlas 7, meta 2, noesis 19, results 3, sigma 7,
signals 2, tensor 2, viv 12, viv_archaeon_test_797363d7 5, viv_dev_h0h5 5, viv_dev_h1h0 5,
viv_dev_h1h0b 5, viv_dev_h1h0c 5, viv_dev_h1h0m 5, xref 2, zeros 2.
There is NO `sfe` schema (the SFE ledger is SQLite on the engine host).

### 1.3 Ports (from ubu002, 2026-09-27 15:22 UTC, bash /dev/tcp, 4 s timeout)

    192.168.1.202:8811  closed/filtered/timeout
    192.168.1.202:8377  closed/filtered/timeout
    192.168.1.202:5432  OPEN
    192.168.1.191 (M2): NOT re-probed by me; the Artemis coordinator probed at ~15:30Z and reported
    8811/8377/5432/22 all closed/filtered (a Windows firewall could explain it).

A closed port from ubu002 is NOT proof of death. M1 8811/8377 being closed is consistent with the
documented retirement of M1 SFE/PEW (2026-09-15), not a new finding. M2 truth lives on M2:
UNKNOWN / NEEDS HOST EVIDENCE; the latest host evidence is in comms (s.1 below, #563/#573/#586).

---------------------------------------------------------------------------------------------------

## 2. SFE engine and clients

Code: SerendipityFoundry/SerendipityFoundryEngine (serve.py, sfe/, deploy/, tests/), Client
SerendipityFoundry/SerendipityFoundryClient (sfclient). ~9.7k LOC core per Archaeon ENGINE_LANDSCAPE.

Declared state (roles/Daedalus/STATUS.md, currency 2026-09-18 03:45Z): "SFE 9.0.1 IS PRODUCTION"
on M2 https://192.168.1.191:8811, schema 9, build 699ca0f9 at b0d752183, ledger eng_906356f7 at
C:\Prometheus-data\sfe\engine.db; supervisor SFEngineM2Watchdog; "SFE on M1 RETIRED; ledger
eng_8a37a5d3 is an archive on SKULLPORT". This STATUS is 9 days stale.

MONITORS.md (currency 2026-09-18):
- SFEngineM2Watchdog: "ACTIVE (state file last_success_at 2026-09-16T11:48:31Z ...)"; history:
  engine DEAD 2026-09-14 05:33 -> 2026-09-16 11:48 (~600 relaunches refused).
- SFEngine (M1): "ACTIVE, schema 8, instance eng_8a37a5d3 ... since 13:34 2026-09-11" (stale row;
  superseded by the M1 retirement).

Host evidence after 2026-09-18 (comms, SELECT only):
- #563 2026-09-24 17:42 -04 Vivarium (measured on SPECTREX5 21:24-21:40Z): "8811 is HUNG, and its
  supervisor is off ... curl https://192.168.1.191:8811/v2/version -> http 000 (timeout) ... port IS
  listening ... pid 19464, started 09-19 08:45 local ... SFEngineM2Watchdog: state Disabled, last run
  2026-09-24 05:25 local, LAST RESULT 2". Cause context: M2 at 98% commit (48 archaeon pool children).
- #573 2026-09-25 07:40 -04 Vivarium dead-man PARKED: upstream UNREACHABLE, "WinError 10061 ...
  actively refused" at https://192.168.1.191:8811/v2/version (i.e. by 11:40Z the process no longer
  held the port).
- #586 2026-09-25 14:08 -04 Cyclops M2 read-only audit: "SFE 9.0.1 is NOT serving on M2 (nothing on
  :8811, SFEngineM2Watchdog disabled). Vivarium is down too. So SFE is not currently usable as
  producer infrastructure under s8."
- No comms message after 2026-09-25 18:10 mentions SFE/8811 except #634 (false positive: the digits
  419388811). Query:
    select id, created_at, sender, subject from comms.messages where created_at > '2026-09-25 14:10'
    and (subject||' '||body) ~* '(serendipity|\msfe\M|8811|sfengine|vivarium|8377|\mpew\M|daedalus)'
    -> 628 (Cyclops, unrelated incident), 634 (false positive).
- Daedalus's last comms post: 2026-09-18 16:07:03 (#460); comms.agents Daedalus last_active_at
  2026-09-18 16:07:03 (SPECTREX5). No owner response to #563 recorded.

Domain use (DB):
- atlas.engine_instance: sfe M2 schema 9 endpoint https://192.168.1.191:8811 last_seen_at
  2026-09-18 11:07:51; sfe M1 schema 8 last_seen 2026-09-11 03:48:52.
- atlas.experiment engine_id='sfe': 57 experiments, last_activity_at 2026-09-18 11:07:51.
- Postgres-ledger ruling (Harmonia #448, 2026-09-18, operator: "SFE ledger moves from SQLite to the
  canonical Postgres on M1"): NOT IMPLEMENTED -- no `sfe` schema exists; `grep -rliE
  'postgres|psycopg' SerendipityFoundry/SerendipityFoundryEngine/sfe` returns nothing.

Clients (dirs with sfclient/8811/SerendipityFoundry references; last commit):
    archaeon/campaign1  18 files  b0281a9b5 2026-09-16
    archaeon/campaign2  34 files  e6a4547d1 2026-09-18
    archaeon/campaign3  33 files  cb9135104 2026-09-17
    archaeon/campaign4  44 files  c9e9d54f1 2026-09-18
    archaeon/campaign5  35 files  c9e9d54f1 2026-09-18
    archaeon/campaign6   5 files  9471a5771 2026-09-19  (Campaign 6 = design only, "nothing built")
    archaeon/frontier    5 files  1049aac73 2026-09-26  (only a sys.path insert of the client dir;
                                                          no 8811 call found in loop.py/scheduler.py)
    archaeon/producer    1 file   7017dc79e 2026-09-17
    vivarium/viv         7 files  1023f81bd 2026-09-17
    genesis/harmonia_a  32 files  7e0bd1100 2026-09-04  (historical integration / GEN2 qualification)
  Python modules importing sfclient: genesis/harmonia_a 8, SFE engine 8, SFE client 7,
  genesis/harmonia_c 5, vivarium/viv 3, vivarium/tools 3, archaeon/campaign1 3, archaeon/campaign2 1,
  archaeon/fossils_b1.py 1.
  Atlas registry also lists bellerophon.toolbox "backends local/sfe/npe; not yet harvested".

Classification: IMPLEMENTED; RECENTLY USED (last domain use 2026-09-18: Campaigns 4/5); no domain
output since; last host evidence (2026-09-25) says down with supervisor disabled; owner idle since
09-18. Current liveness: UNKNOWN / NEEDS HOST EVIDENCE (M2 tasklist/netstat + SFEngineM2Watchdog
state file + engine.db mtime).

---------------------------------------------------------------------------------------------------

## 3. Vivarium (vivarium/, schema viv)

Freshness (count | max timestamps):
    viv.execution_attempt            1254 | opened_at 2026-09-17 20:20:25; closed_at 20:20:26
    viv.execution_step               3208 | started/completed 2026-09-17 20:20:26
    viv.gate_receipt                   55 | evaluated_at 2026-09-17 19:40:03
    viv.intervention_receipt            0 |
    viv.pew_outbox                    262 | created 2026-09-17 20:20:26; delivered 2026-09-17 20:24:02 (262/262 DELIVERED)
    viv.provenance_envelope             0 |
    viv.register_errata                 1 | 2026-09-06
    viv.register_errata_rows          246 |
    viv.research_experiment_events   3865 | occurred_at 2026-09-17 20:20:26
    viv.research_experiment_queue    1242 | created 2026-09-17 19:59:54; claimed 2026-09-17 20:20:25
    viv.start_bundle                  133 | first_seen 2026-09-17 20:20:25
    viv.worker_heartbeat                3 | last_seen 2026-09-25 07:24:39

worker_heartbeat rows:
    vivarium@m2  SPECTREX5 pid 20004 started 2026-09-17 09:52:53 last_seen 2026-09-25 07:24:39 base_sha 6e7ac48f0
    vivarium@m1  SKULLPORT pid 13460 started 2026-09-06 04:19:16 last_seen 2026-09-14 19:53:44
    vivarium@debit-receipt SKULLPORT  2026-09-10 (one-shot)

Queue by status/created_by (select status, created_by, count(*), min, max(created_at) ... group by 1,2):
    completed archaeon 614 (09-06 .. 09-17 19:59)   failed archaeon 76 (09-06 .. 09-11)
    cancelled archaeon 483 (09-06 .. 09-10)         queued archaeon 5 (2026-09-14 23:27 .. 09-15 16:12)
    completed vivarium-canary 22 / failed 17 (2026-09-17)
    small operator/demo/bringup rows 2026-09-05/06/10/11
Rows created per day: 09-17 87 (48 archaeon C4-REH rehearsal + 39 canary), 09-15 4, 09-14 6,
09-13 6, 09-12 31, 09-11 31, 09-10 722, 09-06 342. NOTHING after 2026-09-17.
claimed_by: vivarium@m2 87 (last 2026-09-17 20:20:25); vivarium@m1 639 (last 2026-09-14 19:27).
Events per day: 09-17 584, 09-14 35, 09-13 20, 09-12 155, 09-11 969, 09-10 1957.

Seat/host evidence:
- Vivarium STATUS (2026-09-17): "Is Vivarium alive: YES ... QUALIFIED_FOR_CAMPAIGN".
- MONITORS: VivariumConsumerM2 ACTIVE since 2026-09-17 13:52Z; VivariumDeadmanM2 ACTIVE;
  VivariumOutboxDelivererM2 ACTIVE (HELD_NO_CREDENTIAL at the time; later all delivered).
- comms #563 (2026-09-24): "Consumer parked 2026-09-19T00:29:52Z on the 24 h idle bound with an EMPTY
  queue ... 0 rows enqueued since 09-18 ... the 6-day gap cost no science because nothing was fed to
  the queue." Also self-reported defect F1: dead-man failed to escalate STORE_UNREADABLE, disabled
  itself, "a watchdog that stopped watching and told no one for 31 h".
- comms #573 (2026-09-25 11:40Z): dead-man PARKED 3/3, consumer DEAD, upstream 8811 UNREACHABLE.
- Vivarium comms.agents last_active 2026-09-25 07:40:06.
- The heartbeat last_seen 2026-09-25 07:24 is process/dead-man life WITHOUT work (rule 8).

Classification: IMPLEMENTED and QUALIFIED; last domain execution 2026-09-17 20:20 (C4 rehearsal rows);
MAINTAINED BUT IDLE 09-18..09-24 (empty queue, parked); DOWN/PARKED since 2026-09-25 11:40Z because
SFE is unreachable. 5 archaeon rows from the M1 era (2026-09-14/15) remain `queued` -- stranded
demand, never executed.

---------------------------------------------------------------------------------------------------

## 4. PEW / Evidence Wiki (evidence_wiki/, schema ew, :8377)

Freshness (selected; full list in s.9):
    ew.write_log            6077 | created_at 2026-09-18 14:30:16
    ew.read_log             4981 | created_at 2026-09-23 07:32:06
    ew.claims                147 | created_at 2026-09-17 09:51:38
    ew.evidence              133 | created_at 2026-09-17 06:51:58
    ew.producer_events       287 | received_at 2026-09-18 14:30:16 (09-17: 281, 09-18: 6)
    ew.campaign_observations 32938 | recorded 2026-09-18 02:23:49; ingested 2026-09-18 14:21:37
    ew.derived_artifacts      82 | 2026-09-18 14:35:02
    ew.projection_rows      2877 | built 2026-09-18 14:21:59
    ew.fossil_encounters   12935 | created 2026-09-17 10:02:34
    ew.fossil_players       6013 | created 2026-09-17 09:47:58
    ew.fossil_worlds        1000 | created 2026-09-14 19:27:13
    ew.experiments            79 | created 2026-09-03 21:26:56
    ew.hypotheses             21 | created 2026-09-02

Claims per day (desc): 09-17 4, 09-16 4, 09-15 1, 09-11 8, 09-10 1, 09-09 1, 09-04 1, 09-03 4.
Evidence per day (desc): 09-17 1, 09-16 1, 09-11 2, 09-09 1, 09-04 1, 09-03 4, 09-02 35, 09-01 88.
=> The evidence pathway front-loaded on 09-01/02 (seeding) and trickled to 09-17.

write_log by day/machine/agent since 2026-09-13 (count/accepted): M1 Theophrastus 92+42 (09-13/14),
M1 vivarium 8/14/262 (09-13/14/17 -- the 262 is the outbox flush on 09-17), M2 batteries
(closure/h0h5/lineage/pew/seam) 09-16/17, M2 campaign-ingest 16 (09-17) + 4 (09-18), M2 release-check
18+6, M2 Proteus 4+4 (09-16/17 half rejected). LAST WRITE 2026-09-18 14:30:16 (campaign-ingest /
release-check). Nothing since.

read_log by day since 2026-09-13: M1 watchdog 288/287/207 (09-13..15) then M1 stops; M2 watchdog
193 (09-16), 294, 286, 284, 288, 288, 288 (09-17..22), 90 (09-23) then stops. Non-watchdog reads
(real consumers): Theophrastus/vivarium 09-13/14, a handful 09-15, batteries 09-16/17, release-check
09-17/18. After 2026-09-18 the ONLY reader was the watchdog (rule 8: heartbeat, not use).

Host evidence:
- comms #542 2026-09-23 08:35 Mnemosyne: WATCHDOG PARKED, 8377 on M2, 12 non-productive ticks,
  last_success 2026-09-23T07:25:26, last_reason "search model not ready after uptime 448.4s
  (loading=True)" -- i.e. the service was restarted ~09-23 08:21 local and never became ready.
- comms #563 2026-09-24: "8377 is HUNG the same way ... http 000 (timeout). Port listening
  0.0.0.0:8377, pid 17192, started 09-23 08:21 local".
- Mnemosyne last comms post 2026-09-23 08:35 (the park); comms.agents last_active 2026-09-23 08:35:40.
- Mnemosyne STATUS (2026-09-18): PEW on M2, canonical store, watchdog M2 5 min; M1 PEW DORMANT since
  2026-09-15 17:11.

Backups: MONITORS rows PEWBackupDailyM2 / PEWRestoreVerifyWeeklyM2 ACTIVE as of 2026-09-17 (1.1 GB
dump, 164/164 tables restore-verified). Artifacts live on M2 D:\PrometheusBackups\pew; no DB-side
trace. Status after 2026-09-17: UNKNOWN / NEEDS HOST EVIDENCE. M1 backup jobs: NOT RELIED ON since
2026-09-17 (last evidence 2026-09-13 restore receipt).

Classification: IMPLEMENTED; last domain output 2026-09-18 (C4/C5 ingestion, reader 1.5); idle
09-18..09-23 (watchdog-only reads); watchdog PARKED 2026-09-23; service hung 2026-09-24. Current:
UNKNOWN / NEEDS HOST EVIDENCE. Canonical store itself is up (5432 answers).

---------------------------------------------------------------------------------------------------

## 5. Archaeon producer machinery

Tables:
    archaeon.cadence_gate      10 | updated_at 2026-09-06 07:50:35
    archaeon.cadence_log     1617 | decided_at 2026-09-17 19:22:28
    archaeon.experiment_queue   1 | created 2026-09-05 18:28:51, status QUEUED, never claimed
    archaeon.substrate_census 1310 | taken_at 2026-09-17 20:23:37 (per day: 09-17 20, 09-16 50, 09-15 4, 09-14 6, 09-13 6)

cadence_log since 2026-09-12: ADMITTED 246 (last 2026-09-17 19:22:28), REFUSED_MIN_SEPARATION 331
(last 2026-09-15 16:57:12). Instances: SKULLPORT#<pid> on 09-12..09-15 (one per tick = the M1
ArchaeonTick every 15 min), SPECTREX5#<pid> on 09-16/17 (bursts of 3 = campaign producers). Newest
three rows (09-17 19:22, SPECTREX5#22504) are ADMITTED with detail "human row; autonomous quota does
not apply", queue viv_test_f36ce6fb.research_experiment_queue -- test/rehearsal rows, not the
autonomous tick.

Queue rows created_by=archaeon in viv.research_experiment_queue: last 48 at 2026-09-17 19:59:53-54
(C4-REH-1 rehearsal, comms #401 "S4 GO C4-REH-1 -- rows RUNNING on 8811"); 5 still `queued` since
2026-09-14/15.

MONITORS ArchaeonTick (M1): "UNKNOWN since 2026-09-15 20:57 UTC (last cadence_log row ...) ... last
productive write 2026-09-15 20:12 UTC". There is no MONITORS row for an ArchaeonTick on M2; the M2
cadence rows are campaign-producer rows. Code: archaeon/producer last commit 2026-09-17;
archaeon/deploy (archaeon_tick.cmd, register_archaeon_tick.ps1) last commit 2026-09-06.

Archaeon's CURRENT work is not on this pathway: ENVGATE-02 relaunched 2026-09-25 18:30Z (#593),
24/24 confirmed (#676), verdict WINDOW_NOT_SUPPORTED 2026-09-26 (#710, c5ba19571); frontier
suppression logging repaired 2026-09-26 (#736); archaeon/frontier/registry/EVENTS.jsonl events on
09-20 (48), 09-21 (200,087), 09-22 (100,009) -- overwhelmingly BLOCKED_BY_SUPPRESSION retries (#735:
299,991 rows = ONE suppression decision), i.e. mostly scheduler churn, not new domain output.
Archaeon comms.agents last_active 2026-09-27 09:44 (SPECTREX5, branch main).

Classification: SFE-facing producer/tick = HISTORICAL (last autonomous tick 2026-09-15 on M1; last
producer rows 2026-09-17); archaeon.experiment_queue = HISTORICAL/abandoned; Archaeon seat = ACTIVE
on non-SFE engines (envgate2/z80atlas/frontier).

---------------------------------------------------------------------------------------------------

## 6. Daedalus-owned engine components

Owned (roles/Daedalus/STATUS.md, CHARTER.md): SFE engine + client, serve.py D-23 guard, M2 deploy/
relocation (deploy/relocate_m2.py), SFEngineM2Watchdog script, sfe_contract.json regeneration (with
Harmonia), isolation/attestation (A6). Last commits: SerendipityFoundry 2026-09-18 (C6 interface
delta v0.1, "nothing built"); roles/Daedalus 2026-09-17 23:32. Seat last comms activity
2026-09-18 16:07:03. No reply to #563 (2026-09-24, "Daedalus -- 8811 is HUNG, and its supervisor is
off"). Daedalus STATUS still says "SFE 9.0.1 IS PRODUCTION" (stale by 9 days; contradicted by #563,
#573, #586).

Classification: IMPLEMENTED; MAINTAINED BUT IDLE (owner dark since 2026-09-18) with the production
service reported down -- effectively unattended. Pending C6 / Postgres-ledger work: design/ruling only.

---------------------------------------------------------------------------------------------------

## 7. Coordination substrates (comms, agora)

comms (all ACTIVE):
    comms.messages      744 | last 2026-09-27 11:18:51
    comms.task_queue    111 | created 2026-09-26 00:19:06; updated 2026-09-26 10:14:59
                              status: done 74 (last 09-26 10:14), queued 34 (last 09-25 19:23), active 3 (last 09-19 03:32)
    comms.receipts     2000 | seen 2026-09-27 11:04:33
    comms.agents         49 | last_active 2026-09-27 11:18:51
    comms.agent_instances 141 | last_active 2026-09-27 11:18:51
Messages per day (last 14 d): 09-13 7, 09-14 19, 09-15 1, 09-16 59, 09-17 97, 09-18 64, 09-19 40,
09-21 12, 09-23 12, 09-24 17, 09-25 114, 09-26 63, 09-27 2.
Mentions in last 14 d: SFE/8811/serendipity/sfengine 90 msgs; vivarium/viv. 143 (last 2026-09-25
17:58); pew/8377/evidence wiki 69 (last 2026-09-25 11:29).
Last post per seat: Nestor 09-26 20:45, Archaeon 09-26 20:27, Bellerophon 09-26 12:42, Atlas 09-25
08:43, Vivarium 09-25 07:40, Harmonia 09-25 06:59, Atlas-M2 09-25 06:29, Mnemosyne 09-23 08:35,
Proteus 09-18 19:24, Daedalus 09-18 16:07.

agora:
    agora.machine_probes   132961 | taken_at 2026-09-27 11:15:58 -- last 14 d ONLY machine M4/harry1 (6570 rows)
    agora.intelligence_outputs 18188 | 2026-09-27 11:13:20 -- last 3 d: MachineProbe-M4, HealthCheck-M4,
                                       Pronoia brief/email/dashboard cycle (17 cycles, last 08:15)
    agora.agent_heartbeats     36 | MachineProbe-M4, Pronoia (M4) online today; next newest Elenchus 2026-09-11; rest May 2026
    agora.research_queue      425 | last completed 2026-05-30 (HISTORICAL)
    agora.clio_* / messages / decisions / gpu_reservations: last April-May 2026 (HISTORICAL)
Classification: comms ACTIVELY USED (coordination). agora ACTIVE only as M4 monitoring + Pronoia
reporting loop (scheduled activity; rule 8 says not progress); its queue/research tables HISTORICAL.
MONITORS rows PrometheusMachineProbeM1/M2 say "fails with 0x80070002" -- consistent with no M1/M2 probe rows.

---------------------------------------------------------------------------------------------------

## 8. Atlas (schema atlas) and provenance index

    atlas.harvest_run   119 | started 2026-09-26 09:49:52 (per day: 09-26 3, 09-25 18, 09-24 25, 09-21 5, 09-19 68)
    atlas.experiment   2053 | last_activity_at 2026-09-22 15:07:51
    atlas.fact       333044 | stated_at 2026-09-22 15:09:57
    atlas.git_commit   5848 | authored_at 2026-09-25 08:25:45
    atlas.portfolio_update 10 | issued 2026-09-25 08:47:46
    atlas.engine_instance 136 | last_seen 2026-09-18 11:07:51
    atlas.schema_migrations 12 | applied 2026-09-26 09:49:28
Experiments by engine (count, max last_activity): archaeon.frontier 422 (09-22 15:07), npe 276
(09-19 08:55), sfe 57 (09-18 11:07), vivarium 1242 (09-17 20:20), cosmos 10 (none), unassigned 46
(Atlas proposals).
atlas.engine registry marks sfe and vivarium "LIVE" -- this is Atlas's registry label, not a
liveness measurement (its sfe instance last_seen is 2026-09-18).
Atlas STATUS: seat PARKED for the index loop since 2026-09-19; promotion work 09-24 and one pass
09-25/26 on operator instruction; "index coverage lag 4.9 days". Archaeon ENGINE_LANDSCAPE notes Atlas
does NOT index z80atlas/census/envgate/envgate2 (harvest/archaeon_campaigns.py:59).
Classification: RECENTLY USED, operator-driven (not a running loop).

Receipts/MANIFESTs: file-based in git; newest SFE-related receipt dirs are
SerendipityFoundryEngine deploy/RELEASE_9_0_1_2026-09-17, roles/Vivarium/receipts/window_C4-20260917-W1,
and roles/Vivarium/receipts/INCIDENT_2026-09-24_M2_HOST_EXHAUSTION.md (per #563, main b3b26bf21).
viv.provenance_envelope and viv.intervention_receipt are EMPTY (0 rows) -- implemented tables never used.

---------------------------------------------------------------------------------------------------

## 9. Full table inventory queried (2026-09-27 ~15:15 UTC; rows | max timestamps)

agora: agent_heartbeats 36 (2026-09-27 11:13) | agent_sessions 0 | clio_claim_extractions 1082 (05-19) |
clio_papers 596 (05-30) | clio_quality_snapshots 238 (05-30) | decisions 3 (04-15) | gpu_reservations 4
(05-24) | intelligence_outputs 18188 (09-27 11:13) | machine_probes 132961 (09-27 11:15) | messages 196
(04-29) | open_questions 1 (04-15) | research_queue 425 (05-30) | temp_secrets 0.
archaeon: cadence_gate 10 (09-06) | cadence_log 1617 (09-17 19:22) | experiment_queue 1 (09-05) |
substrate_census 1310 (09-17 20:23).
comms: agent_instances 141 | agents 49 | messages 744 (09-27 11:18) | receipt_instances 2088 |
receipts 2000 | task_queue 111 (09-26 10:14).
viv: as s.3.
ew: agents 18 | campaign_observations 32938 (09-18) | candidate_bumps 1 | claims 147 (09-17) |
constraint_events 60 (09-17) | constraints 40 | coordinates 232 | derived_artifacts 82 (09-18) |
dim_terms 52 | evidence 133 (09-17) | evidence_terms 282 | experiments 79 (09-03) | fossil_edges 31 |
fossil_encounters 12935 (09-17) | fossil_players 6013 (09-17) | fossil_worlds 1000 (09-14) |
hypotheses 21 | ingestion_checkpoints 442 (09-18) | ingestion_conflicts 8 (09-18) | interpretations 2 |
ledger_fork_events 18 | ledger_observations 807 | mechanism_registry 26 | memory_artifacts 1 |
memory_influences 3 | object_namespace 43 | ontology_versions 7 | producer_events 287 (09-18) |
projection_rows 2877 (09-18) | projections 3 | publication_outbox 2147 (09-17) | read_log 4981
(09-23 07:32) | ref_availability_events 2147 | relations 54 (09-15) | schema_migrations 2 (09-17) |
sealed_records 40 | session_splice_events 32 | snapshots 1 | source_packets 90 (09-17) |
term_mappings 308 | typed_refs 2134 | vocab 79 | world_session_bindings 773 | write_log 6077 (09-18 14:30).
atlas: attempt 1742 | blind_spot 7 | campaign 53 | combination 190 | conclusion 483 | defect 221 |
ecosystem 365 | ecosystem_reference 870 | edge 5494 | engine 15 | engine_instance 136 | entity_commit 117 |
experiment 2053 | experiment_score 92 | fact 333044 | fact_evidence 333044 | field_conflict 0 |
git_commit 5848 | harvest_run 119 (09-26) | host 4 | idea 54 | identity_collision 30 | policy_version 2 |
portfolio_update 10 | primitive 20 | primitive_use 4249 | proposition 10 | proposition_evidence 7 |
schema_migrations 12 | seat_instance 83 | segment 3582 | signal 192 | source 313015 | source_link 13382 |
vocab 137.
(Timestamps shown in -04:00 local of the DB session unless marked Z.)

---------------------------------------------------------------------------------------------------

## 10. What would settle the UNKNOWNs (host evidence needed, M2 = SPECTREX5)

1. `netstat -ano | findstr :8811` and `:8377`; `tasklist` for the pids; SFEngineM2Watchdog and
   MnemosyneEvidenceWikiWatchdogM2 state (`schtasks /Query /V /TN ...`) and their state/park files.
2. mtime and last-row time of C:\Prometheus-data\sfe\engine.db (eng_906356f7) -- the only place SFE
   domain activity after 2026-09-18 could hide (no DB trace would exist if a client wrote directly
   to 8811 without Vivarium/PEW).
3. D:\PrometheusBackups\pew newest dump date (PEWBackupDailyM2) and newest restore receipt.
4. D:\Prometheus-data\vivarium\var\deadman-vivarium@m2.park.json presence.
Indirect evidence already argues strongly for DOWN since 2026-09-25 with no recovery reported
(no SFE/PEW/Vivarium posts after 2026-09-25 11:40 by owners; viv/ew untouched since 09-18).
