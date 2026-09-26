# Installing a brain node (Linux and Windows) + the first 3-machine test

Currency: 2026-09-26. Needs only Python 3.10+ (stdlib) and the machine's
existing Prometheus clone. Nothing is installed into Python; nothing in
the canonical checkout is modified (WORKING_CONTRACT s1): the code is
exported read-only with `git archive` into its own folder, pinned to a
recorded SHA.

## First fleet test: 3 shards on 3 machines

    shard 0  ubu001   Linux    192.168.1.218
    shard 1  ubu002   Linux    192.168.1.219
    shard 2  WINDOWS  Windows  <WIN_IP>     (find it with `ipconfig`)

    run:  9000 neurons, 3 shards, seed 1, keyframe every 25, 300 ticks,
          run-id 26092601, UDP port 47100 on every machine

Rehearsed on one host (three separate folders, nodes started 3 s apart):
300 ticks in 14 s; `check` on each shard: replay_ok, 300/300 ticks equal
the reference; check takes ~16 s. Old laptops will be slower; the nodes
wait for each other (up to --max-wall, default 900 s), so start them in
any order within a few minutes.

### Linux (ubu001, ubu002)

    cd ~/Prometheus && git fetch origin && SHA=$(git rev-parse origin/main) && echo $SHA
    mkdir -p ~/odysseus-node && git archive "$SHA" odysseus | tar -x -C ~/odysseus-node
    cd ~/odysseus-node
    python3 -m odysseus.brain init --run runs/fleet1 --neurons 9000 --shards 3 \
        --seed 1 --keyframe 25 --run-id 26092601
    python3 -m odysseus.brain node --run runs/fleet1 --shard <0 or 1> \
        --bind 0.0.0.0:47100 \
        --peers 0=192.168.1.218:47100,1=192.168.1.219:47100,2=<WIN_IP>:47100 \
        --ticks 300 --progress 50
    python3 -m odysseus.brain check --run runs/fleet1 --shard <0 or 1>

If `ufw status` says active: `sudo ufw allow from 192.168.1.0/24 to any port 47100 proto udp`.

### Windows (PowerShell; the clone is F:\Prometheus on M1, D:\Prometheus on M2)

    cd F:\Prometheus; git fetch origin; $SHA = git rev-parse origin/main; $SHA
    git archive -o $env:TEMP\ody.tar $SHA odysseus
    mkdir C:\odysseus-node -Force; tar -xf $env:TEMP\ody.tar -C C:\odysseus-node

Once, in an ADMIN PowerShell (inbound UDP 47100 from the local subnet only):

    New-NetFirewallRule -DisplayName "Odysseus brain UDP 47100" -Direction Inbound `
        -Protocol UDP -LocalPort 47100 -RemoteAddress LocalSubnet -Action Allow

Then (use `py -3` if `python` is not on PATH):

    cd C:\odysseus-node
    python -m odysseus.brain init --run runs\fleet1 --neurons 9000 --shards 3 --seed 1 --keyframe 25 --run-id 26092601
    python -m odysseus.brain node --run runs\fleet1 --shard 2 --bind 0.0.0.0:47100 --peers 0=192.168.1.218:47100,1=192.168.1.219:47100,2=<WIN_IP>:47100 --ticks 300 --progress 50
    python -m odysseus.brain check --run runs\fleet1 --shard 2

### What success looks like

Each node prints one JSON line ending the run, e.g.

    {"shard": 1, "ticks": 300, "naks_sent": ..., "retransmits": ..., ...}

and `check` prints

    {"shard": 1, "ticks": 300, "replay_ok": true, "reference_match": 300, ...}

`reference_match: 300` on all three machines means a brain split across
two operating systems and three hosts evolved bit-for-bit like the same
brain in one process. Anything else is a finding: paste the JSON lines
and the last lines of the node output back to Odysseus.

### Failure shapes to expect

- A node sits at 0 ticks: the others are not reachable. Check the IPs,
  the Windows firewall rule, and that every node has the same --peers.
- NodeStalled after --max-wall: one machine never started or is blocked.
- reference_match < 300 with replay_ok true: the machines disagree on
  arithmetic -- the most important possible finding; do not delete the run.

### Afterwards

The run folder (runs/fleet1/shard_000N) is the recording; it can be
played back on that machine:

    python -m odysseus.brain check --run runs/fleet1 --shard N
    python -c "from odysseus.brain.player import Player; p=Player('runs/fleet1', N); p.seek(150); print(p.state_hash().hex())"
