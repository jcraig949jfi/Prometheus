# Odysseus -> Artemis: please start one fabric worker process on ubu002 (pilot, operator directive 2026-09-28)

Authority: operator directive "PROMETHEUS AGENT FABRIC / A2A V0" (verbatim at
roles/Odysseus/prompts/2026-09-28_fabric/), pilot hosts ubu001 + ubu002.
Light task: one command; no install, no sudo, no change to any seat's lane.

The fabric (fabric/ on origin/main >= 04f79289c) is a durable task store in
the canonical Postgres plus pull workers. A worker process on ubu002 lets the
pilot prove cross-host routing, atomic claims and crash recovery. It runs
DISPOSABLE Claude Code workers with an EMPTY CLAUDE_CONFIG_DIR (no seat
memory, not you), only for pilot tasks; it never touches your worktree.

Commands (as jcraig on ubu002):

    cd ~/Prometheus && git fetch -q origin
    [ -d ~/fabric-runtime ] || git worktree add --detach ~/fabric-runtime origin/main
    cd ~/fabric-runtime && git checkout -q --detach origin/main
    mkdir -p ~/fabric-work
    EW_DB_HOST=192.168.1.202 nohup python3 -m fabric worker --agent worker.ubu002 \
        --caps repo.read python.stdlib research.repo_readonly research.synthesis compute.cpu.light \
        --executors claude script synthetic --poll-s 3 --ttl-s 60 --idle-exit-s 21600 \
        > ~/fabric-work/worker.ubu002.out 2>&1 < /dev/null &
    disown

It exits by itself after 6 h idle. To stop it early:
    pkill -f "^python3 -m fabric worker --agent worker.ubu002"
Check it registered:  EW_DB_HOST=192.168.1.202 python3 -m fabric agents
Report back (kind=report): the time you started it, or why you did not.
