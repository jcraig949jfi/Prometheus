"""Model-based property test for the StateDevice contract (overnight C24). A tiny reference MODEL (dicts + an
explicit expiry rule) is driven with the same random op sequence as the device; every observable answer must
agree. Pins the TTL boundary (a key put at tick T with ttl k is gone from advance(T+k) on, present before),
scope transitions (end_scope(s) discards s and every narrower scope; persistent survives) and capacity.
Runs against every reachable device (Redis is skipped with the reason)."""
from __future__ import annotations

import random

import pytest

from prometheus.toolbox import state as ST

ORDER = {"ephemeral": 0, "episode": 1, "lifetime": 2, "persistent": 3}


class Model:
    def __init__(self, max_keys):
        self.kv = {}; self.max_keys = max_keys; self.tick = 0; self.refused = 0; self.expired = 0

    def advance(self, t):
        self.tick = t
        gone = [k for k, e in self.kv.items() if e["exp"] is not None and e["exp"] <= t]
        for k in gone:
            del self.kv[k]; self.expired += 1

    def put(self, k, v, scope, ttl):
        if k not in self.kv and len(self.kv) >= self.max_keys:
            self.refused += 1; return
        self.kv[k] = {"v": v, "scope": scope, "exp": None if ttl is None else self.tick + ttl}

    def get(self, k):
        e = self.kv.get(k); return None if e is None else e["v"]

    def end_scope(self, s):
        gone = [k for k, e in self.kv.items() if ORDER[e["scope"]] <= ORDER[s] and e["scope"] != "persistent"]
        for k in gone:
            del self.kv[k]
        return len(gone)


def drive(dev, seed: int, n_ops: int = 400, max_keys: int = 6):
    rnd = random.Random(seed); m = Model(max_keys); keys = ["k%d" % i for i in range(9)]; t = 0
    for _ in range(n_ops):
        op = rnd.choice(["put", "put", "get", "get", "advance", "end", "snap"])
        if op == "put":
            k = rnd.choice(keys); v = rnd.randrange(100); sc = rnd.choice(list(ORDER)); ttl = rnd.choice([None, 0, 1, 2, 5])
            dev.put(k, v, scope=sc, ttl=ttl); m.put(k, v, sc, ttl)
        elif op == "get":
            k = rnd.choice(keys); assert dev.get(k) == m.get(k), (seed, k)
        elif op == "advance":
            t += rnd.choice([0, 1, 1, 3]); dev.advance(t); m.advance(t)
        elif op == "end":
            s = rnd.choice(list(ORDER)); assert dev.end_scope(s) == m.end_scope(s), (seed, s)
        else:
            snap = dev.snapshot(); dev.put("zz", 1, scope="persistent"); dev.restore(snap)
            assert dev.get("zz") == m.get("zz")
        for k in keys:
            assert dev.get(k) == m.get(k), (seed, "after", op, k)
    a = dev.accounting()
    assert a["expired"] == m.expired and a["refused"] == m.refused, (seed, a, m.expired, m.refused)


@pytest.mark.parametrize("seed", range(25))
def test_inprocess_device_agrees_with_the_model(seed):
    drive(ST.InProcessStateDevice(max_keys=6), seed)


@pytest.mark.parametrize("seed", range(5))
def test_redis_device_agrees_with_the_model(seed):
    avail = ST.available_devices()["state.redis.v1"]
    if not avail["ok"]:
        pytest.skip("no Redis reachable: %s" % avail["reason"])
    drive(ST.RedisStateDevice(ns="pk_model%d" % seed, max_keys=6), seed, n_ops=150)


def test_ttl_boundary_is_exact():
    d = ST.InProcessStateDevice(); d.advance(10); d.put("a", 1, ttl=3)
    d.advance(12); assert d.get("a") == 1
    d.advance(13); assert d.get("a") is None
    d.put("b", 2, ttl=0); assert d.get("b") == 2          # visible until the clock moves
    d.advance(13); assert d.get("b") is None              # ttl 0 = gone at the next advance, even to the same tick


# C24b: an undrained device event buffer grew without bound (found by the model test's runtime). Bounded,
# oldest-dropped, and the drop is COUNTED in accounting so silence is not mistaken for health.
def test_device_event_buffer_is_bounded_and_drops_are_counted():
    d = ST.InProcessStateDevice(max_events=100)
    for i in range(250):
        d.put("k", i, scope="persistent")
    ev = d.events()
    assert len(ev) == 100 and d.accounting()["events_dropped"] == 150 and ev[-1][4] == 249


# C139: the model extended to STREAMS sharing the key budget with kv: append (maxlen keeps the last n, discards
# counted), read since 0, scope end drops streams too, refusal when the budget is full, snapshot/restore mid-way.
class StreamModel(Model):
    def __init__(self, max_keys):
        super().__init__(max_keys); self.s = {}; self.discarded = 0

    def n_keys(self):
        return len(self.kv) + len(self.s)

    def put(self, k, v, scope, ttl):
        if k not in self.kv and self.n_keys() >= self.max_keys:
            self.refused += 1; return
        self.kv[k] = {"v": v, "scope": scope, "exp": None if ttl is None else self.tick + ttl}

    def append(self, st, rec, scope, maxlen):
        if st not in self.s:
            if self.n_keys() >= self.max_keys:
                self.refused += 1; return -1
            self.s[st] = {"r": [], "next": 1, "scope": scope, "maxlen": maxlen}
        e = self.s[st]; rid = e["next"]; e["next"] += 1; e["r"].append((rid, tuple(rec)))
        if len(e["r"]) > e["maxlen"]:
            e["r"].pop(0); self.discarded += 1
        return rid

    def read(self, st):
        return list(self.s[st]["r"]) if st in self.s else []

    def end_scope(self, s):
        n = super().end_scope(s)
        gone = [k for k, e in self.s.items() if ORDER[e["scope"]] <= ORDER[s] and e["scope"] != "persistent"]
        for k in gone:
            del self.s[k]
        self.discarded += n + len(gone)
        return n + len(gone)


def drive_streams(dev, seed: int, n_ops: int = 400, max_keys: int = 6):
    rnd = random.Random(seed); m = StreamModel(max_keys); keys = ["k%d" % i for i in range(5)]; streams = ["s%d" % i for i in range(5)]; t = 0
    for _ in range(n_ops):
        op = rnd.choice(["put", "append", "append", "read", "get", "advance", "end", "snap"])
        if op == "put":
            k = rnd.choice(keys); v = rnd.randrange(100); sc = rnd.choice(list(ORDER)); ttl = rnd.choice([None, 1, 3])
            dev.put(k, v, scope=sc, ttl=ttl); m.put(k, v, sc, ttl)
        elif op == "append":
            st = rnd.choice(streams); rec = (rnd.randrange(100), rnd.randrange(3)); sc = rnd.choice(list(ORDER)); ml = rnd.choice([1, 2, 4])
            a = dev.append(st, rec, scope=sc, maxlen=ml); b = m.append(st, rec, sc, ml)
            assert (a < 0) == (b < 0) and (a == b or a < 0), (seed, st, a, b)
        elif op == "read":
            st = rnd.choice(streams); assert dev.read(st, since=0) == m.read(st), (seed, st, dev.read(st, since=0), m.read(st))
        elif op == "get":
            k = rnd.choice(keys); assert dev.get(k) == m.get(k), (seed, k)
        elif op == "advance":
            t += rnd.choice([0, 1, 2]); dev.advance(t); m.advance(t)
        elif op == "end":
            s = rnd.choice(list(ORDER)); assert dev.end_scope(s) == m.end_scope(s), (seed, s)
        else:
            snap = dev.snapshot(); dev.append("zz", (1,), scope="persistent"); dev.put("zq", 1, scope="persistent"); dev.restore(snap)
            assert dev.read("zz", since=0) == m.read("zz") and dev.get("zq") == m.get("zq")
        for st in streams:
            assert dev.read(st, since=0) == m.read(st), (seed, "after", op, st)
        for k in keys:
            assert dev.get(k) == m.get(k), (seed, "after", op, k)
    a = dev.accounting()
    assert a["refused"] == m.refused and a["discarded"] == m.discarded and a["expired"] == m.expired, (seed, a, m.refused, m.discarded, m.expired)


@pytest.mark.parametrize("seed", range(30))
def test_inprocess_device_streams_agree_with_the_model(seed):
    drive_streams(ST.InProcessStateDevice(max_keys=6), seed)
