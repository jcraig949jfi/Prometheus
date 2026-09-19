"""Workspace: the mutable, bounded, costed data store a Player keeps during a lifetime.

Four stores, all mechanically neutral: cells (address -> value), streams
(id -> list of values), records (id -> field -> value), links (source ->
[(label, target)]). Values are ints or tuples of ints. Every operation
charges cost units into self.cost; the byte size of every store counts
against one capacity. Nothing here knows what a task is.
"""

from __future__ import annotations

import copy
import random

COSTS = {
    "read": 1,
    "write": 2,
    "append": 2,
    "sread": 1,
    "slen": 1,
    "rec_new": 3,
    "rec_get": 1,
    "rec_set": 2,
    "link": 2,
    "links": 1,
    "link_get": 1,
    "alloc": 1,
    "free": 1,
    "find_per_cell": 1,
}

# DESIGN_C2 s2: every store object charges metadata on creation (records, blocks, procedures).
OBJECT_METADATA_BYTES = 2


def value_size(v) -> int:
    if isinstance(v, tuple):
        return max(1, len(v))
    return 1


def is_value(v) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return True
    return isinstance(v, tuple) and all(isinstance(e, int) and not isinstance(e, bool) for e in v)


class Workspace:
    def __init__(self, cells: int = 256, capacity_bytes: int = 4096):
        self.n_cells = cells
        self.capacity = capacity_bytes
        self.cells = {}
        self.streams = {}
        self.records = {}
        self.links = {}
        self.next_stream = 0
        self.next_record = 0
        self.alloc_ptr = 0
        self.allocations = {}
        self.cost = 0
        self.failed_writes = 0
        self.writes = 0
        self._bytes = 0

    @classmethod
    def empty(cls, cfg: dict = None) -> "Workspace":
        if cfg is None:
            return cls()
        w = cfg["workspace"]
        return cls(cells=w["cells"], capacity_bytes=w["capacity_bytes"])

    # ------------------------------------------------------------ accounting
    def bytes_used(self) -> int:
        return self._bytes

    def recount(self) -> int:
        n = sum(value_size(v) for v in self.cells.values())
        n += sum(sum(value_size(v) for v in s) for s in self.streams.values())
        n += sum(OBJECT_METADATA_BYTES + sum(value_size(v) for v in r.values()) for r in self.records.values())
        n += sum(len(ls) for ls in self.links.values())
        self._bytes = n
        return n

    def _fits(self, extra: int) -> bool:
        return self._bytes + extra <= self.capacity

    def clear(self):
        self.__init__(self.n_cells, self.capacity)

    def snapshot(self) -> dict:
        return copy.deepcopy(
            {
                "cells": self.cells,
                "streams": self.streams,
                "records": self.records,
                "links": self.links,
                "next_stream": self.next_stream,
                "next_record": self.next_record,
                "alloc_ptr": self.alloc_ptr,
                "allocations": self.allocations,
            }
        )

    def restore(self, snap: dict):
        snap = copy.deepcopy(snap)
        self.cells = snap["cells"]
        self.streams = snap["streams"]
        self.records = snap["records"]
        self.links = snap["links"]
        self.next_stream = snap["next_stream"]
        self.next_record = snap["next_record"]
        self.alloc_ptr = snap["alloc_ptr"]
        self.allocations = snap["allocations"]
        self.recount()

    def structure(self) -> dict:
        """Shape without contents, for histories."""
        return {
            "cells_written": len(self.cells),
            "streams": len(self.streams),
            "stream_items": sum(len(s) for s in self.streams.values()),
            "records": len(self.records),
            "record_fields": sum(len(r) for r in self.records.values()),
            "link_sources": len(self.links),
            "links": sum(len(ls) for ls in self.links.values()),
            "bytes": self.bytes_used(),
        }

    # ------------------------------------------------------------ cells
    def read(self, address: int):
        self.cost += COSTS["read"]
        return self.cells.get(int(address) % self.n_cells, 0)

    def write(self, address: int, value) -> bool:
        self.cost += COSTS["write"]
        if not is_value(value):
            self.failed_writes += 1
            return False
        addr = int(address) % self.n_cells
        old = value_size(self.cells[addr]) if addr in self.cells else 0
        if not self._fits(value_size(value) - old):
            self.failed_writes += 1
            return False
        self.cells[addr] = value
        self._bytes += value_size(value) - old
        self.writes += 1
        return True

    def find(self, value) -> int:
        """Address of the first cell equal to value, or -1. Charges one unit per cell scanned."""
        scanned = 0
        for addr, v in self.cells.items():
            scanned += 1
            if v == value:
                self.cost += scanned * COSTS["find_per_cell"]
                return addr
        self.cost += max(1, scanned) * COSTS["find_per_cell"]
        return -1

    # ------------------------------------------------------------ streams
    def append(self, stream_id: int, value) -> bool:
        self.cost += COSTS["append"]
        if not is_value(value) or not self._fits(value_size(value)):
            self.failed_writes += 1
            return False
        sid = int(stream_id)
        self.streams.setdefault(sid, []).append(value)
        self._bytes += value_size(value)
        self.writes += 1
        return True

    def read_stream(self, stream_id: int, index: int):
        self.cost += COSTS["sread"]
        s = self.streams.get(int(stream_id))
        if not s:
            return 0
        i = int(index)
        if -len(s) <= i < len(s):
            return s[i]
        return 0

    def stream_len(self, stream_id: int) -> int:
        self.cost += COSTS["slen"]
        return len(self.streams.get(int(stream_id), ()))

    # ------------------------------------------------------------ records
    def create_record(self, fields: dict = None) -> int:
        self.cost += COSTS["rec_new"]
        fields = dict(fields or {})
        if not self._fits(OBJECT_METADATA_BYTES + sum(value_size(v) for v in fields.values())):
            self.failed_writes += 1
            return -1
        rid = self.next_record
        self.next_record += 1
        self.records[rid] = {int(k): v for k, v in fields.items() if is_value(v)}
        self._bytes += OBJECT_METADATA_BYTES + sum(value_size(v) for v in self.records[rid].values())
        self.writes += 1
        return rid

    def get_field(self, record_id: int, field: int):
        self.cost += COSTS["rec_get"]
        r = self.records.get(int(record_id))
        if r is None:
            return 0
        return r.get(int(field), 0)

    def set_field(self, record_id: int, field: int, value) -> bool:
        self.cost += COSTS["rec_set"]
        r = self.records.get(int(record_id))
        if r is None or not is_value(value):
            self.failed_writes += 1
            return False
        f = int(field)
        old = value_size(r[f]) if f in r else 0
        if not self._fits(value_size(value) - old):
            self.failed_writes += 1
            return False
        r[f] = value
        self._bytes += value_size(value) - old
        self.writes += 1
        return True

    # ------------------------------------------------------------ links
    def create_link(self, source: int, label: int, target: int) -> bool:
        self.cost += COSTS["link"]
        if not self._fits(1):
            self.failed_writes += 1
            return False
        self.links.setdefault(int(source), []).append((int(label), int(target)))
        self._bytes += 1
        self.writes += 1
        return True

    def links_from(self, source: int) -> list:
        self.cost += COSTS["links"]
        return list(self.links.get(int(source), ()))

    def link_get(self, source: int, index: int) -> int:
        self.cost += COSTS["link_get"]
        ls = self.links.get(int(source), ())
        i = int(index)
        if 0 <= i < len(ls):
            return ls[i][1]
        return -1

    # ------------------------------------------------------------ allocation
    def allocate(self, size: int) -> int:
        """A fresh, never-handed-out range of cell addresses; returns the base or -1."""
        self.cost += COSTS["alloc"]
        size = max(1, int(size))
        if self.alloc_ptr + size > self.n_cells:
            return -1
        base = self.alloc_ptr
        self.alloc_ptr += size
        self.allocations[base] = size
        return base

    def free(self, handle: int) -> bool:
        self.cost += COSTS["free"]
        base = int(handle)
        size = self.allocations.pop(base, None)
        if size is None:
            return False
        for a in range(base, base + size):
            v = self.cells.pop(a, None)
            if v is not None:
                self._bytes -= value_size(v)
        return True

    # ------------------------------------------------------------ scramble
    def scramble(self, rng: random.Random):
        """Preserve sizes and shapes; destroy the relationships (control D)."""
        addrs = list(self.cells)
        vals = [self.cells[a] for a in addrs]
        rng.shuffle(vals)
        self.cells = dict(zip(addrs, vals))
        for sid in self.streams:
            rng.shuffle(self.streams[sid])
        all_fields = [(rid, f) for rid, r in self.records.items() for f in r]
        all_vals = [self.records[rid][f] for rid, f in all_fields]
        rng.shuffle(all_vals)
        for (rid, f), v in zip(all_fields, all_vals):
            self.records[rid][f] = v
        targets = [t for ls in self.links.values() for _, t in ls]
        rng.shuffle(targets)
        k = 0
        for src in self.links:
            new = []
            for label, _ in self.links[src]:
                new.append((label, targets[k]))
                k += 1
            self.links[src] = new
