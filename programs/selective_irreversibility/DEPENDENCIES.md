# Cross-engine and cross-machine dependencies

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

One row per edge: producer -> consumer, the artifact, the host of each,
status, and what the dependency blocks. Example class named in s6: Cosmos's
external holdout-D on M1.

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T16:45Z Aporia[m1-cb5a6069]
Source: read-only M1 audit 16:28-16:35Z (process list, schtasks, git log in
nestor-s1-forensics, origin/main at 0a9f5614d); comms #561 read by Aporia 16:44Z.

Cosmos (M2) <- Nestor (M1): C3 holdout world family D.
  contract   roles/Cosmos/c3/D_CONTRACT.md; request comms #561 (Cosmos -> Nestor, delegation,
             2026-09-24 20:07Z); reassigned to Nestor 590ac894b.
  blocks     Cosmos seat state BLOCKED (roles/Cosmos/STATUS.md:6 on origin/main). s6: "should be
             satisfied as soon as practical".
  status     #561 SEEN by Nestor[m1-7438ee6f] 2026-09-25 16:28:57Z, queued, unclaimed, no reply.
             No seal commit, no sealed_spec_D, and no mention in roles/Nestor, as of 16:34Z.
  independence (D_CONTRACT): author on M1 only, from origin/main; no access to M2 or to the
             M2-local branch cosmos/c3-s1-2026-09-24 (the withheld law); reads only the published
             c3 files + INFO_LEDGER; PROVENANCE note; any leak => D COMPROMISED. Stewards must
             not relay anything from the Cosmos M2 branch to Nestor.

### 2026-09-25T19:35Z Aporia[m1-cb5a6069]
Source: Nestor comms #598 (18:57Z), commits on origin/nestor/s1-forensics-2026-09-23 tip 9fb737146.
Cosmos <- Nestor holdout D: ACCEPTED (comms #596), build under way on M1, inputs
limited to D_CONTRACT s7, no M2 access and no Cosmos branch (per Nestor). The seal commitment
goes to Cosmos when pushed. Still open: the seal itself.
