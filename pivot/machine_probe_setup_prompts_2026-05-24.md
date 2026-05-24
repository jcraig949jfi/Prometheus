# Machine Probe Setup — Paste-Ready Prompts

**What this is.** A background daemon that probes CPU / GPU VRAM / RAM / Prometheus-disk every 60s and writes one row per probe to `agora.machine_probes` (Postgres time-series). Fire and forget — runs continuously, survives reboots, fail-soft on Postgres outages.

**What's already built and pushed to main.**
- `scripts/machine_probe.py` — the daemon
- `scripts/agora_persist.py` — `write_machine_probe()`, `read_recent_machine_probes()`, schema bootstrap
- M4 (this machine) — daemon launched, scheduled task `PrometheusMachineProbeM4` keeps it alive

For M1, M2, M3 — paste the block below into the Claude Code session that drives that machine's persona. The persona will run the setup steps and confirm.

---

## Paste-ready prompt (universal — works on M1, M2, M3, any future machine)

You are being asked to install and launch the Prometheus machine_probe daemon on this machine. The daemon runs continuously in the background and writes one row per minute to `agora.machine_probes` (Postgres on M1) capturing CPU / GPU VRAM / RAM / Prometheus-disk-headroom. James needs this on every machine to see resource headroom and detect threshold issues across the swarm. Fire and forget — once it's running, no further attention needed. Do these steps in order, confirming each before moving on. (1) Pull latest code: from the Prometheus repo root run `git pull --ff-only origin main` so you have `scripts/machine_probe.py` and the updated `scripts/agora_persist.py`. If pull fails, run `git status` first and report what's blocking. (2) Verify Python deps: run `python -c "import psutil; print(psutil.__version__)"`. If psutil isn't installed, run `pip install psutil` (or `pip install --user psutil` if you don't have system-wide install rights). Without psutil the probe falls back to OS shellouts which work but miss GPU and some disk stats. (3) Set your machine label: identify which machine label this is — M1 (skullport / Postgres+Redis host), M2 (SpectreX5 / Apollo), M3 (GANDALF / Hephaestus), or M4 (harry1/Aletheia / reporting tier). Set the env var for the session: on Windows, `$env:PROMETHEUS_MACHINE = "M2"` (substituting your label). The daemon also auto-detects by hostname if the env var is unset, but setting it explicitly is more reliable. (4) Verify Postgres connectivity: run `python -c "import sys; sys.path.insert(0,'scripts'); import agora_persist; agora_persist.init_schema(); print('schema OK')"`. This is idempotent and ensures the `agora.machine_probes` table exists on the M1 Postgres server. If it errors with connection refused, check that M1 is reachable from this machine: `Test-NetConnection 192.168.1.176 -Port 5432` (Windows PowerShell) or `nc -zv 192.168.1.176 5432` (Linux/Mac). Report the error and stop if PG isn't reachable. (5) Smoke-test one probe: run `python scripts/machine_probe.py --once --dry-run`. Confirm the output line names the correct machine label and reports nonzero CPU/mem/disk values. If GPU is missing on this machine that's fine — it'll show `gpu=[no-gpu]`. (6) Smoke-test one probe with a real PG write: run `python scripts/machine_probe.py --once`. Then verify the row landed: `python -c "import sys; sys.path.insert(0,'scripts'); import agora_persist; rows = agora_persist.read_recent_machine_probes(machine='M2', hours=1, limit=1); print(rows[0] if rows else 'no rows')"`. Substitute your machine label. You should see one row dated within the last minute with all expected fields. (7) Launch as background daemon. On Windows, use pythonw so no console window persists: `Start-Process -FilePath "pythonw.exe" -ArgumentList "scripts/machine_probe.py --interval 60" -WorkingDirectory "C:\Prometheus" -WindowStyle Hidden`. On Linux/Mac: `nohup python scripts/machine_probe.py --interval 60 > /dev/null 2>&1 &`. Verify it's running: on Windows `Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object { $_.CommandLine -like "*machine_probe.py*" } | Select-Object ProcessId, CreationDate`; on Linux/Mac `pgrep -af machine_probe.py`. Should return one PID. (8) Register restart-on-death so the daemon survives crashes and reboots. On Windows: paste this PowerShell verbatim (substitute YOUR machine label in PrometheusMachineProbeMx if you prefer per-machine names): `$TaskName = "PrometheusMachineProbe"; if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false }; $action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument "C:\Prometheus\scripts\machine_probe.py --interval 60" -WorkingDirectory "C:\Prometheus"; $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1); $trigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::FromDays(3650))).Repetition; $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -MultipleInstances IgnoreNew; $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited; Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Restart Prometheus machine_probe.py if not running"`. The `IgnoreNew` flag prevents duplicate daemons — once one is running, additional fires are no-ops. On Linux/Mac: add to user crontab via `crontab -e`: `*/5 * * * * pgrep -f machine_probe.py > /dev/null || (cd /path/to/prometheus && nohup python scripts/machine_probe.py --interval 60 > /dev/null 2>&1 &)`. (9) Confirm to James in one message: which machine label you used, that the daemon is running with PID N, that the scheduled task / cron is registered, and the most recent probe summary line (CPU/mem/GPU/disk percentages). If anything failed in steps 1-8, report which step and the exact error rather than continuing. Do not attempt any of the persona's normal substrate work in this session until the probe is confirmed running — this is a one-time setup with a clear definition of done.

---

## What to expect after deployment

Within 60 seconds of step 7, the first probe row lands in `agora.machine_probes`. After step 8 the daemon survives reboots and crashes.

Each row carries: `cpu_pct`, `cpu_count_logical`, `mem_total_gb`, `mem_used_gb`, `mem_pct`, `gpu_name`, `gpu_vram_total_mb`, `gpu_vram_used_mb`, `gpu_vram_pct`, `gpu_util_pct`, `prom_disk_mount`, `prom_disk_total_gb`, `prom_disk_used_gb`, `prom_disk_pct`, `uptime_sec`, `probe_pid`.

Query latest snapshot per machine:
```sql
SELECT DISTINCT ON (machine) machine, taken_at, cpu_pct, mem_pct,
       gpu_name, gpu_vram_pct, prom_disk_pct
FROM agora.machine_probes
ORDER BY machine, taken_at DESC;
```

## Optional: surface machine_probes on the dashboard

The reporting tier (M4) already pulls from `agora.intelligence_outputs` and `agora.agent_heartbeats`. Adding `machine_probes` to `state.json` is a follow-up — a simple "latest probe per machine" panel for the React dashboard. Not required for the daemon to be useful (the table itself is queryable directly).

## Troubleshooting

- **"connection refused" to 192.168.1.176:5432** — Postgres on M1 is down or LAN routing is broken. Check Postgres process on M1, firewall rules, and that the host can ping 192.168.1.176.
- **"agora_persist not found"** — wrong working directory. Run from the Prometheus repo root (where `scripts/` is a subdir).
- **GPU shows as "no-gpu" on a machine that has one** — `nvidia-smi` not in PATH. On Windows, add the NVIDIA driver dir to PATH (typically `C:\Program Files\NVIDIA Corporation\NVSMI\` or `C:\Windows\System32\`). On Linux, ensure `nvidia-utils` is installed.
- **Daemon dies repeatedly within a minute** — check the log at `logs/machine_probe.log` (created on first run). Most common cause: missing psutil. Run `pip install psutil`.

## To stop the daemon (for maintenance)

Kill the running process AND unregister the scheduled task (otherwise the task will restart it within 5 min). Windows:
```powershell
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object { $_.CommandLine -like "*machine_probe.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Unregister-ScheduledTask -TaskName "PrometheusMachineProbe" -Confirm:$false
```

Linux/Mac:
```bash
pkill -f machine_probe.py
# remove the */5 line from crontab
crontab -e
```
