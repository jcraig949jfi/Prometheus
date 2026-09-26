+==============================================================================+
| REVIEW PACKET -- ODYSSEUS BRAIN v0: sharded UDP spiking substrate with       |
|                  record / play / pause / rewind / fast-forward / fork        |
| Author: Odysseus (seat), host ubu001 (Ubuntu 26.04.1, 4 cores, 7 GB, no GPU) |
| Date:   2026-09-26                                                           |
| For:    operator (HITL) + external reviewers                                 |
| Status: v0 built, Linux-verified; Windows and cross-host NOT yet run         |
| Self-contained: no repository access needed to review this packet.          |
+==============================================================================+

-----
0. SUMMARY
-----
Mandate (operator charter, 2026-09-26): a "distributed brain" whose
circuitry is sharded across the fleet's machines (RAM + disk donated per
host), slow is acceptable, runs will grow to hundreds of GB, and any run
can be paused, played, rewound, fast-forwarded and microtested inside
playback without rerunning from scratch. Binding: R1 sharded from day
one, R2 Windows + Linux, R3 test-driven, R4 borrow prior art, R5 UDP not
TCP.

Built: a stdlib-only Python substrate. Shards advance in lockstep ticks
and exchange spikes as UDP datagrams with NAK-based repair; each shard
records keyframes + a per-tick log; a Player replays one shard (or all)
with every tick hash-verified, and forks counterfactual microtests.

Result: 71/71 tests pass on Linux (tests committed red BEFORE the code).
Under 40% injected datagram loss, a 6-process, 4000-neuron, 200-tick run
repaired all 18,462 lost datagrams and matched the in-process reference
on 200/200 tick roots. Windows and two-host runs have NOT happened yet.

Lean: continue, but the next two steps (Windows, two real hosts) are the
ones that can falsify the design; nothing below is claimed for them.

-----
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
-----
Commit order (git history is the evidence):
  bd76253c6  charter verbatim + DESIGN.md (12 decisions) + the full test
             suite, committed RED (collection failed: no modules).
  (next)     implementation, then one test corrected (section 5).
  4357454fd  on main: implementation + seat files, 81 passed / 1 skipped
             on the merged tree (71 brain tests + base-role self-test).

Modules (odysseus/brain/): model (placeholder circuit), shard (state +
step), wire (datagram format), frames (keyframes + log), player
(playback + fork), transport (UDP endpoint), node (lockstep protocol),
cluster (reference / in-process / local UDP cluster), CLI.

-----
2. THE CLAIM AND WHY IT MATTERS
-----
Claim: a sharded circuit run over lossy UDP is BIT-IDENTICAL to the same
circuit run in one process, and any tick of any shard can be revisited
and forked later from files alone, with every replayed tick proven by a
hash chain. If this holds across machines and OSes, weak signals found
in long runs can be investigated at the exact tick without rerunning.
If it fails, every downstream microtest is noise.

-----
3. DESIGN AS EXECUTED (prior art borrowed per decision)
-----
D1  Spike at t delivered at t+1 -> lockstep supersteps (BSP, Valiant
    1990; Pregel 2010; NEST min-delay exchange 2005). A shard is never
    more than one tick ahead of any peer.
D2  Barrier = data: every peer gets a TICK_END every tick, even empty.
    No coordinator; superstep boundary is a consistent global snapshot
    (so no Chandy-Lamport markers).
D3  UDP + receiver-driven NAK repair (NORM RFC 5740, PGM RFC 3208,
    Aeron). Outbox[t] freed when every peer's tick t+1 is complete.
D4  Spike on the wire = u32 neuron id (AER; SpiNNaker packets).
D5  Explicit little-endian fixed-width formats + CRC32 (SBE idea). Note:
    `#pragma pack(1)` from the pasted advice does NOT fix `long` being
    4 bytes on Windows and 8 on Linux; explicit widths do.
D6  Integer-only LIF dynamics (Loihi-style fixed point). Reason: libm
    exp/tanh differ between MSVC and glibc in the last bit. Enforced by
    an AST test that rejects true division, float literals, float(),
    math.* in the dynamics modules.
D7  Procedural connectivity: targets(j) is a pure function of (seed, j)
    (GeNN 2021), so routing sends a spike only to shards that own a
    target; traffic = the graph cut.
D8  Keyframes every K ticks + per-tick log (MPEG GOP; rr record/replay).
    Seek = nearest keyframe <= t, then recompute; or step forward from
    the cursor if that is cheaper.
D9  Shard-local replay: each shard logs spikes that ENTERED it, so one
    shard replays alone on one machine.
D10 Fork = counterfactual shard-local replay (activation patching along
    time). diverged_at = first tick the state hash differs; escaped_at =
    first tick its spikes to OTHER shards differ -- after that the rest
    of the brain would react and the local branch is no longer exact.
D11 Merkle root over shard hashes per tick proves a global rewind.
D12 State is a flat int32 buffer, bytearray or memory-mapped file
    (capped, restart-safe -- chosen over the OS pagefile, whose contents
    vanish on reboot). Forks map keyframes copy-on-write.

-----
4. RESULTS (exact; all on ubu001, Python 3.14.4)
-----
Test suite: 71 passed, 3 consecutive runs, 12.1-14.2 s. Merged tree with
base-role self-test: 81 passed, 1 skipped (Task Scheduler absent).

Controls in the suite:
  negative  no-op fork from tick 20 to 59: diverged_at None, escaped None
  positive  ablating a neuron that fires after tick 20: divergence found
            at or before its firing tick; spike removed in the diff
  cheat     flipped byte in datagram (4 offsets), keyframe, log record:
            all rejected; a log record rewritten WITH a valid CRC (a log
            that lies consistently) is caught on replay at the exact tick
  reliab.   20% loss and 10% corruption over real UDP (loopback):
            tick roots identical to reference
  invariance  1 shard vs 2/3/4/7 shards: identical spikes and global
            state digests over 40 ticks

Stress (process mode, not in the suite):
  6 procs x 4000 neurons x 200 ticks, keyframe 25:
    loss 0.4 : 18,462 dropped; 3,158-3,331 NAKs/shard; 2,162-2,529
               retransmits/shard; 57.56 s wall; 25.8 MB max RSS/proc;
               verify root_ok; 0/200 roots differ from reference;
               195,477 spikes; run dir 4.1 MB
    loss 0.0 : 2.87 s wall; 3 NAKs; verify root_ok
  So loss costs time (20x at 40%), not correctness, on this host.

-----
5. INCIDENTS AND WHAT THEY VALIDATED
-----
- One test was changed after the first run (70/71). It asserted that
  seek(41) from tick 39 replays forward from the cursor; keyframe 40 is
  cheaper (1 tick vs 2) and the code chose it. The TEST was wrong. It
  now checks each branch of the cost rule separately. Recorded in the
  seat's calibration ledger. A reviewer should check this was a test
  error and not a goal-post move.
- Name clash (Node.run attribute vs method) broke the first cluster run;
  fixed before any measurement.
- Process hole (seat setup, not the brain): the seat ran `git pull` in
  the canonical checkout before reading the working contract; recorded
  as an incident.

-----
6. KNOWN LIMITS (reported, not hidden)
-----
- End of run is a two-generals problem: a finished node lingers up to
  2 s answering NAKs; loss beyond that can strand a peer. DONE messages
  let everyone leave early when all are finished.
- Every replayed tick hashes the whole shard state: fine at this scale,
  expensive for very large shards (Merkle-per-page is the fix).
- The log index is loaded into memory; million-tick logs need an
  on-disk index (backlog ODYSSEUS-07).
- No keyframe replication, no re-sharding, no node join/leave, no
  multi-shard fork, no multicast yet (backlog 06, 13, 14, 09, 15).
- The circuit is a placeholder with strong period-3 synchrony (~20-30%
  of neurons fire per tick); it exercises the substrate, not reasoning.
- Pure Python: 2.9 s for 200 ticks of 4000 neurons across 6 processes.
  "Massive" needs a vectorised step with bit-identity (backlog 17).

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----
DOES: on one Linux host, over real UDP sockets on loopback, with
injected loss and corruption, the protocol is lossless end to end and
the recording is sufficient to replay, rewind, fast-forward and fork any
tick of any shard, with tampering detected.
DOES NOT: anything about Windows (untested); real networks (loopback
has no reordering, no WiFi, no MTU surprises, no firewall); multiple
hosts; scale beyond 4000 neurons; usefulness for finding weak reasoning
signals (no consumer yet).

-----
8. DECISION / RECOMMENDATION (operator's call)
-----
Lean: continue to the two falsifying steps before adding features:
  (a) Windows run (delegated to Cyclops on M2, comms #679);
  (b) two real hosts, ubu001 <-> ubu002, then a Windows <-> Linux pair.
Operator decisions needed: per-host donation caps (RAM/disk/hours) and
inbound UDP firewall rules on Windows hosts. If (a) or (b) cannot be
made bit-identical, the fallback is to keep integer dynamics and change
transport, not to give up determinism.

-----
9. QUESTIONS FOR THE REVIEWER (answer against us)
-----
Q1 Is bit-identical replay the right bar, or will it block useful
   float/GPU consumers? What would you accept instead, and how would a
   microtest's effect be separated from replay noise without it?
Q2 Is lockstep BSP wrong for a "slow brain" on heterogeneous laptops,
   where the slowest node sets the pace? Would asynchronous (time-warp /
   optimistic) simulation be the better prior art to borrow?
Q3 The escape rule marks a fork inexact once its spikes to other shards
   change. Is there a cheaper exact alternative (light-cone replay)?
Q4 Is a spiking placeholder misleading, given the operator also named
   vectors, tensors and nets? Should the first real payload be a
   sharded tensor graph instead?
Q5 What would falsify this design outright, and should we stop before
   building replication and re-sharding?

-----
10. ARTIFACTS (repository https://github.com/jcraig949jfi/Prometheus)
-----
  odysseus/DESIGN.md                       decisions + prior art
  odysseus/README.md                       usage
  odysseus/brain/*.py                      implementation
  odysseus/tests/*.py                      71 tests (red at bd76253c6)
  roles/Odysseus/prompts/2026-09-26_charter/   charter verbatim + MANIFEST
  roles/Odysseus/prompts/2026-09-26_windows_test/  delegation + MANIFEST
  roles/Odysseus/journal/2026-09-26.md     commands and numbers
  roles/Odysseus/calibration/LEDGER.md     the test correction
  commits: bd76253c6 (tests red), 4357454fd (on main, green)

+==============================================================================+
| END. "Not worth continuing" is a first-class answer. So is "right idea,      |
| wrong substrate". Say which, and why.                                        |
+==============================================================================+
