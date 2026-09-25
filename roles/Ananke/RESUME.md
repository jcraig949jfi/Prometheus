# Ananke -- RESUME after reboot (read right after RESPONSIBILITIES.md)

Written 2026-09-25 ~11:30Z by instance m1-c5725d8e before an operator
reboot / Claude Code update / context reset. Nothing is in flight.

## 1. State at save

- NOTHING RUNNING. PTE-C1 finished 2026-09-25T00:06Z (watchdog exit 0).
  Scheduled task Ananke_PTE_C1 is Disabled (verified). No python job of
  this seat is on the GPU. MONITORS row AnankePTE_C1 = DISABLED.
- Everything is on origin/main (branch ananke/base-role-adopt-2026-09-24
  is fast-forwarded into main at each push; it can be deleted once
  `git branch -r --merged origin/main` lists it).
- Worktrees: Prometheus-worktrees/ananke-base-role (working; branch
  above) and Prometheus-worktrees/ananke-pte-c1-pinned (detached at
  362f2189b, the frozen campaign tree; keep until the review ends, then
  `git worktree remove`).
- Run state: ~/ananke_runs/pte-c1/ (M1 only). A committed copy of the rows
  is roles/Ananke/pte/c1_rows/cells.jsonl.gz (6596 rows, raw sha256
  prefix 2416b7bb3a9e0f37) plus logs and boundary files.

## 2. Where the science is

Read, in order: pte/REVIEW_PACKET_PTE_C1.txt (one screen), pte/C1_REPORT.md
(reading + roadmap), pte/c1_a0/A0_FINDINGS.md (ladder, A0), then the
calibration ledger (unflattering; 13 rows).
One-line result: rare, causally verified, reproduced, size-free packet
transport evolves in RELAY (0.84-0.89 held-out vs 0.500 no-comm); it is
topology-bound; no cross-family transfer; XOR/FLIP NULL; the SUPPORTED
phase boundaries gate a hand design, not evolved machinery. Two unexpected
mechanisms need proper adjudication: M2 delay-line memory in packets
(HOLD cell 4ab2ba014aac967e, post-hoc only) and M3 self-modifying
timing-locked MAJ (0a23398f20cc41a2, f6b623cdb23afd2c).

Operator framing adopted 2026-09-24 (verbatim intent in the chat, recorded
in pte/ANALYSIS_PLAN_C1_A0.md s5): the ladder L1 perturbability -> L2
distal influence -> L2' known-design viability -> L3 discoverability ->
L4 reuse/adaptation -> L5 (C2) concurrent informational organisation;
C1 = habitable zone, C2 = "weather" with three SEPARATE load axes
(traffic density, independent processes, informational conflict).
Seat recommendation from the C1 data: C2's habitable zone must come from
the CAUSALLY verified RELAY/MAJ physics, not from A0 plant viability.

## 3. Open threads (outside the seat)

- Adversarial review requested: Kairos comms #564, Elenchus #565 (no
  reply at save). Answer any review first on resume.
- Comms read through #569 at save. Atlas-M2 #567 and Cosmos #569 reported
  the MONITORS state-word defect; FIXED in the save commit (ledgered).
- Ensorain #566 (WTP-03: its survivors are known completion learners) is
  information, no ask.
- archaeon/tests/test_base_role.py: 10/11; the 1 failure is Nyx's
  pre-existing manifest drift (not this lane).

## 4. Next executable actions (backlog BACKLOG_H0H5.md)

1. Answer reviews if any arrived (comms sync first).
2. PTE-C1b PREREG + run (~2-3 h GPU): fresh-seed replication and
   ablation fingerprints for M2 and M3 (in-flight packet count vs held bit
   for M2; WIMM vs SETRULE vs mut_site split for M3).
3. PTE-C2 PREREG (ANANKE-26): amended boundary criterion (ordinal dials
   only, variance floor, monotone runs), ablation-fingerprint mechanism
   labels, env-variant no-op guard, promotion by comm_delta + fingerprint
   novelty, habitable zone from causally verified cells.
4. ANANKE-27 FLIP zero-comm twin rerun; ANANKE-09 throughput.

## 5. QUESTIONS FOR THE OPERATOR (ask these first after bootstrapping)

Q1 (ANANKE-25, XL) Ananke's PTE and Ensorain's Foundry both charter
   "tensor physics of intelligence" communication physics. Keep Ananke a
   separate lane, or merge PTE into Ensorain's Foundry as a component?
   Recommendation: separate lanes, shared engine (different substrates,
   and two seats give an independent failure mode for each other).
Q2 Order of work: C1b (adjudicate M2/M3, ~2-3 h) before C2, or go straight
   to C2? Recommendation: C1b first -- C2's habitable zone and mechanism
   labels depend on whether M2/M3 are real.
Q3 C2 scale: authorise a RunPod leg (Aether pinned-files path, own torch
   image, a hard dollar ceiling you name) if C2 finds a region that
   strengthens with N? Recommendation: yes with a $10 ceiling; C1 needed
   none (RELAY laws already size-free to N=2304 locally).
Q4 Is the review from Kairos/Elenchus a gate for starting C2, or can C2's
   preregistration proceed in parallel? Recommendation: proceed in
   parallel; do not promote any C1 claim beyond the seat until reviewed.
