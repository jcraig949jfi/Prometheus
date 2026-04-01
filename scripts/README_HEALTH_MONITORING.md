# Pipeline Health Monitoring Scripts

Three Python scripts for monitoring the health of Prometheus pipelines.

## Scripts

### 1. `check_intelligence_pipeline.py`

Monitors the Intelligence Pipeline chain: **Pronoia → Eos → Aletheia → Skopos → Metis → Clymene → Hermes**

**Features:**
- Checks if each agent process is running
- Analyzes log files from the past 2 hours
- Detects errors and warnings
- Verifies output files (reports, briefs, digests)
- **Monitors NVIDIA API health** — tracks timeouts, failures, and retry attempts across Eos + Aletheia
- Generates detailed health report with agent-by-agent status

**Usage:**
```bash
python scripts/check_intelligence_pipeline.py              # Print to stdout
python scripts/check_intelligence_pipeline.py --output report.md  # Save to file
```

**Output:**
- Overall status: [HEALTHY], [DEGRADED], or [CRITICAL]
- **API Health section:** Timeouts, failures, retries (alerts on high rates)
- Per-agent status table
- Detailed logs from past 2 hours
- Error/warning counts

---

### 2. `check_forge_pipeline.py`

Monitors the Forge Pipeline chain: **Nous → Hephaestus → Nemesis**

**Features:**
- Checks if each agent process is running
- Analyzes log files from the past 2 hours
- Counts forge attempts, passes, and API failures (from Hephaestus ledger)
- Tracks Nemesis adversarial grid coverage
- **Monitors Nous backlog** — unprocessed responses awaiting Hephaestus
- **Tracks NVIDIA API issues** — timeouts, failures, retry rates across Nous + Hephaestus
- Auto-alerts when backlog grows or API timeouts spike
- Generates detailed health report

**Usage:**
```bash
python scripts/check_forge_pipeline.py              # Print to stdout
python scripts/check_forge_pipeline.py --output report.md  # Save to file
```

**Output:**
- Overall status: [HEALTHY], [DEGRADED], or [CRITICAL]
- **Pipeline Backlog & Load section:**
  - Nous response queue size (current backlog)
  - NVIDIA API timeout events (past 2h)
  - Retry attempt counts
  - Auto-alerts if timeout/retry rate is high
- Per-agent status table
- Forge metrics: forged/scrapped/api_failed counts
- Nemesis grid fill percentage
- Detailed logs from past 2 hours

---

### 3. `health_dashboard.py`

Combined dashboard that runs both pipelines and displays a quick summary.

**Features:**
- Runs both intelligence and forge checks
- Displays consolidated status
- Can save both reports to disk with `--save` flag
- Quick overall health determination

**Usage:**
```bash
python scripts/health_dashboard.py                    # Display summary to stdout
python scripts/health_dashboard.py --save             # Save both reports to files
```

**Output:**
- Quick status summary for both pipelines
- Overall health indicator: [OK], [WARN], or [ERROR]
- Option to save full reports

---

## Monitoring Features

### Backlog Tracking (Forge Pipeline)

The forge script monitors the **Nous response queue** to detect when Hephaestus is falling behind:

```
Pipeline Backlog & Load
- Nous Response Queue: 1234 unprocessed responses
  - Latest run: 20260331_190000
```

**What it means:**
- **Empty queue** = Hephaestus is keeping up with Nous (healthy)
- **Growing queue** = Nous is generating faster than Hephaestus can forge (backlog building)
- **Large queue (>500)** = Indicates need to investigate Hephaestus issues or activate break-glass forge

### API Health Monitoring

Both scripts detect **NVIDIA API timeout events** and alert when rates are high:

**Forge Pipeline:**
```
- API Timeouts (past 2h): 38 timeout events
  - Nous: 32 timeouts, 75 retries
  - Hephaestus: 6 timeouts, 0 retries
  - **ALERT**: High retry rate indicates API degradation
```

**Intelligence Pipeline:**
```
API Health (past 2 hours)
- API Timeouts: 2 events
- Retry Attempts: 0 events
- API Failures: 4 events
```

**What it means:**
- **Few/no timeouts** = API responding normally
- **Timeouts without retries** = Temporary network blips
- **High timeout + high retry rate** = API is degraded or overloaded (consider rate limiting or break-glass mode)
- **Sustained high failures** = Investigate API service status

Each report includes:

1. **Overall Status** — [HEALTHY]/[DEGRADED]/[CRITICAL]
2. **Agent Status Table** — Quick overview with log counts, errors, last activity
3. **Detailed Status** — Per-agent breakdown with:
   - Process running status
   - Recent log counts
   - Error/warning counts
   - Last activity timestamp
   - Recent log lines (last 5)
   - Agent-specific metrics (forge stats, grid coverage, etc.)

---

## Status Indicators

- **[HEALTHY]** — All agents running, no errors, active log output
- **[DEGRADED]** — Running but with warnings or reduced activity
- **[CRITICAL]** — Errors detected in logs
- **[IDLE]** — No recent activity but no errors

---

## Examples

**Quick check:**
```bash
python scripts/health_dashboard.py
```

**Detailed intelligence pipeline report:**
```bash
python scripts/check_intelligence_pipeline.py
```

**Detailed forge pipeline report with file save:**
```bash
python scripts/check_forge_pipeline.py --output forge_health.md
```

**Full monitoring with report archival:**
```bash
python scripts/health_dashboard.py --save
```

---

## Log Analysis

All scripts analyze logs from the past **2 hours** and look for:

**Healthy indicators:**
- Regular [INFO] messages
- Active API calls / processing
- Data output (forges, reports, digests)

**Warning signs:**
- [WARNING] messages
- API timeouts or failures
- Extended periods without log activity
- Process not running

**Critical issues:**
- [ERROR] or [CRITICAL] in logs
- Repeated API failures
- Database connection errors
- Uncaught exceptions

---

## Report Storage

Reports are automatically saved when using `--output` flag:

- Intelligence pipeline: `agents/pronoia/logs/health_intelligence_*.md`
- Forge pipeline: `agents/nous/runs/health_forge_*.md`
- Dashboard: Both of the above with timestamp

Timestamps are in format: `YYYY-MM-DD_HHMMSS`
