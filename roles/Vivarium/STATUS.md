# VIVARIUM -- status

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md
> (operator, D-23, 2026-09-11); this file adds to them and may not
> contradict them.

**Currency: 2026-09-17 16:4x UTC (12:4x local).** Updated at least every four
hours of activity, per base role s3. Instance for this pass: `m2-fce3fe0b`,
the first boot of this seat on M2 (SPECTREX5), worktree
`D:\Prometheus-worktrees\vivarium-boot-2026-09-16` from `ccb26df01`.

## Is Vivarium alive

**YES.** `vivarium@m2` runs from the pinned detached worktree
`D:\Prometheus-worktrees\vivarium-consumer` at the SHA in
`D:\Prometheus-data\vivarium\var\restart-vivarium@m2.json` (08081c6ed at this
writing), launched and relaunched by the Task Scheduler task VivariumDeadmanM2
(every 5 min; a dead pid is detected after 60 s). Production `viv` carries
migrations 001-010 (window C4-20260917-W1, 2026-09-17 13:46Z-16:xxZ). Engine
eng_906356f7 at https://192.168.1.191:8811 (schema 9). PEW writes wait on
Mnemosyne's token in the outbox (deliverer HELD_NO_CREDENTIAL).

    read it       python -m viv.cli status   /   var\restart-vivarium@m2.json   /   var\deadman-vivarium@m2.state.json
    stop it       python -m viv.cli stop --worker-id vivarium@m2      (clean; the dead-man honours the flag)
    unpark        python -m viv.cli unpark --worker-id vivarium@m2 --by <seat> --reason <why>
    recover       python -m viv.cli release <id> --new-attempt --by <seat> --reason <why>   (stranded OR ENGINE_TRANSPORT-failed rows)
    redeploy      sh vivarium/deploy/redeploy.sh <sha>   (clean stop -> advance the pin -> dead-man relaunch -> restart receipt)

Disposition: **QUALIFIED_FOR_CAMPAIGN** / DEPLOYED_AND_QUALIFIED --
`roles/Vivarium/point_release/READINESS_DISPOSITION.md` (caveats: engine stalls
are Daedalus's 9.0.1; PEW token is Mnemosyne's; B1 read grant must be re-issued
on the M2 ledger).

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

## Point release: where it stands (2026-09-17 16:4x UTC)

    window C4-20260917-W1     EXECUTED: backup verified; 006-010 applied; old rows unchanged; identities bootstrapped;
                              dead-man + deliverer ENABLED; restart receipt ok; s13 fixture 16/16 at the deployed SHA;
                              s14 canary: 9 runs, 10 production defects found and fixed with acceptance tests
                              (READINESS_DISPOSITION.md s2); the hardest row (killed while posting, then a real
                              engine stall) recovered on production in 3 attempts with ONE world and exactly 12
                              observations
    disposition               QUALIFIED_FOR_CAMPAIGN (caveats named); receipts under receipts/window_C4-20260917-W1/
    open, not mine            engine stall (Daedalus 9.0.1, not deployed); PEW writer token (Mnemosyne); B1 read grant
                              for cli_2bb36261 on the M2 ledger (Archaeon/Daedalus); sfclient labels kwarg

## Queue, at this writing (canonical store, UTC)

    queued 5      Archaeon's rows, HELD to 2027-01-01 (viv.cli hold; `held` events); the restart refused until held
    canary rows   created_by vivarium-canary: completed / failed (typed) -- no Campaign 4 work exists in the queue
    outbox        PENDING rows accumulate (no PEW token); deliverer HELD, never parks on that
    last real row 8bc6b162 completed 2026-09-14 23:27:07Z (pre-release)

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
