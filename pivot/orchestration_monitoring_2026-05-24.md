# Orchestration & Intelligence Pipeline — 12h Monitoring Log

**Started:** 2026-05-24 02:55 EDT
**Window:** 12 hours (cycle through ~14:55 EDT)
**Cadence:** hourly wakeup, observations accumulated, roadmap synthesized at end

---

## Baseline (hour 0 — 2026-05-24 02:55 EDT)

**Intelligence pipeline daemon (Pronoia)**
- PID 17396, alive since 2026-05-23 04:47 EDT (~22h uptime)
- Memory: 35.8 MB, CPU: trivial
- 3 cycles in last 12h, all OK (monitor+metis+push+email all succeeded each time)
- Cycle durations: 32s, 39.9s, 145.7s (Nemotron-slow on the 3rd)
- 6 email_dispatched events (3 pairs from pronoia_+self-report)
- Cycle cadence anchored 4h apart: 16:50, 20:49, 00:49

**M4 resources** (fresh snapshot)
- CPU 10.9% · Memory 30.2% used (9.6/31.9 GB) · 22.2 GB free
- Disk C: 17.2% used (789 GB free) · E: 11.5% used (843 GB free)
- Uptime 267 hours (~11 days)
- Top python: only intelligence_loop (37 MB)
- **All headroom green** — no thresholds approached

**Orchestration tier**
- 311 total intelligence_outputs events in last 12h (includes swarm ticks)
- Watchdog scheduled task PrometheusIntelligenceWatchdog firing 30-min cadence
- HealthCheck-M4 task PrometheusHealthCheckM4 just registered, fired once, hourly cadence

**Known issues (carry-over)**
- LLM cascade frequently falls through to Nemotron (Cerebras 429, Groq 413, NVIDIA 502, DeepSeek 402 reported earlier in week) — Nemotron's chain-of-thought leak triggers the deterministic fallback. Brief quality degraded vs full cascade.
- Personas (Aporia, Techne) intentionally have no PG heartbeat — their idle status is normal, not an outage.

---

## Hourly observations

(populated as wakeups fire — each entry is short: deltas from baseline, anomalies, candidate fixes/enhancements)

### Hour 1 — 2026-05-24 04:00 EDT

**Pipeline status:** intelligence_loop PID 17396 alive (5d22h uptime). Watchdog healthy. Last cycle 00:49 EDT; next ~04:49 EDT.

**Healthcheck status:** PrometheusHealthCheckM4 scheduled task firing on schedule (last 03:56:48, next 04:56:45, no missed runs, exit code 0).

**Major positive surprise — machine_probe deployed to all 4 machines.** James (or the personas) ran the paste-ready prompt. In the last 2 hours `agora.machine_probes` accumulated:

| Machine | Probes/2h | Latest CPU | Latest Mem | Latest Disk | Latest GPU VRAM |
|---|---|---|---|---|---|
| M1 | 36 | 14.1% | 56.6% | 31.5% | 5.1% |
| M2 | 33 | 7.9% | 34.8% | 7.0% | **74.0%** (Apollo active) |
| M3 | 39 | 25.2% | 24.4% | **59.9%** (highest) | 5.2% |
| M4 | 92 | 6.1% | 30.5% | 17.2% | 0.0% |

**Observations:**
- M2 GPU VRAM at 74% — Apollo's evolutionary search actively using GPU. Healthy signal.
- M3 disk at 59.9% used (free space declining as forge accumulates substrate?). Worth tracking trend over the 12h window.
- M1 memory at 56.6% — moderate but expected with Postgres + Redis + Pythia.

**Issue caught + fixed mid-cycle**: at hour 1 wakeup, found **two** machine_probe processes running on M4 (PID 14236 from manual launch, PID 6460 from scheduled task). The IgnoreNew flag only tracks instances the scheduler itself started, not manually-spawned ones. Killed PID 14236 (manually-launched). Adds candidate-issue: probe daemon should self-detect and refuse to start if another instance is already running (lockfile pattern).

**Failures/anomalies:** none.

**Pronoia cycles this hour:** 0 (expected; 4h cadence anchored at xx:49).

**Candidate issues added:**
- [ ] **machine_probe self-deduplication**: write a lockfile at startup; if present and the PID inside is alive, log + exit. Prevents double-daemons after manual launches collide with scheduler.
- [ ] **M3 disk trend monitoring**: when prom_disk_pct climbs >1% per day, surface in brief.

### Hour 2 — pending

### Hour 3 — pending

### Hour 4 — pending

### Hour 5 — pending

### Hour 6 — pending

### Hour 7 — pending

### Hour 8 — pending

### Hour 9 — pending

### Hour 10 — pending

### Hour 11 — pending

### Hour 12 — final synthesis + roadmap

---

## Running candidate-issues list

(items I think might be worth fixing/enhancing — accumulate during monitoring, prioritize at end)

- [ ] **LLM cascade reliability**: refill credits / rotate keys / add additional providers so Nemotron isn't the workhorse
- [ ] **HealthCheck deployment on M1/M2/M3**: same scheduled-task pattern, would let the brief surface resource issues across the swarm
- [ ] **Tool outage rule**: currently the deterministic fallback only flags DEAD daemons in Act-on-this. Tools that die between persona invocations are silently ignored. If a tool dies AND its persona is also stale, that's a real anomaly worth flagging.
- [ ] **Pronoia cycle 145s anomaly** (Nemotron slow): tracking variance in `last_cycle_duration_sec` would let the brief flag "cycle 4x slower than baseline" as a degradation signal
- [ ] **HealthCheck-M1..M3 registered as EXPECTED_AGENTS but not deployed yet**: they'll show MISSING on the dashboard. Either deploy or remove from EXPECTED_AGENTS until they're real.
