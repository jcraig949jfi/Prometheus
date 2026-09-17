#!/bin/sh
# Redeploy the pinned consumer to $1: clean stop (or clear a stale flag) ->
# advance the pin -> dead-man relaunch -> wait for the restart receipt at $1.
set -u
SHA="$1"
export EW_DB_HOST=192.168.1.202 VIV_DB_HOST=192.168.1.202 VIV_VAR_DIR=/d/Prometheus-data/vivarium/var
PIN=/d/Prometheus-worktrees/vivarium-consumer/vivarium
BOOT=/d/Prometheus-worktrees/vivarium-boot-2026-09-16/vivarium
PID=$(python -c "import json;print(json.load(open('D:/Prometheus-data/vivarium/var/restart-vivarium@m2.json'))['process']['pid'])")
if tasklist //FI "PID eq $PID" 2>/dev/null | grep -q python; then
  (cd "$PIN" && python -m viv.cli stop --worker-id vivarium@m2 >/dev/null 2>&1)
  until ! tasklist //FI "PID eq $PID" 2>/dev/null | grep -q python; do sleep 2; done
  echo "stopped $PID $(date -u +%T)"
else
  (cd "$PIN" && python -m viv.cli stop --worker-id vivarium@m2 --clear >/dev/null 2>&1)
  echo "consumer $PID was not running; stale flag cleared"
fi
(cd "$BOOT" && python deploy/window.py --confirm C4-20260917-W1 --sha "$SHA" --steps advance \
   --receipt "/d/Prometheus-data/vivarium/window/deploy_window-C4-20260917-W1-advance-$SHA.json" 2>&1 | grep -E '"advance": "')
schtasks //Run //TN VivariumDeadmanM2 | tail -1
until python -c "import json,sys; d=json.load(open('D:/Prometheus-data/vivarium/var/restart-vivarium@m2.json')); sys.exit(0 if d['code']['base_sha'].startswith('$SHA') else 1)" 2>/dev/null; do sleep 3; done
python -c "import json; d=json.load(open('D:/Prometheus-data/vivarium/var/restart-vivarium@m2.json')); print('consumer', d['code']['base_sha'][:9], 'pid', d['process']['pid'], 'ok', d['ok'], d['refuse'])"
