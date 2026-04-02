# Pipeline Health Monitoring Scripts

Three Python scripts for monitoring the Prometheus pipelines. Use these to check on pipeline status when requested.

---

## Overview

| Script | Purpose | Monitors |
|--------|---------|----------|
| `check_intelligence_pipeline.py` | Intelligence pipeline health | Pronoia → Eos → Aletheia → Skopos → Metis → Clymene → Hermes |
| `check_forge_pipeline.py` | Forge pipeline health + backlog | Nous → Hephaestus → Nemesis |
| `health_dashboard.py` | Combined dashboard | Both pipelines at once |

---

## 1. Check Intelligence Pipeline

**Location:** `scripts/check_intelligence_pipeline.py` (11.5 KB)

**Monitors:** Pronoia → Eos → Aletheia → Skopos → Metis → Clymene → Hermes

### Features

- ✓ Checks if each agent process is running
- ✓ Analyzes 2-hour log history for each agent
- ✓ Detects errors and warnings in logs
- ✓ Verifies output files (reports, briefs, digests)
- ✓ **Tracks NVIDIA API health** — timeouts, failures, retries (Eos + Aletheia)
- ✓ Generates detailed markdown health report

### Usage

```bash
# Print report to stdout
python scripts/check_intelligence_pipeline.py

# Save report to file
python scripts/check_intelligence_pipeline.py --output report.md
```

### Output Format

```
# Intelligence Pipeline Health Report
*Generated: 2026-04-01 12:00:00 UTC*

## Overall Status
[HEALTHY] — 7/7 agents healthy

## Agent Status Table
| Agent | Status | Logs | Errors | Last Activity |
|-------|--------|------|--------|------------------|
| PRONOIA | [OK] HEALTHY | 150 lines | — | 2026-04-01 11:50:23,456 |
| EOS | [OK] HEALTHY | 480 lines | — | 2026-04-01 11:59:45,123 |
...

## API Health (past 2 hours)
- API Timeouts: 2 events
- Retry Attempts: 0 events
- API Failures: 4 events

## Detailed Status
[Per-agent breakdown with recent logs and metrics]
```

### Status Indicators

- `[OK] HEALTHY` — Agent running, no errors, active logs
- `[WARN] DEGRADED` — Agent running but with warnings or reduced activity
- `[ERROR] CRITICAL` — Errors detected in logs or process not running
- `[IDLE]` — No recent activity but no errors

### What to Look For

**Healthy signs:**
- All agents show `[OK] HEALTHY`
- Regular [INFO] messages in logs
- Active API calls and data processing
- Consistent timestamps (no gaps > 10 minutes)

**Warning signs:**
- `[WARN] DEGRADED` status
- API timeouts or failures
- Extended periods without log activity
- Process not running

**Critical issues:**
- `[ERROR] CRITICAL` status
- Repeated API failures
- Database connection errors
- Uncaught exceptions in logs

---

## 2. Check Forge Pipeline

**Location:** `scripts/check_forge_pipeline.py` (14.2 KB)

**Monitors:** Nous → Hephaestus → Nemesis

### Features

- ✓ Checks if each agent process is running
- ✓ Analyzes 2-hour log history for each agent
- ✓ Counts forge attempts, passes, API failures (from Hephaestus ledger)
- ✓ Tracks Nemesis adversarial grid coverage (cells filled)
- ✓ **Monitors Nous response backlog** — unprocessed responses awaiting Hephaestus
- ✓ **Tracks NVIDIA API issues** — timeouts, failures, retry rates across Nous + Hephaestus
- ✓ Auto-alerts when backlog grows or API timeouts spike
- ✓ Generates detailed markdown health report

### Usage

```bash
# Print report to stdout
python scripts/check_forge_pipeline.py

# Save report to file
python scripts/check_forge_pipeline.py --output forge_report.md
```

### Output Format

```
# Forge Pipeline Health Report
*Generated: 2026-04-01 12:00:00 UTC*

## Overall Status
[CRITICAL] — 2/3 agents healthy

## Pipeline Backlog & Load
- **Nous Response Queue**: 1234 unprocessed responses
  - Latest run: 20260331_190000
- **API Timeouts (past 2h)**: 28 timeout events
  - Nous: 14 timeouts, 48 retries
  - Hephaestus: 14 timeouts, 0 retries
  - **ALERT**: High retry rate indicates API degradation

## Agent Status Table
| Agent | Status | Logs | Errors | Last Activity |
|-------|--------|------|--------|------------------|
| NOUS | [OK] HEALTHY | 460 lines | — | 2026-04-01 12:05:13,456 |
| HEPHAESTUS | [ERROR] CRITICAL | 6638 lines | 1440 | 2026-04-01 11:45:33,764 |
| NEMESIS | [OK] HEALTHY | 27 lines | — | 2026-04-01 10:51:51,635 |

## Detailed Status
[Per-agent breakdown with forge stats, grid coverage, recent logs]
```

### Backlog Interpretation

The **Nous Response Queue** shows how many concepts are waiting to be forged:

- **Empty queue** = Hephaestus is keeping up with Nous (healthy ✓)
- **Growing queue** = Nous is generating faster than Hephaestus can forge (watch this ⚠)
- **Large queue (>500)** = Hephaestus is falling far behind; investigate or activate break-glass mode ⚠
- **Very large queue (>1000)** = Critical backlog; immediate intervention needed ✗

### API Timeout Interpretation

The script tracks NVIDIA API performance across Nous and Hephaestus:

```
API Timeouts (past 2h): 38 timeout events
  - Nous: 32 timeouts, 75 retries
  - Hephaestus: 6 timeouts, 0 retries
  - ALERT: High retry rate indicates API degradation
```

**What it means:**
- **Few/no timeouts** = API responding normally ✓
- **Timeouts without retries** = Temporary network blips ⚠
- **High timeout + high retry rate** = API degraded or overloaded; consider rate limiting ⚠
- **Sustained high failures** = Investigate NVIDIA API service status ✗

### Status Indicators

- `[OK] HEALTHY` — Agent running, no errors, active logs
- `[WARN] DEGRADED` — Running with warnings or reduced activity
- `[ERROR] CRITICAL` — Errors in logs or process not running
- `[ALERT]` — Backlog growing or API timeouts spiking

### What to Look For

**Healthy signs:**
- All agents show `[OK] HEALTHY`
- Nous Response Queue is empty or small (<100)
- Few or no API timeouts
- Regular forge/scrap activity in logs
- Nemesis grid filling normally (>80%)

**Warning signs:**
- `[WARN] DEGRADED` status
- Nous queue growing (100-500 items)
- API timeouts present but retrying successfully
- Hephaestus scrapping more than usual
- Nemesis grid stalled

**Critical issues:**
- `[ERROR] CRITICAL` status
- Large Nous queue (>500 items)
- High timeout + high retry rate
- Hephaestus not processing items
- Process crashes or uncaught exceptions

---

## 3. Health Dashboard

**Location:** `scripts/health_dashboard.py` (5.8 KB)

**Purpose:** Quick combined status check for both pipelines

### Features

- ✓ Runs both intelligence and forge health checks
- ✓ Displays consolidated status summary
- ✓ `--save` flag archives both reports with timestamp
- ✓ Quick overall health determination

### Usage

```bash
# Quick status summary to stdout
python scripts/health_dashboard.py

# Quick status + save full reports to disk
python scripts/health_dashboard.py --save
```

### Output Format

```
═══════════════════════════════════════════════════════════════
                    PIPELINE HEALTH SUMMARY
═══════════════════════════════════════════════════════════════

INTELLIGENCE PIPELINE
─────────────────────────────────────────────────────────────
Status: [HEALTHY] — 7/7 agents healthy
Last Check: 2026-04-01 12:00:34

FORGE PIPELINE
─────────────────────────────────────────────────────────────
Status: [DEGRADED] — 2/3 agents healthy
Last Check: 2026-04-01 12:00:38
Nous Backlog: 1234 unprocessed responses
API Timeouts: 28 events (past 2h)

OVERALL ASSESSMENT
─────────────────────────────────────────────────────────────
Intelligence: [OK]
Forge: [WARN]
Action Needed: Investigate Hephaestus performance

═══════════════════════════════════════════════════════════════
```

When using `--save`, full detailed reports are saved:
- Intelligence report: `agents/pronoia/logs/health_intelligence_YYYY-MM-DD_HHMMSS.md`
- Forge report: `agents/nous/runs/health_forge_YYYY-MM-DD_HHMMSS.md`

---

## Monitoring Features Summary

### Log Analysis (Both Pipelines)

All scripts analyze logs from the **past 2 hours** and look for:

**Healthy log patterns:**
- Regular [INFO] messages
- Active API calls / processing
- Data output (forges, reports, digests)
- Consistent message frequency

**Warning patterns:**
- [WARNING] messages
- API timeouts or failures
- Extended periods without log activity (>10 minutes)
- Reduced message frequency

**Critical patterns:**
- [ERROR] or [CRITICAL] messages
- Repeated API failures
- Database connection errors
- Uncaught exceptions
- Process restarts

### API Health Tracking

Both scripts detect NVIDIA API performance issues:

**Forge Pipeline tracks:**
- API timeouts from Nous (LLM for concept generation)
- API timeouts from Hephaestus (LLM for code generation)
- Retry attempts (exponential backoff)
- Timeout trends over 2-hour window

**Intelligence Pipeline tracks:**
- API timeouts from Eos (arxiv/scholar fetching)
- API timeouts from Aletheia (LLM for concept analysis)
- Failure counts and retry patterns

### Backlog Monitoring (Forge Only)

Tracks Nous response accumulation:
- Monitors unprocessed responses in latest Nous run
- Compares to Hephaestus checkpoint (what's been processed)
- Detects when Hephaestus falls behind
- Alerts when backlog exceeds thresholds

---

## Common Usage Patterns

### Quick Health Check
```bash
python scripts/health_dashboard.py
```
**When to use:** Daily status check, quick verification before/after manual interventions

### Detailed Intelligence Pipeline Report
```bash
python scripts/check_intelligence_pipeline.py
```
**When to use:** Intelligence pipeline showing warnings; need detailed agent-by-agent breakdown

### Detailed Forge Pipeline Report
```bash
python scripts/check_forge_pipeline.py
```
**When to use:** Forge pipeline showing degradation; need to check backlog and API health

### Full Monitoring with Archival
```bash
python scripts/health_dashboard.py --save
```
**When to use:** After major pipeline activity; archiving reports for later analysis

### Save Individual Reports
```bash
python scripts/check_intelligence_pipeline.py --output intel_$(date +%s).md
python scripts/check_forge_pipeline.py --output forge_$(date +%s).md
```
**When to use:** Troubleshooting specific agent issues; keep timestamped history

---

## Status Indicator Meanings

| Indicator | Meaning | Action |
|-----------|---------|--------|
| `[OK] HEALTHY` | All running, no issues | None needed |
| `[WARN] DEGRADED` | Running but with warnings | Monitor closely; investigate if worsens |
| `[ERROR] CRITICAL` | Errors or process down | Immediate investigation needed |
| `[IDLE]` | No recent activity | Check if intentionally paused |
| `[ALERT]` (Backlog/API) | Threshold exceeded | Check specific metric; may need intervention |

---

## Integration with Pipeline Orchestrator Role

As the Pipeline Orchestrator, you use these scripts to:

1. **Daily health checks** — Run `health_dashboard.py` each morning
2. **Diagnose issues** — Use detailed reports to understand what's wrong
3. **Track API degradation** — Monitor timeout trends to decide if break-glass mode needed
4. **Monitor backlog** — Watch Nous queue to ensure Hephaestus keeps pace
5. **Archive status** — Save reports with `--save` flag for historical analysis
6. **Report to stakeholders** — Use reports as factual basis for status updates

---

## Technical Details

### Log File Locations
- **Intelligence Pipeline**: `agents/pronoia/logs/`, `agents/eos/logs/`, etc.
- **Forge Pipeline**: `agents/nous/logs/`, `agents/hephaestus/logs/`, `agents/nemesis/logs/`

### Data Sources
- **Process Status**: OS process list (checks Python process running)
- **Logs**: JSONL formatted logs from each agent
- **Forge Ledger**: `agents/hephaestus/ledger.jsonl` (forge/scrap history)
- **Nemesis Grid**: `agents/nemesis/grid/grid.json` (adversarial coverage)
- **Nous Queue**: `agents/nous/runs/<latest>/responses.jsonl` (unprocessed responses)

### Time Window
- **Default**: Past 2 hours of logs analyzed
- **Rationale**: Captures recent trends without noise from old issues
- **Customizable**: Can modify hours parameter in script if needed

### Report Generation
- **Format**: Markdown (human-readable, version-control friendly)
- **Storage**: Optionally saved to agent log directories with timestamp
- **Retention**: Keep recent reports for troubleshooting; archive older ones

---

## Troubleshooting Script Issues

If a script fails:

1. **Check Python path**: Ensure Python 3.8+ is available
2. **Check PYTHONPATH**: Ensure Prometheus directory is accessible
3. **Check log file access**: Ensure agent log directories exist and are readable
4. **Check database access**: Ensure DuckDB/ledger files are not locked
5. **Run with verbose output**: Scripts will print errors to stdout

If an agent is showing errors but script reports healthy:
- Check agent log directly: `tail -f agents/<agent>/logs/<agent>*.log`
- Verify process is actually running: `ps aux | grep <agent>`
- Check if logs are being written: `ls -lah agents/<agent>/logs/`

---

## See Also

- `RESPONSIBILITIES.md` — Full Pipeline Orchestrator role definition
- `scripts/README_HEALTH_MONITORING.md` — Original detailed documentation
- `docs/HEPHAESTUS_BACKOFF_FIX.md` — API timeout handling improvements
- `scripts/check_forge_pipeline.py` — Source code for forge monitoring
- `scripts/check_intelligence_pipeline.py` — Source code for intelligence monitoring
