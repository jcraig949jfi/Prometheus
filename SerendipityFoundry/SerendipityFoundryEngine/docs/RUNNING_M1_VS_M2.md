# Running the Engine on M1 vs M2

> **TOPOLOGY RULING (operator, 2026-09-16).** Postgres and Redis are the
> shared substrate (on M1, the canonical store); **every other service runs
> on exactly one machine, never both**. A farm is a future roadmap item and
> to date does not merit it. The Serendipity Foundry Engine's machine is
> **M2** from 2026-09-16. The M1 engine was stopped ~2026-09-15 20:15Z for the
> move and is not coming back; its ledger (eng_8a37a5d3, the production
> identity) is adopted on M2 by `deploy/adopt_m1_ledger.py` once the operator
> lands the data dir here. Until that swap, the engine on M2 serves the twin
> ledger eng_906356f7 and is NOT production (Daedalus ruling, comms #270).
> Everything below that describes "two engines" is history from 2026-09-04
> to 2026-09-15, kept so the shape of the move can be explained; the M1
> column no longer describes a running service.

Two Serendipity Foundry Engines are live as of 2026-09-04, one per machine.
They are **separate engines with separate substrates** — not a cluster, not a
replica pair, and not a failover. Nothing is shared between them.

This document is the M1/M2 difference sheet. `roles/Daedalus/RUNBOOK.md` remains
the operational runbook; where it names a path or a command, this table says
which machine it is true on.

## Why there are two

M1's Claude token budget ran out on 2026-09-04, so the agent work moved to M2
for a few days. M1's services never stopped — they are scheduled tasks and a
watchdog, which need no agent — so M1 stays authoritative for everything it
already held, and M2 got its own instance for new work.

## The difference sheet

| | **M1 / SKULLPORT** | **M2 / SPECTREX5** |
|---|---|---|
| LAN address | `192.168.1.202` | `192.168.1.191` |
| Repo root | `F:\Prometheus` | `D:\Prometheus` |
| Engine tree | pinned worktree `F:\Prometheus-worktrees\daedalus-sfengine` (detached `d5be5ec4b`, since 2026-09-11) | pinned worktree `D:\Prometheus-worktrees\daedalus-sfengine` (detached `ccb26df01` = candidate `726275da`, since **2026-09-16 11:48Z**; before that the canonical checkout, which serve.py's D-23 guard refused from 2026-09-14 05:33 until the move -- the engine was DEAD those two days) |
| Interpreter | `H:\Python312\python.exe` (project venv) | `D:\Prometheus\.venv-m2\Scripts\python.exe` (3.12.10) |
| Engine URL | `https://192.168.1.202:8811/v2` | `https://192.168.1.191:8811/v2` |
| TLS cert (public) | `deploy\m1.crt`, SAN `192.168.1.202`, valid to Dec 2028 | `deploy\m2.crt`, SAN `192.168.1.191`, valid to Sep 2036 |
| TLS key (never in git) | `D:\Prometheus-data\sfe\m1.key`, stays on M1 | `C:\Prometheus-data\sfe\m2.key`, stays on M2 (on the NVMe since 2026-09-17 23:12Z; the `D:\Prometheus-data\sfe` copy is the rollback; the `deploy\` copy is not yet removed) |
| Launcher | `D:\Prometheus-data\sfe\sfengine.cmd` (outside the repo, since 2026-09-12) | `C:\Prometheus-data\sfe\sfengine_m2.cmd` (outside the repo; on the NVMe since 2026-09-17; the tracked `deploy\sfengine_m2.cmd` is superseded and refused by the guard) |
| Database | `D:\Prometheus-data\sfe\engine.db` on M1 (NVMe, since 2026-09-12) | `C:\Prometheus-data\sfe\engine.db` on M2 (NVMe since 2026-09-17 23:12Z -- on M2 `D:` is the Seagate ST8000DM004 **SMR HDD**, which stopped servicing writes 3.4 h into campaign-rate load, see `deploy/LEDGER_TO_NVME_2026-09-17/`; ledger `eng_906356f7`, schema 9) — **a different database**; the canonical `var\engine.db` copy is the schema-4 rollback and is not deleted. Same path string on both machines: identity is the `engine_instance_id`, never the path |
| Kept alive by | scheduled task `SFEngine` (S4U, AtLogOn+AtStartup) | watchdog task `SFEngineM2Watchdog` (S4U, AtStartup + every 5 min) running the PINNED copy `C:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1` (on the NVMe since 2026-09-17; a tracked script under the canonical checkout was replaced mid-run by a `git pull` on 2026-09-16 11:40Z, which is why it is pinned) |
| Log | `D:\Prometheus-data\sfe\sfengine.log` | `C:\Prometheus-data\sfe\sfengine_m2.log`, watchdog `C:\Prometheus-data\sfe\sfengine_m2_watchdog.log` + `.state.json` (every tick) + `.park.json` (on park) |
| Firewall rule | `SFEngine (LAN)`, TCP 8811, `192.168.1.0/24` | `SFEngine M2 (LAN)`, TCP 8811, `192.168.1.0/24` |
| Neighbour to leave alone | D-13 instrument on `:8799` | *(none — D-13 does not run here)* |
| D-13 release pin check | `F:\SerendipityD\RELEASE_MANIFEST.json` gives `50b5c232…` | **not applicable**; there is no `F:` drive on M2 |

Two consequences worth stating plainly:

* **Client identity does not cross machines.** A `gen2_…` token minted on M1 is
  unknown to M2 and vice versa. Register separately on each engine you use.
* **World ids do not cross machines either.** Both engines mint ids from the
  same scheme, so a world id from M1 may be *syntactically* valid on M2 and
  still refer to nothing. Always record which engine a world came from. Moving
  an artifact between them is the explicit import path, which stamps
  `origin=IMPORTED` with source lineage — never a silent copy.

## Keeping alive: why M2 uses a watchdog and M1 uses a task

M1 runs the Engine as an always-on scheduled task and has no watchdog: it comes
back at boot and at logon, but a crashed process stays dead until someone looks.
M2 uses a 5-minute watchdog that probes `/v2/version` and relaunches on failure,
plus an AtStartup trigger, so it recovers from a crash as well as a reboot. Both
principals are S4U, so both survive lock screen and logout.

The M2 watchdog probes `https://192.168.1.191:8811/v2/version` with
`--cacert m2.crt` — not `localhost`, because the Engine binds its LAN address
specifically and never `0.0.0.0`.

## Restart discipline on M2

Same shape as M1's, different names. The launcher `cmd.exe` spawns a child
`python.exe`; killing only one of them leaves the port held.

    # stop: kill whatever holds 8811 AND its launcher parent
    $id = (Get-NetTCPConnection -State Listen -LocalPort 8811).OwningProcess
    $p  = Get-CimInstance Win32_Process -Filter "ProcessId=$id"
    Stop-Process -Id $id -Force; Stop-Process -Id $p.ParentProcessId -Force

    # start: let the watchdog do it, so the running instance is the supervised one
    powershell -NoProfile -ExecutionPolicy Bypass -File `
      C:\Prometheus-data\sfe\sfengine_m2_watchdog.ps1

Verify before declaring it up:

    curl --cacert deploy/m2.crt https://192.168.1.191:8811/v2/version

To advance the M2 build: `git -C D:\Prometheus-worktrees\daedalus-sfengine checkout --detach <sha>`,
then stop + let the watchdog restart, then re-pin `deploy/DEPLOYED_BUILD_M2.json`.
The relocation itself is receipted in `deploy/M2_RELOCATE_2026-09-16/` (tool `deploy/relocate_m2.py`).

On M2 there is no service on `:8799` to protect — but there IS a local
PostgreSQL on `:5432`; see the hazard below.

## Backing up the ledger (9.0.1 and later): never a file copy

Since 9.0.1 the engine holds its SQLite connections OPEN for the life of the
process (a checkout/checkin pool with `wal_autocheckpoint=0`, plus the
checkpointer thread), so `engine.db` on disk is NOT the ledger at any instant:
committed pages sit in `engine.db-wal` until the checkpointer moves them, and a
plain copy of `engine.db` (or of the db+wal pair mid-write) is a torn or stale
snapshot that opens without error. A backup is one of:

    # the SQLite backup API from another process -- consistent, no outage
    python - <<'PY'
    import sqlite3
    src = sqlite3.connect("file:C:/Prometheus-data/sfe/engine.db?mode=ro", uri=True)
    dst = sqlite3.connect("C:/Prometheus-data/sfe/backup/engine_<stamp>.db")
    src.backup(dst); dst.close(); src.close()
    PY

    # or what release_v9.py preflight does: backup API, then re-open the copy
    # and read it (schema_version, row counts) before calling it a backup

Restoring is the reverse and needs the SERVICE STOPPED first (the restart
discipline above), then the copy put in place with no `-wal`/`-shm` files
beside it; `SFE_SCHEMA9_MIGRATION_RECEIPT.md` R1-R6 is the rehearsed
sequence. `test_sfe_session_affinity.py`'s restore test pins the API path.

## Firewall on M2 — the same gotcha as M1, one machine over

M2's NIC is categorized **Public**, and Windows had auto-created two "Query
User" **Block** rules (TCP and UDP, Public profile) scoped to the program
`C:\users\james\appdata\local\programs\python\python312\python.exe` — the exact
interpreter both services run as. A program-level Block beats a port-level
Allow, so the `192.168.1.0/24` allows on 8811 and 8377 never fired.

The symptom is worth memorizing, because it names the cause: an off-box client
gets a **connection timeout, not a refusal**, while `ping` succeeds. A drop is
firewall-shaped; a service bound to the wrong interface would answer with RST.
Verified on 2026-09-04 by having M3 (`192.168.1.176`) curl both ports — both
timed out at 10 s while M1 answered instantly as a positive control.

    # find a program-level block that shadows the port allow
    Get-NetFirewallRule -Direction Inbound -Enabled True -Action Block |
      Where-Object { ($_ | Get-NetFirewallApplicationFilter).Program -match 'python' } |
      Select DisplayName, Profile
    # disable by rule Name (not DisplayName -- these share one)
    Disable-NetFirewallRule -Name "<the Query User{...} name>"

Disabling those opens nothing by itself: the default inbound action is still
Block, and the two scoped Allow rules remain the only thing admitting traffic.
Expect the prompt to return for a *new* interpreter path — answering the
Windows Security Alert with Cancel is what creates these rules in the first
place.

## Minting the M2 cert (or rotating it)

`deploy/make_cert.py` mints a self-signed cert whose CN and SAN are the bind IP,
which is what lets a client pin the cert as its own CA and still pass hostname
verification:

    python deploy/make_cert.py --ip 192.168.1.191 --prefix m2

It refuses to overwrite an existing pair, because rotating a key invalidates
every client's trust anchor. `deploy/.gitignore` excludes `*.key`: the public
`.crt` is committed so clients can trust the engine; the key never leaves the
machine that serves with it.

## The Evidence Wiki (PEW) is the opposite case — read this before touching it

> **SUPERSEDED 2026-09-04 (Mnemosyne).** James ruled that M2 must be FULLY
> INDEPENDENT, PEW included. PEW is now forked on purpose too, exactly like the
> Engine: M2 serves its OWN local `prometheus_fire` (`db_host=localhost`) and
> the two evidence stores diverge from here on — evidence no longer crosses
> machines. The canonical-pointing setup below is HISTORY.
>
> What changed: `scripts\ew_watchdog_m2.ps1` now starts the vanilla
> `python -m ew.service` (bind 0.0.0.0, M2-local Postgres) — no `EW_DB_HOST`
> override; `ops\pew_serve_m2.*` is retired (unused). M2-local `ew` was
> re-seeded from a fresh consistent dump of M1's current `ew` (write_log 3174)
> as the independent starting point, and the fork quarantine was undone. E0-E13
> battery vs 127.0.0.1 = all_pass with M1 write_log provably unchanged
> (independence verified). M1 stays authoritative for itself and is untouched.
> The "read this before touching it" text below is kept for provenance.


The Engine is *forked on purpose*: two engines, two substrates, new work on M2.
PEW is **not**. There is exactly one canonical evidence store — the
`prometheus_fire` database on M1 — and M2's PEW service reads and writes that
one over the LAN.

| | M1 | M2 |
|---|---|---|
| PEW URL | `http://192.168.1.202:8377` | `http://192.168.1.191:8377` |
| Started by | `python -m ew.service` (config defaults) | `evidence_wiki\ops\pew_serve_m2.cmd` |
| Postgres it serves | `localhost` on M1 = **canonical** | `192.168.1.202` = **the same canonical store** |
| Watchdog task | `MnemosyneEvidenceWikiWatchdog` → `scripts\ew_watchdog.ps1` | `MnemosyneEvidenceWikiWatchdogM2` → `scripts\ew_watchdog_m2.ps1` |
| Firewall rule | `Mnemosyne Evidence Wiki 8377` | `Mnemosyne Evidence Wiki M2 8377` |

> **Hazard, live on M2 right now.** M2 has its own PostgreSQL 17.11 — a
> different server (`system_identifier 7681719240261676752`, against M1's
> `7628127204585430828`) — holding a **restored copy** of `prometheus_fire`,
> current as of the 06:20:27 write on 2026-09-04. It is not a replica:
> `pg_is_in_recovery()` is false, so it is writable and will silently diverge
> the moment anything writes to it. A bare `python -m ew.service` on M2 reads
> `config.json`'s `db_host=localhost` and serves **that copy**. That is why M2
> has its own launcher and its own watchdog script, and why the M1-named task
> `MnemosyneEvidenceWikiWatchdog` was deleted on M2: it would resurrect the
> service pointed at the fork.
>
> As of 2026-09-04 12:43 the copy is identical in census to M1 (30 tables,
> 23,480 rows, same latest `write_log` timestamp) and **has not diverged**.
> Treat it as a warm restore of a backup, nothing more. Do not point a service
> at it. For a stronger guard, rename the local database so a defaulted client
> fails loudly instead of writing to a fork.

## Verification battery on M2

All four ran green on 2026-09-04 against the M2 instance:

    # from the repo root
    ./.venv-m2/Scripts/python.exe -m pytest SerendipityFoundry/SerendipityFoundryEngine/tests -q
    #   -> 88 passed

    # from SerendipityFoundryClient/
    ../../.venv-m2/Scripts/python.exe test_harness/harness.py \
        --base-url https://192.168.1.191:8811 --cafile config/m2.crt
    #   -> 12/12 capabilities PASS
    ../../.venv-m2/Scripts/python.exe test_harness/isolation_two_experimenters.py \
        --base-url https://192.168.1.191:8811 --cafile config/m2.crt
    #   -> 7/7 isolation properties hold

    # from evidence_wiki/ — note EW_DB_HOST, or the SQL gates read the local fork
    EW_DB_HOST=192.168.1.202 ../.venv-m2/Scripts/python.exe integration/pew_battery.py \
        --host 192.168.1.191 --port 8377 --machine M2 --agent daedalus-m2-bringup
    #   -> 15/15 gates PASS

The harness defaults still point at M1 (`https://192.168.1.202:8811`,
`config/m1.crt`). That is deliberate — M1 is the older, fuller instance — so on
M2 you must pass `--base-url` and `--cafile` every time. Passing neither tests
M1, which will look like a pass and tell you nothing about M2.

## Winding M2 down

When the M2 window ends, the M2 engine's `var/engine.db` is the only copy of any
work done there. Decide deliberately: keep it, export the artifacts worth
keeping into M1's engine through the import path (which stamps provenance), or
archive the file. Then:

    schtasks /Delete /TN SFEngineM2Watchdog /F
    schtasks /Delete /TN MnemosyneEvidenceWikiWatchdogM2 /F
    Get-NetFirewallRule -DisplayName "SFEngine M2 (LAN)" | Remove-NetFirewallRule
    Get-NetFirewallRule -DisplayName "Mnemosyne Evidence Wiki M2 8377" | Remove-NetFirewallRule

then kill both services and their launcher parents. M1 needs no change at any
point: it never knew M2's engine existed, and M2's PEW was only ever a second
front door onto M1's own database.

*Daedalus, 2026-09-04*
