# Odysseus brain -- design v0 (with prior art)

Currency: 2026-09-26. Charter: roles/Odysseus/prompts/2026-09-26_charter/
(R1 sharded from day one, R2 Windows + Linux, R3 TDD of frames /
playback / pause / rewind / fast-forward, R4 prior art borrowed, R5 UDP).

## 1. What v0 is

A spiking circuit whose neurons are partitioned across SHARDS, one shard
per process, one process per machine (several per machine in tests).
Shards advance in lockstep TICKS and exchange SPIKES as UDP datagrams.
Every shard records its own run: a KEYFRAME of its full state every K
ticks, and a per-tick LOG of the spikes that entered it, the spikes it
emitted, and the hash of its state. From those files a PLAYER can seek
to any tick, step, play, pause, rewind and fast-forward, verifying every
replayed tick against the recorded hash, and FORK a microtest from any
tick without rerunning the experiment.

v0 is an instrument, not a reasoner (north star): it supplies the
substrate that grown circuitry will live in. The circuit model is a
placeholder that exercises the substrate; it will be replaced.

## 2. Decisions and the prior art each is borrowed from

D1  Lockstep supersteps, spikes delivered one tick later.
    A spike emitted at tick t is consumed at tick t+1. A shard therefore
    needs only its peers' tick-t emissions to compute t+1, and can never
    be more than one tick ahead of any peer.
    Borrowed: Bulk Synchronous Parallel (Valiant, CACM 1990); Pregel
    supersteps (Malewicz et al., SIGMOD 2010); NEST's min-delay spike
    exchange (Morrison et al., Neural Computation 2005): communication
    is legal at intervals of the minimum synaptic delay.

D2  The barrier IS the data. Every shard sends every peer a TICK_END
    for every tick, even when it sent no spikes. Receiving TICK_END(t)
    with all its fragments from every peer is the barrier for t+1.
    There is no coordinator. A consistent global snapshot needs no
    Chandy-Lamport marker protocol (Chandy & Lamport, TOCS 1985)
    because the superstep boundary already is one.

D3  UDP with receiver-driven NAK repair (charter R5).
    No connections. Datagrams carry (run, tick, src, dst, frag, nfrag).
    A receiver that lacks a complete tick from a peer after a timeout
    sends NAK(tick); the peer resends that tick from its outbox. The
    outbox for tick t is kept until every peer's TICK_END(t+1) arrives
    (that proves the peer consumed t).
    Borrowed: NORM, NACK-Oriented Reliable Multicast (RFC 5740); PGM
    (RFC 3208); Aeron's NAK-based reliable UDP (Real Logic). Aeron
    itself is not used in v0: it needs a C toolchain and a media driver
    per host, and the measured traffic has not yet asked for it.

D4  Address-event representation. A spike on the wire is the global
    id of the neuron that fired (u32), nothing else.
    Borrowed: AER (Mahowald 1992; Boahen 2000); SpiNNaker's small
    multicast spike packets (Furber et al., Proc. IEEE 2014).

D5  Explicit little-endian wire and file formats with fixed-width
    fields (Python struct '<'), CRC32 per datagram and per log record.
    This is what `#pragma pack(1)` was reaching for, without its trap
    (`long` is 4 bytes on Windows and 8 on Linux; packing does not fix
    that). Borrowed: SBE (Simple Binary Encoding, the Aeron companion).

D6  Integer-only neuron arithmetic.
    Bit-identical replay across Windows and Linux rules out libm
    transcendental functions (MSVC and glibc exp/tanh can differ in the
    last bit). The neuron is a leaky integrate-and-fire in int32 with
    shift-based leak and saturation.
    Borrowed: Loihi's fixed-point LIF (Davies et al., IEEE Micro 2018);
    SpiNNaker fixed-point kernels.

D7  Procedural connectivity: the targets of neuron j are a pure
    function of (seed, j), so any shard can compute where a spike goes
    without holding the global graph, and routing sends a spike only to
    shards that own at least one of its targets (traffic = the cut).
    Borrowed: GeNN procedural connectivity (Knight & Nowotny, Nature
    Computational Science 2021). An explicit per-shard synapse table is
    the next model; the substrate does not depend on which.

D8  Keyframes + per-tick log, like video I-frames and P-frames.
    Seek(t) = load the newest keyframe <= t, then recompute forward
    using the logged inbound spikes. K trades disk for seek time.
    Borrowed: MPEG GOP structure; checkpoint/restart with replay logs
    (rr, O'Callahan et al., USENIX ATC 2017: record inputs, replay
    deterministically).

D9  Shard-local replay. Because each shard logs the spikes that ENTERED
    it, one shard can be replayed alone on one machine with the rest of
    the brain replaced by its recording (rr's idea applied per shard).

D10 Fork = counterfactual replay from a tick with an intervention
    (ablate, clamp, inject). The branch runs shard-locally against the
    recorded inbound spikes and is exact until its outbound spikes to
    OTHER shards differ from the recording; at that tick it is marked
    ESCAPED (the effect has left the shard and shard-local replay is no
    longer exact). How far and how fast an effect spreads is itself the
    measurement.
    Borrowed: activation patching / causal mediation (Vig et al.,
    NeurIPS 2020; Meng et al., NeurIPS 2022), applied along time.

D11 Every tick has a root hash over all shards' state hashes (a Merkle
    tree, Merkle 1987), so a global rewind proves itself with one value
    and a disagreement localises to a shard.

D12 State lives in a flat int32 buffer that can be a plain array or a
    memory-mapped file (RAM + disk, capped per host: the "donated RAM
    and pagefile" of the charter, but restart-safe, unlike a pagefile).
    Forks map a keyframe copy-on-write (mmap ACCESS_COPY, available on
    both Windows and Linux).

## 3. Cross-platform rules (R2)

stdlib only; pathlib paths; os.replace for atomic writes; no fork()-only
multiprocessing, no signals, no SO_REUSEADDR on unicast sockets; explicit
byte order; integer arithmetic in the model. Linux is exercised on
ubu001; Windows execution is PENDING a Windows host (backlog).

## 4. Controls (base role s2)

negative: a no-op fork never diverges; positive: ablating a neuron with
known downstream effect is detected; cheat: a flipped byte in a keyframe,
a log record or a datagram is caught; reliability: runs under injected
datagram loss are bit-identical to runs without loss and to an
in-process reference.

## 5. Known limits of v0

- The end of a run is a two-generals problem: a shard that has finished
  lingers answering NAKs for a bounded time; loss beyond that window can
  strand a peer. Reported, not hidden.
- No replication of keyframes to a second host yet; no re-sharding; no
  global (multi-shard) fork; no multicast (unicast fan-out). Backlog.
