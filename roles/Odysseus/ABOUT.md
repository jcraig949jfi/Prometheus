# Odysseus -- about this seat and its host (for building it a Thread)

Currency: 2026-09-27T15:29Z (from date -u; every host figure below was
measured on ubu001 at that time unless dated otherwise). Written at the
operator's request: "Identify yourself as a role, name, system spec, etc.
I'll work with the team to build you a thread. Do a writeup to do such."
Pure ASCII. Read against origin/main f287a4fdb (ops/ pilot: TH-001..TH-006,
C-001, E-001, E-002; ops/initiatives/GIT_NATIVE_LAB_CONTROL_PLANE.md).

## 1. Who

| field | value |
|---|---|
| seat | Odysseus (created 2026-09-25; name chosen by the seat from the Greek section of the original Deities & Demigods: the strategist and navigator) |
| model | claude-opus-5-5 (heavy tier), Claude Code 2.1.283 |
| how it runs | the node's always-on remote-control session: `claude --dangerously-skip-permissions --remote-control ubu001` in tmux under the user service claude-rc@ubu001 (pid 1680, up 1 d 20 h); the operator drives it from the phone |
| comms | registered on the M1 store as Odysseus, instance ubu001-a96af0b0; EW_DB_HOST=192.168.1.202 in every shell |
| wake | roles/Odysseus/WAKE.md |
| charter | ADOPTED 2026-09-26: distributed brain substrate (prompts/2026-09-26_charter/). Lane FROZEN by the operator 2026-09-27 for more design (prompts/2026-09-27_freeze/); seat PARKED on that lane |
| owns | odysseus/ (brain v0: 73 tests, DESIGN.md, INSTALL.md, review packet); roles/Odysseus/ |
| monitors | none owned or fed; no resident process of its own |
| incidents on record | 1 (a canonical-checkout `git pull` on day one, calibration/LEDGER.md) |

## 2. The host: ubu001

Program name ubu001 (operator, 2026-09-25); no M-number. Twin of ubu002
(Artemis). Expected to be the only resident seat, BUT it is already an
executor host for others: Archaeon[m2-1034e815] ran C-001/E-001 tasks
T-001, T-003 and part of T-005 here over SSH from M2 (E-001 TASKS.md).
Its work area ~/prom_tasks is empty now.

| property | value |
|---|---|
| hardware | Lenovo ThinkPad X1 Carbon 5th gen (20HQS2YJ00); bare metal |
| CPU | Intel Core i5-7300U (Kaby Lake), 2 cores / 4 threads, 0.4-3.5 GHz; AVX2, FMA; no AVX-512 |
| memory | 7.0 GiB RAM, 6.0 GiB available (the RC session holds ~0.45 GiB) + 4 GiB swap file (unused) |
| GPU | Intel HD Graphics 620 (integrated); no CUDA |
| storage | Samsung PM961 NVMe 238.5 GB; / 232 GB, 15 GB used, 207 GB free |
| network | Wi-Fi only: wlp4s0 192.168.1.218/24 (+IPv6), 802.11ac 866.7 Mbit/s link, signal -63 dBm, power save OFF; wired port DOWN (needs a Lenovo extension adapter or USB dongle) |
| power | on AC; battery 98%, health 82% (46.75/57.0 Wh, 342 cycles), charge limits 75/80; lid switch ignored |
| OS | Ubuntu 26.04.1 LTS, kernel 7.0.0-34-generic; NTP synchronized; sshd active; uptime 1 d 20 h |
| reachability | M1 5432 (comms/EW Postgres) open; GitHub push WORKS from this node (every Odysseus commit was pushed from here, via the node's fine-grained token); no outbound SSH key to other hosts; inbound SSH key from M2 only |

## 3. Software

Present: git 2.53.0, gh, python3 3.14.4 (stdlib + python3-psycopg2 +
python3-pytest from apt, installed 2026-09-25 by this seat), tmux, htop,
curl, iw, Claude Code 2.1.283, passwordless sudo.
Absent: pip/venv seeding, numpy, torch, gcc, make, docker, node, cargo,
go, java, julia, lean, sage, gp, R, psql, nvcc.
Consequence (seen in E-002 on the twin): anything needing numpy/torch
(e.g. the PTE engine) cannot run here until installed; stdlib tasks
(E-001's BEE/NPE probes) ran here bit-identical to M2.

## 4. What this seat brings to a Thread

1. Deterministic replay and cross-host verification. Brain v0 proves a
   sharded run bit-identical to an in-process reference under 40%
   datagram loss, and its `check` command lets one machine verify its
   own work from its own folder against a locally recomputed reference
   -- no bulk evidence copied. That is TH-006's question ("so that a
   node can verify as well as execute") in miniature.
2. A fleet inventory. GIT_NATIVE_LAB_CONTROL_PLANE.md s14 already names
   Odysseus's inventory as the SEED for ops/resources/FLEET.yaml +
   hosts/<host>.yaml. This seat holds the fleet map (RESPONSIBILITIES
   s4) and can measure a host the way this file does.
3. Test-first engineering with controls (negative / positive / cheat)
   and review packets; stdlib-only, Windows+Linux-portable code.
4. A second independent vantage point: no shared disk, process table or
   database with M1-M4.

## 5. What fits this host (pilot task classes, s11 of the initiative)

| class | fit | why |
|---|---|---|
| INTEGRITY | GOOD | hash/replay/verification work is CPU-light and exactly this seat's skill |
| ENGINEERING | GOOD | stdlib tools, test suites, small harnesses |
| INFRASTRUCTURE | GOOD | fleet catalog, host fact sheets, node runbooks |
| REVIEW | GOOD | adversarial reading of results; independent of M2's disk |
| INDEX / ARCHIVE | GOOD at repo scale | git archaeology over the whole tree; 207 GB free |
| FORENSIC_MINE / ANALYSIS | MARGINAL | fine if it fits ~5 GB RAM and 4 threads; slow over Wi-Fi if bulk evidence must be copied |
| SCIENCE_RUN | MARGINAL / NOT | stdlib replays yes (E-001 proved it); GPU, torch, large populations, multi-worker campaigns no |
| CLEANUP | GOOD for this host | owns nothing running; can verify absence |
| OPERATOR_DECISION | n/a | |

Not for: GPU work; memory-hungry engines; anything that must be the only
copy; anything that must survive Wi-Fi loss without a retry.

## 6. Candidate Threads (proposals for the operator and team; none claimed)

Ranked by fit. The operator and team choose; this seat starts nothing on
ops/ until a Thread is assigned (ops/README.md: "don't act").

A. TH-006 evidence portability and verification locality (OPEN, no
   owner named). Proposed first Task: take one E-001 task (T-001, BEE
   r038751) and make its "science unchanged" check runnable on a node
   without M2's 282 MB log, by committing a compact content-addressed
   reference (per-tick or per-row hashes, the brain v0 `check` pattern)
   and proving it fails on a tampered row (cheat control). Respects the
   non-goals: no scheduler, no broker, no new credentials.
B. Fleet resource catalog (initiative s14). Measure every reachable host
   into hosts/<host>.yaml when the operator authorises the ops/resources
   layout; this file's s2 is the ubu001 draft (appendix below).
C. Cross-host reproducibility of Attempts: run the same Task on two
   hosts (ubu001 and ubu002 are identical hardware; a Windows host is
   the interesting pair) and record agreement or the first divergence as
   an Attempt fact -- the E-001 finding generalised.
D. The distributed brain (this seat's charter), re-entered as a Thread
   when the operator's design is ready; frozen until then.

## 7. What a Task handed to this seat should carry

Learned from E-002's handoff findings on the twin host:
- inputs reachable from Git (or a named, hashed artifact and where it lives);
- the exact command and the expected result (hash or row count);
- the acceptance criterion STATED, not named;
- environment needs (stdlib only? numpy? torch? Postgres?) and a
  resource envelope (cores, RAM, wall time, disk);
- where outputs may be written (never over frozen outputs).
This seat can push its own commits and receipts (s2); if the pilot
wants the Git relay kept on M2, say so in the Task.

## 8. Risks and operator items for this host

- The node's GitHub token expires 2026-10-25 (ubuntu_swarm_todo.md);
  after that this seat cannot push receipts.
- No DHCP reservation for .218 yet; no BIOS power-on-AC; Wi-Fi only.
- Battery at 82% health is fine; the twin ubu002's is at 34%.
- The RC session is the seat's only runtime; a lapsed Claude login
  stops it until someone logs in from M2.

## Appendix: draft host entry (for the future ops/resources catalog;
## NOT instantiated under ops/ -- the initiative says don't, yet)

    host: ubu001
    program_name: ubu001
    os: Ubuntu 26.04.1 LTS (kernel 7.0.0-34-generic)
    hardware: ThinkPad X1 Carbon 5th gen, bare metal
    cpu: {model: i5-7300U, cores: 2, threads: 4, isa: [avx2, fma]}
    ram_gib: 7.0
    swap_gib: 4
    gpu: none (Intel HD 620 integrated)
    disk: {device: NVMe 238.5 GB, root_free_gb: 207}
    network: {link: wifi, ip: 192.168.1.218, wired: down}
    power: {ac: true, battery_health_pct: 82, charge_limits: [75, 80]}
    runtimes: {python: "3.14.4 stdlib + psycopg2 + pytest", git: "2.53.0", claude_code: "2.1.283"}
    absent: [pip, numpy, torch, gcc, docker, nvcc]
    resident_seats: [Odysseus]
    also_executes_for: [Archaeon (C-001/E-001 over SSH from M2)]
    service_critical: claude-rc@ubu001 (the seat's runtime; do not starve)
    safe_envelope: {cores: 3, ram_gib: 5, disk_gb: 150, wall: "hours, not days"}
    can_push_git: true (token expires 2026-10-25)
    measured: 2026-09-27T15:29Z
