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

### Hour 2 — 2026-05-24 05:00 EDT

**Pronoia 04:49 cycle: clean end-to-end.** First post-orchestration-logging cycle to show all timing data:
- cycle_started 04:48:31 → cycle_complete 04:49:13 (42.1s total)
- portfolio_refresh 27.8s · brief_generated 2.5s · dashboard_pushed 9.4s · email_dispatched 2.0s
- Metis fast (2.5s) — no Nemotron fallthrough this cycle

**Healthcheck**: fired 04:56:48 on schedule. M4 CPU 3.0%, mem 31.5%, disk unchanged.

**machine_probes**: 234 rows last hour, ~58-59 per machine (1/min as designed). Per-machine current state:

| Machine | CPU | Mem | Disk | GPU VRAM | Mem delta vs hour 1 |
|---|---|---|---|---|---|
| M1 | 14.3% | **62.1%** | 31.5% | 5.1% | **+5.5pp** (was 56.6%) |
| M2 | 9.3% | 37.2% | 7.0% | 74.0% | +2.4pp |
| M3 | 26.0% | 24.7% | 59.9% | 5.2% | +0.3pp |
| M4 | 1.6% | 31.3% | 17.2% | 0.0% | +0.8pp |

**New observations:**
- **M1 memory climbing** — 56.6% → 62.1% in 60 min. If sustained, could matter (M1 hosts Postgres + Redis + Pythia). Watch.
- **M3 disk unchanged** at 59.9% — not climbing as I worried last hour.

**Failures last 70min: 8** — all from Atalanta and Pheme self-audit alarms (50+/51+ consecutive null ticks). Sample:
- `atalanta_upstream_not_found`: "Apollo runs root not found; checked F:\Prometheus\apollo\runs, F:\Prometheus\apollo\runs_v2…"
- `pheme_upstream_not_found`: "Ergon eval root not found; checked F:\Prometheus\ergon\learner\evals…"
- Both also firing `*_self_audit_null` alarms

These are real signals — Atalanta (Aporia tool) and Pheme (Ergon tool) need their upstream paths wired (`APOLLO_RUN_ROOTS`, `EVAL_ROOTS` env vars). Per the 2026-05-21 roster doc they were already flagged as "upstream_not_found pending wiring." Still pending.

**Candidate issues added:**
- [ ] **Atalanta/Pheme upstream wiring overdue** — both tools have been alarming for days. Worth a paste-prompt for Aporia and Ergon to set the env vars and restart.
- [ ] **M1 memory growth rate watch** — if M1 mem goes from 56→62 each hour, it'll OOM in ~5 hours. Probably just Postgres warming caches but worth tracking.

### Hour 3 — 2026-05-24 06:03 EDT — **M1 MEMORY ESCALATION**

**Pipeline status:** daemons alive (intel_loop 25h uptime, probe 175min). No Pronoia cycle this hour (next at 08:49).

**⚠ M1 memory escalating fast.** Trajectory from machine_probes:
- 02:55 baseline: 56.6%
- 04:00 hour 1: 56.6% (flat)
- 05:00 hour 2: 62.1% (+5.5pp/hr)
- 05:51: 63.7%
- 05:55: 71.2% (**+7.5pp in 4 min**)
- 05:58: 71.9%
- 06:01: 80.8% (**+9.6pp in 6 min**)
- 06:03 now: **82.1%** (25.9 / 31.6 GB used)

If the rate of the last 10 minutes sustains (~3pp/min), M1 hits OOM in ~6 minutes. Most likely cause: a specific process loaded a large dataset (Pythia DR batch? Postgres VACUUM? Theseus batch?) — not a steady leak. The big jump from 71→81% in 6 min is the tell.

**M1 OOMing would take down Postgres + Redis, which would block the entire orchestration** (Pronoia would lose dual-write, Pythia would lose its queue table, all `log_work` events would be lost). Worth investigating *now* if you can — `ssh skullport` and look at top processes.

**M2 GPU VRAM dropped 74% → 3.6%.** Apollo's evolutionary search appears to have stopped or paused. M2 looks idle (CPU 1.6%, mem 24.4%). Worth checking — might be a graceful generation rollover, might be a crash.

**Other machines: stable.**
| Machine | CPU | Mem | Disk | GPU VRAM |
|---|---|---|---|---|
| M1 | 13.6% | **82.1%** ⚠ | 31.6% | 5.1% |
| M2 | 1.6% | 24.4% | 7.0% | 3.6% ↓ (was 74%) |
| M3 | 25.0% | 24.6% | 59.9% | 5.2% |
| M4 | 8.0% | 31.1% | 17.2% | 0.0% |

**Healthcheck**: 05:56 fire OK, next at 06:56.

**Failures this hour: 8** — same Atalanta + Pheme upstream_not_found alarms. Counts ticked from 50-51 → 52-53 (consistent, not escalating).

**Candidate issues added:**
- [ ] **CRITICAL: machine_probe top-N-procs**: probe should capture top processes by memory so we can identify what's eating M1's RAM without ssh-ing into the machine. This was the gap I felt immediately when M1 spiked.
- [ ] **Threshold-based PushNotification**: M1 mem at 82% should have alerted James in real-time, not wait for the 08:49 email. Add a "soft alarm" rule that fires `success=False` `machine_health_alarm` events at 80% threshold.
- [ ] **Apollo M2 idle-status detection**: GPU VRAM dropping from 74→3.6% in one cycle is either a graceful generation end or a crash. Need to disambiguate via Apollo's heartbeat key_metrics (last cycle ago, last fitness).

### Hour 4 — 2026-05-24 06:36 EDT (accelerated 30-min check)

**M1 memory RECOVERED — was a transient.** Postgres + Redis still reachable; M1 mem dropped from 82.1% (06:03) to 52.6% (06:35). Rock-flat at 52.5% for the last 15 minutes. Most likely cause was a Postgres VACUUM or a Pythia DR query that briefly loaded a large result set, then released. Not a leak — the memory was returned cleanly. **False alarm averted.**

**Lesson captured for the roadmap**: my 30-min response cadence caught the recovery, but a real OOM would have been faster than 30 min. The orchestration needs threshold-based real-time alerts at 90%/95%, not polling.

**M2 Apollo still idle.** GPU VRAM = 3.6% util = 0%, CPU near zero for 10+ consecutive minutes. This is sustained, not transient. Apollo either:
- Finished a generation cycle and is waiting for the next trigger
- Crashed silently mid-run
- Was stopped by James

Apollo's own heartbeat (separate from probe) would resolve this, but Apollo uses its own dual-write thread, not session_telemetry, so it doesn't show on the per-machine probe pulse. Need to cross-reference Apollo's `agora.agent_heartbeats` row.

**Probes still flowing**: M1 59, M2 59, M3 58, M4 58 per hour. Cadence consistent.

**Latest snapshot per machine:**
| Machine | CPU | Mem | Disk | GPU VRAM |
|---|---|---|---|---|
| M1 | 9.2% | 52.6% (recovered) | 31.4% | 5.1% |
| M2 | 1.1% | 24.4% | 7.0% | 3.6% (Apollo idle) |
| M3 | 25.0% | 25.1% | 60.0% | 5.2% |
| M4 | 1.2% | 31.2% | 17.2% | 0.0% |

**Failures last 35min: 4** — only Atalanta + Pheme (same as every cycle).

**Returning to hourly cadence for hour 5.**

**Candidate issues confirmed/added:**
- [x] **Threshold-based real-time alerts** (mem >90%, disk >90%, etc.) — was speculative last hour, confirmed essential this hour. A 30-min polling cadence is OK for monitoring but useless for OOM avoidance.
- [ ] **Apollo heartbeat cross-reference**: when M2 probe shows idle GPU, the brief should also query Apollo's agora.agent_heartbeats row to disambiguate "Apollo done with cycle" vs "Apollo crashed."

### Hour 5 — 2026-05-24 07:38 EDT

**Apollo is dead.** Apollo's `agora.agent_heartbeats` row shows `last_heartbeat` 9,444s (2h 38min) ago. Apollo's daemon-thread heartbeat is supposed to fire every 60s, so 2.5h silence = daemon process crashed or heartbeat thread died. This confirms what the M2 probe was showing earlier (GPU VRAM 74% → 3.6% sustained):

- Apollo's heartbeat: last update ~05:00 EDT
- M2 GPU dropped to 3.6% somewhere around the same time
- M2 has been at ~1% CPU / 24% mem ever since — machine itself is fine, just no Apollo workload

**This was discoverable from the existing data**, but only by cross-referencing Apollo's heartbeat with the M2 probe. Adding to roadmap: Metis should fire "Apollo heartbeat stale" as an Act-on-this item when Apollo's PG heartbeat is >10 min old.

**M1 memory: stable, healthy.** Hour range 32.3% to 55.1%, latest 43.2%. The 82% spike at hour 3 was definitively transient. No anomaly.

**M2 idle confirmed.** GPU VRAM 3.6% (sustained), util 0%, CPU 0.6%. M2 has been almost entirely idle for ~2.5h.

**Pronoia 08:49 cycle hasn't fired yet.** I misread my own monitoring prompt — next cycle is at 08:49 EDT (~1h from now), not by this hour. Will catch it at hour 6.

**Other observations:**
- Healthcheck-M4 fired at 06:56 on schedule (next 07:56)
- Daemons healthy: intel_loop 1611min uptime, probe 270min uptime
- Probes flowing from all 4 machines at ~58-59/hour

**Latest snapshot per machine:**
| Machine | CPU | Mem | Disk | GPU VRAM | Notes |
|---|---|---|---|---|---|
| M1 | 12.4% | 43.2% (recovered) | 31.5% | 5.1% | |
| M2 | 0.6% | 24.4% | 7.0% | 3.6% | **Apollo dead 2.5h** |
| M3 | 25.2% | 25.0% | 60.0% | 5.2% | |
| M4 | 3.9% | 31.5% | 17.2% | 0.0% | |

**Failures last 70min: 8** — same Atalanta/Pheme upstream-not-found pattern. No new alarm types.

**Candidate issues added:**
- [ ] **CRITICAL: Apollo down for 2.5h with no alert.** Apollo's heartbeat staleness should fire an Act-on-this anomaly in the next Metis brief (08:49 cycle). If it doesn't, the brief filter is missing the rule. Add: "any daemon-kind agent with heartbeat >10min stale = Act-on-this."
- [ ] **Apollo silent-crash detection**: Apollo's `key_metrics` (last `generation`, last `phase`) would tell us when it last advanced. If `gen_time_s` last update + 10 minutes < now, it crashed even if the heartbeat thread is somehow still firing.

### Hour 6 — 2026-05-24 08:40 EDT

**Pronoia 08:49 cycle hasn't fired yet** — wakeup landed 9 min early. Will be visible at hour 7. Same timing gap as hour 5's miss (I underestimated the offset).

**Apollo still dead, deteriorating.** Heartbeat now 13,157s (3.65h) stale, was 2.62h at hour 5. Climbing at ~1h per monitoring cycle (i.e., heartbeat write never resumed). Row `status` field still says "online" because that's whatever the last `write_heartbeat` set — `status` is a snapshot field, not a derived one. Real liveness has to come from `last_heartbeat` age, not the `status` column.

**M2 still flatlined** — GPU vram 3.6%, util 0%, CPU 0.7%. No recovery.

**Daemons alive**: intel_loop 27.9h uptime, probe 5.5h uptime.

**Failures last 70min: 12** — Atalanta + Pheme alarms still pinging every ~25 min (3 of each in 70min vs 2 of each at hour 5; small uptick consistent with both tools self-auditing more frequently as their null counts grow).

**Latest snapshot per machine:**
| Machine | CPU | Mem | Disk | GPU VRAM |
|---|---|---|---|---|
| M1 | 11.9% | 42.7% | 31.5% | 5.1% |
| M2 | 0.7% | 24.5% | 7.0% | 3.6% (Apollo dead) |
| M3 | 25.0% | 25.4% | 60.0% | 5.2% |
| M4 | 3.7% | 31.6% | 17.2% | 0.0% |

**Candidate issues confirmed/added:**
- [ ] **Pronoia status field is misleading**: when the dual-write heartbeat thread crashes, the row's `status` field stays at whatever was last written. Either change `status` to a derived field (compute from `last_heartbeat` age) OR add a separate background process that flips agents to "stale" when their PG heartbeat is too old.
- [ ] **Monitoring wakeup phase-alignment**: my hourly wakeups are landing 9 min before the Pronoia cycle each time. The fix is trivial (offset by 10 min) but it's a real lesson — when polling a periodic event, align the poll to fire AFTER the expected event, not before.
- [ ] **Apollo deathwatch**: 3.7h crashed, no auto-restart, no alert from Metis (next brief at 08:49 will be the test). Apollo needs a watchdog like the intelligence_loop has.

### Hour 7 — 2026-05-24 09:32 EDT — **APOLLO FLAGGED CORRECTLY**

**08:49 cycle: clean.** Cycle d79f8af1 completed in 34.4s. All 6 events ok. Metis was fast (1.5s — Cerebras or Groq succeeded, no Nemotron fallthrough).

**Metis brief flagged Apollo in Act-on-this**, in the new format I wired:
> "**Apollo (M2, supervised by Harmonia, evolutionary engine) has been DEAD for 13,662s (~3.8 hours)**
> Heartbeat last seen 13,662s ago; agent unresponsive despite M2 confirmed online and Apollo previously running.
> Investigate Apollo process state on M2 and restart under Harmonia's supervision."

This is the orchestration working as designed — the 3.8h-stale heartbeat triggered an anomaly, the new format surfaced the supervisor + role, and James gets an actionable Act-on-this item in the email.

**Apollo current status**: heartbeat 4.52h stale, still climbing. Crash confirmed. No auto-restart.

**Pythia DR utilization flagged in Watch-this**: "No Deep Research dispatched in last 8h — 15 of 20 daily tokens remaining". Real signal — Aporia's queue may be empty.

**Brief quality issues caught:**

1. **Calliope falsely flagged as DEAD** — "Calliope (M4, daily NotebookLM narrative synthesizer) has been DEAD for 462,478s (~5.3 days)." Calliope is invoke-on-demand (not a daemon); DEAD between runs is normal. Metis is applying the daemon-DEAD rule to tools. Needs a `kind=tool AND invoke_on_demand=true` exclusion.

2. **Apollo `supervised by Harmonia` attribution may be wrong.** Apollo is `kind=daemon` with no operator field in EXPECTED_AGENTS. Metis hallucinated the supervisor — either because Apollo and Harmonia both live on M2, or because the manual_status doc mentions Harmonia. Either way, daemons without an operator should be reported as unsupervised (or with "no supervisor" explicitly), not assigned to whoever else lives nearby.

**Daemons alive**: intel_loop 27.9h, probe 5.5h.

**Failures last 60min: 8** — same Atalanta/Pheme pattern, no new alarm types.

**Latest snapshot per machine:**
| Machine | CPU | Mem | Disk | GPU VRAM |
|---|---|---|---|---|
| M1 | 8.0% | 35.7% | 31.6% | 5.1% |
| M2 | 0.1% | 24.6% | 7.0% | 3.6% (Apollo dead 4.5h) |
| M3 | 25.0% | 25.2% | 60.0% | 5.2% |
| M4 | 0.2% | 31.8% | 17.2% | 0.0% |

**Candidate issues confirmed/added:**
- [x] **Outage-line format** (supervisor + role) — confirmed working end-to-end. Move from "candidate" to "shipped" in the final roadmap.
- [ ] **Invoke-on-demand tool exclusion**: brief should not flag DEAD on kind=tool agents whose `current_op` says "(no postgres heartbeat — see manual_status)" or which are known invoke-on-demand. Calliope is the canonical example.
- [ ] **Supervisor field strict-mode**: when EXPECTED_AGENTS has no `operator` field for an agent, the brief should say "no supervisor" rather than hallucinating one (e.g., "Apollo supervised by Harmonia" — Harmonia doesn't supervise Apollo).

### Hour 8 — 2026-05-24 10:34 EDT — quiet hour

**Apollo: 5.55h stale, no recovery.** Climbing exactly 1h per monitoring cycle = heartbeat thread definitively dead, no auto-restart mechanism. Will be ~7h stale by the next 12:49 cycle when Metis will re-flag it.

**Daemons alive**: intel_loop 29.8h uptime, probe 7.4h uptime.

**Healthcheck**: 09:56 fired on schedule. Next 10:56 (post-wakeup).

**Failures: 8** — identical pattern to every hour (2 each of pheme_self_audit_null, pheme_upstream_not_found, atalanta_self_audit_null, atalanta_upstream_not_found). **No new stage types.** The drumbeat is reliable.

**Probes**: 235 rows last hour (~59/machine — perfect cadence). M1 GPU showed 8% util this hour (mild activity); M2/M4 idle GPU; M3 unchanged.

**Latest snapshot per machine:**
| Machine | CPU | Mem | Disk | GPU VRAM | GPU util |
|---|---|---|---|---|---|
| M1 | 15.5% | 44.0% | 31.5% | 5.1% | 8.0% |
| M2 | 0.4% | 24.4% | 7.0% | 3.6% | 0.0% (Apollo dead) |
| M3 | 25.2% | 25.3% | 60.0% | 5.2% | 0.0% |
| M4 | 0.4% | 32.0% | 17.2% | 0.0% | 0.0% |

**No new candidate issues** — this hour is confirmation that the steady-state pipeline is stable (Pronoia firing every 4h on schedule, probes flowing, healthchecks firing) and the only outstanding problem is Apollo-down (already on the roadmap).

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
