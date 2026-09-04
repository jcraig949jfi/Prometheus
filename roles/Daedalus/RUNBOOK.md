# Serendipity Foundry Engine — Operations Runbook (Daedalus)

Operational reference for keeping the Engine alive, healthy, and honest. All
paths are on **M1 / SKULLPORT** unless noted.

> **Two engines are live since 2026-09-04.** M1 is the original; M2 / SPECTREX5
> (`192.168.1.191`, repo on `D:`) runs a second, independent engine with its own
> empty database, its own TLS cert, and its own tokens. Every `F:`/`H:` path and
> every `192.168.1.202` URL below is M1-only. The difference sheet — paths,
> launchers, watchdogs, restart discipline, wind-down — is
> [`SerendipityFoundry/SerendipityFoundryEngine/docs/RUNNING_M1_VS_M2.md`](../../SerendipityFoundry/SerendipityFoundryEngine/docs/RUNNING_M1_VS_M2.md).
> The Evidence Wiki is deliberately NOT forked the same way: M2's PEW serves
> M1's canonical Postgres. Read that document's PEW section before touching
> anything on M2 — a local restored copy of `prometheus_fire` sits on M2's own
> Postgres and a defaulted `python -m ew.service` there will serve it.

> **This is a maintainer document.** Several steps below run only on M1.
> If you are *integrating* against the Engine from another machine, read
> [`integration/HARMONIA_FIRST_INTEGRATION.md`](../../integration/HARMONIA_FIRST_INTEGRATION.md)
> instead, and run the standard battery:
> `python integration/sfe_battery.py --cacert SerendipityFoundry/SerendipityFoundryClient/config/m1.crt`
>
> Two operator cautions that have already cost time, detailed in that document's
> §10: the Engine legitimately runs as **two** `python.exe` processes (a launcher
> stub and its child — killing the parent kills the server), and reachability is
> answered by `deploy/sfengine.log`, **not** by `Get-NetTCPConnection`, which
> shows only sockets alive at that instant and will report "no clients" on a
> service handling thousands of requests.

## Facts

| | |
|---|---|
| Engine host | M1 / SKULLPORT, IP `192.168.1.202` |
| Listen | `https://192.168.1.202:8811`, TLS, `/v2` API |
| Service | Windows scheduled task **`SFEngine`** (S4U, AtLogOn + AtStartup, runs on battery, no time limit) |
| Launch cmd | `F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\deploy\sfengine.cmd` |
| Interpreter | `H:\Python312\python.exe` (via the project venv) |
| DB | `...\SerendipityFoundryEngine\var\engine.db` (SQLite WAL — authoritative substrate) |
| TLS | `deploy\m1.crt` / `deploy\m1.key` (CN/SAN `192.168.1.202`, valid → Dec 2028). **Key never leaves M1, never enters git.** |
| Firewall | inbound rule `SFEngine (LAN)`, Allow, TCP 8811, RemoteAddress `192.168.1.0/24` |
| Log | `deploy\sfengine.log` |
| Neighbor (do NOT disturb) | live D-13 service on `192.168.1.202:8799` |

## Liveness

```bash
curl --cacert config/m1.crt https://192.168.1.202:8811/v2/version
# → {"api":"v2","schema_version":3,"runtime":"serendipity-foundry-sfe",
#    "registration_open":true,"engine_source_hash":"sha256:…","source_commit":"…"}
```
```powershell
Get-NetTCPConnection -State Listen -LocalPort 8811 | Select LocalAddress,OwningProcess
(Get-ScheduledTask -TaskName SFEngine).State
```

## Clean restart (the ONLY correct way)

The task wrapper does not always stop its child python, which then orphans the
port. Always: stop → kill any orphan on 8811 → start → verify.

```powershell
Stop-ScheduledTask -TaskName SFEngine
Start-Sleep -Seconds 2
$p = (Get-NetTCPConnection -State Listen -LocalPort 8811 -ErrorAction SilentlyContinue).OwningProcess
if ($p) { Stop-Process -Id $p -Force }          # kill the orphan (only on 8811!)
Start-ScheduledTask -TaskName SFEngine
Start-Sleep -Seconds 3
Get-NetTCPConnection -State Listen -LocalPort 8811 | Select OwningProcess
```
Then confirm `/v2/version` answers before declaring it up. **Never** kill the
process on 8799 (that is the D-13 instrument).

## Graceful quiesce (maintenance)

`Stop-ScheduledTask -TaskName SFEngine`, then kill any orphan on 8811 as above.
SQLite WAL leaves `var/engine.db` consistent on process exit; no special drain is
required, but do not `rmtree` the var dir while the process holds it.

## Firewall / reachability troubleshooting (the D-13 gotcha)

If a LAN client (e.g. M2 = `192.168.1.191`) times out:
1. Confirm the client is on `192.168.1.0/24` and can `ping 192.168.1.202`.
2. Confirm the allow rule: `Get-NetFirewallRule -DisplayName "SFEngine (LAN)"` is
   Enabled, Action Allow, Profile Any.
3. Check for a **program-level Block rule** on the Engine's python exe that
   shadows the port allow (Block beats Allow):
   ```powershell
   $exe = (Get-Process -Id (Get-NetTCPConnection -State Listen -LocalPort 8811).OwningProcess).Path
   Get-NetFirewallRule -Direction Inbound -Enabled True -Action Block |
     ? { ($_ | Get-NetFirewallApplicationFilter).Program -ieq $exe }
   ```
   If any match, disable it (`Disable-NetFirewallRule`). As of 2026-09-01 the
   Engine exe (`H:\Python312\python.exe`) is NOT shadowed.

## Standing verification battery (after ANY change, before ANY onboarding)

From `SerendipityFoundryClient/`:
```bash
python -m pytest ../SerendipityFoundryEngine/tests -q      # unit + isolation regressions (all green)
python test_harness/harness.py                             # live capability harness (12/12)
python test_harness/isolation_two_experimenters.py         # live isolation (7/7)
```
And confirm the D-13 pin is untouched:
```bash
grep source_tree_hash F:/SerendipityD/RELEASE_MANIFEST.json   # 50b5c232…
```

## Minting a client token (onboarding an experimenter)

Registration is unauthenticated; the token is shown once and stored only as a
hash. Do it from any LAN client that trusts the cert:
```bash
curl --cacert config/m1.crt -X POST https://192.168.1.202:8811/v2/clients \
     -H 'content-type: application/json' -d '{"name":"harmonia-m2"}'
# → {"client_id":"cli_…","token":"gen2_…","note":"token shown once; store it"}
```
Hand the experimenter: the base URL, the **public** cert `m1.crt`, and their
token. Never send the private key.
