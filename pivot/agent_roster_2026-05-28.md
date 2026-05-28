# Agent Roster — 2026-05-28

*Auto-generated 2026-05-28T00:33:27.796795+00:00 by `scripts/agent_roster.py` from `EXPECTED_AGENTS` + `agora.agent_heartbeats` + `agora.intelligence_outputs` (last 24h). Run `python scripts/agent_roster.py` to regenerate.*

## Summary

- **45 total agents** (28 active · 14 shelved · 0 slowed · 1 deprecated)
- **6 with fresh PG heartbeat** (<10 min)
- **By kind:** 26 tool, 5 daemon, 5 operator, 5 healthcheck, 4 pipeline-stage
- **⚠ 2 agents in PG but not in EXPECTED_AGENTS** (add them to portfolio_monitor.py to get full taxonomy): Clio-test, HealthCheck-harry1

## Agents grouped by persona

### Aporia — void detection + Deep Research dispatch + tool supervision

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Atalanta | M1 | tool | active | 22m | 96 ev | E-track primitive hunter (reads Apollo organisms) |
| Clio | M1 | tool | active | 58m | — | paper scanner (arxiv/openalex/semantic-scholar) |
| Hypatia | M1 | tool | active | 52m | 24 ev | D-track curator (proof decomposition with R1-R5 ladder) |
| Polyhymnia | M1 | tool | active | 19m | 83 ev | Aporia-supervised tool (recent addition) |
| Pythia | M1 | tool | active | 57s | 12 ev | deep research report producer (~20 tokens/day) |
| Clio-test | M1 | tool | unknown | 9.4d | — |  |

### Charon — falsification swarm orchestrator (ferryman)

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Acheron | M2 | tool | active | 12m | 43 ev | HARD-5 coordinate-collision detector — Iris-complement; flag… |
| Charon_Loop | M2 | tool | active | 3m | — | rotation orchestrator (Stygian/Lethe/Acheron/Moros/Hecate/Ne… |
| Erebos | M2 | tool | active | 24m | 43 ev | composer/forger — plugin host for 25 hypothesis-generator ar… |
| Hecate | M2 | tool | active | 3m | 44 ev | continuous gradient archaeology — recomputes MI(kill_pattern… |
| Lethe | M2 | tool | active | 16m | 43 ev | anti-anchor miner — cold LLM probes against recently-settled… |
| Moros | M2 | tool | active | 7m | 44 ev | cross-pollination automator — multi-frontier-model adversari… |
| Nephele | M2 | tool | active | 32m | 43 ev | Clio-fallback substrate gatherer — slow-roll arxiv RSS rotat… |
| Pollux | M2 | tool | active | 28m | 43 ev | numerical-coincidence scanner — Spearman correlation before/… |
| Stygian | M2 | tool | active | 20m | 43 ev | v10-battery attack worker — picks Atlas number-theoretic pro… |

### Ergon — Learner-corpus consumer + ingest pipeline supervisor

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Penelope | M2 | tool | active | 1.0d | — | substrate ingest loop — Learner-corpus consumer |
| Pheme | M1 | tool | active | 22m | 96 ev | demand voicer — publishes per-pattern Learner-deficit profil… |
| Talos | M1 | tool | active | 39m | 24 ev | Ergon-supervised tool (recent addition) |

### Techne — substrate / Σ-kernel toolsmith

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Theseus | M1 | tool | active | 1.8d | — | substrate generation engine (catalog cross-product, mutation… |

### Harmonia — scientist swarm orchestrator (Phylax/Sophia/Iris/Argos/Telos) *(lifecycle: shelved)*

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Argos | M2 | tool | shelved | 3.7d | — | lens-fingerprint accretion |
| Harmonia_Loop | M2 | tool | shelved | 3.6d | — | rotation orchestrator for Harmonia swarm |
| Iris | M2 | tool | shelved | 3.7d | — | prose-to-symbol compressor |
| Phylax | M2 | tool | shelved | 3.6d | — | pre-promotion gate + retraction-adjacency sentinel |
| Sophia | M2 | tool | shelved | 3.6d | — | coordinate-system scout (closed-loop axis-space invention) |
| Telos | M2 | tool | shelved | 3.7d | — | stalled-specimen reviver / negative-space patroller |

### (Unsupervised — no persona)

| Agent | Machine | Kind | Lifecycle | PG age | Activity (24h) | Role |
|---|---|---|---|---|---|---|
| Aletheia | ? | pipeline-stage | active | — | — | knowledge graph harvester |
| Calliope | M4 | tool | active (on-demand) | 8.8d | — | daily NotebookLM narrative synthesizer (invoke-on-demand) |
| Eos | ? | pipeline-stage | active | — | — | external scanner |
| HealthCheck-M4 | M4 | healthcheck | active | 36m | — | M4 CPU/mem/disk snapshot (hourly) |
| Hephaestus | M3 | daemon | active | 40s | — | forge — substrate generator with falsification battery |
| Pronoia | M4 | daemon | active | 33s | 50 ev | reporting orchestrator (intelligence_loop) |
| Apollo | M2 | daemon | shelved | 3.6d | — | evolutionary search engine (genetic; one of the few non-LLM … |
| Coeus | ? | pipeline-stage | shelved | — | — | causal analysis |
| HealthCheck-M1 | M1 | healthcheck | shelved | — | — | M1 CPU/mem/disk snapshot (hourly) |
| HealthCheck-M2 | M2 | healthcheck | shelved | — | — | M2 CPU/mem/disk snapshot (hourly) |
| HealthCheck-M3 | M3 | healthcheck | shelved | — | — | M3 CPU/mem/disk snapshot (hourly) |
| HealthCheck-harry1 | harry1 | healthcheck | unknown | 3.7d | — | per-machine resource snapshot (harry1) |
| Hermes | ? | pipeline-stage | deprecated | — | — | alerting |
| Nemesis | M3 | daemon | shelved | — | — | adversarial pre-promotion tester |
| Nous | M4 | daemon | shelved | — | — | combinatorial substrate seeder for Hephaestus |

## Full census table

| Agent | Machine | Kind | Operator | Lifecycle | PG status | PG age | log_work 24h | Declared? |
|---|---|---|---|---|---|---|---|---|
| Hephaestus | M3 | daemon | — | active | online | 40s | — | ✓ |
| Pronoia | M4 | daemon | — | active | online | 33s | 50 | ✓ |
| HealthCheck-M4 | M4 | healthcheck | — | active | online | 36m | — | ✓ |
| Aporia | M1 | operator | — | active | online | 9.4d | — | ✓ |
| Charon | M2 | operator | — | active | — | — | — | ✓ |
| Ergon | M1 | operator | — | active | online | 1.3d | — | ✓ |
| Techne | M1 | operator | — | active | — | — | — | ✓ |
| Aletheia | ? | pipeline-stage | — | active | — | — | — | ✓ |
| Eos | ? | pipeline-stage | — | active | — | — | — | ✓ |
| Acheron | M2 | tool | Charon | active | online | 12m | 43 | ✓ |
| Atalanta | M1 | tool | Aporia | active | online | 22m | 96 | ✓ |
| Calliope | M4 | tool | — | active (on-demand) | online | 8.8d | — | ✓ |
| Charon_Loop | M2 | tool | Charon | active | online | 3m | — | ✓ |
| Clio | M1 | tool | Aporia | active | online | 58m | — | ✓ |
| Erebos | M2 | tool | Charon | active | online | 24m | 43 | ✓ |
| Hecate | M2 | tool | Charon | active | online | 3m | 44 | ✓ |
| Hypatia | M1 | tool | Aporia | active | online | 52m | 24 | ✓ |
| Lethe | M2 | tool | Charon | active | online | 16m | 43 | ✓ |
| Moros | M2 | tool | Charon | active | online | 7m | 44 | ✓ |
| Nephele | M2 | tool | Charon | active | online | 32m | 43 | ✓ |
| Penelope | M2 | tool | Ergon | active | online | 1.0d | — | ✓ |
| Pheme | M1 | tool | Ergon | active | online | 22m | 96 | ✓ |
| Pollux | M2 | tool | Charon | active | online | 28m | 43 | ✓ |
| Polyhymnia | M1 | tool | Aporia | active | online | 19m | 83 | ✓ |
| Pythia | M1 | tool | Aporia | active | online | 57s | 12 | ✓ |
| Stygian | M2 | tool | Charon | active | online | 20m | 43 | ✓ |
| Talos | M1 | tool | Ergon | active | online | 39m | 24 | ✓ |
| Theseus | M1 | tool | Techne | active | online | 1.8d | — | ✓ |
| Apollo | M2 | daemon | — | shelved | online | 3.6d | — | ✓ |
| Nemesis | M3 | daemon | — | shelved | — | — | — | ✓ |
| Nous | M4 | daemon | — | shelved | — | — | — | ✓ |
| HealthCheck-M1 | M1 | healthcheck | — | shelved | — | — | — | ✓ |
| HealthCheck-M2 | M2 | healthcheck | — | shelved | — | — | — | ✓ |
| HealthCheck-M3 | M3 | healthcheck | — | shelved | — | — | — | ✓ |
| HealthCheck-harry1 | harry1 | healthcheck | — | unknown | online | 3.7d | — | — |
| Harmonia | M2 | operator | — | shelved | — | — | — | ✓ |
| Coeus | ? | pipeline-stage | — | shelved | — | — | — | ✓ |
| Hermes | ? | pipeline-stage | — | deprecated | — | — | — | ✓ |
| Argos | M2 | tool | Harmonia | shelved | online | 3.7d | — | ✓ |
| Clio-test | M1 | tool | Aporia | unknown | online | 9.4d | — | — |
| Harmonia_Loop | M2 | tool | Harmonia | shelved | online | 3.6d | — | ✓ |
| Iris | M2 | tool | Harmonia | shelved | online | 3.7d | — | ✓ |
| Phylax | M2 | tool | Harmonia | shelved | online | 3.6d | — | ✓ |
| Sophia | M2 | tool | Harmonia | shelved | online | 3.6d | — | ✓ |
| Telos | M2 | tool | Harmonia | shelved | online | 3.7d | — | ✓ |

## Drift report

**Lifecycle=active but heartbeat stale (>1h):**
- `Penelope` (1.0d) — daemon/tool likely crashed; investigate or mark `lifecycle='shelved'`.
- `Theseus` (1.8d) — daemon/tool likely crashed; investigate or mark `lifecycle='shelved'`.

**In PG but not declared in EXPECTED_AGENTS:**
- `Clio-test` (M1, tool, operator=Aporia) — add to EXPECTED_AGENTS to get full dashboard treatment.
- `HealthCheck-harry1` (harry1, healthcheck, operator=—) — add to EXPECTED_AGENTS to get full dashboard treatment.

---

**Sources**
- Code: [`scripts/portfolio_monitor.py`](../scripts/portfolio_monitor.py) → `EXPECTED_AGENTS`
- DB: `agora.agent_heartbeats` (live), `agora.intelligence_outputs` (log_work events)
- Regenerate: `python scripts/agent_roster.py`
