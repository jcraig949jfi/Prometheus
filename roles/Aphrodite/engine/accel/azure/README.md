# Azure CPU acceleration -- ACCEL_CANARY_v1 run kit (WRITTEN, NOT EXECUTED)

Engineering/conformance track only (operator ruling 2026-09-23). Nothing here
has been run against Azure: the M4 host has no `az` CLI and no Azure
credential, and the seat did not install or search for either. No Azure result
may be used scientifically until `ACCEL_EQUIVALENCE_*.json` from the VM says
`EQUIVALENT` with 0 mismatches under `../ACCEL_CANARY_v1.md`.

## Files

| file | role |
|---|---|
| `azure.env` | config: PINNED_SHA, region, VM size, workers, hard ceiling, price assumptions |
| `budget_guard.py` | refuses (exit 3) if the worst-case cost > $3 |
| `run_azure_canary.sh` | whole lifecycle; ALWAYS deletes the resource group |
| `cleanup.sh` | deletes every RG tagged `purpose=aphrodite-accel-canary` (idempotent sweep) |

## Cost model (assumed list prices -- verify before running)

| item | assumed USD/h |
|---|---|
| Standard_F16s_v2 (16 vCPU, 32 GiB, Linux PAYG, East US) | 0.677 |
| 30 GB StandardSSD OS disk (E4, ~$2.40/month) | 0.0033 |
| Standard public IPv4 | 0.005 |
| **all-in** | **0.6853** |

Guard formula: `worst = all_in * ceil(MAX_MINUTES/60) * 1.10 + $0.05`.
With `MAX_MINUTES=90`: billed as 2 h -> **worst case $1.56**. The largest
whole-hour ceiling under $3 is **3 h** (3 x 0.6853 x 1.10 + 0.05 = $2.31;
4 h would be $3.07 and is refused). Expected actual spend for the canary is far
lower (see "Expected runtime").

## Expected runtime

M4 measurement (`../ACCEL_EQUIVALENCE_cpu_pool3_M4.json`, 3 workers, host
shared with the science seat): 429.9 s wall-clock, 1,138 s summed cell CPU,
longest single cell 5.8 s, conformance full sweep 137 s (52 s uncontended).
F16s_v2 = 8 physical cores / 16 threads; assuming ~10 effective workers,
the run is ~2-4 min (bounded below by the single ~52-137 s conformance task),
plus ~5 min provisioning, SSH and teardown: **~10 min end to end, ~$0.15-0.25
actual spend**, worst case $1.56 by the guard, hard stop at 90 min.

## Kill layers (any one stops compute billing)

1. `trap cleanup EXIT INT TERM HUP` -> `az group delete --yes --no-wait`.
2. Local watchdog subprocess -> `az group delete` after `MAX_MINUTES`.
3. Azure-side `az vm auto-shutdown` (deallocates) at start + `MAX_MINUTES`,
   plus in-VM `shutdown -h` and `timeout` on the remote run.

Layer 3 stops compute but leaves disk/IP (cents/day) if layers 1-2 both fail
(e.g. the operator's laptop sleeps); run `cleanup.sh` afterwards to be sure.

## What the OPERATOR must provide

1. A machine with bash (Linux, WSL, or Git Bash), `git`, `ssh`/`scp`,
   `python3` (or `python`), and the Azure CLI installed.
2. `az login` into a subscription you authorise for <= $3 of spend
   (optionally `az account set -s <subscription-id>`).
3. vCPU quota: >= 16 vCPUs of the **FSv2 family** and >= 16 total regional
   vCPUs in `LOCATION` (new PAYG subscriptions are often 10 total; check with
   `az vm list-usage -l eastus -o table`). If quota is short, set
   `VM_SIZE=Standard_F8s_v2`, `WORKERS=8`, `VM_PRICE_PER_HOUR=0.338`.
4. Verify the three prices in `azure.env` against the current Azure price
   page for your region; edit them if they differ (the guard re-checks).
5. Set `PINNED_SHA=` in `azure.env` to the pushed head of
   `aphrodite/accel-azure-cpu-2026-09-23` (a local clone containing that
   commit is required; the VM receives `git archive` of exactly that SHA and
   needs no GitHub access).
6. Run: `bash roles/Aphrodite/engine/accel/azure/run_azure_canary.sh`
7. Afterwards: `bash roles/Aphrodite/engine/accel/azure/cleanup.sh` and confirm
   the listing is empty. Results land in `azure/results/<UTC stamp>/`
   (`BACKEND_RUN_azure.json`, `ACCEL_EQUIVALENCE_cpu_pool16_azure_Standard_F16s_v2.json`,
   `run.log`); hand them to the Aphrodite seat for commit.
