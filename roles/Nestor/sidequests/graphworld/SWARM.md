# THE PRIMORDIAL MACHINE -- five-session swarm plan (v0)

Currency: 2026-09-14 (Nestor-A[m1-918ab2b0]). Supersedes OPTIONS_2026-09-14.md
as the working plan; that file stays as the first read. Authority: operator
directive, verbatim with the ChatGPT brief, at
roles/Nestor/prompts/2026-09-14_graphworld_swarm/00_OPERATOR_DIRECTIVE.md.

Posture (operator): a moonshot side quest, five Claude sessions looping in
parallel, friendly competition, build a chimera. NOT a gated 10-year
program. What survives from doctrine, and only this:

  1. Every claim is a RECEIPT with its rows committed (no rows, no claim).
  2. Every board claim ran a CHEAT control (success injected / answer leaked /
     oracle bypassed) and the instrument caught it.
  3. Engineering and science are separate ledgers (contract enforces it).
  4. Kills and negative results score. Breaking another lane's result scores.
  5. Hands off production seats (SFE/Daedalus, Vivarium, PEW, wforge/Ludus):
     read them, fossil-quarry them, copy semantics, never edit them. A
     production change leaves as a packet to the owner.
  No preregistration commits, no eligibility dossiers, no waiting for
  reviews. A one-line hypothesis goes on the bus BEFORE the run; that is
  the preregistration.

## 1. Measured ground (2026-09-14, what the swarm starts from)

- Substrate: container gw-substrate, falkordb/falkordb:latest = Redis 8.6.3
  + FalkorDB graph 4.20.4 + vectorset, AOF on, restart unless-stopped,
  --cpus 4, bound 127.0.0.1:6390. Streams, Lua EVAL, GRAPH.QUERY smoke-pass.
- From Windows Python: XADD pipelined 57,820/s; single round trip 0.329 ms
  (PING, loopback into WSL2). So ANY per-tick Redis call costs >= 0.33 ms
  unless batched or run server-side in Lua: that one number is B's prior.
- DO NOT use port 6379: a system redis 7.0.15 with auth runs there (owner
  unknown; not ours).
- Host M1 SKULLPORT also runs SFE + Vivarium. 16 logical cores, CPU ~8% at
  07:10. GPU RTX 5060 Ti 16 GB (torch 2.11 cu128). F: is an SMR HDD (the
  30.8x write stall): no hot data on F:. C: has ~70 GB free. WSL ext4 has
  844 GB free.
- venv: C:/Users/jcrai/lab/gw-venv (uv, system site packages): numpy 2.2,
  scipy, torch cuda, numba 0.65, tensorly 0.9, quimb 1.15,
  python-graphblas 2025.2.0, redis, falkordb, zstandard, pyarrow, pytest.
- wforge Encounter (SerendipityFoundry/worldfoundry/wforge/world.py): the
  reference world. Integer-only, xorshift streams, trace hash per tick. It
  is the SEMANTIC ORACLE for every faster world: same mechanics + seed +
  actions => same trace hash, zero tolerance.
- FalkorDB source build: in progress by A (WSL ~/lab/falkordb, output
  ~/lab/falkor-out/libfalkordb.so). Stock image needs no build.

## 2. The chimera we are building (target: CHIMERA-0)

    E: selection (MAP-Elites / QD, archive in Redis)
        | genomes (bytes)                         ^ receipts, branch points
        v                                         |
    C: tensor brains (TT cores, plastic rank)  <-> D: metered channel
        | actions int32 [envs,slots,act]            (Streams + Lua per-bit
        v                                            charge, codebooks)
    B: batched soup (vectorised/compiled world,  trace-hash oracle)
        | events                                  
        v                                         
    A: event fabric (Streams -> batched durable writer) + bus + board

CHIMERA-0 = one receipt in which E evolves C's brains in B's batched world,
two slots talk through D's channel, events drain through A's fabric, and
the trace hashes of a sample of episodes match a wforge Encounter replay.
Interfaces: primordial/core/contract.py (World, Brain, Channel, Genome,
receipt). HOT-PATH RULE: no English, no str, no JSON on the hot path;
integer arrays and packed bytes only. Symbols are uint codes.

Nobody waits for another lane: each lane codes against the contract with a
10-line stub of what it needs (E evolves bitstrings on a stub world until
B's batched world lands; C trains on a stub world; D runs a 2-slot toy).

## 3. Lanes (owner directory; nobody edits another lane's directory)

A  CONDUCTOR + FABRIC      primordial/core, primordial/bus, primordial/fabric,
   (Nestor-A[m1-449a9e76] since 11:39; predecessor m1-918ab2b0 stopped 07:29,
    see POSTMORTEM_2026-09-14_A_D.md) roles/Nestor/sidequests/graphworld/*
   A0 LIVENESS (added): every lane has a bus hello; audit board scores.
   A1 bus, contract, board, boot kit ........ DONE at v0 (tests in commit)
   A2 FalkorDB from source, reproducible artifact + untouched baseline with
      their bench harness (Track J) .......... BUILT 07:29; smoke PASS (loads, Cypher
      answers); see primordial/fabric/A2_BUILD.md; untouched baseline bench NOT run
   A3 stream ledger: world -> XADD -> batched durable writer -> SQLite;
      1/100/10k events, N producers, slow writer, kill -9 producer / writer
      / redis, restart, duplicates, ordering; count lost/dup exactly (Track B).
      Done = kill matrix rows + packet for Daedalus. Quick rows committed
      (93153bfcd); full run 11:39 by m1-449a9e76.
   A4 CHIMERA-0 integration harness.

B  SOUP (worlds, physics kernels, compilation)        primordial/soup
   B1 CROSSOVER CRUCIBLE (Track A): Encounter semantics as (a) wforge
      reference, (b) numpy batched over n_envs, (c) numba, (d) Redis Lua:
      regs in one string key, one EVALSHA per tick AND one EVALSHA running
      k ticks server-side, (e) FalkorDB Cypher. Sweep n_envs 1..65536 and
      concurrent producers 1..16. Oracle: trace hash == wforge for sampled
      episodes. Done = steps/s surface + where each form wins. Cheat control:
      an implementation that skips the lin_ops must FAIL the oracle.
   B2 GRAPHWORLD TOY (Track D): entities on a lattice, world state as
      boolean sparse relations (ADJACENT, SEES, THREATENS, OWNS...),
      transition rules as GraphBLAS mxm / ewise / masks in
      python-graphblas AND as Cypher in FalkorDB, same trajectory hash.
   B3 OP CENSUS (Track H): count which primitive ops B1/B2 actually execute;
      derive the instruction vocabulary from rows, not from the list.

C  BRAIN (tensor brains, plasticity, representation ecology, GPU crossover)
                                                       primordial/brain
   C1 TT-POLICY: an organism's policy as a tensor train over observation
      digits (uint16 -> base-16 digits -> one core per digit) contracted to
      action logits; batched contraction on CPU (numpy/numba) vs GPU (torch)
      over batch size; find the crossover (Track 10). Done = crossover rows.
   C2 PLASTIC RANK: online adaptation (local core updates + TT-rounding that
      grows rank on surprise, shrinks it under a memory charge) in a world
      with regime_period switches. Question: does rank track regime change?
      Cheat control: a brain given the regime flag directly must be flagged
      as leaking by the probe that scores C2.
   C3 REPRESENTATION ECOLOGY (Track F/9): same task, brains as dense table /
      CP / Tucker / TT / bitset / tiny program; charge memory+flops+error;
      report the Pareto set, not a winner.

D  LINGUA (symbolic compression pressure, channels, codebooks)
                                                       primordial/lingua
   D1 METERED CHANNEL (Track C): 2-slot world where yield depends on a
      register only slot 0 observes and only slot 1 can move. Messages go
      through Streams; one Lua script settles per-bit charge atomically
      against the sender's charge. Cost = a*bits + b*decode + d*behavioural
      error. Done = bits-vs-yield Pareto front across a,b,d.
      Anti-silence control: a*=0 vs a*>0 must differ; silence must lose yield.
      Cheat control: a leaked side channel (shared seed) must be detected by
      permuting the codebook between episodes.
   D2 CONSEQUENTIAL SYMBOLS: a code is consequential iff ablating it drops
      yield beyond episode noise; count them; test recurrence/transfer
      across worlds (Track C "Omega7" test).
   D3 QUERY NICHE (Track E), once B2 exists: organisms buy observations as
      graph queries, charged by touched edges / result size / plan cost;
      re-label node ids and add irrelevant edges between episodes.

E  SELECTION (QD, evolution, pressures, engine-as-organism)   primordial/qd
   E1 QD CORE: vectorised MAP-Elites with the archive in Redis (hash per
      cell, zset per niche) so several instances share one archive; runs on
      a stub world today, B's batched world when it lands.
   E2 BRANCH POINTS (the science ledger): an operational definition of a
      "meaningful branch point" (e.g. a new cell whose lineage survives k
      generations AND transfers to a held-out world), measured per CPU-hour.
      Cheat control: a random-genome filler must score ~0.
   E3 ENGINE AS ORGANISM (Track G): stock FalkorDB image; genome = runtime
      config (CACHE_SIZE, THREAD_COUNT, OMP_THREAD_COUNT, query rewrites)
      over a fixed Cypher corpus; exact-output gate against the default
      config, then fitness = wall time / instructions. Cheat control: a
      config that returns truncated results must die at the gate.
      Later: PreJIT kernel sets once A2's build exists.

Board metrics (pm:board:<metric>): steps_per_s_verified (oracle-equal only),
bits_saved_at_parity, branch_points_per_cpu_h, pareto_points, kills (auto
from KILL receipts), bounties (a KILL receipt naming another lane's exp_id
in `refutes`; A audits and moves the score).

## 4. Hardware budget (M1 also runs SFE and Vivarium: do not starve them)

- Each lane: <= 3 cores sustained (OMP_NUM_THREADS=3, NUMBA_NUM_THREADS=3,
  torch.set_num_threads(3)); bursts to 6 for <= 10 min, announced on bus.
- GPU: C owns it. Others post `ask gpu` and use <= 4 GB when granted.
- Hot data: C:/Users/jcrai/lab/pm-data/<lane>/ (cap 10 GB/lane) or WSL
  ~/lab/pm-data/<lane>/. Never F:.
- Benchmarks record `host_load` (1-min load or CPU %) in engineering; a
  speed claim measured while another lane was bursting is INDETERMINATE.
- Private substrate for clean benchmarks (the shared one is the bus):
  ports B 6391, C 6392, D 6393, E 6394, via primordial/ops/substrate.sh.

## 5. Git (D-23 in miniature)

- Integration branch: nestor/sidequest-graphworld-2026-09-14 (never main).
- Lane L instance: worktree F:/Prometheus-worktrees/nestor-gw-<l>, branch
  nestor/gw-<l>-2026-09-14 from the integration tip.
- Commit ONLY your lane directory, your rows under
  primordial/ledger/rows/<L>/, your ledger file primordial/ledger/<L>.jsonl,
  and your journal roles/Nestor/sidequests/graphworld/journal/<L>.md.
  Disjoint paths make every rebase clean.
- Integrate: git fetch; git rebase origin/nestor/sidequest-graphworld-2026-09-14;
  tests pass; git push origin HEAD:nestor/sidequest-graphworld-2026-09-14
  (non-ff => rebase once and retry; never force).
- Subject: `Nestor-<L>[<tag>]: <what changed>`; trailer `Nestor-Instance:
  <L> <tag>` beside the mandated Claude-Session trailer.
- Contract change: only lane A commits primordial/core; others post
  `ask contract` with the diff they need.

## 6. The loop (every iteration, 30-90 min)

  1. sync:    git fetch + rebase; python -m primordial.bus read;
              python -m comms sync Nestor (outside-world messages only)
  2. choose:  next item in your lane (or a bounty); bus claim <exp_id>
              and post the one-line hypothesis
  3. build:   smallest thing that makes the hypothesis die or live
  4. control: cheat control, then positive control where it applies
  5. receipt: rows to primordial/ledger/rows/<L>/<exp_id>.*; then
              bus.receipt(rec, board={...})
  6. land:    commit your paths; integrate (section 5); post the SHA
  7. journal: 3-8 lines in journal/<L>.md: what ran, numbers, what died,
              what you would steal from another lane next

Shell gotchas already paid for: Git Bash rewrites /mnt/c paths passed to
wsl.exe (prefix MSYS_NO_PATHCONV=1); heredocs with quotes hang (write a
script file, run it); never redirect a background job's output with a pipe
to tail; clone with core.autocrlf=false for anything built in Linux.

## 7. Where it hands back to Prometheus

- A3 packet -> Daedalus (ledger ingestion), only with the kill matrix.
- New axes (representation x channel x substrate x execution) -> Theophrastus
  as dimensions it can cross.
- Anything production-shaped -> a review packet to the owning seat.
- Fossils (dead variants) stay in the ledger with their rows.
