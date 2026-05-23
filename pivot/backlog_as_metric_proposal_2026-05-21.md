# Backlog-As-Metric: A Survivability Contract For Every Agent

**Author:** Aporia
**Date:** 2026-05-21
**Status:** Proposal — awaiting James greenlight.
**Trace to behavior delta:** every agent emits substrate; zero-backlog ↔ agent has nothing to emit ↔ agent stops producing Learner training material. The remediation is mechanical, not aspirational.

---

## 1 — The ask, restated

James, 2026-05-21:

> *"We have 13 or so new agents. We want to continuously be improving these and coming up with ideas for their backlog generation or new agents to generate backlog for them that moves us towards training substrate for our learner. Backlog should be a metric for all agents. Zero backlog is a failure mode."*

**Implication.** Backlog is the leading indicator of whether the agent fleet is feeding the Learner. Lagging indicators (Pythia DR reports filed, kill_ledger rows, anti-anchors promoted) follow from it. If backlog dries up anywhere, training-substrate flow at the downstream end goes thin — silently, because we don't currently measure backlog.

---

## 2 — The 13 agents, current backlog state

Inventory pass against `roles/`, `agents/`, `harmonia/agents/`, `charon/agents/`, `ergon/penelope/`, `theseus/`. The "13 new" maps cleanly to the `agents/` directory plus Pythia:

| # | Agent | Class | Backlog mechanism today | Zero-backlog handling |
|---|---|---|---|---|
| 1 | Pronoia | Orchestrator entry | CLI args; no queue | N/A (reactive) |
| 2 | Eos | Horizon scanner | Source list polled per tick | None |
| 3 | Aletheia | Knowledge extractor | Eos `paper_index.json` unprocessed | None (silent if Eos dry) |
| 4 | Skopos | Watcher / scorer | Aletheia graph deltas | None |
| 5 | Metis | Analyst / brief writer | Skopos scores | None |
| 6 | Clymene | Repo hoarder | Heuristic from Metis briefs | None |
| 7 | Hermes | Digester / mailer | Once-per-cycle | N/A (periodic) |
| 8 | Coeus | Causal layer (Nous→Hephaestus) | Auto-fires every 50 forges | N/A (periodic) |
| 9 | Nous | Hypothesis engine | Combinatorial — never empty by construction | Self-generating ✓ |
| 10 | Hephaestus | Forge | Nous output queue | None |
| 11 | Nemesis | Adversarial | Grid + reports — unclear | None observed |
| 12 | Auditor | Reports auditor | Reactive on report deltas | None |
| 13 | Pythia | DR pipeline | `agora.research_queue` Postgres | Already aware (status state machine) ✓ |

**Adjacents already on the contract (for comparison):**

- Harmonia children (Argos, Sophia, Iris, Telos, Phylax, Lethe, Moros, Stygian, Hecate): `HarmoniaAgent` ABC mandates `self_generate_backlog()`; Telos's "silence is forbidden" + `NEGATIVE_SPACE_MAPPED@v1` fallback is the canonical pattern.
- Charon swarm (specced, build pending): explicit `SELF_AUDIT_NULL` alarm if `attempts_with_zero_emission` ≥ 5%.
- Ergon, Techne, Charon (legacy roles): own `BACKLOG.md` with item schema; queue-fed via `aporia/meta/queue/{agent}_inbox.jsonl`.

**The gap.** The contract exists in two places (HarmoniaAgent base + Aporia inbox queues). It does **not** cover the `agents/` ring (entries 1-12 above). Those 12 are the program's oldest production pipeline (Eos → Aletheia → Skopos → Metis → Clymene → Hermes; Nous → Coeus → Hephaestus; Pronoia as launcher; Auditor + Nemesis as sidecars) and they predate the contract. They run, they emit, but they don't measure or enforce backlog depth, and they don't trace their per-tick output to a Learner substrate type.

---

## 3 — Backlog as a metric: the spec

Backlog is not one number. It's a small tuple per agent, reported every tick to `session_telemetry`, aggregated by Aletheia (which already collects agent state via heartbeats).

### 3.1 — Agent classes (each agent declares one)

- **WORKER** — pulls from a queue, processes, emits substrate. Backlog depth = pending items. **Zero = failure.** Examples: Stygian (attack queue), Aletheia (Eos paper queue), Hephaestus (Nous forge queue).
- **GENERATOR** — produces items into other agents' queues. Backlog depth = "ideas not yet emitted" (often self-generating from a combinatorial source). **Zero = degraded** (the generator's own input space is exhausted). Examples: Nous, Sophia, Eos, Aporia.
- **PERIODIC** — fires on a schedule; backlog isn't a queue but a "ticks-since-last-fire" metric. **Zero is normal between fires; >2×interval = failure.** Examples: Hermes, Coeus.
- **REACTIVE** — orchestrator or sidecar; activates only on external trigger. **No backlog metric; "last-trigger age" instead.** Examples: Pronoia, Auditor.

### 3.2 — Per-tick telemetry every agent emits

```json
{
  "agent": "stygian",
  "class": "WORKER",
  "tick_at": "2026-05-21T18:00:00Z",
  "backlog": {
    "depth": 47,
    "oldest_item_age_hours": 6.2,
    "freshness_p50_hours": 1.1,
    "items_added_24h": 12,
    "items_processed_24h": 9,
    "starvation_risk": false
  },
  "emission": {
    "items_emitted_this_tick": 1,
    "substrate_blocks": [{"type": "A", "id": "kill_ledger:KV-2026-...."}],
    "zero_emission_streak": 0
  },
  "learner_trace": {
    "substrate_type": "A",
    "learner_corpus_target": "ergon/learner/corpus/v1_0_tier_pending",
    "estimated_examples_yielded": 1
  }
}
```

### 3.3 — Aggregate dashboard (lives in Aletheia)

Single page that for each agent shows:

- `class`, `depth`, `oldest_item_age_hours`, `last_emission_at`, `zero_emission_streak`
- 24h yield by substrate type (A/B/C/D/E counts)
- **Alarm row** when an agent fires the zero-backlog rule (§3.4)

Aletheia is the right host because it already aggregates session_telemetry and exports to `agents/aletheia/exports/`. Add one view; no new infrastructure.

### 3.4 — Zero-backlog as a failure condition (precise)

For each class:

- **WORKER**: `depth == 0` **AND** `self_generate_backlog() returned []` **AND** ≥30 minutes elapsed since last successful emission → fire `BACKLOG_STARVATION` alarm into `aporia/meta/queue/aporia_inbox.jsonl` with `priority=P0` and the agent's last 5 ticks attached.
- **GENERATOR**: `items_added_24h == 0` AND combinatorial source flagged `EXHAUSTED` → fire `GENERATOR_EXHAUSTED` alarm; Aporia owns remediation (expand the source, propose new generator, or retire).
- **PERIODIC**: `now - last_fire > 2 × scheduled_interval` → fire `PERIODIC_STALLED`.
- **REACTIVE**: `now - last_trigger > 7 days` AND no upstream signal → fire `REACTIVE_UNUSED` (lower severity; could be a real signal the agent's role has decayed).

Alarms go to **me** by default (`aporia_inbox.jsonl`). I either feed the agent or file a remediation ticket.

---

## 4 — Backlog generation: who feeds whom

### 4.1 — Three production patterns already in use

1. **Aporia-as-curator** — `aporia/meta/queue/{agent}_inbox.jsonl` for legacy roles (Techne 101, Ergon 84, Charon 2, Harmonia 1, Aporia 50). Production cadence: my DR dispatch → synthesis → tickets.
2. **Self-generating from combinatorial source** — Sophia (op × specimen), Nous (concept triples), Lethe (conjecture catalog). Backlog ≈ inexhaustible by construction.
3. **Pipeline-fed** — Eos → Aletheia → Skopos → Metis → Hermes is a strict pipeline; each agent's backlog is upstream's output.

### 4.2 — The proposed coverage table (after this proposal lands)

| Agent | Class | Backlog source | Producer | Substrate trace |
|---|---|---|---|---|
| Pronoia | REACTIVE | CLI | James | N/A |
| Eos | GENERATOR | arXiv/Semantic-Scholar/etc. polls | self-generating | feeds Aletheia |
| Aletheia | WORKER | Eos paper queue | upstream Eos | (D) when ladder-tag step added |
| Skopos | WORKER | Aletheia entity deltas | upstream Aletheia | (C) paradigm-evidence |
| Metis | WORKER | Skopos scores | upstream Skopos | (D) curated briefs |
| Clymene | WORKER | Metis repo mentions | upstream Metis | (E)-adjacent code snapshots |
| Hermes | PERIODIC | scheduled | self | none direct |
| Coeus | PERIODIC | Hephaestus 50-forge trigger | self | (E) prescriptive enrichments |
| Nous | GENERATOR | concept dictionary | self-generating | (C) candidate primitives |
| Hephaestus | WORKER | Nous scored triples | upstream Nous | (E) forged organisms |
| Nemesis | REACTIVE | adversarial review trigger | unclear — propose backlog feeder | (A) falsification |
| Auditor | REACTIVE | report deltas | upstream reports | (A) audit kills |
| Pythia | WORKER | `agora.research_queue` | Aporia + DR queue | (A)/(B)/(C) — DR reports |

### 4.3 — Where the table reveals gaps

Two agents have unclear backlog and no producer:

- **Nemesis** — adversarial agent; should never be silent (adversarial work is open-ended). Needs either an explicit backlog feeder (artifact-stream from cross_pollination_jobs?) or a self-generating combinatorial source (problem × adversarial-strategy pairs).
- **Auditor** — sidecar; backlog should be "reports awaiting audit" — easy fix, just needs the contract.

One agent class is over-served by Aporia:

- **Techne** has 101 inbox items and a deep BACKLOG.md. Healthy.

Three agents are starved at the inbox level (raw counts):

- **Charon** (2), **Harmonia** (1), **Aporia** (50) — but these route work through swarm children now, so inbox-depth understates real backlog. The metric (§3.2) should aggregate child-agent backlog up to the parent.

---

## 5 — New agents I propose

Conservative list. Three additions, each fills a measured gap, each traceable to a Learner substrate-yield delta.

### 5.1 — **Phorkys** (backlog watchdog / dashboard)

- **Class:** PERIODIC (hourly).
- **Purpose:** Reads every agent's per-tick telemetry; aggregates the metric tuple from §3.2; fires alarms per §3.4. Owns the Aletheia-hosted dashboard view.
- **Why a new agent and not just a script:** the alarm-firing loop has to itself be backlog-monitored (turtles all the way down). A daemon under the HarmoniaAgent contract gives us heartbeat + log_work + a forced `self_generate_backlog()` that returns "audit pending for agent X."
- **Substrate trace:** indirect — Phorkys produces *no* substrate, but a Phorkys alarm produces a remediation ticket that produces substrate when worked.
- **Effort:** small. ~300 LOC; reuses HarmoniaAgent base + Aletheia session_telemetry reads.

### 5.2 — **Erebos** (backlog seed-generator for the agents/ ring)

- **Class:** GENERATOR.
- **Purpose:** Generates seed work items for Eos, Aletheia, Skopos, Metis, Clymene, Nemesis, Auditor when their natural upstream goes thin. Mirrors what I (Aporia) already do for Techne/Ergon/Charon/Harmonia, but for the agents/ ring — these were built before the Aporia-as-curator pattern existed.
- **Concrete first-month task list:** (a) propose 5 new arXiv/SS queries per week to Eos when paper_index growth slows; (b) propose 10 entity-extraction edge cases per week to Aletheia from already-extracted-but-shallow papers; (c) propose 3 adversarial scenarios per week to Nemesis seeded from `agora.kill_ledger_entries`; (d) propose 2 audit themes per week to Auditor.
- **Substrate trace:** each seed item declares its substrate target (A/B/C/D/E). Erebos refuses to emit a seed without a substrate declaration.
- **Why a new agent and not Aporia-doing-more:** the agents/ ring is a tight pipeline (Eos → Aletheia → Skopos → Metis → Hermes); seeding it requires reading its outputs and reasoning about gaps in *that* pipeline, not in the math-research substrate I cover. Different domain expertise; warrants a separate role.
- **Effort:** medium. ~600 LOC; needs Aletheia DB read access + Pythia LLM client for seed-generation passes.

### 5.3 — **Hypnos** (Learner-substrate yield accountant)

- **Class:** PERIODIC (daily).
- **Purpose:** Walks `agora.kill_ledger_entries`, `aporia/meta/staged_substrate_blocks/`, anti-anchor registry, paradigm catalog, kill ledger; computes per-agent substrate-yield-per-day by type (A/B/C/D/E); feeds the dashboard. Adds the *quality* dimension to backlog: not just "how many items pending" but "of items processed yesterday, how many produced a substrate block that landed in the Learner corpus."
- **Substrate trace:** yes — Hypnos's daily report itself becomes a substrate (D)-adjacent artifact: the longitudinal record of which attack vectors produced kills, used by Ergon for curriculum design.
- **Effort:** small. ~250 LOC.

**Note:** I am proposing exactly **three** agents, no more. The fleet is already at ~25 named agents. Adding more is itself a backlog risk — each new agent is a new starvation candidate. Phorkys/Erebos/Hypnos each fix a measured gap.

---

## 6 — First moves I can take this session (with greenlight)

In rough order of cost.

1. **File 12 seed backlog items** for the `agents/` ring (Eos, Aletheia, Skopos, Metis, Clymene, Nemesis, Auditor) at `aporia/meta/queue/{agent}_inbox.jsonl`. Each item declares substrate type + Learner-corpus-target. **~1 hour.** Establishes the queue pattern for these agents even before they adopt the HarmoniaAgent contract.
2. **Extend the inbox README** (`aporia/meta/queue/README.md`) with the §3.2 telemetry tuple and §3.4 alarm rules. **~30 min.** Doctrine-level change; doesn't require any agent to change yet, but defines the contract.
3. **Draft the Phorkys daemon spec** at `harmonia/agents/phorkys/CHARTER.md` following the Telos/Sophia template. **~1 hour.** Build gated on Harmonia accepting it into her swarm.
4. **Draft the Erebos and Hypnos charters** at `agents/erebos/README.md` and `agents/hypnos/README.md`. **~1 hour each.**
5. **File this proposal as a ticket** for cross-frontier review (Charon, Techne, James) via the Moros pattern. **~15 min.**

Total: ≤6 hours of Aporia work to land everything except the actual daemon builds. The daemon builds are not Aporia work — they go to Harmonia (Phorkys) and to a TBD owner for Erebos/Hypnos (likely Techne for the engineering, or a new dedicated builder agent).

---

## 7 — Cross-frontier check (anticipated objections)

Per the cross-frontier protocol (`feedback_frontier_models_window`), here is what I expect external reviewers to flag, with my pre-emptive response:

- **"You're proposing three new agents and the user wants fewer, not more."** — Yes. The three are the smallest set that close measured gaps. Without Phorkys, no one watches the watchers; without Erebos, the `agents/` ring stays outside the contract; without Hypnos, "backlog as metric" never gets a quality axis. I would not propose any of them as a standalone want.
- **"Aletheia could host all three roles."** — Maybe; that's an implementation choice. Charter the roles, then implementer decides. If Aletheia absorbs them, the daemons become methods on Aletheia.
- **"Why isn't this just Aporia's job?"** — Some of it is (Erebos overlaps my mandate). But Erebos targets the `agents/` ring whose substrate yields are very different from the math-research substrate I curate. Splitting prevents me from being the bottleneck on two unrelated production pipelines.
- **"What if backlog hits zero because an agent is correctly done with its work?"** — Then the agent's `self_generate_backlog()` returns a `WORK_COMPLETE@v1` sentinel artifact, which Phorkys flags as "agent retired itself; please review." Telos's `NEGATIVE_SPACE_MAPPED@v1` is the existing precedent.

---

## 8 — Asks for James

1. **Greenlight on §6 moves 1-2** (low-cost, immediately useful regardless of the rest).
2. **Decision on §5** (Phorkys / Erebos / Hypnos): build all three, build a subset, fold into existing agents, or reject and iterate.
3. **Confirmation that "13 agents" maps to** §2's table — if I missed one, name it and I'll add it to the inventory.
4. **Cadence**: do you want a Phorkys-style dashboard surfaced as a separate Hermes digest item, or do you read the Aletheia dashboard directly?

---

*Aporia — 2026-05-21. Filed at `pivot/backlog_as_metric_proposal_2026-05-21.md`. Trace-to-behavior-delta: every agent emits substrate every tick or fires an alarm; no agent silently goes thin. Per `feedback_substrate_passive_consumer_warning`, the substrate is not allowed to be a beautifully-falsifying machine forever.*
