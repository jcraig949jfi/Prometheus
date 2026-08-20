# Prometheus Portfolio Brief
*Generated: 2026-08-20 11:44:46 AM UTC*
*Author: Metis (multi-machine reporter mode)*

---

## Act on this

**Hephaestus @ M3, forge — substrate generator with falsification battery — DEAD, daemon stopped**
No heartbeat for 117799min (7067990s). Was last ALIVE at 2026-05-28T01:38:15.244017-04:00.
Investigate the process on M3 and restart, or kill watchdog if intentional.

## Watch this

**No Deep Research dispatched or received in last 24h**
DR pipeline idle. Either Pythia's queue is empty or upstream intent (Aporia tickets) hasn't been refilled.
Check Pythia queue depth; refill DR ticket inbox if dry.

## Parked threads — yours to unstick (46 parked, 2 decisions pending)

- **15 thread(s) gated on:** charon-cosign (DESIGN_W001) — e.g. RETRY-RL-00
  We built an experiment to re-test 725 old failed results that the archive itself flagged as killed-only-because-the-sample-was-too-small. Before it runs, Charon (our independent skeptic) must approve the design and hide fake test cases in the data so the experiment can't fool itself — one Charon session unlocks all 15 of these threads.
- **11 thread(s) gated on:** GPU slot + strategy-group harness check — e.g. SB-SWEEP-S00
  These scan 68,770 'sleeping beauty' number sequences — highly structured but connected to nothing — to find which detection strategy wakes them up. Each scan waits for a free GPU and a quick check that the scanning code for that strategy still runs.
- **8 thread(s) gated on:** CPNT test_spec is a stub — spec authoring needed — e.g. CAT-MATH-0476
  Eight 'CPNT' problems (zeta-derivative moments, prime races, sign changes of psi(x)-x, explicit Mertens bounds...) all carry the same placeholder test description: 'see specific test' — and that specific test was never written anywhere in the repo. Several look genuinely computable once someone writes the actual recipe (what statistic, what data, what counts as pass/fail). One spec-authoring session unblocks all eight; until then attacking them would mean inventing the goalposts mid-shot.
- **3 thread(s) gated on:** heredity rule (first cycle) — e.g. LAD-R10-DESIGN
  House rule: no new machinery until one failure has demonstrably taught the system something — the probe running now is testing exactly that. These are designs for new reasoning-test graders, so they wait for that first learning loop to close.
- **1 thread(s) gated on:** Artin L-function data absent from local mirror — e.g. CAT-MATH-0260
  The test wants to check that a certain family of L-functions has no forbidden poles — but our local database copy simply doesn't contain that family (it has modular-form, Dirichlet, and elliptic-curve L-functions only; we verified with a census of all 24 million rows). The fix is a download, not code: pull the Artin L-function subset from the public LMFDB into the mirror, and the test unblocks with a one-line existence check.
- **1 thread(s) gated on:** RL batches complete first — e.g. RETRY-WIDE-000
  This extends the re-test experiment from the 725 flagged failures to the wider 3,378. It waits for the first 725 so we know the method works before scaling it.
- **1 thread(s) gated on:** Z-drive not mounted on M1 — e.g. BACKUP-Z-TARGET
  The database backups now run weekly to the E: drive (a different disk in the same machine), but DECISION 2 wanted a copy on Z: too — and Z: is not mapped in this machine's sessions. You know the share name: one net-use command (or telling the loop the UNC path via STEERING.md) adds the second copy.
- **1 thread(s) gated on:** translator build — e.g. LAD-BPRIME
  B-prime is a sealed exam of 24 novel math claims that can only be graded once, ever — a second look would turn it into training data. It waits for the 'translator' (the tool that converts claims into checkable form) to exist, so our one clean shot isn't wasted.
- **DECISION pending:** Ratify the PROMETHEUS-0 constitution (10 articles)
  PROMETHEUS-0 is the planned master organism that births and prunes specialized child agents; its 10-article constitution defines what it may never do without you (spawn freely, change its own rules, spend money, touch the outside world). Signing it is the first of three gates before that experiment can start.
- **DECISION pending:** Budget envelope above $0 / paid-tier procurement
  Everything currently runs on free tiers and local GPUs; several queued experiments (the model zoo, the execution-discipline replication, bigger probe arms) need paid API calls. A monthly dollar ceiling from you opens those lanes — until then they stay parked, not dead.

## For the record

Session-model activity (the live operating model): 122 non-cron commits in 72h. Ground truth: engine/PULSE.md.


**1 agents ALIVE** (Pronoia).

**Anomalies tracked:** 28 (Apollo, Hephaestus, Clio, Pythia, Hypatia).

---
*Deterministic brief (primary mode) — every line computed from state; no LLM in the loop.*
