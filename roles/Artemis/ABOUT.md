# Artemis -- about this seat and its host

Currency: 2026-09-27T15:58Z (s3 re-measured; rest 15:04Z) (from date -u; every figure below measured
on the host at that time unless dated otherwise). Written at the
operator's request ("Write a note about yourself. Machine specs, etc").
Pure ASCII.

## 1. Who

- Seat: Artemis, created 2026-09-25. The operator asked the session to
  choose its own name from the Greek pantheon of the original Deities &
  Demigods; it chose Artemis, the huntress: patient, precise, brings back
  what it aimed at. Creation exchange verbatim:
  roles/Artemis/prompts/2026-09-25_creation/.
- Charter: PENDING (to be discussed with the operator). Until then: no
  lane, no monitor, no science (RESPONSIBILITIES.md s0).
- Model: claude-opus-5-5 (heavy tier), Claude Code 2.1.283.
- Comms: registered on the canonical M1 store as Artemis; instance tag
  ubu002-<first 8 of session id> (first instance ubu002-78a7bd7b).
  EW_DB_HOST=192.168.1.202 is required in every shell before comms.
- Wake: roles/Artemis/WAKE.md.

## 2. The host: ubu002

ubu002 is the host's program name (operator ruling 2026-09-25), not an
M-number placeholder. Artemis is likely the only seat resident here.

Fleet as the operator gave it: M1 (SKULLPORT, the comms/Evidence Wiki
database), M2 (SPECTREX5), M3, M4, two laptops, and ubu002.

| property | value |
|---|---|
| hardware | Lenovo ThinkPad X1 Carbon 5th gen (20HQS2YJ00), BIOS N1MET37W 1.22; bare metal (systemd-detect-virt: none) |
| CPU | Intel Core i5-7300U (Kaby Lake), 2 cores / 4 threads, 0.4-3.5 GHz; AVX, AVX2, FMA, SSE4.2; NO AVX-512 |
| memory | 7.0 GiB RAM (about 6.0 GiB available at idle) + 4 GiB swap file |
| GPU | Intel HD Graphics 620 (integrated). No CUDA, no discrete GPU |
| storage | Samsung PM961 NVMe 256 GB (MZVLW256HEHP); / is 232 GB LVM ext, 20 GB used, 201 GB free |
| power | laptop on AC; battery BAT0 present, 78%, not charging |
| network | Wi-Fi only (wlp4s0, 192.168.1.219/24 + IPv6); wired enp0s31f6 DOWN |
| OS | Ubuntu 26.04.1 LTS, kernel 7.0.0-34-generic, graphical.target; NTP synchronized; sshd active |
| uptime | 1 day 20 h at measurement |

## 3. Software on the host

Re-measured 2026-09-27; supersedes the 2026-09-25 list.

Present: git 2.53.0; python3 3.14.4 with, from apt, psycopg2 and pytest
(installed 2026-09-25 by this seat) and numpy 2.3.5, scipy, CPU-only
torch 2.9.1, numba, pip 25.1.1, requests, hypothesis, psutil, yaml,
cryptography (installed 2026-09-27 14:20Z: `apt-get install
python3-numpy python3-torch`, 235 packages incl. gcc and make; plus
`apt-get install gh` -- by a different session on this host, see
journal 2026-09-27); Claude Code; passwordless sudo.

Absent (2026-09-27): fastapi, uvicorn, pydantic, redis, cupy, sklearn,
falkordb, pytest-timeout; docker, node, cargo, go, java, julia, lean,
sage, gp, R, psql client; any GPU runtime; Windows Task Scheduler. No
local Postgres or Redis (only ports 22 and 53 listen). The base-role
self-test reports 10 passed, 1 skipped (the scheduler check).

What runs here unchanged (P_portability s4, 2026-09-27): SFE core and
canary, BEE z80atlas, toolbox, Archaeon z80atlas, ensorain/wtp,
Aphrodite, Aether's tests on CPU; anything needing fastapi, Redis or a
local Postgres does not.

Policy: install only what a lane needs, resolved by required capability
(base role rule 2), journaled with the command. Host facts here are
dated and re-measured at boot, not trusted (calibration 2026-09-27).

## 4. Reachability

- To M1 (192.168.1.202): 5432 (Postgres, comms + ew) OPEN; 8811 (engine),
  8377 (Evidence Wiki API) and 22 CLOSED from here.
- Repository: canonical checkout /home/jcraig/Prometheus (fetch and
  worktree management only); worktrees under
  /home/jcraig/Prometheus-worktrees/ (current:
  artemis-base-role). Pushes to github.com/jcraig949jfi/Prometheus work.

## 5. What this host is and is not good for

A fair reading of the numbers, for whoever writes the charter:

- GOOD: a coordinating, auditing, reading, writing or light-analysis
  seat; single-threaded CPU work; small pure-Python or stdlib
  experiments; git archaeology across the whole tree; being a second,
  independent vantage point on the program (it shares no disk, process
  table or local database with M1-M4).
- MARGINAL: numeric work once numpy/scipy are installed, if it fits in
  about 5 GB and 4 threads; short CPU-bound sweeps.
- NOT: GPU training or inference; memory-hungry engines (the SFE, large
  populations, multi-worker campaigns); any long-running service that
  must survive the operator closing the lid or moving it off Wi-Fi.
  Nothing on this host should be the only copy of anything.
