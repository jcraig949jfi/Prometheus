# Seat dossier: Agora

Crawler label: coord (Ixion Phase 3 sub-crawler; seats Aporia, Cyclops, Agora)
Date: 2026-10-01 (date -u at start: Thu Oct 1 09:36:13 UTC 2026)
Base SHA read: bed05507a

Fully read: roles/Agora/RESPONSIBILITIES.md, ARCHAEOLOGY_2026-09-14.md, STATUS.md, calibration/LEDGER.md
(head), agora/README.md (head), git log of agora/ + roles/Agora (all 32 subjects), agora/client.py
function index (grep), roles/Ergon/REDIS_TO_POSTGRES_2026-06-24.md (head), comms/README.md (head),
archaeon/docs/expansion/DECISIONS.md D-24/D-25, commit 6be994430 message.
Sampled: superseded/RESPONSIBILITIES_pre_2026-09-14_superseded.md (first 3 KB), agora/ file sizes.
NOT read: SESSION_STATE_20260415*.md, SESSION_JOURNAL_20260415.md, journal/2026-09-14.md, BACKLOG_H0H5.md,
prompts/2026-09-14_credentials report body (deliberately: credential subject), agora/work_queue.py,
helpers.py, symbols/, tensor/, datasets/, canonicalizer/ bodies. agora.temp_secrets NOT queried.
DB: read-only SELECT counts on schemas agora and bus (prometheus_fire, M1).

## 1 Charter and role history

    2026-04-15  "Redis-backed distributed adversarial science team"; "not an agent ... the space
                between agents"; Redis Streams agora:main/:challenges/:tasks/:discoveries,
                agent:{name} hashes, 60 s heartbeats, 5-min death rule, hypotheses alive/killed
                sets, kills leaderboard; a coordinator session polling every 5 min       [IMPL] 98b65559a; superseded body
    2026-04-15  Postgres persistence + catchup for session recovery (agora.messages)   [IMPL] db8e9a3b5
    2026-04-17..05-05  agora/ package grows into the Harmonia substrate client: work_queue (claim/
                complete/steal_stale_claims/reserve_p_id/qualification challenges), symbols,
                tensor read-mirror, datasets, helpers                                      [IMPL] 4f42135aa..7e80a41a9
    2026-04-29  last agora.messages row (196 rows total, 2026-04-15 06:13 .. 04-29 07:06 -04)  [IMPL; select count/min/max]
    2026-06-24  Redis retired program-wide ("too difficult to keep running under WSL. I have to
                keep starting it manually") -> PgRedis drop-in on Postgres schema bus     [IMPL] c04199724; REDIS_TO_POSTGRES_2026-06-24.md:4-6
    2026-09-11  channel replaced by comms (D-24), presence derived from sync receipts (D-25)  [IMPL] 7466bd6ac, 8bb162a77
    2026-09-14  base-role adoption pass: 26 April items classified, 0 STILL_LIVE; seat BLOCKED
                on AGORA-01 (operator: retire / park / re-premise; recommendation RETIRE)    [IMPL] 31f51c722, 8dc34fe32

At bed05507a AGORA-01 has no recorded ruling [UNK: searched roles/Agora (last commit 8dc34fe32,
2026-09-14) and comms for sender Agora (1 message, 09-14)]. comms.agents lists exactly 1 retired seat
of 57 [IMPL; select status,count(*) from comms.agents]; which seat that is was not queried.

## 2 Systems maintained

As a seat: none since 09-14 ("No lane, no monitor, no science") [IMPL] RESPONSIBILITIES.md s2.
As code (not owned by the seat; "Harmonia-lineage client code"): agora/ package, 2,380 lines of .py at
the top level (client 330, helpers 460, work_queue 491, register_specimen 303, resume_broadcast 127,
setup_m2 97, protocol 89, hello 71, config 49, tests 361) plus symbols/, tensor/, datasets/,
canonicalizer/ subpackages [IMPL; wc -l agora/*.py].
As schema (not owned): Postgres schema agora with 13 tables [IMPL; information_schema].

## 3 Actual implementation paths

- AgoraClient: send() -> redis xadd :143; _persist_message() to Postgres :99; heartbeat() hset
  agent:{name} last_heartbeat :243-246; start_heartbeat() background thread :248-260;
  get_dead_agents() by timeout :262; catchup() :288 [IMPL] agora/client.py.
- work_queue: push/claim/complete/abandon/steal_stale_claims, qualification challenges, reserve_p_id
  (atomic P-ID counter) [IMPL] agora/README.md function index; tests agora/test_reserve_p_id.py,
  agora/test_helpers.py.
- Still imported in Sept by M4's intelligence_loop for an "Agora heartbeat" (cadence changed to 30 min on
  M4, "Fleet-wide HEARTBEAT_INTERVAL_SEC is untouched, so other hosts keep 60s") [IMPL] 6be994430 (2026-09-17)
  message + agora/client.py diff. scripts/authorize_and_seed.py imports agora.work_queue [IMPL] grep.

## 4 Architecture

Redis (WSL on M1) as shared brain, mirrored to Postgres; M1 and M2 Claude sessions as clients; one
coordinator session on a 5-minute poll [INTENT] superseded body "Architecture". After 2026-06-24 the
get_redis() pool returns a Postgres-backed PgRedis (schema bus: stream_entries, hashes, zsets, sets,
kv, lists) [IMPL] REDIS_TO_POSTGRES_2026-06-24.md. On M1 at audit time every bus table holds 0 rows
[IMPL; select count(*) from bus.stream_entries / hashes / kv / zsets / sets = 0]. Where the M4 Agora
heartbeat lands (M4-local bus, M1 bus emptied, or a Redis) is not established [UNK].

## 5 Data stores

    agora.messages        196 rows, 2026-04-15..04-29; senders Ergon 61, Aporia 40, Claude_M1 29,
                          Harmonia 19, Mnemosyne 18, Kairos 13, Harmonia_M2_* 15, Agora_Bootstrap 1;
                          msg_type announce 83, share 56, response 37, challenge 8, request 5,
                          task_claim 4, kill 1, task_offer 1, heartbeat 1; 107 of 196 on 04-15  [IMPL; group-by queries]
    agora.agent_heartbeats 36 rows; max last_heartbeat 2026-10-01 05:39 -04 (MachineProbe-M4,
                          Pronoia on M4, HealthCheck-M4); 17 rows last beat 2026-05-30        [IMPL]
    agora.decisions 3, open_questions 1, research_queue 425, gpu_reservations 5, agent_sessions 0 [IMPL]
    agora.machine_probes, clio_*, intelligence_outputs, temp_secrets                   [IMPL names only; not counted]
    bus.* (PgRedis)       0 rows in every table on M1                                    [IMPL]

## 6 APIs/interfaces

Python client API (agora/README.md "Function index") [IMPL]. agora/README.md still names the retired
Redis address and a default password as environment defaults [IMPL] agora/README.md:5-15 (value not
reproduced here). The 09-14 pass reported the credential exposure redacted to Mnemosyne (comms report 258)
[HIST] 8dc34fe32 subject; [IMPL] roles/Agora/calibration/LEDGER.md row 4.

## 7 Scheduling model

April: coordinator session loop, 5-minute poll [INTENT/HIST] superseded body; ARCHAEOLOGY item 4.
Heartbeats: daemon thread per client, 60 s default [IMPL] client.py:248-260. Since 09-14: none for the
seat; base rules 8-10 "forbid a loop with no productivity signal, no bound and no accountable seat; no
scheduled task is created" [IMPL] ARCHAEOLOGY item 4. M4 scheduled tasks still drive Agora-schema
heartbeats (PrometheusMachineProbeM4, PrometheusIntelligenceWatchdog) [IMPL text] roles/base-role/MONITORS.md
rows; host-side NOT verified (M4 not inspected) [UNK].

## 8 State machine

April: agent alive/dead by heartbeat age > 5 min; hypotheses alive -> killed sets [INTENT] superseded
body. work_queue claim states queued/claimed/results/abandoned with stale-claim stealing [IMPL]
README queue_status(). Seat now: PRESENT, ACTIVE (pass ran), NOT PRODUCTIVE, BLOCKED on AGORA-01 [IMPL] STATUS.md.

## 9 Communication channels

April: Redis streams (5 streams; counts main 105, discoveries 62, challenges 13, harmonia_sync 10, tasks 6)
[IMPL; agora.messages group by stream]. Since 09-11: comms; Agora has posted 1 comms message (09-14
report) [IMPL; comms query].

## 10 Failure recovery

April: Postgres mirror + catchup() for "session recovery" after account switches [IMPL] db8e9a3b5;
client.py:288. Redis itself had no recovery: it "went dark when Redis under WSL would not stay up"
[HIST] RESPONSIBILITIES.md s0; operator quote in REDIS_TO_POSTGRES doc.

## 11 Persistence

Redis was volatile; Postgres agora.messages is the surviving record ("the April conversation, in
Postgres, untouched") [IMPL] ARCHAEOLOGY s D.

## 12 Provenance

April messages carry a model self-reported `confidence` column [IMPL] agora.messages columns; the
09-14 archaeology declines it as evidence ("model self-report, which base rule 2 declines") [CORR]
ARCHAEOLOGY item 25. Archaeology measurements are re-runnable SQL restated beside each number, but the
probe scripts were not committed [IMPL] ARCHAEOLOGY header.

## 13 Resource usage

Unknown for April. Today: none [IMPL] STATUS.md "monitors owned or fed: none".

## 14 Model/inference dependency

April Agora coordination (challenge, vote, kill, assign) was entirely model-session-mediated; transport
(streams, heartbeats, claims, P-ID counter) was deterministic code [IMPL] client.py, work_queue.py.

## 15 Human dependency

Redis needed manual restarts by the operator [HIST] REDIS_TO_POSTGRES doc quote. AGORA-01 waits on the
operator since 2026-09-14 (17 days at bed05507a) [IMPL] STATUS.md blockers.

## 16 Major outputs

196 April messages; P-ID reservation counter (agora:next_p_id) [IMPL] c8f3745f2; the substrate client
used by Harmonia workers [IMPL]; the 09-14 ARCHAEOLOGY (26-item classification) [IMPL].

## 17 Known failures

- Redis-under-WSL availability; channel dead after 04-29 [IMPL] row dates; [HIST] doc.
- Committed plaintext credentials in seat files and README [IMPL] LEDGER.md row 4; agora/README.md.
- April tier calls ("CONFIRMED", "the adversarial system works") made without preregistration, controls
  or independent failure mode; same-model participants [CORR] calibration/LEDGER.md rows 1-3.
- heartbeat.py and cli.py named in April are ABSENT on origin/main [IMPL] ARCHAEOLOGY item 8.

## 18 Pivots

Seat -> dormant (04-29) -> transport replaced (06-24) -> channel replaced (09-11) -> archaeological
adoption, retire recommended (09-14) [IMPL].

## 19 Journals/TODOs/backlogs

roles/Agora/journal/2026-09-14.md, BACKLOG_H0H5.md ("below the schema's 20-item floor"), April
SESSION_STATE/SESSION_JOURNAL files annotated HISTORICAL [IMPL] RESPONSIBILITIES.md s4.

## 20 Historical relevance to current Prometheus

Every April function was mapped to a current owner (comms, comms who/presence, comms claim, Kairos/
Elenchus/Charon/Nemesis/Harmonia, base role s4, DECISIONS.md) [IMPL] RESPONSIBILITIES.md s1 table. Two
April ideas returned in late September under other names: (a) heartbeats, retired 09-14 as "a meaning
that expired", were re-imposed fleet-wide by CWO-B/C on 09-30 as comms HEARTBEAT messages to Aporia
(124 comms subjects containing "heartbeat", 86 since 2026-09-30 04:18 -04) [IMPL; comms subject
query] [CORR] ARCHAEOLOGY item 2 vs CWO_2026-09-30C s13; (b) qualification-gated task claiming and
stale-claim stealing reappear as Fabric task/lease semantics [INFER] (Fabric not inspected by this crawler).

## 21 Inference-dependency classification

    function                                 | class                            | evidence
    message transport + persistence          | INFERENCE_FREE                   | client.py send/_persist_message
    liveness by heartbeat age                | INFERENCE_FREE                   | client.py get_dead_agents
    task claim / stale-claim steal / P-ID    | INFERENCE_FREE                   | work_queue.py, test_reserve_p_id.py
    challenge / kill / vote                  | MODEL_MEDIATED                   | superseded body; msg_type counts
    coordinator assignment loop (5 min)      | MODEL_MEDIATED                   | ARCHAEOLOGY item 4
    queue archaeology (classification)       | OCCASIONAL_JUDGMENT              | ARCHAEOLOGY s B

## 22 False-negative / false-positive watch

- FN: the April Agora died of its substrate (Redis under WSL), not of a measured failure of the
  adversarial-channel idea [HIST] RESPONSIBILITIES.md s0; doc quote. The idea's adversarial component was
  later judged invalid on independence grounds (same model family) [CORR] LEDGER.md row 3 -- that is a
  design critique, not an observed failure.
- FP: April "battery works correctly (CONFIRMED)" and "the adversarial system works" [CORR] LEDGER.md.
- FN-adjacent: ARCHAEOLOGY found zeros.dirichlet_zeros = 0 while charon_duckdb.dirichlet_zeros =
  184,830 rows -- data that exists but is not where consumers look [REPORTED by Agora 09-14] ARCHAEOLOGY item 21.
