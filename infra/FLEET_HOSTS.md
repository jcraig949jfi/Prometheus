# Fleet hosts (machines)

The physical machines Prometheus runs on. Seats/agents are tracked separately in `docs/fleet/FLEET_CENSUS.md`.
Started 2026-10-02 by Achilles (ELSA). **TBD = not recorded yet: the operator fills it in** (Task Manager → Performance on
Windows, or `nproc; free -h; lscpu | grep "Model name"` on Linux).

Role tags (for routing work, e.g. as Fabric `required_caps`):
`heavy.cpu` many cores · `gpu` local GPU · `db` hosts shared state · `light` small Claude/script worker ·
`command` operator desk, not a worker · `ram.32g` 32 GB+ RAM

## Windows machines (8)

| Host | Hardware | RAM | GPU | Role / tags | Notes |
|---|---|---|---|---|---|
| M1 | TBD (many cores) | TBD | RTX 5060 | `heavy.cpu` `gpu` `db` | Canonical Postgres (192.168.1.202), Fabric store. |
| M2 | TBD (many cores; runs 13-16 workers) | 32 GB | RTX 5060 | `heavy.cpu` `gpu` `ram.32g` | Main SSH/admin box for the Ubuntu nodes (key `jcraig@M2`). |
| M3 | TBD | TBD | TBD | TBD | |
| M4 | TBD (8 cores) | TBD | TBD | `heavy.cpu`? | |
| ELSA | Dell Optiplex 980, i7-860 4C/8T (no AVX, no iGPU) | 6 GB DDR3 (1 slot free; 16 GB max) | Radeon HD 5450 | `light` | Achilles' seat; builds the autoinstall stick. 192.168.1.163. Ubuntu conversion candidate. |
| LIZZIE-42 | Auusda A146, Celeron | 8 GB soldered | iGPU | `command` | Windows 11 Pro, clean. Broken built-in screen (external monitor). |
| TBD | | | | | |
| TBD | | | | | |

## Linux nodes (5)

All Ubuntu Server 26.04.1, kernel 7.0.0-38, user `jcraig`, Claude Code, `~/Prometheus`. Details: `infra/ubuntu_nodes/ubuntu_server_machines.md`.

| Host | Hardware | CPU | RAM | Disk | Net | Role / tags | State (2026-10-02) |
|---|---|---|---|---|---|---|---|
| ubu001 | ThinkPad X1 Carbon 5th | i5 7th gen, 2C/4T | 8 GB | 238 GB NVMe | Wi-Fi .218 | `light` | Ready; phone session live |
| ubu002 | ThinkPad X1 Carbon 5th | i5 7th gen, 2C/4T | 8 GB | 238 GB NVMe | Wi-Fi .219 | `light` | Ready; phone session live |
| ubu003 | Dell Latitude E7240 | i7-4600U, 2C/4T | 8 GB | 256 GB SATA SSD | Ethernet .220 | `light` | Provisioned; Claude login pending |
| ubu004 | HP Pavilion x360 14m-ba0xx | i3-7100U, 2C/4T | 8 GB | 500 GB 5400 rpm HDD (slow) | Wi-Fi .178 | `light` | Provisioned; Claude login + token pending; SSD wishlisted |
| ubu005 | ThinkPad P52s | 8th-gen i5/i7 (TBD), 4C/8T | TBD | PM991 256 GB 2242 (arriving) | Ethernet/Wi-Fi | `light` | Waiting on the SSD (HDD1 connector broken) |

## Candidates

| Machine | Expected | Verdict |
|---|---|---|
| 2x 2010 mobile workstations (basement) | Quad first-gen i7, up to 32 GB, Quadro GPU; ~25-40 W idle | Worth it as `ram.32g` CPU nodes if they boot and are 64-bit. Each needs a ~$25 SSD. |

## Capacity notes

- **M1/M2 do the heavy lifting** (many cores, GPUs, RAM). The small nodes are for **wide, light, parallel** work:
  Claude/Codex sessions (mostly waiting on the network), stdlib checks, small search shards, triage.
- More hosts add **local** capacity only. Model throughput is set by the inference accounts (2x Claude Max, Codex,
  Augment) and their rate limits, so tie node workers to account "lanes".
- Long jobs on cheap hardware need **checkpointing + leases**: a node will disappear mid-task.
