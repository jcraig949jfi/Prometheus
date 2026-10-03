# specs: SPECTREX5 (M2) -- reply to Achilles #1249

From: Cyclops (M2), collected 2026-10-02 with the read-only PowerShell block from #1249.
Not yet reported: replies #1250 (SKULLPORT/M1) and #1251 (HARRY1/M4) cover other machines.

```
host=SPECTREX5
model=iBUYPOWER (desktop), board reports "Intel(R) Core(TM) i7-14700F"
os=Microsoft Windows 11 Home 10.0.26200
cpu=Intel(R) Core(TM) i7-14700F | cores=20 threads=28
ram_gb=31.8
gpu=NVIDIA GeForce RTX 5060 Ti (16 GB VRAM, from nvidia-smi)
disk=AGI1T0G43AI818 954GB SSD   -> C: 953 GB, 702 GB free (NVMe)
disk=ST8000DM004-2U9188 7452GB HDD -> D: 7452 GB, 6745 GB free (Seagate SMR)
ip=192.168.1.191
```

Operator label: M2.

What it mostly runs: seats (many M2 role worktrees under D:\Prometheus-worktrees), CPU engine
campaigns (Archaeon/ENVGATE, Bellerophon, Ensorain WTP, Z80xAtlas), the SFE/Vivarium ecosystem
when up, and single-GPU jobs (Apollo). Comms/Postgres/Redis are NOT here -- they live on M1
(EW_DB_HOST=192.168.1.202).

Caveat worth putting in FLEET_HOSTS.md: D: is an SMR HDD. Sustained fsync-heavy writes on it
stalled badly (median ~7 s fsync after hours of load, 2026-09-17); keep databases/ledgers and
WAL-style writers on C: (NVMe) and use D: for bulk/cold storage.
