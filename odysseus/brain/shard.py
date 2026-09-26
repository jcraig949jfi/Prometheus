"""One shard: the neurons of one contiguous id block and their state.

State is a flat int32 buffer, three words per neuron (v, refractory
countdown, fired-last-tick), held in a bytearray or a memory-mapped file
(DESIGN D12). Arithmetic is integer-only (DESIGN D6).
"""
import hashlib
import mmap
import sys

from . import model

if sys.byteorder != "little":  # state bytes are hashed as-is; the fleet is x86/ARM LE
    raise ImportError("odysseus.brain requires a little-endian host")


class Shard:
    STATE_WORDS = 3

    def __init__(self, spec, shard_id, backing=None, initial=None, buffer=None):
        self.spec = spec
        self.shard_id = shard_id
        self.lo, self.hi = model.shard_range(spec, shard_id)
        self.n = self.hi - self.lo
        self.nbytes = 4 * self.STATE_WORDS * self.n
        self.tick = -1  # the state is "after tick self.tick"
        self._file = None
        self._map = None
        if initial is not None and len(initial) != self.nbytes:
            raise ValueError("initial state has the wrong size")
        if buffer is not None:
            if len(buffer) < self.nbytes:
                raise ValueError("buffer too small")
            self._buf = buffer
        elif backing is not None:
            self._file = open(backing, "w+b")
            self._file.write(initial if initial is not None else bytes(self.nbytes))
            self._file.flush()
            self._map = mmap.mmap(self._file.fileno(), self.nbytes)
            self._buf = self._map
        else:
            self._buf = bytearray(initial if initial is not None else bytes(self.nbytes))
        self._w = memoryview(self._buf)[: self.nbytes].cast("i")

    # -- state access -------------------------------------------------
    def state_bytes(self):
        return bytes(memoryview(self._buf)[: self.nbytes])

    def state_hash(self):
        return hashlib.sha256(memoryview(self._buf)[: self.nbytes]).digest()

    def load_state(self, raw, tick):
        if len(raw) != self.nbytes:
            raise ValueError("state has the wrong size")
        memoryview(self._buf)[: self.nbytes] = raw
        self.tick = tick

    def v(self, gid):
        return self._w[self.STATE_WORDS * (gid - self.lo)]

    def fired(self, gid):
        return self._w[self.STATE_WORDS * (gid - self.lo) + 2] == 1

    def fired_gids(self):
        w, lo = self._w, self.lo
        return [lo + i for i in range(self.n) if w[3 * i + 2]]

    # -- dynamics -----------------------------------------------------
    def step(self, remote_inbound, ablate=frozenset(), inject=None):
        """Advance one tick. `remote_inbound` are gids other shards emitted last tick.

        Returns the sorted gids this shard emits this tick.
        """
        spec, w, lo, hi = self.spec, self._w, self.lo, self.hi
        t = self.tick + 1
        current = [0] * self.n
        for j in self.fired_gids() + list(remote_inbound):
            for g, wt in model.targets(spec, j):
                if lo <= g < hi:
                    current[g - lo] += wt
        emitted = []
        clip = spec.v_clip
        for i in range(self.n):
            gid = lo + i
            k = 3 * i
            c = current[i] + model.drive_at(spec, t, gid)
            if inject:
                c += inject.get(gid, 0)
            v = w[k]
            v = v - (v >> spec.leak_shift) + c
            if v > clip:
                v = clip
            elif v < -clip:
                v = -clip
            r = w[k + 1]
            fire = False
            if r > 0:
                r -= 1  # refractory: integrates, cannot fire
            elif v >= spec.theta:
                fire = True
            if gid in ablate:
                fire = False
                v = 0
            if fire:
                v = 0
                r = spec.refractory
                emitted.append(gid)
            w[k] = v
            w[k + 1] = r
            w[k + 2] = 1 if fire else 0
        self.tick = t
        return emitted

    def close(self):
        self._w.release()
        if self._map is not None:
            self._map.close()
            self._map = None
        if self._file is not None:
            self._file.close()
            self._file = None
