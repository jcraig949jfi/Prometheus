"""WTP-LM01 resource accounting (directive s5; steward rulings R1b-d).

No scalar exchange rate. Every arm carries one Meter that records separately:
  persistent_bytes   bytes of state that survive between calls (measured, not declared: sum of nbytes of
                     the arm's persistent() arrays after each call)
  peak_persistent    max of the above over the life
  bytes_written      bytes appended/overwritten into persistent state
  bytes_read         bytes of persistent state read by predict/learn
  ops                elementary operations (distance terms, multiply-adds, solves counted by size)
  replay_ops         ops spent on replay/consolidation/refit (a subset of ops, reported separately)
  wall               seconds inside the arm's own calls
  n_queries, n_obs   call counts
  external_bytes     storage outside the arm's state (declared; 0 unless an arm uses it)
Audit fields used by the cheat fixtures:
  full_read_violations   predict calls whose bytes_read < the store bytes they were obliged to read (R1d)
  persist_growth_on_query predict calls after which persistent bytes grew (R1c: a refit kept between queries)"""
import time

import numpy as np


class Meter:
    FIELDS = ("persistent_bytes", "peak_persistent", "bytes_written", "bytes_read", "ops", "replay_ops", "wall",
              "n_queries", "n_obs", "external_bytes", "full_read_violations", "persist_growth_on_query")

    def __init__(self):
        for f in self.FIELDS:
            setattr(self, f, 0)
        self.wall = 0.0

    def as_dict(self):
        return {f: (float(getattr(self, f)) if f == "wall" else int(getattr(self, f))) for f in self.FIELDS}


def nbytes(arrays):
    return int(sum(np.asarray(a).nbytes for a in arrays))


class Metered:
    """Base for every LM01 arm. Subclasses implement _observe, _predict, persistent(), and optionally
    _reconstruct (history recovery for R(t)) and must_read_bytes() (the R1d obligation)."""
    name = "arm"
    category = "UNCLASSIFIED"

    def __init__(self):
        self.meter = Meter()

    def persistent(self):
        return []

    def must_read_bytes(self):
        return 0

    def _sync(self):
        pb = nbytes(self.persistent())
        self.meter.persistent_bytes = pb
        self.meter.peak_persistent = max(self.meter.peak_persistent, pb)
        return pb

    def observe(self, A, y):
        t0 = time.perf_counter()
        self._observe(np.asarray(A), np.asarray(y, float))
        self.meter.n_obs += len(y)
        self.meter.wall += time.perf_counter() - t0
        self._sync()

    def predict(self, A):
        before = nbytes(self.persistent())
        read0 = self.meter.bytes_read
        t0 = time.perf_counter()
        out = self._predict(np.asarray(A))
        self.meter.wall += time.perf_counter() - t0
        self.meter.n_queries += 1
        if self.meter.bytes_read - read0 < self.must_read_bytes():
            self.meter.full_read_violations += 1
        if self._sync() > before:
            self.meter.persist_growth_on_query += 1
        return out

    def reconstruct(self, idx, A):
        """Best recovery of admitted observations idx (at cells A) from persistent state alone. Default: the
        arm's own prediction at the cell (a lossy arm cannot address individual records)."""
        m = self.meter
        saved = (m.bytes_read, m.ops, m.wall, m.n_queries, m.full_read_violations, m.persist_growth_on_query)
        out = self._reconstruct(np.asarray(idx), np.asarray(A))
        m.bytes_read, m.ops, m.wall, m.n_queries, m.full_read_violations, m.persist_growth_on_query = saved
        return out

    def _reconstruct(self, idx, A):
        return self._predict(A)
