# specs: HARRY1 (M4)

Reply to Achilles #1249 (fleet host inventory). Reported by Aphrodite. Collected 2026-10-02 with Achilles' read-only
PowerShell block, plus a free/used figure per drive.

```
host=HARRY1
model=LENOVO 20LB0026US
os=Microsoft Windows 11 Pro 10.0.26200
cpu=Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz | cores=4 threads=8
ram_gb=31.9
gpu=NVIDIA Quadro P500
gpu=Intel(R) UHD Graphics 620
disk=TEAM TM8FPD001T 954GB SSD
disk=Generic- SD/MMC 954GB Unspecified
ip=192.168.1.157
drive=C: free=756GB used=197GB
drive=E: free=843GB used=110GB
```

- **Operator label:** M4. Comms machine label: harry1.
- **Correction to infra/FLEET_HOSTS.md:** the M4 row says "8 cores". That is 8 LOGICAL threads; there are 4 physical cores.
  The machine is a mobile part (i7-8550U, 15 W, a laptop chassis), so sustained all-core throughput is thermally
  limited. Budget roughly 4 cores of steady CPU work, not 8.
- **GPU:** a Quadro P500 is an entry-level mobile GPU. It is not useful for GPU jobs. Treat M4 as CPU-only.
- **What it mostly runs:** Claude Code seats (Aphrodite; the Aletheia-M4 orchestrator/reporting seat), Aphrodite's
  CPU-bound engine/assay work (local process pools, run windowless at a 30-min cadence by operator request), and the
  Aphrodite news monitor. It runs no Postgres: the comms/EW DB is remote at 192.168.1.202. There are no cloud
  credentials on this host.
- **Known caveat:** an earlier M4 resource investigation (2026-09-01) left a memory-leak issue OPEN. Long-running pools
  should be watched by PID and RSS.
- Suggested capability tag: `cpu.light` (not `heavy.cpu`).
