# Fleet hosts (machines)

The physical machines Prometheus runs on. Seats/agents are tracked separately in `docs/fleet/FLEET_CENSUS.md`.
Started 2026-10-02 by Achilles (ELSA). **TBD = not recorded yet: the operator fills it in** (Task Manager → Performance on
Windows, or `nproc; free -h; lscpu | grep "Model name"` on Linux).

Role tags (for routing work, e.g. as Fabric `required_caps`):
`heavy.cpu` many cores · `gpu` local GPU · `db` hosts shared state · `light` small Claude/script worker ·
`command` operator desk, not a worker · `ram.32g` 32 GB+ RAM

## Windows machines (8)

Specs reported on comms 2026-10-02 (replies to Achilles #1249: #1250-#1255) unless noted.

| Host (label) | Hardware | CPU | RAM | GPU | Disk | IP | Role / tags | Notes |
|---|---|---|---|---|---|---|---|---|
| SKULLPORT (M1) | MicroElectronics G731 desktop | Ryzen 7 7700X, 8C/16T | 32 GB | RTX 5060 Ti 16 GB | 2x 1 TB NVMe + 3x 4 TB HDD | .202 | `heavy.cpu` `gpu` `db` | Postgres 17 for the fleet (comms, fabric, evidence_wiki). Seats: Aporia, Nestor, Hecate, Ananke, Atlas. Win 11 Home. |
| SPECTREX5 (M2) | iBUYPOWER desktop | i7-14700F, 20C/28T | 32 GB | RTX 5060 Ti 16 GB | 1 TB NVMe (C:) + 8 TB SMR HDD (D:) | .191 | `heavy.cpu` `gpu` | Most cores in the fleet. Keep DBs/WAL writers on C:; the SMR D: stalls on fsync-heavy load. SSH/admin box for the ubu nodes. |
| GANDALF (M3) | OEM desktop | i7-920 (2008), 4C/8T, **no AVX** | 24 GB | GTX 1070 8 GB | 500 GB SATA SSD | .161 | `light` `gpu.small` | Seats only (Epimetheus, Techne, Nyx). No virtualization in firmware. Win 10 Home (out of support). |
| HARRY1 (M4) | ThinkPad T580 (20LB) laptop | i7-8550U, 4C/8T (15 W) | 32 GB | Quadro P500 (not useful) | 1 TB SSD | .157 | `cpu.light` `ram.32g` | Aphrodite seat + engine pools. Thermally limited: budget ~4 cores. Open memory-leak issue: watch long pools by RSS. |
| BUCKKEEP | LG gram 15Z90Q laptop | i7-1260P, 12C/16T (4P+8E) | 32 GB | Iris Xe | 1 TB NVMe | .162 | `cpu.light` `ram.32g` | Aether seat. Parallel scaling is poor (8 units = 1.8x); waves of 3. Background shells reaped under memory pressure. |
| DESKTOP-RUAPVAI | N100 mini PC | Intel N100, 4C/4T | 16 GB | UHD (iGPU) | 1 TB SSD | .160 | `cpu.light` | Theseus seat; small numpy sweeps. No operator label yet. |
| ELSA | Dell Optiplex 980 | i7-860, 4C/8T (no AVX, no iGPU) | 16 GB DDR3-1333 (4x 4 GB, all 4 DIMM slots; board max) -- verified 2026-10-05T22:57Z via Win32_PhysicalMemory, was 6 GB (3x 2 GB) | Radeon HD 5450 | 240 GB SATA SSD | .163 | `light` | Achilles' seat; builds the autoinstall stick. Ubuntu conversion candidate (16 GB max). |
| LIZZIE-42 | Auusda A146 laptop | Celeron | 8 GB soldered | iGPU | SATA SSD | | `command` | Windows 11 Pro, clean. Broken built-in screen (external monitor). |

**Heavy compute is really two machines:** M2 (20C/28T) and M1 (8C/16T), each with a 16 GB RTX 5060 Ti. Everything else is
laptop-class or old. No Windows host runs a Fabric worker (DEF-ODY-012); Fabric workers are Linux (ubu nodes).

## Linux nodes (6)

All Ubuntu Server 26.04.1, kernel 7.0.0-38, user `jcraig`, Claude Code, `~/Prometheus`. PrometheusWorker
(generic execution, roles/generic-worker-role/) runs on ubu001-006. Details: infra/ubuntu_nodes/ubuntu_server_machines.md "PrometheusWorkers". Details: `infra/ubuntu_nodes/ubuntu_server_machines.md`.

| Sticker label | Host | Hardware | CPU | RAM | Disk | Net | Role / tags | State (2026-10-02) |
|---|---|---|---|---|---|---|---|---|
| Lenovo ThinkPad X1 Carbon 5th #1 | ubu001 | ThinkPad X1 Carbon 5th (20HQS2YJ00) | i5-7300U, 2C/4T | 8 GB | 238 GB NVMe | Wi-Fi .218 | `light` | Ready; phone session live |
| Lenovo ThinkPad X1 Carbon 5th #2 | ubu002 | ThinkPad X1 Carbon 5th (20HQS2YJ00) | i5-7300U, 2C/4T | 8 GB | 238 GB NVMe | Wi-Fi .219 | `light` | Ready; phone session live |
| Dell Latitude E7240 | ubu003 | Dell Latitude E7240 | i7-4600U, 2C/4T | 8 GB | 256 GB SATA SSD | Ethernet .220 | `light` | Provisioned; Claude login pending |
| HP Pavilion x360 14" | ubu004 | HP Pavilion x360 14m-ba0xx | i3-7100U, 2C/4T | 8 GB | 500 GB 5400 rpm HDD (slow) | Wi-Fi .178 | `light` | Provisioned; Claude login + token pending; SSD wishlisted |
| Lenovo ThinkPad P52s | ubu005 | ThinkPad P52s (20LB0010US) | i5-8350U, 4C/8T | 22 GB | Team MP33 1 TB NVMe, USB-C enclosure | Ethernet .222 (Wi-Fi .227) | `light` | Worker active 2026-10-04; Claude login pending |
| Dell Inspiron 3647 | ubu006 | Dell Inspiron 3647 (small desktop) | i3-4130, 2C/4T | 16 GB (2x 8 GB, 2026-10-04) | 500 GB 7200 rpm HDD | Ethernet .225 (Wi-Fi .226) | `light` | Worker active 2026-10-03; Claude login pending |

Verified over SSH 2026-10-06 (dmidecode/lscpu). Claude Code 2.1.288-289 on all six, all on jcraig949@gmail.com: ubu001/002 by interactive login;
ubu003-006 by one shared `claude setup-token` OAuth token (2026-10-06, ~1 yr), verified with `claude -p` on each. Stickers: label + hostname + IP
(the two X1 Carbons are identical).

## Candidates

| Machine | Expected | Verdict |
|---|---|---|
| 2x 2010 mobile workstations (basement) | Quad first-gen i7, up to 32 GB, Quadro GPU; ~25-40 W idle | Worth it as `ram.32g` CPU nodes if they boot and are 64-bit. Each needs a ~$25 SSD. |

## Capacity notes

- **M1/M2 do the heavy lifting** (M2 20C/28T, M1 8C/16T, both RTX 5060 Ti 16 GB). The small nodes are for **wide, light, parallel** work:
  Claude/Codex sessions (mostly waiting on the network), stdlib checks, small search shards, triage.
- More hosts add **local** capacity only. Model throughput is set by the inference accounts (2x Claude Max, Codex,
  Augment) and their rate limits, so tie node workers to account "lanes".
- Long jobs on cheap hardware need **checkpointing + leases**: a node will disappear mid-task.

## Scale-out policy (operator, 2026-10-03)

**Internal fleet first, big iron after the gates.** Experiments are proven on the internal fleet (M1/M2 for the heavy
pilots, ubu nodes for wide light work). Only after they pass their gates do they scale out to rented capacity: cloud CPU
(AWS C8i/C8a, Azure HB/F, GCP C4/C4D; spot about $0.02/vCPU-hr, e.g. 192 cores for about $8.50/hr) or RunPod for GPUs.

What makes that hand-off cheap:
- **Same environment local and remote:** a pinned container or lockfile, so a gated pilot runs unchanged on a 384-vCPU VM.
- **Chunked + checkpointed tasks:** spot VMs and laptops both vanish mid-task; the same design covers both.
- **A cost estimate in the gate packet:** core-hours measured on the pilot × spot price, before any spend.
- **Cloud workers join Fabric** as `heavy.cpu` workers through a secure tunnel to M1 (Tailscale/WireGuard; open item in
  `infra/ubuntu_nodes/ubuntu_swarm_todo.md`), drain the queue, then shut down.
