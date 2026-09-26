"""A shard node: runs one shard in lockstep with its peers over UDP and records it.

Protocol (DESIGN D1-D3). At tick t a node:
  1. waits until it holds a COMPLETE tick t-1 from every peer (TICK_END plus
     all fragments, digest verified); while waiting it NAKs any peer whose
     tick t-1 is incomplete after `nak_timeout`, and answers peers' NAKs from
     its outbox;
  2. steps its shard on the union of those spikes, records the tick, writes a
     keyframe every `keyframe_interval` ticks;
  3. sends every peer its routed spikes for t, always ending with TICK_END.
Outbox[t] is dropped once every peer's tick t+1 is complete (the peer consumed t).
After the last tick the node sends DONE and lingers answering NAKs until every
peer has said DONE or `linger` expires (the two-generals limit, DESIGN s5).
"""
import collections
import sys
import time

from . import model, wire
from .frames import RunDir
from .shard import Shard


class NodeStalled(RuntimeError):
    pass


NodeSummary = collections.namedtuple(
    "NodeSummary",
    "shard ticks naks_sent retransmits dropped corrupt_received foreign wall_s",
)


class _PeerTick:
    __slots__ = ("frags", "end")

    def __init__(self):
        self.frags, self.end = {}, None

    def complete(self):
        if self.end is None or len(self.frags) != self.end.nfrag:
            return False
        gids = [g for f in self.frags.values() for g in f]
        return wire.spike_digest(gids) == self.end.digest

    def gids(self):
        return [g for f in self.frags.values() for g in f]


class Node:
    def __init__(self, run_path, shard_id, endpoint, peers, ticks,
                 nak_timeout=0.03, linger=2.0, max_wall=120.0, progress=0):
        self.rundir = RunDir.open(run_path)
        self.spec = self.rundir.spec
        self.s = shard_id
        self.ep = endpoint
        self.peers = {p: tuple(a) for p, a in peers.items() if p != shard_id}
        self.ticks = ticks
        self.nak_timeout, self.linger, self.max_wall = nak_timeout, linger, max_wall
        self.progress = progress
        self.shard = Shard(self.spec, shard_id)
        self.rec = self.rundir.recorder(shard_id)
        self.outbox = {}  # tick -> {peer: [datagrams]}
        self.inbox = collections.defaultdict(dict)  # tick -> {peer: _PeerTick}
        self.done_peers = set()
        self.naks_sent = self.retransmits = self.corrupt = self.foreign = 0

    # -- receiving ----------------------------------------------------
    def _handle(self, data):
        try:
            p = wire.decode(data)
        except wire.CorruptPacket:
            self.corrupt += 1
            return
        if p.run_id != self.rundir.run_id or p.dst != self.s or p.src not in self.peers:
            self.foreign += 1
            return
        if p.kind == wire.NAK:
            for dgram in self.outbox.get(p.tick, {}).get(p.src, ()):
                self.ep.send(dgram, self.peers[p.src])
                self.retransmits += 1
        elif p.kind == wire.DONE:
            self.done_peers.add(p.src)
        elif p.tick >= self.shard.tick - 1:  # ignore repeats of consumed ticks
            pt = self.inbox[p.tick].setdefault(p.src, _PeerTick())
            if p.kind == wire.SPIKES:
                pt.frags[p.frag] = p.gids
            else:
                pt.end = p
            if pt.end is not None and len(pt.frags) == pt.end.nfrag and not pt.complete():
                self.inbox[p.tick][p.src] = _PeerTick()  # inconsistent: discard, NAK repairs

    def _complete(self, tick, peer):
        pt = self.inbox.get(tick, {}).get(peer)
        return pt is not None and pt.complete()

    def _wait_for(self, tick, t0):
        """Pump the socket until every peer's `tick` is complete."""
        last_nak = {p: time.monotonic() for p in self.peers}
        while True:
            missing = [p for p in self.peers if not self._complete(tick, p)]
            if not missing:
                return
            now = time.monotonic()
            if now - t0 > self.max_wall:
                raise NodeStalled("shard %d waiting for tick %d from %s" % (self.s, tick, missing))
            for p in missing:
                if now - last_nak[p] >= self.nak_timeout:
                    self.ep.send(wire.encode_nak(self.rundir.run_id, tick, self.s, p), self.peers[p])
                    self.naks_sent += 1
                    last_nak[p] = now
            got = self.ep.recv(self.nak_timeout)
            if got is not None:
                self._handle(got[0])

    # -- sending ------------------------------------------------------
    def _emit(self, tick, emitted):
        routed = {p: [] for p in self.peers}
        for g in emitted:
            for d in model.dest_shards(self.spec, g):
                if d in routed:
                    routed[d].append(g)
        box = {}
        for p, gids in routed.items():
            box[p] = wire.encode_tick(self.rundir.run_id, tick, self.s, p, gids)
            for dgram in box[p]:
                self.ep.send(dgram, self.peers[p])
        self.outbox[tick] = box

    def _prune(self, tick):
        # Every peer's tick `tick` is complete, so every peer consumed our tick-1.
        self.outbox.pop(tick - 1, None)
        for t in [t for t in self.inbox if t < tick]:
            del self.inbox[t]

    # -- main loop ----------------------------------------------------
    def run(self):
        t0 = time.monotonic()
        k = self.rundir.keyframe_interval
        try:
            for t in range(self.ticks):
                inbound = []
                if t > 0:
                    self._wait_for(t - 1, t0)
                    inbound = sorted(g for p in self.peers for g in self.inbox[t - 1][p].gids())
                    self._prune(t - 1)
                out = self.shard.step(inbound)
                self.rec.record(t, inbound, out, self.shard.state_hash())
                if t % k == 0:
                    self.rec.keyframe(t, self.shard.state_bytes())
                self._emit(t, out)
                if self.progress and (t + 1) % self.progress == 0:
                    print("shard %d tick %d/%d naks %d retransmits %d" % (
                        self.s, t + 1, self.ticks, self.naks_sent, self.retransmits),
                        file=sys.stderr, flush=True)
            # Peers have consumed our last useful tick once their final tick is complete.
            if self.ticks > 0:
                self._wait_for(self.ticks - 1, t0)
            self._linger()
        finally:
            self.rec.close()
            self.shard.close()
        return NodeSummary(self.s, self.ticks, self.naks_sent, self.retransmits,
                           self.ep.stats.dropped, self.corrupt, self.foreign,
                           round(time.monotonic() - t0, 3))

    def _linger(self):
        end = time.monotonic() + self.linger
        last = 0.0
        while time.monotonic() < end and not self.done_peers >= set(self.peers):
            now = time.monotonic()
            if now - last >= self.nak_timeout:
                for p, a in self.peers.items():
                    self.ep.send(wire.encode_done(self.rundir.run_id, self.ticks, self.s, p), a)
                last = now
            got = self.ep.recv(self.nak_timeout)
            if got is not None:
                self._handle(got[0])
        # One last DONE burst so a peer still lingering can leave early.
        for p, a in self.peers.items():
            self.ep.send(wire.encode_done(self.rundir.run_id, self.ticks, self.s, p), a)
