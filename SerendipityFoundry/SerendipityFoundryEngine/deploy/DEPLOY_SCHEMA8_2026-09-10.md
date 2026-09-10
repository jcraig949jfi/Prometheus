# Deploying schema 8 to M1 — runbook

**Daedalus, 2026-09-10.** Authority: the operator, via Archaeon
(`roles/Archaeon/prompts/2026-09-10_delegation/DAEDALUS.md`), granted **subject
to three conditions**. This document is condition (c). It is committed *before*
the deploy on purpose: a rollback written after the outage is a post-mortem.

> **STATUS AT TIME OF WRITING: NOT DEPLOYED.** Condition (a) is not met.
> See [§0](#0-the-gate). Run `python deploy/preflight_deploy.py` — it prints
> `CLEAR TO DEPLOY` or `DO NOT DEPLOY` and never changes anything.

---

## 0. The gate

```
cd F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine    # or any checkout
python deploy/preflight_deploy.py --json
```

Fail-closed, and **UNKNOWN counts as failure**: "I could not tell whether the
campaign was still running" is exactly the state in which one must not restart
the engine underneath it.

| condition | gate | how it is answered |
|---|---|---|
| (a) | `cs-c3-2` drained | Vivarium's **live** queue, Archaeon's readout, and the engine's own ledger — all three must agree |
| (a) | engine quiet ≥ 300 s | no event written recently; a consumer mid-attempt writes continuously |
| (c) | this runbook committed | names a rollback and a backup |
| (c) | backup fresh (< 6 h) | taken with the service **stopped** |
| build | pin describes this tree | `engine_source_hash` recomputed from `sfe/*.py` |
| build | nothing readable becomes unreadable | see [§5](#5-the-one-thing-that-breaks-existing-data) |

The campaign's rows are in **Vivarium's Postgres**, not in the engine, so the
engine cannot see them. The SFE venv has no `psycopg2`; use the interpreter
that does:

```
cd F:\Prometheus\vivarium
H:\Python312\python.exe -m viv.cli ls --status queued  --limit 2000 | find /c "cs=cs-c3-2"
H:\Python312\python.exe -m viv.cli ls --status running --limit 2000 | find /c "cs=cs-c3-2"
H:\Python312\python.exe -m viv.cli ls --status claimed --limit 2000 | find /c "cs=cs-c3-2"
```

All three must be `0`. Note `viv.cli candidates cs-c3-2` does **not** answer
this — its view reports `registered / retained / executed` and never breaks out
queued vs running.

---

## 1. Identities

Four, and they are not interchangeable. Collapsing them is the failure this
project has already had.

| identity | value | names |
|---|---|---|
| `engine_source_hash` **before** | `sha256:084f951f866cc50aec73c6403528abc234fd514742b25ffd1aff5515a271feff` | the running BUILD — authoritative |
| `engine_source_hash` **after** | `sha256:5380cb90f42dc83b4c6bd4710566e92c3ca2a3d154eacca1069cbc40d187876e` | the candidate BUILD |
| `schema_version` | **7 → 8** | the LEDGER'S SHAPE |
| `engine_instance_id` **before** | `eng_8a37a5d305969034d488c43e` | the LEDGER |
| `engine_instance_id` **after** | `eng_8a37a5d305969034d488c43e` — **must be identical** | the LEDGER |
| git commit | see `deploy/CANDIDATE_BUILD.json` → `identities.git_commit` | a TREE, best-effort |

**The instance id must not change.** It is minted once per database and travels
with the substrate. If it differs after the restart, the service is pointed at a
*different ledger* and the deploy has replaced state rather than upgraded it —
stop and restore.

---

## 2. Before you touch anything

The deployment tree is `F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine`.

> **That tree is a shared working copy on `vivarium/v0-2026-09-05`, far behind
> `main`, carrying other roles' uncommitted work.** A deploy there is a **file
> copy**. Never `git checkout -- .`, `git clean`, `git pull` or `git switch` in
> `F:\Prometheus` to "fix" a deploy. `deploy\m1.key` also lives only on M1 and
> is never in git — do not copy over it.

```powershell
# 1. what is actually running now
curl.exe --cacert deploy\m1.crt https://192.168.1.202:8811/v2/version

# 2. the gate
python deploy\preflight_deploy.py
```

---

## 3. Deploy

```powershell
# --- STOP -------------------------------------------------------------
Stop-ScheduledTask -TaskName SFEngine
# Stop-ScheduledTask ALONE ORPHANS THE PROCESS TREE. The orphan keeps the
# socket and the OLD build goes on serving, so the deploy appears to do
# nothing. Tree-kill the launcher stub, then confirm the port is free.
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*SerendipityFoundryEngine\serve.py*' } |
  ForEach-Object { taskkill /PID $_.ProcessId /T /F }
Get-NetTCPConnection -State Listen -LocalPort 8811 -ErrorAction SilentlyContinue
#   ^ must return NOTHING before continuing.

# --- BACK UP (condition c) -------------------------------------------
# WITH THE SERVICE STOPPED. A file copy of a live SQLite database with a WAL
# is not a snapshot. THIS PATH IS THE ROLLBACK.
$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\backup"
New-Item -ItemType Directory -Force -Path $backup | Out-Null
python -c "import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute(\"VACUUM INTO ?\",(sys.argv[2],)); c.close()" `
  "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\engine.db" `
  "$backup\engine-schema7-$stamp.db"
Get-ChildItem $backup\engine-schema7-*.db | Select Name,Length,LastWriteTime

# --- COPY THE BUILD ---------------------------------------------------
# From a checkout at the deployed commit. sfe/*.py is what the build hash is
# computed over; serve.py and the client ship with it.
$src = "<your checkout>\SerendipityFoundry"
$dst = "F:\Prometheus\SerendipityFoundry"
Copy-Item "$src\SerendipityFoundryEngine\sfe\*.py"          "$dst\SerendipityFoundryEngine\sfe\"          -Force
Copy-Item "$src\SerendipityFoundryEngine\serve.py"          "$dst\SerendipityFoundryEngine\"             -Force
Copy-Item "$src\SerendipityFoundryClient\sfclient\*.py"     "$dst\SerendipityFoundryClient\sfclient\"     -Force

# --- THE CEILING (see section 5) -------------------------------------
# deploy\sfengine.cmd MUST pass --max-artifact-bytes 33554432, or one
# already-stored artifact becomes unreadable. Verify before starting:
Select-String -Path "$dst\SerendipityFoundryEngine\deploy\sfengine.cmd" -Pattern "max-artifact-bytes"

# --- START ------------------------------------------------------------
Start-ScheduledTask -TaskName SFEngine
Start-Sleep -Seconds 25          # binding can take ~20s
curl.exe --cacert deploy\m1.crt https://192.168.1.202:8811/v2/version
```

The migration runs on the **first open**, inside `Store.initialize()`. It is
additive: `_migrate_7_to_8` adds `budget_reservations` and `cost_events` and
back-fills nothing. There is **no down-migration**.

### Verify

```powershell
python deploy\verify_deploy.py
```

Expect `schema_version: 8`, `engine_source_hash:
sha256:5380cb90f42dc83b4c6bd4710566e92c3ca2a3d154eacca1069cbc40d187876e`, and
`engine_instance_id: eng_8a37a5d305969034d488c43e` **unchanged**.

---

## 4. ROLLBACK

Code alone is **not** a rollback across a migration. A schema-7 engine opened
against a schema-8 ledger **refuses to start**:

> `RuntimeError: db schema version 8 is NEWER than this engine's 7; refusing to
> run (would misread state)` — `sfe/store.py`

That is the correct failure direction — a loud outage rather than a silent
downgrade of live data — and it is why the **snapshot is the rollback**.

```powershell
# 1. stop, and tree-kill as in section 3
Stop-ScheduledTask -TaskName SFEngine
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*SerendipityFoundryEngine\serve.py*' } |
  ForEach-Object { taskkill /PID $_.ProcessId /T /F }

# 2. RESTORE THE DATA. Both halves, or neither.
$backup = "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\backup"
$latest = (Get-ChildItem $backup\engine-schema7-*.db | Sort LastWriteTime -Desc)[0].FullName
$var    = "F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var"
Move-Item "$var\engine.db" "$var\engine-schema8-failed-$(Get-Date -Format 'yyyyMMdd-HHmmss').db"
Remove-Item "$var\engine.db-wal","$var\engine.db-shm" -ErrorAction SilentlyContinue
Copy-Item $latest "$var\engine.db"

# 3. RESTORE THE CODE, from a checkout you own — never by git-cleaning F:\Prometheus
git -C <a checkout you own> fetch origin
git -C <a checkout you own> checkout 85d6ff06049fe399ecf6dbda3c3e430d8c8f48e7 -- SerendipityFoundry/
#   then copy sfe\*.py, serve.py and sfclient\*.py in exactly as in section 3

# 4. start, and verify the instance id is STILL eng_8a37a5d305969034d488c43e
Start-ScheduledTask -TaskName SFEngine
Start-Sleep -Seconds 25
curl.exe --cacert deploy\m1.crt https://192.168.1.202:8811/v2/version
```

**What a rollback costs:** every cost event and budget reservation written under
schema 8 between the deploy and the rollback. They live only in the schema-8
ledger, and the restored snapshot predates them. Keep the failed database
(step 2 moves it aside rather than deleting it) — it is the only copy.

---

## 5. The one thing that breaks existing data

v8 introduces a per-artifact size ceiling where there was **none**, and it
applies on **read** as well as write (`sfe/runtime.py`, `get_artifact_content`:
`if len(content) > ceiling: raise ValidationError(...)`).

Measured on the live store, 2026-09-10:

| | |
|---|---|
| v8 default ceiling | 16 777 216 B (16 MiB) |
| blobs stored | 2 138 |
| **over the ceiling** | **1** — `sha256:05f052c8…`, 33 554 432 B (32 MiB) |
| that artifact | `wld_275033f4505ae3ac8a6b69c1`, NATIVE, created 2026-09-03 |
| next largest blob | 8 MiB — comfortably clear |

Under the default, that artifact becomes **unreadable** the moment the new build
starts. Not corrupted, not deleted — refused. A deploy may add a limit; it must
not silently retire data that was readable an hour earlier.

**Therefore `deploy\sfengine.cmd` must pass `--max-artifact-bytes 33554432`.**
That keeps every existing artifact readable while still installing a ceiling
where there was none. The preflight gate checks this and fails without it.

---

## 6. Who else moves in this window

Batch these into the same window; each is a fail-closed check on someone else's
side that a build change trips.

1. **Archaeon's reader guard — 7 → 8.** `archaeon/config.py`
   (`expected_schema_version: int = 7`) with the guard in `archaeon/fossils.py`
   (`if have_v is None or have_v > ten.expected_schema_version:`) means
   Archaeon's fossil reader **refuses a schema-8 ledger**. The order says
   Archaeon moves it on this report. *Owner: Archaeon.*
2. **Harmonia's conformance contract.** `roles/Harmonia/contracts/sfe_contract.json`
   pins `engine_source_hash` **exactly** and `conformance_check.py` is
   fail-closed, so any build change halts the automated seats. It is **already
   stale** — pinned schema 6 / `sha256:2f42e87f…` against a live schema 7 /
   `sha256:084f951f…`, so it has been stale since the v7 deploy and is overdue
   independently of this one. Regenerate with
   `roles/Harmonia/contracts/generate_sfe_contract.py`. *Owner: Harmonia.*
3. **Vivarium restarts the consumer — condition (b).** The consumer holds a
   client and a session against the old build; it must be restarted after the
   engine is up, and the restart confirmed in the deploy report. *Owner:
   Vivarium.*

---

## 7. After

- `python deploy/make_pin.py` → refresh `deploy/DEPLOYED_BUILD.json`
  (it has hardcoded a schema version before; check the value it writes).
- `python deploy/verify_deploy.py` → must be clean.
- Record in this file: the actual `engine_instance_id` before and after, the
  backup filename, and the timestamp of the restart.

### Deploy record

| | |
|---|---|
| deployed at | *not yet deployed* |
| instance id before | `eng_8a37a5d305969034d488c43e` |
| instance id after | — |
| backup file | — |
| verify_deploy | — |
| consumer restarted by Vivarium | — |
