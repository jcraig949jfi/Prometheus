#!/bin/bash
# Install (or re-pin) a PrometheusWorker on an Ubuntu node -- roles/generic-worker-role/RESPONSIBILITIES.md s2.
# Run ON the node as jcraig:   bash install_prometheus_worker.sh <code-sha> [--enable]
#   <code-sha>  the commit the worker CODE is pinned to (WORKING_CONTRACT s6); re-run with a new SHA to advance it
#   --enable    start the systemd user service (needs GitHub push access: the worker's claims are pushes)
# Idempotent. Layout (all under $HOME, beside the canonical clone ~/Prometheus):
#   ~/prometheus-worker-code    detached at <code-sha>: the worker's code (never edited)
#   ~/prometheus-worker-state   detached at origin/main, re-synced by the worker: the work graph it claims from
#   ~/prometheus-worker         scratch: runs/ (pinned exec worktrees, removed after each run) and results/
set -eu
SHA=${1:?usage: install_prometheus_worker.sh <code-sha> [--enable]}
ENABLE=${2:-}
CANON=$HOME/Prometheus
CODE=$HOME/prometheus-worker-code
STATE=$HOME/prometheus-worker-state
BASE=$HOME/prometheus-worker
UNIT=$HOME/.config/systemd/user/prometheus-worker.service

git -C "$CANON" fetch -q origin
if [ -e "$CODE/.git" ]; then git -C "$CODE" checkout -q --detach "$SHA"; else git -C "$CANON" worktree add -q --detach "$CODE" "$SHA"; fi
if [ ! -e "$STATE/.git" ]; then git -C "$CANON" worktree add -q --detach "$STATE" origin/main; fi
mkdir -p "$BASE" "$(dirname "$UNIT")"
echo "code  $(git -C "$CODE" rev-parse --short HEAD)   state $(git -C "$STATE" rev-parse --short HEAD)"

cat > "$UNIT" <<EOF
[Unit]
Description=PrometheusWorker (generic execution; roles/generic-worker-role) on %H
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$CODE
Environment=PYTHONIOENCODING=utf-8
Environment=PROMETHEUS_WORKER_CAPS=linux
ExecStart=/usr/bin/python3 -m workgraph.worker --repo $STATE --base $BASE --instance %H-svc --poll 15 --idle-sleep 300
Restart=on-failure
RestartSec=60
KillSignal=SIGTERM
KillMode=mixed
TimeoutStopSec=300
Nice=10

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload

cd "$CODE"
python3 -m workgraph.worker --repo "$STATE" --base "$BASE" --dry-run | head -20
if git -C "$STATE" push --dry-run -q origin HEAD:refs/heads/probe-$(hostname)-worker 2>/dev/null; then
  echo "push access: OK"
  PUSH=1
else
  echo "push access: NONE (no GitHub token) -- service NOT enabled"
  PUSH=0
fi
if [ "$ENABLE" = "--enable" ] && [ "$PUSH" = 1 ]; then
  systemctl --user enable -q prometheus-worker.service
  systemctl --user restart prometheus-worker.service
  sleep 3
  echo "service: $(systemctl --user is-active prometheus-worker.service)"
else
  echo "service: installed, not started"
fi
