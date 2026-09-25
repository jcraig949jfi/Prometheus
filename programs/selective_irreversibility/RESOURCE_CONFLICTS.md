# Resource conflicts

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Per host (M1, M2, and any other): the contended resource (CPU cores, RAM,
GPU, disk, the M1 Postgres, the operator's attention), the claimants, and
who yields and why. Frozen work outranks new work (s6).

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T16:45Z Aporia[m1-cb5a6069]
Source: read-only M1 audit 16:28-16:35Z (process list, schtasks, git log in
nestor-s1-forensics, origin/main at 0a9f5614d); comms #561 read by Aporia 16:44Z.

M1 at 16:34Z: Nestor 12 workers (10 CSA + 2 XA, = its STATUS cap). CPU ~33% (one sample), RAM
19.7/31.6 GB free, GPU idle (1%, 1061 MiB, no compute). Also resident: FoundryAPI
(F:/SerendipityD, ignored per operator ruling), Ollama, Postgres (the canonical comms/EW store).
No conflict today. Potential conflict: Cosmos-D authorship vs Nestor's running campaign. That is a
conflict for Nestor's attention, not for CPU.
Service noise, not ours: schtask PrometheusMachineProbeM1 fails every minute (0x80070002).
