# Agent Roster — 2026-05-21

*Generated 2026-05-21 from git history (last 30 days) + `agora.intelligence_outputs` (last 14 days) + `docs/state.json`. "Last produced" is the most recent of: a commit whose subject names the agent, OR a `log_work` event whose stage prefix matches the agent name. Empty `_tick_complete` events count as "producing" (the loop fired) but the data may indicate empty work — see Section 6.*

---

## 1. Summary by persona / owner

| Persona | Tools supervised | Status of persona | Active tools (substantive output in last 24h) |
|---|---|---|---|
| **Aporia** (M1) | Clio, Pythia, **Hypatia**, **Atalanta** | active (this session) | Pythia (live), Hypatia (just launched, D-track dispatching), Atalanta (upstream_not_found sentinel — Apollo path needs wiring) |
| **Techne** (M1) | Theseus (mis-attrib `James`) | never heartbeated PG | Theseus (Fire #34 just landed) |
| **Harmonia** (M2) | Phylax, Sophia, Iris, Argos, Telos, Harmonia_Loop | not registered; loop ALIVE | all 5 ticking; **Sophia stopped writing proposals**, others producing artifacts |
| **Charon** (M2/M1?) | Stygian, Lethe, Acheron, Moros, Hecate, Charon_Loop | not registered; loop ALIVE | all 5 ticking; mostly empty-result loops |
| **Ergon** (?) | Penelope, **Pheme** | not registered | Penelope ticking, 90% drop in batch volume vs prior 24h; Pheme (just launched, demand voicer — upstream_not_found sentinel pending Ergon eval-root wiring) |
| _(unsupervised)_ | Apollo, Hephaestus, Calliope, Pronoia, Metis, Nemesis, Nous | n/a | Apollo + Hephaestus daemons ALIVE; Calliope on-demand |

---

## 2. Full roster — one row per agent

Sorted by persona, then by activity recency. `LC` = last commit · `LE` = last log_work event · ages relative to 2026-05-21 08:00 EDT.

| Agent | Machine | Kind | Owner | Status | Last commit | Last event | Notes |
|---|---|---|---|---|---|---|---|
| Aporia | M1 | persona | — | DEAD 2.9d | 2026-05-19 — DR-discipline doctrine | — | source of intent for Pythia + Clio; **chokepoint** |
| Clio | M1 | tool | Aporia | **ALIVE 2026-05-23** | 2026-05-23 — MemoryError hardening + .bat launcher | 2026-05-23 05:16 — first post-restart cycle ticking (2+2+1 new papers in first 5 queries) | died 2026-05-20 10:20 with MemoryError (Theseus leak window); restarted detached 2026-05-23 05:16; save() now MemoryError-tolerant with streaming fallback |
| Clio-test | M1 | tool | Aporia | DEAD | — | — | leftover dup row from initial registration; safe to drop |
| Pythia | M1 | tool | Aporia | **ALIVE** | **2026-05-21 07:40 — ISL-04 Bianchi modular forms** | **2026-05-21 07:44 — DR dispatched** | recovered from 25h gap; in-flight-timeout + auto-retry + abandon-after-N shipped 2026-05-21 |
| **Hypatia** | M1 | tool | Aporia | **ALIVE** | **2026-05-23 — built** | **2026-05-23 04:33 — `hypatia_dispatch` HYP-2026-05-23-001 (MATH-0001 → row 352)** | D-track curator: 1 problem/day from 537-catalog → typed-D DR (proof decomposition with R1-R5 ladder) for Ergon worked-solutions corpus |
| **Atalanta** | M1 | tool | Aporia | **ALIVE** (upstream_not_found) | **2026-05-23 — built** | **2026-05-23 04:33 — `atalanta_upstream_not_found`** | E-track primitive hunter: reads Apollo organisms, fires Type-E DR for high-reuse / unnamed-composite candidates. Needs `APOLLO_RUN_ROOTS` wired to actual Apollo output path |
| Techne | M1 | persona | — | never PG | 2026-05-19 — Hecate v0.2 (retract Techne ticket) | — | supervises Theseus |
| Theseus | M1 | tool | Techne (currently `James`) | DEAD 26m | **2026-05-21 05:45 — Fire #34 inventory** | 2026-05-21 07:13 — `theseus_batch_complete` | substrate generation engine; mis-attributed |
| Harmonia | M2 | persona | — | not reg | 2026-05-19 22:22 — swarm launcher | — | supervises 6-tool swarm |
| Harmonia_Loop | M2 | tool | Harmonia | STALE 164s | 2026-05-19 — single-instance lock | — | rotation orchestrator (no `harmonia_loop_*` stages logged) |
| Phylax | M2 | tool | Harmonia | DEAD 7m | 2026-05-19 — wire Pythia DR enqueue | 2026-05-21 07:37 — `phylax_tick_complete` | pre-promotion gate; ticks empty |
| Sophia | M2 | tool | Harmonia | DEAD 6m | 2026-05-19 — swarm v0.1 | 2026-05-21 07:38 — `sophia_tick_complete` | **proposal output collapsed 137→0**; running meta-tasks |
| Iris | M2 | tool | Harmonia | STALE 254s | 2026-05-19 — swarm v0.1 | 2026-05-21 07:40 — `iris_tick_complete` | prose-to-symbol compressor |
| Argos | M2 | tool | Harmonia | STALE 164s | 2026-05-19 — daily DR cap protection | **2026-05-21 07:41 — `argos_tick_complete`** | lens-fingerprint accretion |
| Telos | M2 | tool | Harmonia | DEAD 9m | 2026-05-19 — per-FID lens history | **2026-05-21 07:44 — `telos_tick_complete`** | stalled-specimen reviver |
| Charon | M2? | persona | — | not reg | 2026-05-19 11:02 — DR-discipline | — | supervises 6-tool swarm |
| Charon_Loop | M2? | tool | Charon | ALIVE 17s | 2026-05-19 — single-instance lock | — | rotation orchestrator (no `charon_loop_*` stages logged) |
| Stygian | M2? | tool | Charon | ALIVE 17s | 2026-05-19 — swarm v0.1 | **2026-05-21 07:44 — `stygian_tick_complete`** | ticks return `dr_seeded=False` — empty |
| Hecate | M2? | tool | Charon | STALE 258s | 2026-05-19 — v0.2 stratified sampling | 2026-05-21 07:40 — `hecate_tick_complete` | retracts Techne tickets |
| Lethe | M2? | tool | Charon | DEAD 17m | 2026-05-19 — swarm v0.1 | 2026-05-21 07:27 — `lethe_tick_complete` | conjecture loop |
| Acheron | M2? | tool | Charon | DEAD 13m | 2026-05-19 — swarm v0.1 | 2026-05-21 07:31 — `acheron_tick_complete` | swarm member |
| Moros | M2? | tool | Charon | DEAD 9m | 2026-05-19 — swarm v0.1 | 2026-05-21 07:35 — `moros_tick_complete` | swarm member |
| Ergon | ? | persona | — | not reg | 2026-05-18 — Penelope v0.1 | — | supervises Penelope |
| Penelope | M2 | tool | Ergon | DEAD 23m | 2026-05-19 — v0.3 Fire #29 compliance | 2026-05-21 07:21 — `penelope_batch_complete` | substrate ingest loop; 76→7 batches |
| **Pheme** | M1 | tool | Ergon | **ALIVE** (upstream_not_found) | **2026-05-23 — built** | **2026-05-23 04:33 — `pheme_upstream_not_found`** | Demand voicer: scans Ergon eval output → publishes per-pattern failure-rate profile → biases Hypatia/Atalanta selection toward Learner deficits. Closes supply-demand loop. Needs `EVAL_ROOTS` wired |
| **Talos** | M1 | tool | Ergon | **ALIVE** | **2026-05-23 — built (Phase 0: corpus builder)** | **2026-05-23 11:49 — `talos_corpus_growth` 24,668 examples (Hephaestus 18,564 / Prometheus substrate 6,104)** | Reasoning-code specialist: corpus builder for a Qwen-2.5-Coder-1.5B LoRA. Phase 0 = curate; Phase 1 = train (GPU loop owner TBD). Eval harness scaffolded with 5 hand-written cases across 4 capability targets (algo-gen / refactor / counterex / pushback). Apollo + external_oss + synthetic streams need wiring. |
| **Polyhymnia** | M1 | tool | Aporia | **ALIVE** | **2026-05-24 — built (Phase 0: one-tensor agent)** | **2026-05-24 07:06 — `polyhymnia_scour_prometheus_self_run` 2,136 cells from first scour (49 disciplines registered, 21 object_kinds, 89 free_tags)** | The one-tensor-of-all-tensor-knowledge agent. Sparse content-addressable tensor on disk; scour rotation populates it. Phase 0 ships 1 scour (prometheus_self); future scours (Wikipedia / arXiv / OEIS / MathWorld / GitHub topics / fringe) plug into `scours/REGISTRY`. Lenses + games slated for Phase 0.5. |
| Apollo | M2 | daemon | — | **ALIVE 57s** | 2026-05-18 — Hephaestus roadmap (touched apollo) | — (uses own heartbeat thread, no log_work) | evolutionary search; grinding |
| Hephaestus | M3 | daemon | — | **ALIVE 20s** | 2026-05-18 — v2 roadmap | — (uses own heartbeat thread, no log_work) | forge; grinding |
| Pronoia | M4 | daemon | — | UNKNOWN | — (no commits) | — | reporting orchestrator; running per `auto: portfolio update` commits every 4h |
| Calliope | M4 | tool | — | DEAD 2.3d | 2026-05-19 — body+numstat enrichment | 2026-05-19 — `calliope_daily_narrative` | on-demand; not a daemon — DEAD is expected between runs |
| Metis | M4 | tool | — | not in state | 2026-05-19 — email cleanup | — | invoked by Pronoia each cycle |
| Nemesis | M3 | daemon | — | UNKNOWN | — | — | never deployed |
| Nous | M4 | daemon | — | UNKNOWN | — | — | never deployed |
| Aletheia | ? | pipeline-stage | — | UNKNOWN | 2026-05-18 — Pythia v0.2 conform | 2026-05-18 — `aletheia_feedback_implemented` | knowledge graph harvester |
| Coeus | ? | pipeline-stage | — | UNKNOWN | — | — | causal analysis; dormant |
| Eos | ? | pipeline-stage | — | UNKNOWN | 2026-05-18 — backout substrate redirect | — | external scanner |
| Hermes | ? | pipeline-stage | — | UNKNOWN | 2026-05-17 — deprecated | — | deprecated, do not redeploy |

---

## 3. Detail by persona

### Aporia (M1 · Claude Code session)
- **Identity**: void detection, Deep Research dispatch, anti-anchor verification, Clio supervision, typed-DR substrate production
- **Tools**: Clio (paper scanner) · Pythia (DR producer) · **Hypatia (D-track curator, new 2026-05-23)** · **Atalanta (E-track primitive hunter, new 2026-05-23)**
- **Substantive output last 7 days**: DR-prompt-discipline doctrine; Pythia in-flight-timeout hardening (90 min default, max-retries=2, requeue-then-abandon); 52-candidate follow-up miner + dispatch; Techne self-claims triage (5 abstracted DRs); 184 DR reports completed 5/21-5/22; **typed-DR substrate pivot doc + 3 new agents shipped 2026-05-23**
- **Substantive output last 24h**: Hypatia first dispatch HYP-2026-05-23-001 (MATH-0001, row 352); Atalanta + Pheme launched (sentinel ticks pending upstream wiring)
- **Notes**: pivot to typed-DR substrate production (A/B/C/D/E by target) is live. Hypatia owns D; Atalanta owns E; A/B/C remain Aporia + Lethe + Sophia ad-hoc. Pheme (operator=Ergon) provides demand signal. See `pivot/persona_seed_prompts_2026-05-21.md` for the broader plan that motivated these.

### Techne (M1 · Claude Code session)
- **Identity**: substrate generation / Σ-kernel toolsmith
- **Tools**: Theseus (substrate generation engine)
- **Substantive output last 7 days**: Theseus Fire #27–#34 (multi-phase episode composer, completeness-boosted selection, catalog_pair metadata, etc.)
- **Substantive output last 24h**: Theseus Fire #34 landed at 05:45 today
- **Notes**: Theseus is still registered with `operator="James"` — needs re-registration (see paste-prompt from 2026-05-19). Techne herself never wrote a Postgres heartbeat — operating without dashboard visibility.

### Harmonia (M2 · Claude Code session)
- **Identity**: scientist swarm orchestrator
- **Tools**: Harmonia_Loop (rotation) · Phylax · Sophia · Iris · Argos · Telos
- **Substantive output last 7 days**: swarm v0.1 launch (5/19); per-tool patches (DR cap protection, lens history, single-instance lock); operational hardening 3-patch series; Windows .bat launcher
- **Substantive output last 24h**: ticks firing every ~5 min for all 5 tools, but Sophia's `proposal_written` events dropped 137→0. Phylax/Iris/Argos/Telos producing artifacts but most show `dr_seeded=False`, `errors=0`, `verdicts={'pass':0,'flag':0,'block':0}` — i.e. processing empty inputs.
- **Notes**: Harmonia is the most active swarm-by-count but the lowest substantive-output-per-tick ratio. Without ticket inflow, the swarm cycles on dry queues.

### Charon (machine TBD · Claude Code session)
- **Identity**: kill-tier / falsification swarm (the ferryman)
- **Tools**: Charon_Loop (rotation) · Stygian · Lethe · Acheron · Moros · Hecate
- **Substantive output last 7 days**: swarm v0.1 launch (5/19 08:27); DR-discipline catch-in-flight-duplicates; Hecate v0.2 stratified sampling; swarm-wide DR-prompt-discipline doctrine adoption
- **Substantive output last 24h**: 5 tools ticking every ~5–10 min; Lethe + Hecate work on `saxl_conjecture` but most ticks return `candidate=False`, `dr_seeded=False`, `errors=0`. Same empty-loop pattern as Harmonia.

### Ergon (machine TBD · Claude Code session)
- **Identity**: Learner-corpus consumer / training corpus orchestrator
- **Tools**: Penelope (substrate ingest loop) · **Pheme (demand voicer, new 2026-05-23)**
- **Substantive output last 7 days**: Penelope v0.1 → v0.3 evolution (Fire #29 contract compliance, git pull integration)
- **Substantive output last 24h**: 7 batch_complete events (down from 76 prior 24h). Latest: "0 ingested, 13 dup-skip" — Penelope is finding only duplicates, meaning upstream Theseus isn't producing new substrate fast enough.
- **Pheme (new)**: lives at `agents/pheme/` but operator=Ergon. Scans Ergon eval output, computes per-pattern failure-rate profile, publishes to `agents/pheme/artifacts/demand_latest.json`. Currently fires `upstream_not_found` sentinel every tick — needs `EVAL_ROOTS` (default tries `ergon/learner/evals`, `ergon/evals`, `ergon/diagnostic_c/eval_runs`) wired to wherever Ergon actually writes eval results.

---

## 4. Unsupervised daemons (no persona)

- **Apollo (M2)** — evolutionary search. ALIVE, grinding. Heartbeats via own thread; doesn't use `session_telemetry` so no `log_work` events. To see what it's doing, check Postgres heartbeat `status_json.key_metrics` or `apollo/RESUME.md`.
- **Hephaestus (M3)** — forge. ALIVE, grinding. Same telemetry pattern as Apollo. Forge rate ~2.5% (by design, per James's clarification 2026-05-17).
- **Pronoia (M4)** — reporting orchestrator, intelligence_loop.py PID 13308. Running per `auto: portfolio update` commits every 4 hours; doesn't show in state.json this cycle (degraded snapshot).
- **Metis (M4)** — Pronoia invokes Metis each 4h cycle to write the portfolio brief. LLM cascade currently failing on all 4 providers as of 2026-05-19 evening (Cerebras 429, Groq 413, NVIDIA 502, DeepSeek 402).
- **Calliope (M4)** — daily NotebookLM narrative; invoke-on-demand, not a daemon. DEAD between runs is expected.
- **Nemesis (M3), Nous (M4)** — instrumented but never deployed. Skip.

---

## 5. Pipeline-stage agents (run inside `pronoia.py` chain)

- **Aletheia** — knowledge graph harvester (transient per-cycle)
- **Coeus** — causal analysis (dormant; concept weights predate current ledger)
- **Eos** — external scanner
- **Hermes** — deprecated 2026-05-17 (email handling moved to `scripts/send_brief_email.py`)

---

## 6. Diagnostic — why output feels low despite many active agents

Cross-checking commits + intel events against actual substrate-relevant deliverables in the last 24 hours:

- **Real substrate produced**: 1 Pythia DR report (last 4 minutes), 0–1 Theseus fires, 0 Sophia proposals, 0 Clio paper scans
- **Loop ticks fired**: ~430 (Harmonia + Charon swarms), each logging `success=True`
- **Ratio**: roughly 1 substrate artifact per ~200–400 loop ticks

The loop ticks ARE work — but most of them are processing empty queues. The agents follow the pattern: "iterate over inbox → if empty, write artifact saying 'processed=0, errors=0' → success." There is no escalation signal when N consecutive ticks return nothing useful.

**Two attribution issues worth fixing later:**
1. Theseus → owner should be Techne, not James
2. Personas (Charon, Harmonia, Ergon) never registered themselves in `agora.agent_heartbeats`, so they appear only as `operator=` fields on their tools rather than as first-class rows. Adding them would let Metis brief on persona-level liveness.

**Two daemons run without `session_telemetry`** (Apollo, Hephaestus) — their work is real but invisible to `log_work`-based dashboards. They're tracked through their own heartbeat threads + `key_metrics` in `status_json`.

---

## 7. Where to look next

- Pythia heartbeat: `python scripts/agora_persist.py list` shows the AI_Pro compute-window state
- Per-agent commits: `git log --since=7\ days\ ago --grep='<AgentName>' --no-merges`
- Per-agent log_work events: SQL `SELECT * FROM agora.intelligence_outputs WHERE stage LIKE '<agent_lowercase>%' ORDER BY finished_at DESC LIMIT 20;`
- Live dashboard: https://jcraig949jfi.github.io/Prometheus/

This document is point-in-time; regenerate with the source script after major roster changes. The data extraction logic lives in this conversation — happy to make it a `scripts/agent_roster.py` if you want it on a schedule.
