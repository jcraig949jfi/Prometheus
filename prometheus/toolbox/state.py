"""StateDevice -- Phase 2 (directive s6, s7, s8, s23, s26). HOT world state with lifetimes; never the evidence archive.

The protocol is the kernel's ontology; Redis is one implementation. Semantics are defined here, in the
in-process reference, and any other device must reproduce them (the conformance test in tests/test_state.py
runs the same script against every available device).

Lifetimes (s7):  scope in {"ephemeral", "episode", "lifetime", "persistent"}; an optional integer ttl in TICKS
(the device is told the logical clock through advance(tick); it never reads a wall clock). Scope ends are
explicit: end_scope("episode") discards every episode-scoped key. Persistent keys survive everything but
delete(). "retained"/"discarded" are events the device emits so an Observer can account for forgetting.

Primitives (s6): put/get/delete (kv), hset/hget (record), append/read (stream), zadd/zrange (ranked),
and accounting() -- every call is counted so a Substrate can charge a Player for remembering.

Events (s8): the device appends (tick, kind, player, key_id, value) tuples to an internal event list drained
by events(); kinds are the kernel's EVENT_ID (STATE_READ, STATE_WRITE, ...) so a stream transport can carry
them unchanged.

Snapshot boundary (s26): snapshot() returns the COMPLETE logical state (all scopes, ttls, streams) as bytes;
restore() rebuilds it. A RedisStateDevice snapshot is a dump of the keys under its namespace, so a crashed
run is reconstructable from the last snapshot + the receipts, never from Redis alone.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from prometheus.toolbox.contracts import EVENT_ID, Event

SCOPES = ("ephemeral", "episode", "lifetime", "persistent")
CAPS_KV = frozenset({"ext.state.ttl.v1"})
CAPS_STREAM = frozenset({"ext.state.stream.v1"})


@runtime_checkable
class StateDevice(Protocol):
    kind: str
    capabilities: frozenset

    def advance(self, tick: int) -> None: ...
    def end_scope(self, scope: str) -> int: ...
    def put(self, key: str, value: int | bytes, *, scope: str = "episode", ttl: Optional[int] = None, player: int = -1) -> None: ...
    def get(self, key: str, *, player: int = -1) -> Optional[int | bytes]: ...
    def delete(self, key: str, *, player: int = -1) -> bool: ...
    def hset(self, key: str, field: str, value: int | bytes, *, scope: str = "episode", ttl: Optional[int] = None, player: int = -1) -> None: ...
    def hget(self, key: str, field: str, *, player: int = -1) -> Optional[int | bytes]: ...
    def append(self, stream: str, record: Tuple[int, ...], *, scope: str = "episode", maxlen: Optional[int] = None, player: int = -1) -> int: ...
    def read(self, stream: str, since: int = 0, *, player: int = -1) -> List[Tuple[int, Tuple[int, ...]]]: ...
    def zadd(self, key: str, member: str, score: int, *, scope: str = "episode", player: int = -1) -> None: ...
    def zrange(self, key: str, lo: int, hi: int, *, player: int = -1) -> List[Tuple[str, int]]: ...
    def events(self) -> List[Event]: ...
    def accounting(self) -> Dict[str, int]: ...
    def snapshot(self) -> bytes: ...
    def restore(self, snapshot: bytes) -> None: ...


def _key_id(key: str) -> int:
    import hashlib
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], "big")


class InProcessStateDevice:
    """Reference device. Bounded: `max_keys` and per-stream `maxlen` refuse growth with a recorded event
    rather than an exception (a full memory is an experimental condition, not a crash)."""

    kind = "state.inprocess.v1"
    capabilities = frozenset({"ext.state.ttl.v1", "ext.state.stream.v1", "ext.events.v1", "ext.snapshot.v1", "ext.cost.v1", "ext.reference.v1"})

    def __init__(self, max_keys: int = 4096, default_maxlen: int = 1024):
        self.max_keys = max_keys; self.default_maxlen = default_maxlen
        self._tick = 0
        self._kv: Dict[str, dict] = {}       # key -> {"v": value, "scope", "exp": tick|None}
        self._h: Dict[str, dict] = {}        # key -> {"f": {field: value}, "scope", "exp"}
        self._s: Dict[str, dict] = {}        # stream -> {"r": [(id, record)], "next": int, "scope", "maxlen"}
        self._z: Dict[str, dict] = {}        # key -> {"m": {member: score}, "scope"}
        self._ev: List[Event] = []
        self._c = {"reads": 0, "writes": 0, "deletes": 0, "expired": 0, "refused": 0, "stream_ops": 0, "ranked_ops": 0, "discarded": 0}

    # ------------------------------------------------------------------ clock and scopes
    def advance(self, tick: int) -> None:
        self._tick = tick
        for store in (self._kv, self._h, self._s, self._z):
            for k in [k for k, e in store.items() if e.get("exp") is not None and e["exp"] <= tick]:
                del store[k]; self._c["expired"] += 1
                self._ev.append((tick, EVENT_ID["TASK_CHANGE"], -1, _key_id(k), -2))   # -2 = expired by ttl

    def end_scope(self, scope: str) -> int:
        if scope not in SCOPES:
            raise ValueError(scope)
        n = 0
        order = {"ephemeral": 0, "episode": 1, "lifetime": 2, "persistent": 3}
        for store in (self._kv, self._h, self._s, self._z):
            for k in [k for k, e in store.items() if order[e["scope"]] <= order[scope] and e["scope"] != "persistent"]:
                del store[k]; n += 1
        self._c["discarded"] += n
        self._ev.append((self._tick, EVENT_ID["TASK_CHANGE"], -1, order[scope], -n))
        return n

    def _exp(self, ttl: Optional[int]) -> Optional[int]:
        return None if ttl is None else self._tick + int(ttl)

    def _room(self, store: dict, key: str, player: int) -> bool:
        if key in store or sum(len(s) for s in (self._kv, self._h, self._s, self._z)) < self.max_keys:
            return True
        self._c["refused"] += 1
        self._ev.append((self._tick, EVENT_ID["RESOURCE_CHANGE"], player, _key_id(key), -1))
        return False

    # ------------------------------------------------------------------ kv
    def put(self, key, value, *, scope="episode", ttl=None, player=-1) -> None:
        if scope not in SCOPES:
            raise ValueError(scope)
        if not self._room(self._kv, key, player):
            return
        self._kv[key] = {"v": value, "scope": scope, "exp": self._exp(ttl)}
        self._c["writes"] += 1; self._ev.append((self._tick, EVENT_ID["STATE_WRITE"], player, _key_id(key), value if isinstance(value, int) else len(value)))

    def get(self, key, *, player=-1):
        self._c["reads"] += 1; e = self._kv.get(key)
        self._ev.append((self._tick, EVENT_ID["STATE_READ"], player, _key_id(key), 1 if e else 0))
        return None if e is None else e["v"]

    def delete(self, key, *, player=-1) -> bool:
        self._c["deletes"] += 1
        return any(store.pop(key, None) is not None for store in (self._kv, self._h, self._s, self._z))

    # ------------------------------------------------------------------ records
    def hset(self, key, field, value, *, scope="episode", ttl=None, player=-1) -> None:
        if key not in self._h:
            if not self._room(self._h, key, player):
                return
            self._h[key] = {"f": {}, "scope": scope, "exp": self._exp(ttl)}
        self._h[key]["f"][field] = value; self._c["writes"] += 1
        self._ev.append((self._tick, EVENT_ID["STATE_WRITE"], player, _key_id(key + "/" + field), value if isinstance(value, int) else len(value)))

    def hget(self, key, field, *, player=-1):
        self._c["reads"] += 1; e = self._h.get(key)
        return None if e is None else e["f"].get(field)

    # ------------------------------------------------------------------ streams
    def append(self, stream, record, *, scope="episode", maxlen=None, player=-1) -> int:
        if stream not in self._s:
            if not self._room(self._s, stream, player):
                return -1
            self._s[stream] = {"r": [], "next": 1, "scope": scope, "exp": None, "maxlen": maxlen or self.default_maxlen}
        s = self._s[stream]; rid = s["next"]; s["next"] += 1
        s["r"].append((rid, tuple(int(x) for x in record)))
        if len(s["r"]) > s["maxlen"]:
            s["r"].pop(0); self._c["discarded"] += 1
        self._c["stream_ops"] += 1; self._ev.append((self._tick, EVENT_ID["MESSAGE"], player, _key_id(stream), rid))
        return rid

    def read(self, stream, since=0, *, player=-1):
        self._c["stream_ops"] += 1; s = self._s.get(stream)
        return [] if s is None else [(rid, rec) for rid, rec in s["r"] if rid > since]

    # ------------------------------------------------------------------ ranked
    def zadd(self, key, member, score, *, scope="episode", player=-1) -> None:
        if key not in self._z:
            if not self._room(self._z, key, player):
                return
            self._z[key] = {"m": {}, "scope": scope, "exp": None}
        self._z[key]["m"][member] = int(score); self._c["ranked_ops"] += 1

    def zrange(self, key, lo, hi, *, player=-1):
        self._c["ranked_ops"] += 1; z = self._z.get(key)
        if z is None:
            return []
        items = sorted(z["m"].items(), key=lambda kv: (kv[1], kv[0]))
        return items[lo: hi + 1 if hi >= 0 else None]

    # ------------------------------------------------------------------ events / accounting / snapshot
    def events(self) -> List[Event]:
        out, self._ev = self._ev, []
        return out

    def accounting(self) -> Dict[str, int]:
        return dict(self._c, keys=sum(len(s) for s in (self._kv, self._h, self._s, self._z)))

    def snapshot(self) -> bytes:
        def enc(v):
            return {"b": v.hex()} if isinstance(v, (bytes, bytearray)) else v
        d = {"tick": self._tick, "kv": {k: dict(e, v=enc(e["v"])) for k, e in self._kv.items()},
             "h": {k: dict(e, f={f: enc(v) for f, v in e["f"].items()}) for k, e in self._h.items()},
             "s": self._s, "z": self._z, "c": self._c}
        return json.dumps(d, sort_keys=True).encode()

    def restore(self, snapshot: bytes) -> None:
        def dec(v):
            return bytes.fromhex(v["b"]) if isinstance(v, dict) and "b" in v else v
        d = json.loads(snapshot.decode())
        self._tick = d["tick"]; self._c = d["c"]
        self._kv = {k: dict(e, v=dec(e["v"])) for k, e in d["kv"].items()}
        self._h = {k: dict(e, f={f: dec(v) for f, v in e["f"].items()}) for k, e in d["h"].items()}
        self._s = {k: dict(e, r=[(rid, tuple(rec)) for rid, rec in e["r"]]) for k, e in d["s"].items()}
        self._z = d["z"]; self._ev = []


class RedisStateDevice:
    """EXPLORATORY adapter (allowed by directive s34 once the in-process reference exists). Same semantics,
    keys namespaced under `ns`; ttl is LOGICAL ticks (implemented by the device on advance(), NOT by Redis
    EXPIRE, so replay does not depend on wall time). Constructed only if a server answers; otherwise the
    registry row is UNAVAILABLE with the reason. Snapshot = SCAN of the namespace -> JSON, so the evidence
    boundary (s23) holds: nothing scientific lives only here.
    """

    kind = "state.redis.v1"
    capabilities = frozenset({"ext.state.ttl.v1", "ext.state.stream.v1", "ext.events.v1", "ext.snapshot.v1", "ext.cost.v1"})

    def __init__(self, url: str = "redis://127.0.0.1:6379/0", ns: str = "pk", max_keys: int = 4096, default_maxlen: int = 1024):
        import redis
        self.r = redis.Redis.from_url(url, socket_timeout=2, decode_responses=False); self.r.ping()
        self.ns = ns; self.max_keys = max_keys; self.default_maxlen = default_maxlen
        self._tick = 0; self._ev: List[Event] = []
        self._c = {"reads": 0, "writes": 0, "deletes": 0, "expired": 0, "refused": 0, "stream_ops": 0, "ranked_ops": 0, "discarded": 0}
        self._meta: Dict[str, dict] = {}     # key -> {"scope", "exp", "type"}  (the device owns lifetimes)
        self.r.delete(*self.r.keys(self._k("*")) or ["_"])

    def _k(self, key: str) -> str:
        return "%s:%s" % (self.ns, key)

    def _enc(self, v):
        return b"i:" + str(int(v)).encode() if isinstance(v, int) else b"b:" + bytes(v)

    def _dec(self, raw):
        if raw is None:
            return None
        return int(raw[2:]) if raw[:2] == b"i:" else bytes(raw[2:])

    def advance(self, tick: int) -> None:
        self._tick = tick
        for k in [k for k, m in self._meta.items() if m.get("exp") is not None and m["exp"] <= tick]:
            self.r.delete(self._k(k)); del self._meta[k]; self._c["expired"] += 1
            self._ev.append((tick, EVENT_ID["TASK_CHANGE"], -1, _key_id(k), -2))

    def end_scope(self, scope: str) -> int:
        order = {"ephemeral": 0, "episode": 1, "lifetime": 2, "persistent": 3}
        ks = [k for k, m in self._meta.items() if order[m["scope"]] <= order[scope] and m["scope"] != "persistent"]
        if ks:
            self.r.delete(*[self._k(k) for k in ks])
            for k in ks:
                del self._meta[k]
        self._c["discarded"] += len(ks)
        self._ev.append((self._tick, EVENT_ID["TASK_CHANGE"], -1, order[scope], -len(ks)))
        return len(ks)

    def _room(self, key, player) -> bool:
        if key in self._meta or len(self._meta) < self.max_keys:
            return True
        self._c["refused"] += 1; self._ev.append((self._tick, EVENT_ID["RESOURCE_CHANGE"], player, _key_id(key), -1)); return False

    def put(self, key, value, *, scope="episode", ttl=None, player=-1) -> None:
        if not self._room(key, player):
            return
        self.r.set(self._k(key), self._enc(value)); self._meta[key] = {"scope": scope, "exp": None if ttl is None else self._tick + ttl, "type": "kv"}
        self._c["writes"] += 1; self._ev.append((self._tick, EVENT_ID["STATE_WRITE"], player, _key_id(key), value if isinstance(value, int) else len(value)))

    def get(self, key, *, player=-1):
        self._c["reads"] += 1; v = self._dec(self.r.get(self._k(key)))
        self._ev.append((self._tick, EVENT_ID["STATE_READ"], player, _key_id(key), 0 if v is None else 1)); return v

    def delete(self, key, *, player=-1) -> bool:
        self._c["deletes"] += 1; self._meta.pop(key, None); return bool(self.r.delete(self._k(key)))

    def hset(self, key, field, value, *, scope="episode", ttl=None, player=-1) -> None:
        if key not in self._meta and not self._room(key, player):
            return
        self.r.hset(self._k(key), field, self._enc(value)); self._meta.setdefault(key, {"scope": scope, "exp": None if ttl is None else self._tick + ttl, "type": "h"})
        self._c["writes"] += 1; self._ev.append((self._tick, EVENT_ID["STATE_WRITE"], player, _key_id(key + "/" + field), value if isinstance(value, int) else len(value)))

    def hget(self, key, field, *, player=-1):
        self._c["reads"] += 1; return self._dec(self.r.hget(self._k(key), field))

    def append(self, stream, record, *, scope="episode", maxlen=None, player=-1) -> int:
        if stream not in self._meta:
            if not self._room(stream, player):
                return -1
            self._meta[stream] = {"scope": scope, "exp": None, "type": "s", "next": 1, "maxlen": maxlen or self.default_maxlen}
        m = self._meta[stream]; rid = m["next"]; m["next"] += 1
        self.r.rpush(self._k(stream), json.dumps([rid, [int(x) for x in record]]))
        if self.r.llen(self._k(stream)) > m["maxlen"]:
            self.r.lpop(self._k(stream)); self._c["discarded"] += 1
        self._c["stream_ops"] += 1; self._ev.append((self._tick, EVENT_ID["MESSAGE"], player, _key_id(stream), rid)); return rid

    def read(self, stream, since=0, *, player=-1):
        self._c["stream_ops"] += 1
        return [(rid, tuple(rec)) for rid, rec in (json.loads(x) for x in self.r.lrange(self._k(stream), 0, -1)) if rid > since]

    def zadd(self, key, member, score, *, scope="episode", player=-1) -> None:
        if key not in self._meta and not self._room(key, player):
            return
        self._meta.setdefault(key, {"scope": scope, "exp": None, "type": "z"}); self.r.zadd(self._k(key), {member: int(score)}); self._c["ranked_ops"] += 1

    def zrange(self, key, lo, hi, *, player=-1):
        self._c["ranked_ops"] += 1
        return [(m.decode(), int(s)) for m, s in self.r.zrange(self._k(key), lo, hi, withscores=True)]

    def events(self) -> List[Event]:
        out, self._ev = self._ev, []; return out

    def accounting(self) -> Dict[str, int]:
        return dict(self._c, keys=len(self._meta))

    def snapshot(self) -> bytes:
        dump = {}
        for key, m in self._meta.items():
            rk = self._k(key)
            if m["type"] == "kv":
                dump[key] = {"m": m, "v": self.r.get(rk).hex()}
            elif m["type"] == "h":
                dump[key] = {"m": m, "f": {f.decode(): v.hex() for f, v in self.r.hgetall(rk).items()}}
            elif m["type"] == "s":
                dump[key] = {"m": m, "r": [x.decode() for x in self.r.lrange(rk, 0, -1)]}
            else:
                dump[key] = {"m": m, "z": [(mm.decode(), int(s)) for mm, s in self.r.zrange(rk, 0, -1, withscores=True)]}
        return json.dumps({"tick": self._tick, "c": self._c, "d": dump}, sort_keys=True).encode()

    def restore(self, snapshot: bytes) -> None:
        d = json.loads(snapshot.decode()); self._tick = d["tick"]; self._c = d["c"]; self._meta = {}
        self.r.delete(*self.r.keys(self._k("*")) or ["_"])
        for key, e in d["d"].items():
            m = e["m"]; self._meta[key] = m; rk = self._k(key)
            if m["type"] == "kv":
                self.r.set(rk, bytes.fromhex(e["v"]))
            elif m["type"] == "h":
                for f, v in e["f"].items():
                    self.r.hset(rk, f, bytes.fromhex(v))
            elif m["type"] == "s":
                for x in e["r"]:
                    self.r.rpush(rk, x)
            else:
                for mm, s in e["z"]:
                    self.r.zadd(rk, {mm: s})


def available_devices() -> Dict[str, Any]:
    """Every device that can be constructed on this host, with the reason for each that cannot."""
    out: Dict[str, Any] = {"state.inprocess.v1": {"ok": True}}
    try:
        RedisStateDevice(); out["state.redis.v1"] = {"ok": True}
    except Exception as exc:                                    # noqa: BLE001
        out["state.redis.v1"] = {"ok": False, "reason": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
    return out
