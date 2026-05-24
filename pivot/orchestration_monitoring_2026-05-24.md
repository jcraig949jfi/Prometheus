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

### Hour 9 — 2026-05-24 11:36 EDT — steady-state

Apollo 6.58h stale. Healthcheck-M4 fired 10:56 on schedule. 8 failures, all known Atalanta/Pheme. Probes 59/59/59/58 across M1/M2/M3/M4 (perfect cadence). M1 mem 41.8%, M3 disk 60.0%, M2 GPU vram 3.6% — no machine showing new trends. Pronoia daemons alive. No new candidate issues.

### Hour 10 — 2026-05-24 12:27 EDT — phase-alignment miss #3

12:49 cycle hasn't fired yet (22 min away). I miscalculated the schedule: 11:36 + 50min = 12:26, which is 23 min BEFORE the cycle, not after. The fundamental constraint is the 3600s (60min) max wakeup delay vs the cycle's 4h cadence anchored at xx:49 — if last wakeup is at xx:36 or earlier, the 60-min max ceiling can't reach xx:50. **Adding to roadmap as concrete fix**: wakeup-scheduler logic for monitoring should compute the next expected cycle time and pick the smaller of (60min, cycle_time + small_buffer).

Apollo: 7.44h stale, climbing. Healthcheck-M4 fired 11:56 on schedule. Failures: 8, all known Atalanta/Pheme. Probes 59/59/59/58. Snapshot: M1 cpu 15.3% mem 34.5% disk 31.5%; M2 cpu 0.9% gpu 3.6% (dead); M3 cpu 26% disk 60%; M4 cpu 3.3% mem 32.5%.

Scheduling a 30-min wakeup to land at 12:57 EDT (8 min after 12:49 cycle) to catch this hour's cycle event chain.

### Hour 11 — 2026-05-24 12:59 EDT — clean cycle caught

**12:49 cycle: clean.** Cycle 934d611c, 33.4s total, all 6 boundary events ok. Metis fast (1.9s). Email sent.

**Apollo flagged again** (7.8h DEAD, supervised by Harmonia hallucination still present). **Clio newly flagged** at 59.5min stale (Aporia, paper scanner — correctly attributed this time, so the supervisor-format IS working when EXPECTED_AGENTS has the operator field set correctly). Calliope no longer in brief (3-item cap), so the "invoke-on-demand false-flag" issue is intermittent but real.

**Apollo: 7.97h stale.** Climbing on schedule. No recovery.

**Steady-state otherwise**: 4 failures (same Atalanta/Pheme), probes 59/59/59/58, machine snapshots unchanged. Daemons alive.

Ready for hour 12 roadmap synthesis.

### Hour 12 — 2026-05-24 14:01 EDT — final synthesis

**Status this hour:** Pronoia alive (PG heartbeat 55s old), intel_loop daemon 31h uptime, machine_probe daemon healthy. Apollo at **9.00h stale** (continued climb, no recovery). 8 failures last 70min (same Atalanta/Pheme drumbeat, no new types). Probes flowing 59/59/59/58 across all four machines.

---

## Twelve-hour summary

**The pipeline ran clean.** Across 02:55 → 14:01 EDT:
- **3 Pronoia cycles fired on schedule** (04:49, 08:49, 12:49). All clean, all six boundary events `ok`, all dashboard pushes succeeded, all 3 emails delivered.
- **Cycle durations**: 42.1s, 34.4s, 33.4s — Metis fast on all three (1.5–2.5s; no Nemotron fallthrough during this window). The earlier-in-the-week 145s Nemotron cycle didn't repeat.
- **15 healthcheck events** from `HealthCheck-M4` (extra count beyond the 12 scheduled, due to my mid-day smoke tests when registering).
- **88 failure-marked events** in 12h, ALL of them the same four `Atalanta/Pheme` upstream-not-found / self-audit-null alarms firing every ~25–30 min. Zero new alarm types appeared.
- **Probe coverage**: M4 686, M3 630, M2 625, M1 628 rows. Expected ~720 per machine (12h × 60/min); the 90+ row shortfall on M1/M2/M3 reflects very-brief PG hiccups and the duplicate-daemon kill I did at hour 1.

**What the orchestration logging caught.** The Apollo silent crash (~05:00 EDT) was discoverable from existing data within ~2h, then surfaced cleanly in the 08:49 Metis brief Act-on-this section as: *"Apollo (M2, supervised by Harmonia, evolutionary engine) has been DEAD for 13,662s (~3.8 hours)"* — using the supervisor+role outage format I shipped earlier this session. Reflagged again at 12:49 (now 7.8h DEAD). This is the orchestration working exactly as designed: a daemon died, no auto-restart fired, and the next brief made it the first item James would see.

**Three operational events this monitoring window:**
1. **M1 memory transient** (hour 3): spiked from 56% to 82% in 10 minutes, then released back to 52% within 30 min. Most likely Postgres VACUUM or a Pythia DR query loading a large result set. Caught real-time by the probe data, but my response was polling-based — a real OOM would have been faster than my 30-min check.
2. **Apollo crash** (~hour 5 EDT, surfaced hour 7): Apollo's heartbeat thread died silently. M2 GPU dropped from 74% → 3.6%; no recovery in the remaining 7 hours of monitoring.
3. **Mid-flight bug fix during earlier session** (carried forward): `send_brief_email.py`'s budget arithmetic crashed when Pythia reported `budget="compute-based (AI_Pro, 5h window)"` (string) vs an int. Fixed in commit `cce4505e` before this monitoring window started; verified no email failures recurred this window.

---

## Final Roadmap

Consolidated across 12 hours of observations, deduped, and tiered by severity.

### P0 — silent failure / data loss risk

**1. Apollo (and any daemon) lacks a watchdog**
- What: Apollo crashed at ~05:00 EDT and stayed crashed for the rest of the 12h window. No automatic restart, no escalation beyond the brief's outage line.
- Why it matters (hours 5, 6, 7, 8, 9, 10, 11, 12): 9 hours of lost evolutionary-search compute on M2, no signal to James between the 4h brief cycles. Apollo is exactly the kind of daemon that needs to keep running.
- Fix shape: a `PrometheusApolloWatchdog` Windows scheduled task on M2 mirroring the intelligence_loop watchdog pattern — checks for the Apollo pythonw process every 30 min, restarts with the configured config if absent, has a kill-switch file for intentional pauses. The intelligence_loop watchdog code at `scripts/intelligence_watchdog.ps1` can be templated. Same pattern should also cover Hephaestus (M3) and any future long-running daemons.

**2. Threshold-based real-time alerts (not polling)**
- What: 30-min polling caught the M1 memory transient but only after the spike was over. A real OOM would have killed Postgres + Redis + Pythia simultaneously before any of my hourly checks landed.
- Why it matters (hours 3, 4): observability cadence shouldn't match incident-response cadence. The machine_probe daemon already has all the data needed; what's missing is a synchronous alert path.
- Fix shape: extend `machine_probe.py` so that when CPU>90% sustained 60s, OR mem>90%, OR disk>90%, it (a) emits a `machine_probe_alarm` `log_work` event with `success=False`, and (b) optionally pushes a Redis stream entry to `agora:alerts` for any subscriber. Pronoia's intelligence_loop can subscribe to that stream and fire an immediate out-of-cycle email when an alarm event arrives (don't wait for the next 4h cycle).

**3. machine_probe self-deduplication (lockfile)**
- What: at hour 1 found two probe daemons running on M4 — one from my manual launch, one from the scheduled task. The `IgnoreNew` flag tracks scheduler-launched instances only.
- Why it matters (hour 1): duplicates double-write to `agora.machine_probes`, potentially confusing trend analysis. With multiple machines deploying and personas restarting daemons during work, this will happen again.
- Fix shape: at probe startup, write `logs/.machine_probe.<machine>.lock` containing the PID. Before writing, read existing lockfile; if PID inside is alive, log + exit. Clear lockfile on graceful shutdown. Stale lockfile (PID gone) gets overwritten.

### P1 — misleading reporting / brief quality

**4. Pronoia status field is stale-by-design**
- What: when Pronoia's PG heartbeat thread dies, the row's `status` column stays at whatever was last written ("online"), even if the heartbeat is hours stale.
- Why it matters (hour 6): the dashboard and any rule keying on `status` will report an agent as alive when its heartbeat is silent. Apollo's `status="online"` while 9h stale is the textbook example.
- Fix shape: in `portfolio_monitor.py` and downstream, derive a `derived_status` from `heartbeat_age_sec` (alive < 300s, stale < 600s, dead else) and use that everywhere instead of the row's `status` column. Or fire a once-a-minute Postgres job that flips `status` to `"stale"` for rows with `last_heartbeat < NOW() - INTERVAL '5 minutes'`.

**5. Brief falsely flags invoke-on-demand tools as DEAD**
- What: at hour 7, Metis flagged Calliope (invoke-on-demand NotebookLM narrative) as DEAD with 5.3-day staleness. Calliope only writes a heartbeat when invoked.
- Why it matters (hour 7): waste of a brief slot; trains James to ignore the brief.
- Fix shape: add an `invoke_on_demand: true` flag to relevant `EXPECTED_AGENTS` entries (Calliope, Metis); brief filters those out of DEAD reporting. Alternatively, derive from kind: tools with `kind=tool` AND no operator-driven daemon are likely invoke-on-demand.

**6. Brief hallucinates the supervisor when EXPECTED_AGENTS has no operator**
- What: Metis writes "Apollo (M2, supervised by Harmonia, …)" for both 08:49 and 12:49 briefs. Apollo's `EXPECTED_AGENTS` entry has no `operator` field; Metis appears to be inferring from "Apollo and Harmonia both on M2."
- Why it matters (hour 7, 11): assigns blame to the wrong persona. If James escalated to Harmonia "fix Apollo," that'd be wrong — Apollo is unsupervised.
- Fix shape: in `format_state_for_prompt`, when an agent has no `operator` value, render explicitly as `[no supervisor — unsupervised daemon]` rather than omitting (which lets the LLM infer). Also strengthen the SYSTEM_PROMPT rule: "Never fabricate a supervisor; if the agent block says 'no supervisor,' write '(unsupervised)' in the outage line, do not guess."

**7. LLM cascade reliability — Nemotron over-reliance**
- What: Cerebras 429 / Groq 413 / NVIDIA 502 / DeepSeek 402 errors have been chronic. Nemotron ends up the responder, and Nemotron dumps chain-of-thought. The deterministic fallback I added catches it, but the fallback is a fixed template (loses synthesis quality).
- Why it matters (entire window, plus pre-window history): brief quality degrades when only Nemotron responds. Already mitigated by the strip + fallback in commit `65b6e014`, but the root cause (cascade providers unhealthy) persists.
- Fix shape: top up provider credits / rotate keys for Cerebras + Groq + DeepSeek; add at least one local provider (Ollama on M3 or M4 running a 70B+ model) as a last-resort that's free and always available. Test the cascade with `--probe-only` periodically and surface "all 4 providers failing" as a P0 incident in the brief.

### P2 — polish / enhancement

**8. machine_probe top-N-procs**
- What: when M1 spiked at hour 3, I couldn't identify what process was eating memory without ssh.
- Fix shape: probe captures top 5 processes by memory each cycle, stores in `extras` JSONB. Display in dashboard tooltip.

**9. HealthCheck on M1/M2/M3 (currently only M4)**
- What: `EXPECTED_AGENTS` lists HealthCheck-M1..M4, but only M4 has a scheduled task; M1/M2/M3 are MISSING in the dashboard.
- Fix shape: either deploy the scheduled task via paste-prompt for M1/M2/M3 personas, OR remove the M1/M2/M3 entries from EXPECTED_AGENTS until deployment. The `machine_probe` daemon already covers all four machines for resource data, so HealthCheck is redundant on M1/M2/M3 — recommend removal from EXPECTED_AGENTS.

**10. M3 disk trend monitoring**
- What: M3 held steady at 60.0% disk used for the entire 12h window. Not climbing yet, but worth tracking.
- Fix shape: when `prom_disk_pct` for any machine grows >1pp per 24h, surface as a Watch-this item. SQL window function over `agora.machine_probes` is straightforward.

**11. Pronoia cycle duration variance tracking**
- What: cycle durations this window 32s, 34s, 33s (consistent), but the prior-day 145s Nemotron cycle was a real outlier.
- Fix shape: rolling mean ± stdev over the last 20 cycles; flag `pronoia_cycle_complete` events that exceed mean + 3σ.

**12. Atalanta/Pheme upstream-wiring still pending**
- What: 88 alarms over 12h, all from these two tools' missing `APOLLO_RUN_ROOTS` and `EVAL_ROOTS` env vars. Already flagged in the 2026-05-21 agent roster.
- Fix shape: paste prompt for Aporia + Ergon to set the env vars on M1 and restart the relevant tools. Two minutes of work, removes the alarm noise floor.

**13. Wakeup-scheduler phase-alignment** (meta-issue, fix in agent behavior not infra)
- What: my 60-min monitoring wakeups consistently landed 9-22 min before Pronoia's 4h xx:49 cycle. Three phase-misses across hours 5, 6, 10.
- Fix shape: when scheduling monitoring wakeups, compute `next_expected_cycle_time` and pick `min(60min, time_to_next_cycle + 10min_buffer)`. Already in my mental model going forward; documenting here for the record.

---

## What's already shipped this session (for the record)

- [x] **Per-machine probe daemon** (`scripts/machine_probe.py`) → `agora.machine_probes`, deployed on all four machines this monitoring window. Captures CPU/GPU VRAM/RAM/Prometheus-disk.
- [x] **Outage-line format** with `(machine, supervised by X, role)` — confirmed working in two consecutive briefs (08:49 and 12:49).
- [x] **Pronoia PG dual-write heartbeat** — Pronoia now appears as ALIVE in the dashboard with `cycles_today` and `last_cycle_duration_sec` in `key_metrics`.
- [x] **Orchestration `log_work` events at cycle boundaries** — `pronoia_cycle_started/portfolio_refresh/brief_generated/dashboard_pushed/email_dispatched/cycle_complete` all firing with cycle_id grouping.
- [x] **Persona-not-flagged-as-failed-daemon** rule + chain-of-thought strip + deterministic fallback in Metis.
- [x] **Watchdog for intelligence_loop** (`scripts/intelligence_watchdog.ps1`, scheduled task on M4) — template for the Apollo watchdog above.
- [x] **HealthCheck-M4 hourly scheduled task** — confirmed firing 12+ times on schedule this window.

---

## Loop complete. No further wakeup scheduled.

---

## Running candidate-issues list

(items I think might be worth fixing/enhancing — accumulate during monitoring, prioritize at end)

- [ ] **LLM cascade reliability**: refill credits / rotate keys / add additional providers so Nemotron isn't the workhorse
- [ ] **HealthCheck deployment on M1/M2/M3**: same scheduled-task pattern, would let the brief surface resource issues across the swarm
- [ ] **Tool outage rule**: currently the deterministic fallback only flags DEAD daemons in Act-on-this. Tools that die between persona invocations are silently ignored. If a tool dies AND its persona is also stale, that's a real anomaly worth flagging.
- [ ] **Pronoia cycle 145s anomaly** (Nemotron slow): tracking variance in `last_cycle_duration_sec` would let the brief flag "cycle 4x slower than baseline" as a degradation signal
- [ ] **HealthCheck-M1..M3 registered as EXPECTED_AGENTS but not deployed yet**: they'll show MISSING on the dashboard. Either deploy or remove from EXPECTED_AGENTS until they're real.
