# Redis Event Bus — Distributed Agent Communication

*Moving from file-polling to event-driven coordination across machines*

---

## Why Redis Streams (Not Something Else)

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **File-based (current)** | Zero dependencies, works now | No notifications, rsync latency, file locking across machines | Outgrown |
| **SQLite `events` table + polling** | Single dependency, already used | Polling is wasteful, cross-machine SQLite is fragile | Not scalable |
| **Redis Pub/Sub** | Simple, real-time | No persistence — if consumer is offline, events are lost | Too fragile |
| **Redis Streams** | Persistent, consumer groups, backpressure, cross-machine native, simple API | One new dependency (Redis) | **Right choice** |
| **NATS / RabbitMQ / Kafka** | Industrial-grade | Overkill for 12 agents on 2 machines | Too heavy |
| **HTTP webhooks** | Language-agnostic | Every agent needs a web server, error handling is complex | Over-engineered |

Redis Streams hits the sweet spot: one dependency, persistent event log, consumer groups for fan-out, cross-machine natively, and a 5-line Python API per agent.

---

## What Agents Actually Need to Say

Looking at the real communication patterns:

### Events (one agent notifies others that something happened)

```
eos.paper_found          → Aletheia should extract it
aletheia.entity_created  → Nous can use it, Pronoia tracks growth
aletheia.gap_found       → Nous should target it, Pronoia tracks
metis.brief_ready        → Hermes should include it
nous.batch_complete      → Hephaestus should forge from it
hephaestus.tool_forged   → Nemesis should test it, Aletheia should absorb it
hephaestus.tool_scrapped → Arcanum should classify it, Aletheia should record failure
nemesis.failure_found    → Coeus should update graphs, Aletheia should record
coeus.rebuilt            → Nous should update sampling weights
ignis.experiment_done    → Aletheia should deposit results
rhea.evolution_done      → Aletheia should deposit genome, Arcanum should sample waste stream
rhea.corpus_verified     → Aletheia should deposit verified chains
pronoia.gate_blocked     → Hermes should alert James
pronoia.violation        → Hermes should alert James
```

### Queries (one agent asks another for state)

```
pronoia → aletheia: get_substrate_health()
nous → aletheia: get_concepts()
nous → coeus: get_sampling_weights()
hephaestus → coeus: get_enrichment(combo_key)
pronoia → all: get_agent_status()
```

### The Pattern

Events are **pub/sub with persistence** — Redis Streams.
Queries are **request/response** — keep these as direct function calls or SQLite reads. Don't over-stream.

---

## Stream Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     REDIS SERVER                             │
│                  (Machine A or dedicated)                     │
│                                                              │
│  Stream: prometheus:events                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ {id: 1, agent: "eos", event: "paper_found",        │    │
│  │  data: {title: "...", arxiv_id: "...", ...}}        │    │
│  │                                                      │    │
│  │ {id: 2, agent: "hephaestus", event: "tool_forged", │    │
│  │  data: {name: "chaos_x_dialectics_x_feedback",     │    │
│  │         accuracy: 0.67, calibration: 0.27, ...}}    │    │
│  │                                                      │    │
│  │ {id: 3, agent: "nemesis", event: "failure_found",   │    │
│  │  data: {tool: "...", mutation: "negation_inject",   │    │
│  │         task: "...", failure_geometry: {...}}}       │    │
│  │                                                      │    │
│  │ {id: 4, agent: "pronoia", event: "gate_blocked",   │    │
│  │  data: {reason: "substrate_starvation",             │    │
│  │         health: {entities: 2, relations: 3}}}       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Consumer Groups:                                            │
│    "aletheia"    → reads: paper_found, tool_forged,         │
│                    tool_scrapped, failure_found,             │
│                    experiment_done, corpus_verified           │
│    "nous"        → reads: entity_created, gap_found,        │
│                    coeus_rebuilt                              │
│    "hephaestus"  → reads: batch_complete                    │
│    "nemesis"     → reads: tool_forged                       │
│    "coeus"       → reads: tool_forged, tool_scrapped,       │
│                    failure_found                              │
│    "hermes"      → reads: brief_ready, gate_blocked,        │
│                    violation                                  │
│    "pronoia"     → reads: ALL (constitutional guardian)      │
│                                                              │
│  Stream: prometheus:health (lightweight, high-frequency)     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ {agent: "ignis", status: "running",                 │    │
│  │  experiment: "evolve_L22", gen: 340, eta: "45m"}    │    │
│  │ {agent: "hephaestus", status: "forging",            │    │
│  │  combo: "chaos_x_fep_x_neural", gate: 3}           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Machine A agents ──── localhost:6379 ────── Machine A Redis
Machine B agents ──── machineA:6379 ────── Machine A Redis (remote)
```

### Why One Stream, Not Per-Agent Streams

With 12 agents, per-agent streams create 12+ streams to monitor. One stream with consumer groups is simpler:
- Every event goes to `prometheus:events`
- Each agent subscribes via a consumer group with an event type filter
- Pronoia subscribes to ALL events (constitutional guardian)
- Redis handles fan-out, persistence, and backpressure

A second stream `prometheus:health` carries lightweight heartbeats so Pronoia can detect dead agents.

---

## The Python Client: `lib/event_bus.py`

Every agent imports this. ~80 lines.

```python
"""
Prometheus Event Bus — Redis Streams wrapper.

Usage:
    from lib.event_bus import EventBus

    bus = EventBus(agent_name="hephaestus")

    # Publish
    bus.emit("tool_forged", {"name": "chaos_x_fep", "accuracy": 0.67})

    # Subscribe (blocking loop — run in thread or as main loop)
    for event in bus.listen(["tool_forged", "batch_complete"]):
        handle(event)

    # Health heartbeat
    bus.heartbeat({"status": "forging", "combo": "chaos_x_fep", "gate": 3})
"""

import json
import time
import redis
from datetime import datetime

REDIS_URL = os.environ.get("PROMETHEUS_REDIS_URL", "redis://localhost:6379")
EVENTS_STREAM = "prometheus:events"
HEALTH_STREAM = "prometheus:health"

class EventBus:
    def __init__(self, agent_name):
        self.agent = agent_name
        self.r = redis.from_url(REDIS_URL)
        self.group = agent_name
        # Create consumer group if not exists
        try:
            self.r.xgroup_create(EVENTS_STREAM, self.group, id="0", mkstream=True)
        except redis.ResponseError:
            pass  # Group already exists

    def emit(self, event_type, data=None):
        """Publish an event to the stream."""
        self.r.xadd(EVENTS_STREAM, {
            "agent": self.agent,
            "event": event_type,
            "data": json.dumps(data or {}),
            "timestamp": datetime.now().isoformat(),
        })

    def listen(self, event_types=None, timeout_ms=5000):
        """Yield events matching event_types. Blocking with timeout."""
        consumer = f"{self.agent}_worker"
        while True:
            entries = self.r.xreadgroup(
                self.group, consumer,
                {EVENTS_STREAM: ">"},
                count=10, block=timeout_ms
            )
            if not entries:
                continue
            for stream_name, messages in entries:
                for msg_id, fields in messages:
                    event = {
                        "id": msg_id,
                        "agent": fields.get(b"agent", b"").decode(),
                        "event": fields.get(b"event", b"").decode(),
                        "data": json.loads(fields.get(b"data", b"{}")),
                        "timestamp": fields.get(b"timestamp", b"").decode(),
                    }
                    if event_types is None or event["event"] in event_types:
                        yield event
                    # Acknowledge the message
                    self.r.xack(EVENTS_STREAM, self.group, msg_id)

    def heartbeat(self, status_data):
        """Publish a health heartbeat (trimmed stream, last 100 per agent)."""
        self.r.xadd(HEALTH_STREAM, {
            "agent": self.agent,
            "data": json.dumps(status_data),
            "timestamp": datetime.now().isoformat(),
        }, maxlen=1000)

    def get_health(self):
        """Read latest heartbeat from each agent."""
        entries = self.r.xrevrange(HEALTH_STREAM, count=100)
        latest = {}
        for msg_id, fields in entries:
            agent = fields.get(b"agent", b"").decode()
            if agent not in latest:
                latest[agent] = {
                    "data": json.loads(fields.get(b"data", b"{}")),
                    "timestamp": fields.get(b"timestamp", b"").decode(),
                    "msg_id": msg_id,
                }
        return latest
```

---

## Per-Agent Integration

### Graceful Degradation

Every agent wraps event bus calls in try/except. If Redis is down, the agent continues operating with file-based fallback. The event bus enhances coordination — it doesn't gate functionality.

```python
# Pattern for every agent:
try:
    from lib.event_bus import EventBus
    bus = EventBus("hephaestus")
except Exception:
    bus = None  # Redis unavailable, file-based fallback

def notify(event, data):
    if bus:
        bus.emit(event, data)
    # Always write to file regardless (existing behavior preserved)
    append_to_ledger(event, data)
```

### Eos (Machine A) — Publisher

```python
# After each paper found:
bus.emit("paper_found", {
    "title": paper.title,
    "arxiv_id": paper.arxiv_id,
    "url": paper.url,
    "relevance_score": score,
    "related_experiments": ["ignis_ejection", "rhea_1.5b"],
})
```

**Listens to:** Nothing. Pure publisher. Fire-and-forget scanner.

### Aletheia (Machine A) — Publisher + Subscriber

```python
# Listens for papers to extract:
for event in bus.listen(["paper_found", "tool_forged", "tool_scrapped",
                         "failure_found", "experiment_done", "corpus_verified"]):
    if event["event"] == "paper_found":
        extract_and_deposit(event["data"])
    elif event["event"] == "tool_forged":
        deposit_tool_entity(event["data"])
    elif event["event"] == "tool_scrapped":
        deposit_failure_entity(event["data"])
    elif event["event"] == "failure_found":
        deposit_failure_pattern(event["data"])
    elif event["event"] == "experiment_done":
        deposit_experiment_result(event["data"])
    elif event["event"] == "corpus_verified":
        deposit_verified_chain(event["data"])

    # After every deposit:
    bus.emit("entity_created", {"count": n_new, "types": types})
```

**This is the key change.** Aletheia becomes *reactive* — it doesn't poll for new data; it responds to events from every other agent. The substrate grows automatically because every agent's completion event triggers an Aletheia deposit.

### Nous (Machine B) — Publisher + Subscriber

```python
# Listens for substrate changes that affect concept pool:
for event in bus.listen(["entity_created", "gap_found", "coeus_rebuilt"]):
    if event["event"] == "entity_created":
        refresh_concept_pool()  # Pull new concepts from Aletheia
    elif event["event"] == "gap_found":
        prioritize_gap_concepts(event["data"])  # Target substrate holes
    elif event["event"] == "coeus_rebuilt":
        update_sampling_weights(event["data"])

# After each batch:
bus.emit("batch_complete", {
    "run_id": run_id,
    "n_combos": len(results),
    "top_score": max_score,
    "path": responses_path,
})
```

### Hephaestus (Machine B) — Publisher + Subscriber

```python
# Listens for new Nous batches:
for event in bus.listen(["batch_complete"]):
    new_combos = load_new_combos(event["data"]["path"])
    for combo in prioritize(new_combos):
        result = forge(combo)
        if result.passed:
            bus.emit("tool_forged", {
                "name": combo.key,
                "accuracy": result.accuracy,
                "calibration": result.calibration,
                "concepts": combo.concepts,
                "path": result.path,
            })
        else:
            bus.emit("tool_scrapped", {
                "name": combo.key,
                "reason": result.failure_reason,
                "concepts": combo.concepts,
            })
```

**Before:** Hephaestus polls Nous directories every 5 minutes.
**After:** Hephaestus reacts instantly when Nous finishes a batch.

### Nemesis (Machine B) — Publisher + Subscriber

```python
# Listens for new tools to attack:
for event in bus.listen(["tool_forged"]):
    tool = load_tool(event["data"]["path"])
    failures = run_adversarial(tool)
    for failure in failures:
        bus.emit("failure_found", {
            "tool": event["data"]["name"],
            "mutation_type": failure.mr,
            "task": failure.task,
            "failure_geometry": failure.details,
        })
```

**Before:** Nemesis reloads forge directory every 2 minutes.
**After:** Nemesis attacks each new tool within seconds of forging.

### Coeus (Machine B) — Publisher + Subscriber

```python
# Listens for forge results and failures:
for event in bus.listen(["tool_forged", "tool_scrapped", "failure_found"]):
    buffer.append(event)
    if len(buffer) >= 50:  # Rebuild every 50 events
        rebuild_causal_graphs(buffer)
        bus.emit("coeus_rebuilt", {
            "top_drivers": top_concepts,
            "new_synergies": synergies,
            "confounders": confounders,
        })
        buffer.clear()
```

### Ignis (Machine B — GPU) — Publisher

```python
# After every experiment:
bus.emit("experiment_done", {
    "type": "evolution",  # or "eval_v2", "logit_lens", "decomposition"
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "layer": 22,
    "sr": 0.633,
    "es": 0.733,
    "flipped": 8,
    "broken": 3,
    "genome_path": "results/batch4_followup/stage3_lora_L22/best_multilayer_genome.pt",
})

# Heartbeat during long runs:
bus.heartbeat({
    "status": "evolving",
    "experiment": "evolve_L22_gate_v",
    "generation": 340,
    "best_fitness": 29.137,
    "eta_minutes": 45,
})
```

### Rhea (Machine B — GPU) — Publisher

```python
# After evolution:
bus.emit("evolution_done", {
    "model": model_name,
    "sr": survival_rate,
    "metacognition": meta_score,
    "genome_path": genome_path,
})

# After self-corpus verification:
bus.emit("corpus_verified", {
    "n_chains": len(verified),
    "accuracy": accuracy,
    "model": model_name,
    "path": corpus_path,
})
```

### Pronoia (Machine A — Guardian) — Subscriber to ALL

```python
# Pronoia listens to EVERYTHING:
for event in bus.listen():  # No filter — constitutional guardian sees all
    # Track pillar activity
    update_pillar_health(event)

    # Constitutional checks
    if event["event"] == "tool_forged":
        substrate_deposit_expected("hephaestus", event)
    if event["event"] == "experiment_done":
        substrate_deposit_expected("ignis", event)

    # Check if substrate deposit followed within 60 seconds
    # If not: constitutional violation

    # Periodic checks (every N events)
    if event_count % 100 == 0:
        health = get_substrate_health()
        if health_below_threshold(health):
            bus.emit("gate_blocked", {"reason": "substrate_starvation", "health": health})

    # Agent liveness (check heartbeats)
    agent_health = bus.get_health()
    for agent, status in agent_health.items():
        if age(status["timestamp"]) > timedelta(hours=2):
            bus.emit("violation", {"type": "agent_dead", "agent": agent})
```

### Hermes (Machine A — Reporter) — Subscriber

```python
# Listens for alerts and compiles digest:
for event in bus.listen(["gate_blocked", "violation", "brief_ready"]):
    digest_buffer.append(event)
    if time_to_send():
        send_digest(digest_buffer)
        digest_buffer.clear()
```

---

## What This Replaces

| Current Mechanism | Replaced By | Latency Change |
|-------------------|-------------|---------------|
| Hephaestus polls Nous dir every 5 min | `batch_complete` event | 5 min → instant |
| Nemesis reloads forge/ every 2 min | `tool_forged` event | 2 min → instant |
| Coeus triggered every 50 forges (counted manually) | 50-event buffer on stream | Manual → automatic |
| rsync every 5 min for cross-machine files | Events cross machines natively via Redis | 5 min → instant |
| Pronoia checks substrate health on timer | Pronoia monitors all events in real-time | Timer → continuous |
| James reads output directories to see what happened | Hermes digest includes all events | Manual → email |

**Files still matter.** Redis carries *notifications*. The actual data (forge tools, genomes, knowledge_graph.db) stays in files. An event says "I forged a tool at path X" — the consumer reads path X. Redis is the nervous system; the filesystem is the body.

---

## Redis Setup

### Machine A (hosts Redis)

```bash
# Install
sudo apt install redis-server  # Linux
# or: brew install redis  # Mac
# or: choco install redis  # Windows (via Memurai or WSL)

# Config for remote access from Machine B
# /etc/redis/redis.conf:
bind 0.0.0.0
protected-mode no  # or use requirepass
maxmemory 256mb
maxmemory-policy allkeys-lru

# Start
sudo systemctl start redis
```

### Machine B (connects remotely)

```bash
# Set environment variable:
export PROMETHEUS_REDIS_URL="redis://machineA_ip:6379"
```

### Stream Maintenance

```bash
# Trim events older than 7 days (run weekly via cron):
redis-cli XTRIM prometheus:events MINID ~(7_days_ago_id)

# Monitor stream length:
redis-cli XLEN prometheus:events
redis-cli XLEN prometheus:health
```

### Memory Budget

Redis Streams are efficient. 10,000 events ≈ 5-10MB. At ~200 events/day (12 agents), 7 days of history = ~1,400 events = ~1MB. Set maxmemory to 256MB and never think about it again.

---

## What This Enables Next

### Phase 1 (now): Event notifications
Agents publish events. Other agents react. Pronoia monitors everything. Latency drops from minutes to milliseconds.

### Phase 2 (future): Distributed task queues
Redis Streams can also serve as work queues. Instead of Hephaestus polling for work, Pronoia can push prioritized forge tasks:
```python
bus.emit("forge_task", {"combo_key": "chaos_x_fep_x_neural", "priority": 0.95})
```
Hephaestus reads from its consumer group and processes in priority order.

### Phase 3 (future): Multi-worker scaling
Consumer groups support multiple workers. When James gets a second GPU:
```
Machine C joins consumer group "ignis"
→ Ignis experiments are automatically load-balanced across B and C
→ No code changes needed — Redis handles distribution
```

### Phase 4 (future): Agent SDK integration
Claude Code Agent SDK can publish/subscribe to the same Redis streams. An autonomous Athena CLI instance becomes just another consumer in the `pronoia` consumer group — it reads all events and makes decisions about what to run next.

---

## Migration Path (No Big Bang)

**Week 1:** Install Redis on Machine A. Deploy `lib/event_bus.py`. Add `bus.emit()` to Hephaestus and Nemesis (the tightest loop). Keep file-based fallback.

**Week 2:** Add subscribers to Aletheia (react to `tool_forged`, `tool_scrapped`). Add Pronoia constitutional monitoring. Substrate deposits become event-driven.

**Week 3:** Add Ignis/Rhea publishers. Add Nous subscriber (react to `entity_created`, `coeus_rebuilt`). The full loop closes.

**Week 4:** Remove rsync polling. Remove file-based polling loops from Hephaestus and Nemesis. Events are now the primary coordination mechanism. Files are storage, not communication.

Each week is additive. Nothing breaks. The event bus enhances; it doesn't replace. If Redis goes down, agents fall back to file-based polling automatically.

---

## The Constitutional Connection

Redis Streams make the Constitution enforceable in real-time:

- **Law 1 (Substrate is product):** Pronoia watches all events. If `tool_forged` is not followed by `entity_created` within 60 seconds, it's a violation.
- **Law 3 (Every agent feeds substrate):** Every agent's completion event is tracked. An agent that emits work events but never triggers `entity_created` is violating Law 3.
- **Law 4 (Parallel):** Pronoia tracks events per pillar per hour. If substrate pillar goes dark while reasoning pillar is active, it triggers the gate.
- **Law 5 (Novelty):** Pronoia tracks `tool_forged` events and computes AST similarity in real-time. Monoculture alert if similarity exceeds threshold.

The event bus IS the constitutional enforcement mechanism. Not a separate audit — a live, continuous, real-time constitutional monitor.
