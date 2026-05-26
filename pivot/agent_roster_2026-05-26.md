# Agent Roster — 2026-05-26

*Auto-generated 2026-05-26T09:51:23.587608+00:00 by `scripts/agent_roster.py` from `EXPECTED_AGENTS` + `agora.agent_heartbeats` + `agora.intelligence_outputs` (last 24h). Run `python scripts/agent_roster.py` to regenerate.*

## Summary

- **45 total agents** (28 active · 14 shelved · 0 slowed · 1 deprecated)
- **7 with fresh PG heartbeat** (<10 min)
- **By kind:** 26 tool, 5 daemon, 5 healthcheck, 5 operator, 4 pipeline-stage
- **⚠ 2 agents in PG but not in EXPECTED_AGENTS** (add them to portfolio_monitor.py to get full taxonomy): Clio-test, HealthCheck-harry1

## Agents grouped by persona

### Aporia — void detection + Deep Research dispatch + tool supervision

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Atalanta | M1 | tool | active | 11m | 96 ev | E-track primitive hunter (reads Apollo organisms) |
| Clio | M1 | tool | active | 38m | — | paper scanner (arxiv/openalex/semantic-scholar) |
| Hypatia | M1 | tool | active | 11m | 24 ev | D-track curator (proof decomposition with R1-R5 ladder) |
| Polyhymnia | M1 | tool | active | 14m | 61 ev | Aporia-supervised tool (recent addition) |
| Pythia | M1 | tool | active | 10s | 9 ev | deep research report producer (~20 tokens/day) |
| Clio-test | M1 | tool | unknown | 7.8d | — |  |

### Charon — falsification swarm orchestrator (ferryman)

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Acheron | M2 | tool | active | 10m | 45 ev | Charon swarm member — boundary-condition falsifier |
| Charon_Loop | M2 | tool | active | 1m | — | rotation orchestrator for Charon swarm |
| Erebos | M2 | tool | active | 20m | 9 ev | Charon swarm member (recent addition) |
| Hecate | M2 | tool | active | 1m | 46 ev | Charon swarm member — stratified sampling + Techne ticket re… |
| Lethe | M2 | tool | active | 14m | 45 ev | Charon swarm member — conjecture-loop falsifier |
| Moros | M2 | tool | active | 5m | 46 ev | Charon swarm member — critic + sharper-battery designer |
| Nephele | M2 | tool | active | 30m | 45 ev | Charon swarm member (recent addition) |
| Pollux | M2 | tool | active | 26m | 45 ev | Charon swarm member (recent addition) |
| Stygian | M2 | tool | active | 18m | 45 ev | Charon swarm member — kill-tier falsifier |

### Ergon — Learner-corpus consumer + ingest pipeline supervisor

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Penelope | M2 | tool | active | 8m | 30 ev | substrate ingest loop — Learner-corpus consumer |
| Pheme | M1 | tool | active | 11m | 96 ev | demand voicer — publishes per-pattern Learner-deficit profil… |
| Talos | M1 | tool | active | 57m | 24 ev | Ergon-supervised tool (recent addition) |

### Techne — substrate / Σ-kernel toolsmith

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Theseus | M1 | tool | active | 4.3h | 32 ev | substrate generation engine (catalog cross-product, mutation… |

### Harmonia — scientist swarm orchestrator (Phylax/Sophia/Iris/Argos/Telos) *(lifecycle: shelved)*

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Argos | M2 | tool | shelved | 2.0d | — | lens-fingerprint accretion |
| Harmonia_Loop | M2 | tool | shelved | 2.0d | — | rotation orchestrator for Harmonia swarm |
| Iris | M2 | tool | shelved | 2.0d | — | prose-to-symbol compressor |
| Phylax | M2 | tool | shelved | 2.0d | — | pre-promotion gate + retraction-adjacency sentinel |
| Sophia | M2 | tool | shelved | 2.0d | — | coordinate-system scout (closed-loop axis-space invention) |
| Telos | M2 | tool | shelved | 2.0d | — | stalled-specimen reviver / negative-space patroller |

### (Unsupervised — no persona)

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Aletheia | ? | pipeline-stage | active | — | — | knowledge graph harvester |
| Calliope | M4 | tool | active (on-demand) | 7.2d | — | daily NotebookLM narrative synthesizer (invoke-on-demand) |
| Eos | ? | pipeline-stage | active | — | — | external scanner |
| HealthCheck-M4 | M4 | healthcheck | active | 54m | — | M4 CPU/mem/disk snapshot (hourly) |
| Hephaestus | M3 | daemon | active | 31s | 20 ev | forge — substrate generator with falsification battery |
| Pronoia | M4 | daemon | active | 2s | 55 ev | reporting orchestrator (intelligence_loop) |
| Apollo | M2 | daemon | shelved | 2.0d | — | evolutionary search engine (genetic; one of the few non-LLM … |
| Coeus | ? | pipeline-stage | shelved | — | — | causal analysis |
| HealthCheck-M1 | M1 | healthcheck | shelved | — | — | M1 CPU/mem/disk snapshot (hourly) |
| HealthCheck-M2 | M2 | healthcheck | shelved | — | — | M2 CPU/mem/disk snapshot (hourly) |
| HealthCheck-M3 | M3 | healthcheck | shelved | — | — | M3 CPU/mem/disk snapshot (hourly) |
| HealthCheck-harry1 | harry1 | healthcheck | unknown | 2.1d | — | per-machine resource snapshot (harry1) |
| Hermes | ? | pipeline-stage | deprecated | — | — | alerting |
| Nemesis | M3 | daemon | shelved | — | — | adversarial pre-promotion tester |
| Nous | M4 | daemon | shelved | — | — | combinatorial substrate seeder for Hephaestus |

## Full census table

| Agent | Machine | Kind | Operator | Lifecycle | PG status | PG age | log_work 24h | Declared? |
|---|---|---|---|---|---|---|---|---|
| Hephaestus | M3 | daemon | — | active | online | 31s | 20 | ✓ |
| Pronoia | M4 | daemon | — | active | online | 2s | 55 | ✓ |
| HealthCheck-M4 | M4 | healthcheck | — | active | online | 54m | — | ✓ |
| Aporia | M1 | operator | — | active | online | 7.8d | — | ✓ |
| Charon | M2 | operator | — | active | — | — | — | ✓ |
| Ergon | M1 | operator | — | active | online | 3.2h | 1 | ✓ |
| Techne | M1 | operator | — | active | — | — | — | ✓ |
| Aletheia | ? | pipeline-stage | — | active | — | — | — | ✓ |
| Eos | ? | pipeline-stage | — | active | — | — | — | ✓ |
| Acheron | M2 | tool | Charon | active | online | 10m | 45 | ✓ |
| Atalanta | M1 | tool | Aporia | active | online | 11m | 96 | ✓ |
| Calliope | M4 | tool | — | active (on-demand) | online | 7.2d | — | ✓ |
| Charon_Loop | M2 | tool | Charon | active | online | 1m | — | ✓ |
| Clio | M1 | tool | Aporia | active | online | 38m | — | ✓ |
| Erebos | M2 | tool | Charon | active | online | 20m | 9 | ✓ |
| Hecate | M2 | tool | Charon | active | online | 1m | 46 | ✓ |
| Hypatia | M1 | tool | Aporia | active | online | 11m | 24 | ✓ |
| Lethe | M2 | tool | Charon | active | online | 14m | 45 | ✓ |
| Moros | M2 | tool | Charon | active | online | 5m | 46 | ✓ |
| Nephele | M2 | tool | Charon | active | online | 30m | 45 | ✓ |
| Penelope | M2 | tool | Ergon | active | online | 8m | 30 | ✓ |
| Pheme | M1 | tool | Ergon | active | online | 11m | 96 | ✓ |
| Pollux | M2 | tool | Charon | active | online | 26m | 45 | ✓ |
| Polyhymnia | M1 | tool | Aporia | active | online | 14m | 61 | ✓ |
| Pythia | M1 | tool | Aporia | active | online | 10s | 9 | ✓ |
| Stygian | M2 | tool | Charon | active | online | 18m | 45 | ✓ |
| Talos | M1 | tool | Ergon | active | online | 57m | 24 | ✓ |
| Theseus | M1 | tool | Techne | active | online | 4.3h | 32 | ✓ |
| Apollo | M2 | daemon | — | shelved | online | 2.0d | — | ✓ |
| Nemesis | M3 | daemon | — | shelved | — | — | — | ✓ |
| Nous | M4 | daemon | — | shelved | — | — | — | ✓ |
| HealthCheck-M1 | M1 | healthcheck | — | shelved | — | — | — | ✓ |
| HealthCheck-M2 | M2 | healthcheck | — | shelved | — | — | — | ✓ |
| HealthCheck-M3 | M3 | healthcheck | — | shelved | — | — | — | ✓ |
| HealthCheck-harry1 | harry1 | healthcheck | — | unknown | online | 2.1d | — | — |
| Harmonia | M2 | operator | — | shelved | — | — | — | ✓ |
| Coeus | ? | pipeline-stage | — | shelved | — | — | — | ✓ |
| Hermes | ? | pipeline-stage | — | deprecated | — | — | — | ✓ |
| Argos | M2 | tool | Harmonia | shelved | online | 2.0d | — | ✓ |
| Clio-test | M1 | tool | Aporia | unknown | online | 7.8d | — | — |
| Harmonia_Loop | M2 | tool | Harmonia | shelved | online | 2.0d | — | ✓ |
| Iris | M2 | tool | Harmonia | shelved | online | 2.0d | — | ✓ |
| Phylax | M2 | tool | Harmonia | shelved | online | 2.0d | — | ✓ |
| Sophia | M2 | tool | Harmonia | shelved | online | 2.0d | — | ✓ |
| Telos | M2 | tool | Harmonia | shelved | online | 2.0d | — | ✓ |

## Drift report

**Lifecycle=active but heartbeat stale (>1h):**
- `Theseus` (4.3h) — daemon/tool likely crashed; investigate or mark `lifecycle='shelved'`.

**In PG but not declared in EXPECTED_AGENTS:**
- `Clio-test` (M1, tool, operator=Aporia) — add to EXPECTED_AGENTS to get full dashboard treatment.
- `HealthCheck-harry1` (harry1, healthcheck, operator=—) — add to EXPECTED_AGENTS to get full dashboard treatment.

---

**Sources**
- Code: [`scripts/portfolio_monitor.py`](../scripts/portfolio_monitor.py) → `EXPECTED_AGENTS`
- DB: `agora.agent_heartbeats` (live), `agora.intelligence_outputs` (log_work events)
- Regenerate: `python scripts/agent_roster.py`
