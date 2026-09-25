#!/usr/bin/env bash
# ACCEL_CANARY_v1 on one Azure CPU VM. WRITTEN, NOT EXECUTED by the seat.
#
# Lifecycle: budget guard -> create RG -> arm three kill layers -> create VM ->
# ship `git archive PINNED_SHA` -> run canary -> pull JSONs back -> ALWAYS
# delete the resource group.
#
# Kill layers (any one suffices to stop billing of compute):
#   1. trap on EXIT/INT/TERM/HUP -> az group delete
#   2. local watchdog: after MAX_MINUTES -> az group delete (independent process)
#   3. Azure-side auto-shutdown schedule (deallocates the VM) at now+MAX_MINUTES,
#      plus `timeout` on the remote run and an in-VM `shutdown -h`.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="${1:-$HERE/azure.env}"
set -a; source "$CFG"; set +a
PY="${PY:-$(command -v python3 || command -v python)}"

: "${PINNED_SHA:?set PINNED_SHA in azure.env to the pushed commit to run}"
command -v az >/dev/null || { echo "az CLI not found"; exit 2; }
az account show -o none || { echo "not logged in: run 'az login' first"; exit 2; }

"$PY" "$HERE/budget_guard.py" "$CFG" || { echo "budget guard refused; nothing created"; exit 3; }

REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
git -C "$REPO" cat-file -e "${PINNED_SHA}^{commit}" || { echo "PINNED_SHA not in local repo"; exit 2; }
FULL_SHA="$(git -C "$REPO" rev-parse "${PINNED_SHA}^{commit}")"

STAMP="$(date -u +%Y%m%d%H%M%S)"
RG="aphrodite-accel-canary-${STAMP}"
VM="canary"
WORK="$(mktemp -d)"
RESULTS="$HERE/results/$STAMP"
mkdir -p "$RESULTS"
START_EPOCH="$(date +%s)"
DEADLINE_EPOCH=$(( START_EPOCH + MAX_MINUTES * 60 ))
WD_PID=""

cleanup() {
  local rc=$?
  set +e
  echo "[cleanup] deleting resource group $RG (rc=$rc)"
  az group delete -n "$RG" --yes --no-wait
  [ -n "$WD_PID" ] && kill "$WD_PID" 2>/dev/null
  rm -rf "$WORK"
  echo "[cleanup] delete requested. Verify with: az group exists -n $RG   (expect false after a few minutes)"
  echo "[cleanup] or sweep everything tagged for this canary: bash $HERE/cleanup.sh"
}
trap cleanup EXIT INT TERM HUP

az group create -n "$RG" -l "$LOCATION" \
  --tags purpose=aphrodite-accel-canary sha="$FULL_SHA" max_minutes="$MAX_MINUTES" -o none
echo "[rg] $RG created in $LOCATION"

# Layer 2: independent watchdog (survives a hung main script; not a laptop sleep).
( sleep $(( MAX_MINUTES * 60 )); echo "[watchdog] hard ceiling hit"; az group delete -n "$RG" --yes --no-wait ) &
WD_PID=$!

ssh-keygen -q -t ed25519 -N "" -f "$WORK/key"
az vm create -g "$RG" -n "$VM" --image "$IMAGE" --size "$VM_SIZE" \
  --admin-username aphro --ssh-key-values "$WORK/key.pub" \
  --os-disk-size-gb "$OS_DISK_GB" --storage-sku "$OS_DISK_SKU" \
  --public-ip-sku Standard --nsg-rule SSH -o json > "$WORK/vm.json"
IP="$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))['publicIpAddress'])" "$WORK/vm.json")"
echo "[vm] $VM_SIZE up at $IP"

# Layer 3: Azure-side auto-shutdown (deallocate) at the deadline, UTC HHMM.
SHUT="$("$PY" -c "import datetime,sys;print(datetime.datetime.fromtimestamp(int(sys.argv[1]),datetime.timezone.utc).strftime('%H%M'))" "$DEADLINE_EPOCH")"
az vm auto-shutdown -g "$RG" -n "$VM" --time "$SHUT" -o none
echo "[vm] auto-shutdown scheduled at ${SHUT} UTC"

SSH=(ssh -i "$WORK/key" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=30 "aphro@$IP")
SCP=(scp -i "$WORK/key" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)

REMAIN_MIN=$(( (DEADLINE_EPOCH - $(date +%s)) / 60 ))
"${SSH[@]}" "sudo shutdown -h +$(( REMAIN_MIN > 2 ? REMAIN_MIN - 1 : 1 ))" || true

# Ship exactly the pinned SHA (engine tree only). No credentials on the VM.
git -C "$REPO" archive --format=tar "$FULL_SHA" roles/Aphrodite/engine \
  | "${SSH[@]}" "mkdir -p ~/w && tar -x -C ~/w"

RUN_TIMEOUT=$(( DEADLINE_EPOCH - $(date +%s) - 300 ))
[ "$RUN_TIMEOUT" -gt 60 ] || { echo "not enough time left before the hard ceiling"; exit 4; }
echo "[run] workers=$WORKERS timeout=${RUN_TIMEOUT}s sha=$FULL_SHA"
"${SSH[@]}" "cd ~/w/roles/Aphrodite/engine/accel && python3 --version && nproc && \
  timeout ${RUN_TIMEOUT}s python3 -u parallel_tier3c.py --workers $WORKERS \
    --backend cpu_pool$WORKERS --host azure_${VM_SIZE} --head-sha $FULL_SHA \
    --out BACKEND_RUN_azure.json && \
  (python3 compare_reference.py BACKEND_RUN_azure.json; echo compare_rc=\$?)" \
  | tee "$RESULTS/run.log"

"${SCP[@]}" "aphro@$IP:w/roles/Aphrodite/engine/accel/BACKEND_RUN_azure.json" "$RESULTS/"
"${SCP[@]}" "aphro@$IP:w/roles/Aphrodite/engine/accel/ACCEL_EQUIVALENCE_*.json" "$RESULTS/"
echo "[done] results in $RESULTS ; elapsed $(( $(date +%s) - START_EPOCH ))s"
# trap deletes the resource group now.
