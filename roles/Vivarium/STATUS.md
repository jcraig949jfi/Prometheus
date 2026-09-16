# VIVARIUM -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

**Currency: 2026-09-16 16:5x UTC (12:5x local).** Updated at least every four
hours of activity, per base role s3. Instance for this pass: `m2-fce3fe0b`,
the first boot of this seat on M2 (SPECTREX5), worktree
`D:\Prometheus-worktrees\vivarium-boot-2026-09-16` from `ccb26df01`.

## Is Vivarium alive

**No consumer is running anywhere.** `vivarium@m1` (pid 13460, build
fb7aa5bed, pinned `F:\Prometheus-worktrees\vivarium-consumer`) last
heartbeated **2026-09-14 23:53:44Z** and died with the operator-ordered M1
reboot (~23:55Z; Nestor comms #262/#263). Found at this boot, 09-16 11:46Z,
**35.9 h later** -- the second unobserved death in three days (receipt
`receipts/CONSUMER_DEATH_2026-09-14_M1_REBOOT.md`; backlog C11). Stranded 0
(IDLE at the reboot); no park record (a dead process cannot park).

**Not relaunched, and not relaunchable today** (base rule 9):

    M1 SFE 8811 / M1 PEW 8377   do not answer from M2 (connect times out)
    M1 shell                    none from M2 (22, 5985, 5986 closed)
    M2 SFE 192.168.1.191:8811   LIVE, but it is the twin eng_906356f7
                                (build 726275da), not the production ledger
    production ledger           eng_8a37a5d3, "wherever it runs; today:
                                nowhere" (Daedalus RULING, comms #270)
    M2 PEW 192.168.1.191:8377   LIVE (Mnemosyne)
    tokens on M2                none: no config.local.json here

The consumer follows the production ledger to M2. Prepared this pass, NOT
launched: `vivarium/deploy/prepare_m2.py` (pinned detached worktree, two
launchers, secrets presence by key name, store/PEW/engine preconditions,
tasks registered with the dead-man DISABLED). Its receipt today reads
store OK, PEW OK, engine WRONG_ENGINE (the twin), secrets ABSENT.

## Topology ruling (operator, in chat, 2026-09-16 ~12:45 UTC)

"Postgres and redis are shared, everything else runs at either machine,
not both at this point; a farm is a future roadmap item if it merits
scaling; to date it does not." Read for this seat: the canonical store
stays the M1 cluster (this seat's identity guard is pinned to it); the
SFE ecosystem -- engine, PEW, this consumer, Archaeon's tick -- runs on M2
and ONLY on M2; exactly one consumer instance, as the charter already
requires. Which LEDGER the M2 engine serves (M1's eng_8a37a5d3 carried
over per ccb26df01 / Daedalus #270, or a fresh start on the twin) was
asked in chat and not yet answered; I proceed on (a) carried over, which
is what everything below is keyed to.

## Queue, at this writing (canonical store, UTC)

    queued 5   Archaeon tick rows, created 09-15 03:27:10Z .. 20:12:09Z
               (oldest waiting 33 h); HELD, never cancelled by inference
               (Daedalus #270: "hold the 5 rows"; Archaeon #267: "late,
               not lost")
    stranded 0   completed 579   failed 79   cancelled 492
    last row done   8bc6b162 completed 2026-09-14 23:27:07Z

## What has to happen before the relaunch (not mine; in order)

1. Operator lands M1's `D:\Prometheus-data\sfe` (engine.db ~640 MB, blobs,
   backup) on M2; Daedalus verifies identity, swaps the twin's data dir,
   starts build 726275da on the ledger -> `/v2/version` reports
   eng_8a37a5d3 at 192.168.1.191:8811 (#270 steps 1-2).
2. Harmonia promotes the staged contract against M2 (#256/#270 step 3);
   `roles/Harmonia/contracts/sfe_contract.json` base_url becomes
   192.168.1.191.
3. **Operator gate (mine to ask):** carry `vivarium/config.local.json` (the
   two tokens, nothing else needed -- every other key is set by the
   launcher's environment) from M1's pinned worktree to
   `D:\Prometheus-worktrees\vivarium-consumer\vivarium\` on M2, with a
   receipt. No seat copies a token across hosts (#270).
4. Then: `python vivarium/deploy/prepare_m2.py --sha <SHA> --register`
   reads green -> `schtasks /Change /TN VivariumDeadmanM2 /ENABLE` is the
   launch (its first tick relaunches the consumer once the engine identity
   holds); Archaeon's grant on the migrated ledger is Daedalus's route.

## Landed this pass (main, fast-forward; all tested on the merged tree)

* **viv/db.py identity guard** (a6d1ba114): `connect()` proves the cluster
  via comms.identity; production schema `viv` is PINNED to
  prometheus-canonical and no variable can re-aim it; refusal closes the
  connection and carries the incident signature. Found because on M2 an
  unset VIV_DB_HOST reached the quarantined fork (c84e26826cc12217) and
  `run` would have created viv.* there and ticked green. 7 controls.
* **THEO-REQ-004** (6d21bd5ef, a9f81c7d6): executors declare witness
  truncation BOTH WAYS (a complete vector at exactly 64 was refused as
  undeclared; no bound moved); `success_mask_hex` on ca_density_v0 in the
  library's encoding with a wrapper-vs-classify parity refusal; pinned
  fixture 4f211943 -> 3655c564 with the arithmetic byte-identical. 12
  controls. Replied #280; task #246 done.
* **THEO-REQ-006** (6358acea9): `{"count": k}` entries in
  `ic_density_set` (exact-count ensemble, library dbc41fd2f); refused at
  the executor's entry with n_cells; null/float paths byte-identical. 15
  controls.
* **C11b dead-man** (f249ae21c): `viv/deadman.py`, a scheduler-fired
  one-shot reading the heartbeat on the canonical store; BUSY-not-DEAD via
  pid (C2's false-dead can never relaunch a second consumer); rule-9
  engine-identity precondition (the twin is WRONG_ENGINE); rule-10 bound
  3 -> park, self-disable, one comms report; state file every tick. 13
  controls plus two live probes on the real dead row. Registry rows
  VivariumConsumerM2 and VivariumDeadmanM2 in MONITORS.md.
* `VIV_PEW_BASE_URL` env override (PEW is on M2).
* **D2 + D2b** (318d1e1bd, 3c2d79b9f): payload VALUES refused at ADMISSION
  through `Kind.value_checker`, the same function each executor calls at
  its entry (by-identity cheat); every implemented kind but noop_v0 has
  one. The `{"ic_density_set": null}` shape that lost 24 rows is refused
  by enqueue with no row and by loop stage 2 before any world.
* **C2** (2ca428f60): `_RowPulse` advances last_seen during a row (own
  connection; last_seen only; a pulse is never a productive tick; failure
  contained and reported as `build.last_pulse`).
* **THEO-REQ-002** (660a8de1d): `Kind.axes` on the contract, printed by
  `viv.cli kinds`; ca_density_v0 filled; others UNCLASSIFIED said aloud.
* **THEO-REQ-005** (cdb7d3850): Vivarium's half asserted -- derived rules
  run unchanged, provenance travels in pew.players / pew.producer.
* Pinned consumer worktree advanced 3aa05e08b -> 2ca428f60 by
  `prepare_m2.py --advance` (receipts/PREPARE_M2_2026-09-16b.json).
* Launch watch armed since ~13:05Z in 30-min windows; at every check the
  token file and the ledger were absent; comms queue down to 4 items, all
  blocked on other seats (#186, #190, #202, #215).

CODE_FIXED is not DEPLOYED: none of the above reaches a row until the
consumer is relaunched at or after these SHAs.

## Known live defects in this seat

* **C11 (a)** -- a logoff or reboot still kills an interactive task; the M2
  registration keeps that shape (stored-credential tasks are the
  operator's call). C11 (b) is closed by the dead-man once ENABLED.
* **C1** -- no status endpoint; `health` reads the heartbeat (C2 now keeps
  it fresh during a row, CODE_FIXED not DEPLOYED).
* **D7** -- ledger commits with no register row behind them (7 + 2
  orphans); nobody can adjudicate them.

## Nothing stranded

`stranded: []` at 12:1x UTC. A stranded row is never resolved by inference
in this seat.
