#!/usr/bin/env bash
# Start (or restart) a Redis 8 + FalkorDB substrate container.
# usage (from Git Bash):
#   MSYS_NO_PATHCONV=1 wsl.exe -e bash /mnt/f/Prometheus-worktrees/<wt>/primordial/ops/substrate.sh <port> <name> [cpus]
# shared bus: 6390 gw-substrate (lane A owns it); private: B 6391 C 6392 D 6393 E 6394
set -eu
PORT=${1:?port}; NAME=${2:?name}; CPUS=${3:-2}
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker volume create "$NAME-data" >/dev/null
docker run -d --name "$NAME" --restart unless-stopped --cpus "$CPUS" \
  -p "127.0.0.1:$PORT:6379" -v "$NAME-data:/var/lib/falkordb/data" \
  --entrypoint redis-server falkordb/falkordb:latest \
  --loadmodule /var/lib/falkordb/bin/falkordb.so \
  --appendonly yes --dir /var/lib/falkordb/data >/dev/null
sleep 2
docker exec "$NAME" redis-cli PING
docker exec "$NAME" redis-cli MODULE LIST | grep -A1 '^name$' | grep -v '^name$\|--' | tr '\n' ' '; echo
