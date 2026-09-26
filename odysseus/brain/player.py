"""Playback of a recorded run: seek, step, play, pause, rewind, fast-forward, fork.

Every recomputed tick is checked against the recorded state hash and
outbound spikes; a mismatch raises ReplayDivergence (never a silent
drift). A Player replays ONE shard against its recorded inbound spikes
(shard-local replay, DESIGN D9); GlobalPlayer drives all shards and
proves the whole brain with the tick's Merkle root (DESIGN D11).
"""
import collections
import hashlib
import mmap
import os
import tempfile
import threading
from pathlib import Path

from . import model
from .frames import RunDir
from .shard import Shard

Frame = collections.namedtuple("Frame", "tick inbound outbound state_hash")
Diff = collections.namedtuple("Diff", "added removed")


class ReplayDivergence(RuntimeError):
    def __init__(self, shard, tick, what):
        super().__init__("shard %d diverged from the recording at tick %d (%s)" % (shard, tick, what))
        self.shard, self.tick, self.what = shard, tick, what


class Stats:
    def __init__(self):
        self.keyframes_loaded = 0
        self.ticks_recomputed = 0


class Player:
    def __init__(self, run_path, shard, mmap_dir=None):
        self.run = RunDir.open(run_path)
        self.spec = self.run.spec
        self.shard_id = shard
        self.log = self.run.shard_log(shard)
        self.stats = Stats()
        self._pause = threading.Event()
        self._backing = None
        if mmap_dir is not None:
            Path(mmap_dir).mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix="player_s%d_" % shard, suffix=".state",
                                        dir=str(mmap_dir))
            os.close(fd)
            self._backing = Path(name)
        self.mmap_dir = mmap_dir
        self.shard = Shard(self.spec, shard, backing=self._backing)
        self._keyframes = self.log.keyframe_ticks()
        if not self._keyframes or self._keyframes[0] != self.log.first_tick:
            raise ValueError("run has no keyframe at its first tick")
        self._load_keyframe(self._keyframes[0])

    # -- properties ---------------------------------------------------
    @property
    def tick(self):
        return self.shard.tick

    @property
    def first_tick(self):
        return self.log.first_tick

    @property
    def last_tick(self):
        return self.log.last_tick

    @property
    def paused(self):
        return self._pause.is_set()

    def state_hash(self):
        return self.shard.state_hash()

    def state_bytes(self):
        return self.shard.state_bytes()

    def v(self, gid):
        return self.shard.v(gid)

    # -- mechanics ----------------------------------------------------
    def _load_keyframe(self, k):
        self.shard.load_state(self.log.load_keyframe(k), k)
        self.stats.keyframes_loaded += 1

    def _advance(self):
        t = self.shard.tick + 1
        rec = self.log.record(t)
        out = self.shard.step(rec.inbound)
        h = self.shard.state_hash()
        self.stats.ticks_recomputed += 1
        if out != rec.outbound:
            raise ReplayDivergence(self.shard_id, t, "outbound spikes")
        if h != rec.state_hash:
            raise ReplayDivergence(self.shard_id, t, "state hash")
        return Frame(t, rec.inbound, out, h)

    # -- transport controls -------------------------------------------
    def seek(self, t):
        if not self.first_tick <= t <= self.last_tick:
            raise IndexError("tick %d outside recording [%d, %d]" % (t, self.first_tick, self.last_tick))
        if t == self.tick:
            return
        k = max(x for x in self._keyframes if x <= t)
        if not (self.tick < t and t - self.tick <= t - k):
            self._load_keyframe(k)
        while self.tick < t:
            self._advance()

    def step(self):
        self.seek(self.tick + 1)

    def step_back(self):
        self.seek(self.tick - 1)

    def play(self, until=None, on_frame=None):
        """Play forward to `until` (default: the end), one verified frame at a time.

        Stops early, leaving `paused` set, when pause() is called from the
        frame callback or another thread. Returns the number of ticks played.
        """
        until = self.last_tick if until is None else min(until, self.last_tick)
        self._pause.clear()
        n = 0
        while self.tick < until and not self._pause.is_set():
            f = self._advance()
            n += 1
            if on_frame is not None:
                on_frame(f)
        return n

    def pause(self):
        self._pause.set()

    def rewind(self, n):
        self.seek(max(self.first_tick, self.tick - n))

    def fast_forward(self, n):
        self.seek(min(self.last_tick, self.tick + n))

    # -- microtests ---------------------------------------------------
    def fork(self, ablate=(), inject=None):
        return Branch(self, ablate, inject)

    def close(self):
        self.shard.close()
        if self._backing is not None:
            try:
                self._backing.unlink()
            except OSError:
                pass


class Branch:
    """A counterfactual continuation of one shard from the player's current tick.

    Runs against the RECORDED inbound spikes. It is exact until the tick at
    which its spikes to other shards differ from the recording (escaped_at);
    after that the rest of the brain would have reacted, and shard-local
    replay no longer tells the truth (DESIGN D10).
    """

    def __init__(self, player, ablate, inject):
        self.spec, self.log, self.s = player.spec, player.log, player.shard_id
        self.start = player.tick
        self.ablate = frozenset(ablate)
        self._inject = dict(inject) if inject else None
        self._map = self._file = None
        if player.mmap_dir is not None and self.start in player._keyframes:
            # Copy-on-write view of the keyframe: pages are shared until written.
            self._file = open(self.log.keyframe_path(self.start), "rb")
            self._map = mmap.mmap(self._file.fileno(), self.log.state_size(self.start),
                                  access=mmap.ACCESS_COPY)
            self.shard = Shard(self.spec, self.s, buffer=self._map)
            self.shard.tick = self.start
            if self.shard.state_hash() != player.state_hash():
                raise ReplayDivergence(self.s, self.start, "keyframe vs player state")
        else:
            self.shard = Shard(self.spec, self.s, initial=player.state_bytes())
            self.shard.tick = self.start
        self.diverged_at = None
        self.escaped_at = None
        self._out = {}

    @property
    def tick(self):
        return self.shard.tick

    @property
    def exact_until(self):
        """Last tick this branch is guaranteed exact (None: exact throughout)."""
        return self.escaped_at

    def _remote(self, gids):
        return [g for g in gids if any(d != self.s for d in model.dest_shards(self.spec, g))]

    def step(self):
        t = self.shard.tick + 1
        rec = self.log.record(t)
        inj, self._inject = self._inject, None  # injection applies on the first branch tick
        out = self.shard.step(rec.inbound, ablate=self.ablate, inject=inj)
        self._out[t] = out
        if self.diverged_at is None and self.shard.state_hash() != rec.state_hash:
            self.diverged_at = t
        if self.escaped_at is None and self._remote(out) != self._remote(rec.outbound):
            self.escaped_at = t
        return out

    def run(self, until):
        while self.shard.tick < until:
            self.step()

    def outbound_at(self, t):
        return self._out[t]

    def diff_at(self, t):
        a, b = set(self._out[t]), set(self.log.record(t).outbound)
        return Diff(a - b, b - a)

    def state_hash(self):
        return self.shard.state_hash()

    def close(self):
        self.shard.close()
        if self._map is not None:
            self._map.close()
            self._file.close()


class GlobalPlayer:
    """All shards of a run, moved together; the tick root proves the whole brain."""

    def __init__(self, run_path, mmap_dir=None):
        self.run = RunDir.open(run_path)
        self.players = [Player(run_path, s, mmap_dir=mmap_dir)
                        for s in range(self.run.spec.n_shards)]

    @property
    def tick(self):
        return self.players[0].tick

    def seek(self, t):
        for p in self.players:
            p.seek(t)

    def root(self):
        from .frames import merkle_root
        return merkle_root([p.state_hash() for p in self.players])

    def recorded_root(self, t):
        return self.run.tick_root(t)

    def global_digest(self):
        return hashlib.sha256(b"".join(p.state_bytes() for p in self.players)).digest()

    def close(self):
        for p in self.players:
            p.close()
