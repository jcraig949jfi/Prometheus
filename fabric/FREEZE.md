# Fabric v0.2: FROZEN for the adoption experiment (2026-09-28)

**Operator ruling:** "After D12 and the lease cutover, freeze Fabric v0.2 for an adoption experiment. No dashboard,
streaming, push, scheduler, priority optimizer, or more protocol work." Odysseus's job now shifts from building
the fabric to trying to break it under real science.

## What is frozen

The code under `fabric/` at the commit that adds this file (git tag `fabric-v0.2`). Workers advertise the probed
capability `fabric.runtime==0.2`. Experiment tasks require it, so a pre-freeze worker (for example the v0.1 pilot
worker on ubu002) never claims them.

| part | state |
|---|---|
| store | Tasks, Attempts, leases, artifacts, events, messages. The fabric lease is the one authority, and legacy ARC3 detection stays until the old helper copies are merged away. |
| worker | generic `worker.<host>[.<env>]`; python.*/pin.*/fabric.runtime capabilities probed; runtime deposits artifacts |
| claude executor | empty config, pinned worktree, explicit model, Read/Grep/Glob scoped, Write only to out/, `rogit` for git, plain git denied, secret paths denied |
| script executor | repo file or module at the pinned SHA, no shell, env allow-list |
| CLI | submit (`--skill`, `--replicas`), tasks/show/events/artifacts/get/cancel, lease, worker, gateway |
| gateway | A2A v1.0 JSON-RPC (TCK: MUST 68/0, SHOULD 8/0/0) |
| lease frontends | Ananke lease.py and nestor_lease.py use the fabric row |

## Allowed changes while frozen

Only **defect repairs that block science or safety**. Each one must be:
1. logged as an incident in the running experiment's ledger (it counts against the fabric);
2. committed separately with the defect id;
3. accompanied by a regression test.

A new capability, method, option, protocol feature, or scheduling or priority logic is NOT allowed. Proposals go
to `fabric/BACKLOG_AFTER_FREEZE.md`.

## Node runtime

Persistent node workers run from a detached worktree `~/fabric-runtime` at the frozen commit. They must never run
from a development checkout. Start a node worker with:

```
git -C ~/Prometheus fetch origin && git -C ~/Prometheus worktree add --detach ~/fabric-runtime fabric-v0.2
cd ~/fabric-runtime && EW_DB_HOST=192.168.1.202 python3 -m fabric worker --agent worker.<host> \
    --caps repo.read research.repo_readonly research.synthesis compute.cpu.light --executors claude script
```

The claude executor also needs `~/.config/prometheus/claude.env` on the node, containing `CLAUDE_CODE_OAUTH_TOKEN`.
It is never printed, logged or committed.

## Incident log (defect repairs made under this freeze)

- **2026-09-29, DEF-ODY-015** (roles/Odysseus/fabric_pilot/DEFECTS.md): the per-worker checkout cache was
  unbounded, filled ubu001's disk, and failed 20 real Tasks.
  - Repair: `fabric/worker.py` `gc_bases` / `KEEP_BASES`.
  - Regression test: `fabric/tests/test_executors.py::test_gc_bases_keeps_only_most_recent`.
  - It rolls into `~/fabric-runtime` at a quiet point.
