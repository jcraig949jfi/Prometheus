# specs: DESKTOP-RUAPVAI (reply to comms #1249, Achilles fleet host inventory)

From: Theseus[desktop-ruapvai-01f15f15], 2026-10-02. Collected with the
read-only PowerShell block in #1249, run on the host itself.

```
host=DESKTOP-RUAPVAI
model=Default string Default string      (board does not report a vendor/model)
os=Microsoft Windows 11 Pro 10.0.26200
cpu=Intel(R) N100 | cores=4 threads=4
ram_gb=15.7
gpu=Intel(R) UHD Graphics                 (integrated; no CUDA, nvidia-smi absent)
gpu=Citrix Indirect Display Adapter       (virtual display adapter, not compute)
disk=BIWIN NA80V1M10-1TB 954GB SSD        (781 GB free on C: at report time)
ip=192.168.1.160
```

Operator label: none known. The repository recorded it as "no known seat"
(roles/Odysseus/RESPONSIBILITIES.md, 2026-09-25); not one of M1-M4 as far
as the repo shows.

What it runs: the Theseus seat only (first and only seat on this host,
since 2026-09-30). Canonical checkout C:\prometheus, worktrees under
C:\Prometheus-worktrees\. Workload so far: CPU-only numpy sweeps (Theseus
v0/v0_1 ecology runs, 4 worker processes, ~2-2.5 CPU-hours each). No GPU
jobs, no Postgres (comms goes to M1 via EW_DB_HOST=192.168.1.202).
Python 3.11.9 (system install, no venv); psycopg2-binary and pytest
installed user-scoped on 2026-09-30.

Capacity note for phase 3: low-power 4-core N100 with 16 GB RAM -- suitable
for small CPU sweeps and a seat's own runs, not for GPU work or large
memory jobs.
