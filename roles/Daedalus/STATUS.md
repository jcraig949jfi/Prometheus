# Daedalus -- status

Currency: 2026-09-12 13:55 local -- seat IDLE/parked on the operator's instruction; wakes on Harmonia's contract result or a substrate failure (base role s3 requires this file; refreshed at
least every four hours of activity).

## Where I am working

| | |
|---|---|
| worktree | `F:\Prometheus-worktrees\daedalus-d23` |
| branch | `daedalus/d23-workspace` |
| base_sha | `c8d576e41` at boot; merged forward to `de033f529` |
| dirty | no (tracked) |
| base role read at | `2b79c140a`; re-read at `c8d576e41` |
| comms | booted 14:06; queue EMPTY at 17:24 (6, 35, 29, 32 done); last sync read through 181 |

## What is running

| | |
|---|---|
| SFE on M1 | `https://192.168.1.202:8811`, schema **8** |
| build | `sha256:5380cb90f42dc83b4c6bd4710566e92c3ca2a3d154eacca1069cbc40d187876e` |
| ledger | `eng_8a37a5d305969034d488c43e`, **`D:\Prometheus-data\sfe\engine.db` (NVMe, since 09-12 11:58)**; F: copy = rollback, not deleted |
| code from | `F:\Prometheus-worktrees\daedalus-sfengine`, detached `d5be5ec4b` |
| process | restarted by me 09-12 11:59 for the ledger move (outage 80.2 s, receipt `deploy/LEDGER_MOVE_2026-09-12/apply.json`) |
| SFE on M2 | `https://192.168.1.191:8811`, schema **4** (`0fd24e0f3`), verify twin, no consumer |

## Engine health, plainly

PRESENT, ACTIVE, VALID at rest, and the measured stall trigger is gone from
the path: the ledger moved off the Seagate HDD to NVMe on 09-12 11:58.
Acceptance (same C9 shape): before 633.8 s / 53 calls over 5 s; after
20.5 s / 0. **STORAGE_REMEDY_CONFIRMED** (`deploy/LEDGER_MOVE_2026-09-12/
ACCEPTANCE.md`). Not shown: that minute-scale episodes cannot recur by some
other trigger; Vivarium's stall detector remains the instrument.

## Open, in order (operator's reorder of 17:00, relayed review)

Done today after the reorder: MONITORS repair (`b11c9931b`: SFEngine
not-a-loop with its real freshness gap; M2 watchdog state file + 3-tick
bound + park, CODE_FIXED not deployed on M2); B1 readiness (`f2b8b3415`:
tool for the owner, delegations to Vivarium and Archaeon, grantee principal
is the gap); KAIROS-01 (`8fc4531f3`: census (b), 8 claims on M1, all mine).

1. Deploy candidate `8c53d04e6` (A6 + B3 + C7, hash 726275da) in one
   window ONCE Harmonia regenerates the contract (comms 215); otherwise
   both consumers' gates read state 3.
2. B1 ISSUED by Vivarium and verified (gnt_1ecdeae6; deploy/B1_2026-09-12).
   Archaeon's parity + retirement of the raw-ledger read (F-25) is theirs.
3. Ancestry: COMPLETE on the canary, no schema (deploy/fossil_ancestry.py).
4. Archaeon re-points sfe_db to D: (216); F: copy is frozen.
3. **A6** vocabulary revised with the operator, then A6 + B3 + C7 (+ H1)
   in ONE deploy window.
4. Canonical-copy deletion, separately from any engine restart.
5. D-WD-1: an M1 watchdog with the rule-10 bound (M1 has none today).

## Blocked on someone else

- B1: Vivarium runs the grant tool at its next sync (grantee posted by
  Archaeon, comms 185); I post scope id + lifecycle from its receipt.
- nk_landscape_v0: Archaeon's yes/no on the permutation direction (inside
  `spec_hash`) before any corpus; Vivarium's registration (comms 186).
- `archaeon/tests/conftest.py` forces Postgres on the base-role self-check
  (prompt at `roles/Daedalus/prompts/2026-09-11_base_role/`).

## Held awaiting the operator

- Deploy window for the next build (A6 + C7 + B3 + any H1 fix): a restart.
- Removal of the canonical copies of the ledger, blobs, rollback and key.
- The four-verdict vocabulary in `DESIGN_A6_ATTESTATION_2026-09-11.md`.
