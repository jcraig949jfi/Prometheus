# Agent Portfolio + Monitoring Design — 2026-05-12

**Status:** in-flight; chip-away revival per user-directed sequence (Hephaestus → Apollo → news research → ...). Substrate + Learner remains 90% of effort; portfolio revival is the 10%.
**Author:** Aporia, drafted during chip-away portfolio revival session.

## §0 Why this doc exists

Prometheus has 13+ agents that have accumulated substantial infrastructure but went dark when attention pivoted (most around 2026-04-25 to the substrate-vocabulary / Learner thread). The previous orchestrator survey missed all 13 of them because they sit under `agents/` which is blanket-gitignored at line 169 of `.gitignore`. Apollo is the exception at top-level `apollo/` (tracked).

This doc serves two purposes:

1. **Portfolio index** — single source of truth for which agents exist, their current state, where their RESUME doc lives, and what 10 min of attention would unblock for each.
2. **Monitoring dashboard design** — when continuous daemons (Apollo, Hephaestus) get revived on M2, how do we see what they're doing without spinning up windows or babysitting terminals.

Two purposes in one doc because the portfolio drives what needs monitoring, and the monitoring design drives what the per-machine `agentic_loop.py` framework has to expose.

## §1 The 13-agent portfolio (current state)

Surveyed 2026-05-12. Each agent: path, status (HOT / WARM / LUKEWARM / COLD / DORMANT / MISSING), last activity, RESUME doc location, value, 10-min revival cost.

**Tracked at top-level (visible to git):**

- **Apollo** — `apollo/`. LUKEWARM (last activity 2026-04-25 01:40, 17 days idle). Evolutionary computation engine for reasoning improvements via LLM-guided program synthesis; v2.1 roadmap in progress (NSGA-III, racing, FAISS, batch LLM). Substantial infrastructure: src/, scripts/, configs/, checkpoints/, journal/, lineage/, graveyard/, dashboard/. RESUME at `apollo/RESUME.md` (chip 2, 2026-05-12). 10-min revival: import check, PID cleanup, relaunch.

**Tracked separately:**

- **Charon** — `charon/`. HOT (last activity 2026-05-09). Falsification battery operator; Substrate Cartography Suite recently shipped. Not a dormant initiative; in active use.

**Under `agents/` (blanket gitignored; resume docs live in `pivot/` until/unless we add `!agents/*/RESUME.md` exception):**

- **Hephaestus** — `agents/hephaestus/`. LUKEWARM (last activity 2026-04-02, 40 days idle). Forge for reasoning tool primitives via NVIDIA/Augment API + 5-gate validation + 15-trap battery; ~1,945 forged tools across 9 versions; 4,905 ledger entries. RESUME at `pivot/agents_hephaestus_resume_2026-05-12.md` (chip 1, 2026-05-12). 10-min revival: identify entry point in `src/`, check API key, restart loop.
- **Nous** — `agents/nous/`. State unknown (filed for next chip). Provides scored concept combinations to Hephaestus. **Direct dependency of Hephaestus — must be alive for Hephaestus to forge anything.**
- **Coeus** — `agents/coeus/`. State unknown. Provides causal-intelligence directives to Hephaestus's queue.
- **Aletheia** — `agents/aletheia/`. State unknown.
- **Auditor** — `agents/auditor/`. State unknown.
- **Clymene** — `agents/clymene/`. State unknown.
- **Eos** — `agents/eos/`. State unknown. Note: same agent as "Dawn" per `feedback_dawn_alias.md`.
- **Hermes** — `agents/hermes/`. State unknown (config explicitly gitignored at `.gitignore` line 10-11).
- **Metis** — `agents/metis/`. State unknown.
- **Nemesis** — `agents/nemesis/`. State unknown.
- **Pronoia** — `agents/pronoia/`. State unknown.
- **Skopos** — `agents/skopos/`. State unknown.
- **Shared** — `agents/shared/`. Infrastructure used by multiple agents, not its own agent.

**Top-level dormant subsystems** (not under `agents/` but should be in the portfolio):

- **Ignis** — `ignis/`. LUKEWARM (2026-04-25, 17 days). Ejection-finding work, characterized across 3 scales. 65 .py + 22 .md. Future chip.
- **Cartography** — `cartography/`. LUKEWARM (2026-04-25, 17 days). 1066 .py + 12,162 .md — the largest dormant corpus. Future chip.
- **Rhea** — `rhea/`. COLD (2026-03-25, 48 days). Self-improving loop, scaling to 1.7B. Future chip.

## §2 Chip progress

- **Chip 1: Hephaestus** — done 2026-05-12. RESUME at `pivot/agents_hephaestus_resume_2026-05-12.md`. Located, surveyed, three hypotheses for stoppage documented. Revival paths specified (minimal restart / port to M2 / refactor).
- **Chip 2: Apollo** — done 2026-05-12. RESUME at `apollo/RESUME.md`. Located, surveyed, v2.1 roadmap status captured. Revival paths specified (Path A minimal restart recommended).
- **Chip 3: Nous** — pending. Hephaestus depends on Nous, so Nous needs revival before Hephaestus can usefully run. Nous is the natural next chip.
- **Chip 4 onward: Coeus, Cartography, Ignis, Rhea, ...** — TBD sequence; each ~30-45 min of chip-away attention to locate + survey + write RESUME.

The pace: one chip per session checkpoint when the substrate-vocabulary / Learner work has a natural pause. ~10-15 hours of total attention across whenever-the-time-is-available to chip through the full 13.

## §3 Monitoring dashboard design

### §3.1 The model

Two layers:

**Layer A — per-daemon STATUS.json.** Each continuous daemon (Apollo, Hephaestus, eventually others) writes a small JSON file to its own directory every 5-15 minutes. The schema is identical across daemons so a single reader can aggregate. Format:

```json
{
  "agent": "apollo_v2_evolution",
  "machine": "M2",
  "status": "running",
  "last_heartbeat": "2026-05-12T14:32:00Z",
  "pid": 18472,
  "uptime_seconds": 3621,
  "current_op": "evaluating generation 47 (population 80)",
  "throughput_24h": {"generations": 11, "evaluations": 880, "killed_early": 312},
  "key_metrics": {
    "best_fitness_vector": [0.82, 0.71, 0.91, 0.65, 0.88, 0.79],
    "population_diversity": 0.43,
    "vram_used_mb": 11800,
    "last_checkpoint": "2026-05-12T13:15:00Z",
    "eta_next_checkpoint_min": 35
  },
  "recent_errors": [],
  "next_action": "continue generation 47 evaluation; checkpoint after"
}
```

Apollo-specific keys live under `key_metrics`. Hephaestus's would have `forges_this_session`, `current_combo`, `pass_scrap_rate_hour`. The outer schema (agent, machine, status, last_heartbeat, pid, uptime, current_op, throughput_24h, recent_errors, next_action) is universal.

**Layer B — top-level portfolio_STATUS.md.** A second daemon (or a function inside `agentic_loop.py`) reads all the per-daemon STATUS.json files, plus the schedule.yaml entries, plus git state, and regenerates a single human-readable markdown digest every 10-15 minutes. Lives at `pivot/portfolio_STATUS.md`. Format:

```markdown
# Prometheus Portfolio Status — auto-generated 2026-05-12T14:35:00Z

## Continuous daemons

### Apollo (M2) — running, uptime 1h
- Current: evaluating generation 47
- Best fitness vector: [0.82, 0.71, 0.91, 0.65, 0.88, 0.79]
- Throughput 24h: 11 generations, 880 evaluations, 312 early-killed
- Next checkpoint: ~35 min
- No errors.

### Hephaestus (M2) — running, uptime 6h
- Current: forging Autopoiesis × Counterfactual Reasoning × Satisfiability
- Throughput 24h: 84 forges (32 passed, 52 scrap), 38% rate
- Last successful forge: 12 min ago
- No errors.

## Scheduled (cron-fired)

### Gemini Deep Research burn (cloud routine) — last fired 06:01 UTC
- 20 reports landed at aporia/docs/deep_research_batch_2026-05-12/
- Next fire: tomorrow 06:00 UTC

### Cartography weekly refresh (M4) — last fired 2026-05-08 (4 days ago)
- Next fire: Sunday 02:00 UTC

## Dormant (have RESUME docs but not running)

- Nous: pending chip
- Coeus: pending chip
- Ignis: pending chip
- Rhea: pending chip
- ... (8 more)

## Recent kills / falsifications across the substrate

- 2026-05-12 13:48: Hephaestus scrap — combo declined by model
- 2026-05-12 13:22: Apollo gen 47 ind #18 killed early (racing)
- ... (last 10 events)

## Anomalies

(none in last 24h)
```

### §3.2 Access patterns

The markdown digest lives in git, so anywhere git is reachable, the dashboard is reachable. Three primary access paths:

- **From M1 terminal**: `cat pivot/portfolio_STATUS.md` or open in any editor.
- **From Claude Code remote-control (phone or laptop)**: open the file via Claude Code's file browser; auto-refresh every 10-15 min.
- **From GitHub mobile / web**: refresh the repo's view of `pivot/portfolio_STATUS.md`. Latency = git push cadence + GitHub mirror lag (~30 seconds).

No web server. No TUI. No native dashboard. Just markdown that's always up to date.

### §3.3 Refresh + push cadence

The portfolio monitor daemon runs on M1 (since it has the cleanest view of git state). Once every 10-15 minutes it:

1. Reads all `<agent>/STATUS.json` files it knows about (path list lives in `pivot/agent_registry.jsonl`).
2. Reads `pivot/schedule.yaml` for cron-fired schedule state.
3. Reads `git log -10 --all` for recent commit-side activity (kills, claims, syntheses).
4. Regenerates `pivot/portfolio_STATUS.md`.
5. Auto-commits with message like `portfolio_STATUS auto-update <ISO timestamp>` — git history records the dashboard's own movement.

Auto-commits will create commit-spam in git log, but each is small (~50 lines markdown) and clearly tagged. A `git log --grep="portfolio_STATUS auto-update" --invert-grep` filter excludes them when reading real commit history.

Alternative if auto-commit-spam is unwanted: write the digest to a non-tracked path (`portfolio_STATUS.local.md`) and have a manual `git portfolio-push` command for when you want to share it.

### §3.4 What dashboard does NOT do

- No real-time WebSocket / push notifications. The 10-15 min cadence is sufficient for continuous daemons that take hours per state change (Apollo) or seconds-to-minutes per state change (Hephaestus).
- No interactive controls. Clicking "stop Apollo" is not a feature. To stop Apollo: SSH or Claude Code remote-control into M2, kill the service. The dashboard is read-only.
- No phone-native app. Markdown via Claude Code remote-control or GitHub web is the phone story.
- No multi-user. Single-user-multi-project per the earlier architecture discussion.

## §4 Continuous-daemon framework requirements

For Apollo + Hephaestus to run continuously on M2 with clean monitoring, the `agentic_loop.py` per-machine framework needs:

1. **`continuous_daemons` registry** in `<machine>/schedule.yaml` — same file as scheduled cron entries, separate section. Each daemon entry: `id`, `entry_point`, `service_unit_name`, `restart_policy`, `health_check`, `vram_budget_mb`, `cpu_priority`.

2. **Service-install helper** — a small script that takes a `continuous_daemons` entry and installs it as a Windows service or systemd unit. Avoids manual installation per daemon. Runs once per daemon at setup.

3. **STATUS.json write contract** — each daemon's code commits to writing its STATUS.json every N minutes. This is a code change per daemon, NOT framework work. For Apollo: add a status-emit function called at the end of each generation. For Hephaestus: add status-emit at the end of each forge attempt.

4. **Heartbeat to Agora STREAM_MAIN** — same daemons additionally heartbeat to Agora so cross-machine visibility exists. If Apollo on M2 stops heartbeating to the shared Redis, M1's monitor sees it within 15 min.

5. **Health-check loop** — the `agentic_loop.py` on each machine includes a health-check pass: every wake, verify the registered continuous daemons are still alive (process exists, last STATUS.json age < threshold). If unhealthy, optionally restart per policy.

## §5 Specific to Apollo's slowness

Apollo "extremely slow" is a feature for this architecture, not a problem. Specifically:

- **Generations take hours.** STATUS.json poll cadence (5 min) catches every state change with high resolution.
- **Checkpoints sparse.** Apollo's checkpoint cadence is probably hourly or per-generation. The dashboard surfaces "last checkpoint X min ago" and "ETA next checkpoint Y min" so you can tell whether it's making progress without watching the actual generation log.
- **Resumable.** Apollo can be killed and restarted from any checkpoint; lineage / graveyard preserved. So service restarts during OS reboots or M2 maintenance don't lose work.
- **Long-horizon value.** The point of running Apollo continuously is that 1000 generations across 30 days yields evolutionary structure that no 5-generation-burst-then-pause can reach. Continuous-slow is the whole bet.

Apollo's slowness also means it's a low-overhead monitoring target. A daemon that updates its STATUS.json every 5 min and writes a checkpoint every hour generates minimal IO load.

## §6 Next chip in this sequence

**Nous** (`agents/nous/`). Reason: Hephaestus depends on Nous; before Hephaestus has anything to forge, Nous needs to be producing scored concept combinations. Same chip pattern: locate, survey state, write RESUME (probably to `pivot/agents_nous_resume_2026-05-NN.md`), update this portfolio index.

After Nous: Coeus (also a Hephaestus dependency). Then Cartography (largest dormant corpus, news-research adjacent). Then Ignis, Rhea, and the rest.

The sequence respects dependencies: revival is most useful in dependency order, so an agent's prerequisites are alive when it revives.

## §7 Open questions

- **Gitignore exception for `!agents/*/RESUME.md`?** Currently the 11 agents under `agents/` need their RESUME docs in `pivot/` (centralized but disconnected from the agent's directory). Adding the gitignore exception lets each agent keep its RESUME in-place. One-line low-risk change to `.gitignore`. Worth doing for consistency once we have RESUME docs for more than 2-3 agents.

- **STATUS.json schema** — the schema above is a sketch. Once Apollo or Hephaestus actually starts writing one, the schema firms up based on what's actually useful to observe. Reasonable to defer schema-freeze until 1-2 daemons are emitting and we have empirical feedback.

- **Auto-commit cadence for portfolio_STATUS.md** — 10-15 min seems reasonable but may produce commit-spam. Alternative: write to local-only path, push manually. Worth deciding before standing up the monitor daemon.

- **Where does the `agentic_loop.py` framework actually get built?** Not in this chip (that's infrastructure work). When it's time, the natural home is `pivot/agentic_loop.py` or maybe `agora/scripts/agentic_loop.py` (since it sits adjacent to Agora's existing primitives).

## §8 What's been done in this chip

- Apollo RESUME doc at `apollo/RESUME.md` (in-place since `apollo/` is tracked).
- This portfolio + monitoring design doc at `pivot/agent_portfolio_and_monitoring_2026-05-12.md`.
- Surfaced the full 13-agent portfolio with state-of-each.
- Documented monitoring dashboard design at the markdown-digest level.
- Specified the STATUS.json schema and the continuous-daemon framework requirements.

## §9 What's not yet done

- The `agentic_loop.py` framework itself (infrastructure; deferred until after a few more chips of revival, OR when the substrate-shaped pipeline pilot returns evidence).
- Per-machine `schedule.yaml` files (await framework).
- Service-install helper script (await framework).
- Apollo + Hephaestus actual STATUS.json emission code (small additions to each agent's runner; deferred until revival proper).
- The portfolio monitor daemon that writes `portfolio_STATUS.md` (await framework).
- Remaining 11 agent RESUME docs (chip 3 onward).

This doc is the connective tissue: it shows where each piece lives and what's needed to revive each, so when the framework arrives the integration is mechanical.
