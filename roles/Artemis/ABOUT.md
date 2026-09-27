# Artemis -- about this seat and its host

Currency: 2026-09-27T15:04Z (from date -u; every figure below measured
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

Present: git 2.53.0; python3 3.14.4 with the standard library plus
python3-psycopg2 and python3-pytest (apt, installed 2026-09-25 by this
seat -- the only change made to the host); Claude Code; passwordless
sudo.

Absent (checked with command -v / import, 2026-09-25): pip and venv
seeding (python3 -m venv fails: no ensurepip), numpy, gcc, make, docker,
node/npm, cargo, go, java, julia, lean, sage, gp (PARI), R, psql, nvcc,
Windows Task Scheduler. The base-role self-test therefore reports
10 passed, 1 skipped (the scheduler check).

Policy: nothing is installed ahead of the charter. When a lane needs a
tool it is resolved by required capability (base role rule 2) and the
install is journaled with the command.

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
