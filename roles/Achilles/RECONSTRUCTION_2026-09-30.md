# Achilles first run -- forensic reconstruction of the reporting stack

Currency: 2026-10-01T01:40Z. Read at origin/main 9e4d75e62 from ELSA (not the
M4 loop host; M4 facts below come from committed artifacts, seat files and
the M1 database, not from inspecting M4). Charter: roles/Achilles/prompts/
2026-09-30_charter/. Method: three read-only survey passes (reporting
lineage; schedulers / hosts / comms data model; roster / state / task /
experiment sources), then five registry passes (four seat groups, one engine
catalogue) written to roles/Achilles/census/registry/ with path:line sources.

## 1. What still runs

| piece | state | evidence |
|---|---|---|
| scripts/intelligence_loop.py (Pronoia Era 2) on M4 | RUNNING every 4 h | "auto: portfolio update" commits through 2026-10-01; launched by task PrometheusIntelligenceWatchdog (scripts/register_intelligence_watchdog.ps1) |
| scripts/portfolio_monitor.py -> docs/state.json | RUNNING, WRONG MODEL | live state.json: 48 agents, 33 DEAD / 15 MISSING, Redis unreachable, data_source postgres_fallback; hard-coded May EXPECTED_AGENTS roster; its "observability" block has no tracked source (M4 runs uncommitted code; MONITORS row MetisStateProducer UNLOCATED) |
| scripts/metis_portfolio.py -> docs/portfolio_brief.md | RUNNING, OWNERLESS | METIS-01 ruled NO; reads infra_status, which the producer stopped emitting 2026-09-01 |
| scripts/send_brief_email.py (Gmail SMTP_SSL) | RUNNING | agora.intelligence_outputs email_dispatched success, last 2026-10-01T00:15Z, no failures in 72 h; credentials HERMES_* from agents/eos/.env on M4 (gitignored); claimed by Hermes |
| .github/workflows/pages.yml | RUNNING | deploys docs/ to https://jcraig949jfi.github.io/Prometheus/ on push to main |
| comms (Postgres schema comms on M1) | RUNNING | the successor of Agora; agents, agent_instances, messages, receipts, task_queue |
| ops/fleet/CENSUS.json + fleet_status.py (Aporia) | HAND-MAINTAINED | prometheus.fleet_census.v1, 16 live seats only, no schedule |

## 2. What no longer runs (and why, where determinable)

| piece | ended | why |
|---|---|---|
| Agora Redis streams (agora/, roles/Agora) | 2026-04-29 / Redis retired 2026-06-24 | replaced by comms 2026-09-11; agora/README still points at dead 192.168.1.176; seat BLOCKED on AGORA-01 (recommends RETIRE) |
| agora.agent_heartbeats as liveness | stale | write-once "online" labels (e.g. "Theseus online" from the May engine, 2026-06-05); presence only |
| pronoia.py (Era 1 chain) | deleted 3b3c74bc0, 2026-04-23 | repo cleanup for external visibility |
| agents/hermes mailer | deprecated 2026-05-17 | superseded by scripts/send_brief_email.py |
| agents/aletheia knowledge graph; Aletheia_M4 reporting session | March / May 2026 | "Aletheia_M4 owns the fleet status schema" (stations/M2_STATUS.json) but no such schema was ever committed |
| agents/alethelia (truthful reporter v0.1) | DORMANT, hand-run 08-20, 08-27, 09-11 | no host (ALET-04 open) |
| stations/*_STATUS, pivot/agent_roster_*, calliope_daily, weekly_recap output | August / May | not invoked or not committed |
| PrometheusMachineProbeM1/M2 | DEAD | error 0x80070002 every run (MONITORS.md) |

## 3. Where the source of truth lives now

Seat state: roles/<Seat>/WORK_STATE.json (prometheus.work_state.v1, MWO-0001
s9; also on seat branches), STATUS.md, journal/. Fleet orders:
ops/work_orders/CURRENT.md (MWO-0004), ops/fleet/CWO_*.md (CWO-2026-09-30C
governing), ops/fleet/QUEUE.json, CENSUS.json, UNOWNED.json. Messages:
comms on M1. Experiments: commit vocabulary, roles/<Seat>/prereg, receipts,
REVIEW_PACKET*, ops/campaigns/*/E-*/RESULT.md; ew.experiments stops at
2026-09-03. Loops: roles/base-role/MONITORS.md.

## 4. Reuse decisions (smallest coherent extension)

- SCHEMA: extend Aporia's prometheus.fleet_census.v1 rather than invent one.
  v2 keeps every v1 column per seat and adds provenance fields. CENSUS.json
  stays Aporia's (lane discipline); the census reads it as evidence.
- DATA: comms.api.connect() (read-only session forced), comms tables,
  ew.experiments, agora tables (weak/legacy), WORK_STATE across branches
  (the MWO-0001 rule fleet_status.py does not yet implement), atlas
  host and engine conventions, MONITORS.md parsed exactly as the base-role
  self-test parses it.
- PUBLICATION: the existing docs/ -> pages.yml path; new files under
  docs/fleet/ (one .gitignore exception). The M4 dashboard (docs/index.html,
  state.json) is left untouched; its 0/48 agents-alive view is reported as a
  data-quality defect, not rewritten.
- EMAIL: the existing mailer, not a new transport. scripts/send_brief_email.py
  gains build_fleet_census(): the census section (counts, changes, attention,
  the agent table) goes into the body of every brief email, loud STALE /
  UNAVAILABLE text when the block is old or missing, and the census
  timestamp in the mailer's own email_dispatched receipt so the next census
  can verify delivery. The M4 loop picks the change up through its
  pull --rebase --autostash on every rejected push.
- SCHEDULER: a user-level Windows Scheduled Task on ELSA (the registration
  pattern of roles/Aphrodite/monitors/news), not Fabric (no scheduler,
  Linux-only workers, Windows CLI defect #1135) and not a Claude /loop
  (dies with the session). Registry row in MONITORS.md with bound 4 and
  accountable seat Achilles (rule 10).

## 5. Data-quality problems found (reported, not fixed in other lanes)

1. docs/state.json reports 0 of 48 agents alive from a retired roster; the
   brief email's TL;DR repeats it ("agents alive 0/48"). Owner: the
   ownerless producer (METIS-01R) / Pronoia.
2. M4 runs uncommitted portfolio_monitor code (the observability block has
   no tracked source).
3. atlas/registry.json engine paths are stale for Cosmos, Ananke, Ensorain
   (roles/<Seat> instead of prometheus/cosmos, prometheus/ananke, ensorain/)
   and calls primordial branch-only and crius LIVE.
4. Conflicting seat states: Hecate (STATUS ACTIVE vs WORK_STATE BLOCKED),
   Odysseus (STATUS ACTIVE vs WORK_STATE BLOCKED), Theseus and Techne (own
   READY vs Aporia's census WORKING/ACTIVE), Atlas (READY vs loop PARKED),
   Arachne, Talos, Hermes (deprecated 2026-05-17 vs re-adopted ACTIVE).
5. Conflicting hosts: Aether (M2 vs BUCKKEEP), Daedalus, Hephaestus,
   Mnemosyne, Ludus (docs vs newest status).
6. Archaeon's WORK_STATE exists only on a branch; fleet_status.py reads
   main only and misses it.
7. Chiron exists only on origin/chiron/base-role-adopt-2026-09-21.
8. INHERITANCE.md lists Icarus twice; Theophrastus has no entry-file row.
9. Engine ownership drift (recorded in engines.json notes): cartography
   (Harmonia commits, Charon claim), integration, engine/necropolis
   (Rhadamanthus commits, Mnemosyne named), collider, attacks.
10. Engines with recent commits and no recorded owner: docs/ (the M4 loop),
    ops/fleet, ops/work_orders, alien_circuitry, incubation*, ama_game.
11. 7% of non-merge commits (779 of 10607) carry no seat attribution.
12. Six Gen-1 role-title directories (CrossDomainCartographer,
    EvolutionaryArchitectAndReasoningSpeciesEngineer, MPADatabaseArchitect,
    PipelineOrchestrator, ScienceAdvisor, StructuralMathematician) are
    historical role documents, not seats; the census lists them as such.

## 6. Retired or bypassed by Achilles

Nothing was deleted or disabled. Bypassed as census sources: the
EXPECTED_AGENTS roster and agora.agent_heartbeats as liveness (kept as weak
presence only), stations/*_STATUS, pivot/agent_roster_*.
