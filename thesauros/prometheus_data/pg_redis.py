"""PgRedis — a Postgres-backed drop-in for the subset of redis-py the substrate uses.

Why: Redis under WSL needs manual restarts; the message bus kept dropping. This
backs the bus on the always-on local Postgres (prometheus_fire, schema `bus`)
instead, with no caller changes for anything that goes through get_redis().

Implements only the surface actually used across the codebase:
  streams      xadd, xrange, xrevrange, xread, xlen
  hashes       hset, hget, hgetall, hdel
  sorted sets  zadd, zrange, zrevrange, zrangebyscore
  sets         sadd, smembers
  kv + ttl     get, set, setex, expire, delete, keys, incr
  misc         ping, pipeline (immediate-exec), close

Semantics match redis-py with decode_responses configurable. Stream ids are
'<ms>-<seq>' (wall-clock ms) so existing wall-clock catch-up logic (e.g.
xrange(min=f"{cutoff_ms}-0")) keeps working. xread `block` is emulated by a short
poll loop (Postgres has no blocking pop); this is fine for the bus's poll cadence.

NOT a full Redis: no consumer groups (xreadgroup/xack), no pub/sub, no clustering.
Nothing in the codebase uses those (audited 2026-06-24).
"""
from __future__ import annotations

import os
import time
import json
import fnmatch
from typing import Any, Optional

import psycopg2
import psycopg2.extras


def _now_ms() -> int:
    return int(time.time() * 1000)


def _to_bytes(v: Any) -> bytes:
    if isinstance(v, bytes):
        return v
    if isinstance(v, str):
        return v.encode("utf-8")
    return str(v).encode("utf-8")


def _to_text(v: Any) -> str:
    if isinstance(v, bytes):
        return v.decode("utf-8")
    return str(v)


def _parse_id(tok: Any, *, hi: bool) -> tuple[int, int]:
    """Parse a redis stream id / range token into (ms, seq).
    '-'/0 -> min; '+' -> max; 'ms' -> (ms, 0 or maxseq); 'ms-seq' -> exact."""
    if tok in (b"+", "+"):
        return (1 << 62, 1 << 30)
    if tok in (b"-", "-", 0, "0"):
        return (0, 0)
    s = _to_text(tok)
    if "-" in s:
        ms, seq = s.split("-", 1)
        return (int(ms), int(seq))
    return (int(s), (1 << 30) if hi else 0)


class _Pipeline:
    """Minimal pipeline: executes each call immediately, buffers results."""

    def __init__(self, client: "PgRedis"):
        self._c = client
        self._results: list = []

    def __getattr__(self, name):
        method = getattr(self._c, name)

        def proxy(*a, **k):
            self._results.append(method(*a, **k))
            return self

        return proxy

    def execute(self):
        r, self._results = self._results, []
        return r

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class PgRedis:
    def __init__(self, decode_responses: bool = False, dsn: Optional[str] = None):
        self.decode = decode_responses
        self._conn = psycopg2.connect(dsn or self._default_dsn())
        self._conn.autocommit = True

    @staticmethod
    def _default_dsn() -> str:
        return (
            f"host={os.environ.get('PROMETHEUS_FIRE_HOST', 'localhost')} "
            f"port={os.environ.get('PROMETHEUS_FIRE_PORT', '5432')} "
            f"dbname={os.environ.get('PROMETHEUS_FIRE_DB', 'prometheus_fire')} "
            f"user={os.environ.get('PROMETHEUS_FIRE_USER', 'lmfdb')} "
            f"password={os.environ.get('PROMETHEUS_FIRE_PASSWORD', 'lmfdb')}"
        )

    def _cur(self):
        return self._conn.cursor()

    def _out(self, v):
        if v is None:
            return None
        b = bytes(v) if isinstance(v, memoryview) else v
        if self.decode:
            return _to_text(b)
        return _to_bytes(b)

    # ---- misc ----
    def ping(self):
        with self._cur() as c:
            c.execute("SELECT 1")
            return True

    def pipeline(self, transaction=True):
        return _Pipeline(self)

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

    # ---- streams ----
    def xadd(self, stream, fields: dict, id: str = "*", **kw):
        stream = _to_text(stream)
        ms = _now_ms()
        payload = {_to_text(k): _to_text(v) for k, v in fields.items()}
        with self._cur() as c:
            c.execute(
                "SELECT coalesce(max(seq),-1)+1 FROM bus.stream_entries WHERE stream=%s AND ts_ms=%s",
                (stream, ms),
            )
            seq = c.fetchone()[0]
            entry_id = f"{ms}-{seq}"
            c.execute(
                "INSERT INTO bus.stream_entries(stream, ts_ms, seq, id, fields) VALUES (%s,%s,%s,%s,%s)",
                (stream, ms, seq, entry_id, json.dumps(payload)),
            )
        return entry_id.encode() if not self.decode else entry_id

    def _row_to_entry(self, eid, fields):
        d = fields if isinstance(fields, dict) else json.loads(fields)
        if self.decode:
            data = {k: v for k, v in d.items()}
            return (eid, data)
        return (eid.encode(), {k.encode(): _to_bytes(v) for k, v in d.items()})

    def xrange(self, stream, min="-", max="+", count=None):
        stream = _to_text(stream)
        lo, hi = _parse_id(min, hi=False), _parse_id(max, hi=True)
        q = ("SELECT id, fields FROM bus.stream_entries WHERE stream=%s "
             "AND (ts_ms,seq) >= %s AND (ts_ms,seq) <= %s ORDER BY ts_ms,seq")
        params = [stream, lo, hi]
        if count:
            q += " LIMIT %s"
            params.append(int(count))
        with self._cur() as c:
            c.execute(q, params)
            return [self._row_to_entry(r[0], r[1]) for r in c.fetchall()]

    def xrevrange(self, stream, max="+", min="-", count=None):
        stream = _to_text(stream)
        lo, hi = _parse_id(min, hi=False), _parse_id(max, hi=True)
        q = ("SELECT id, fields FROM bus.stream_entries WHERE stream=%s "
             "AND (ts_ms,seq) >= %s AND (ts_ms,seq) <= %s ORDER BY ts_ms DESC, seq DESC")
        params = [stream, lo, hi]
        if count:
            q += " LIMIT %s"
            params.append(int(count))
        with self._cur() as c:
            c.execute(q, params)
            return [self._row_to_entry(r[0], r[1]) for r in c.fetchall()]

    def xlen(self, stream):
        with self._cur() as c:
            c.execute("SELECT count(*) FROM bus.stream_entries WHERE stream=%s", (_to_text(stream),))
            return c.fetchone()[0]

    def _resolve_last(self, stream, last_id):
        if last_id in (b"$", "$"):
            with self._cur() as c:
                c.execute("SELECT coalesce(max((ts_ms,seq)),(0,0)) FROM bus.stream_entries WHERE stream=%s", (stream,))
                row = c.fetchone()[0]
            return tuple(row) if row else (0, 0)
        return _parse_id(last_id, hi=False)

    def xread(self, streams: dict, count=None, block=None):
        keys = {_to_text(k): self._resolve_last(_to_text(k), v) for k, v in streams.items()}
        deadline = time.time() + (block / 1000.0 if block else 0)
        while True:
            out = []
            with self._cur() as c:
                for stream, after in keys.items():
                    q = ("SELECT id, fields FROM bus.stream_entries WHERE stream=%s "
                         "AND (ts_ms,seq) > %s ORDER BY ts_ms,seq")
                    params = [stream, after]
                    if count:
                        q += " LIMIT %s"
                        params.append(int(count))
                    c.execute(q, params)
                    rows = c.fetchall()
                    if rows:
                        entries = [self._row_to_entry(r[0], r[1]) for r in rows]
                        out.append((stream.encode() if not self.decode else stream, entries))
            if out or not block or time.time() >= deadline:
                return out or None
            time.sleep(0.2)

    # ---- hashes ----
    def hset(self, key, field=None, value=None, mapping=None):
        key = _to_text(key)
        items = {}
        if mapping:
            items.update(mapping)
        if field is not None:
            items[field] = value
        n = 0
        with self._cur() as c:
            for f, v in items.items():
                c.execute(
                    "INSERT INTO bus.hashes(key,field,value) VALUES(%s,%s,%s) "
                    "ON CONFLICT(key,field) DO UPDATE SET value=EXCLUDED.value",
                    (key, _to_text(f), psycopg2.Binary(_to_bytes(v))),
                )
                n += 1
        return n

    def hget(self, key, field):
        with self._cur() as c:
            c.execute("SELECT value FROM bus.hashes WHERE key=%s AND field=%s", (_to_text(key), _to_text(field)))
            row = c.fetchone()
        return self._out(row[0]) if row else None

    def hgetall(self, key):
        with self._cur() as c:
            c.execute("SELECT field, value FROM bus.hashes WHERE key=%s", (_to_text(key),))
            rows = c.fetchall()
        k = (lambda s: s) if self.decode else (lambda s: s.encode())
        return {k(f): self._out(v) for f, v in rows}

    def hdel(self, key, *fields):
        with self._cur() as c:
            c.execute("DELETE FROM bus.hashes WHERE key=%s AND field = ANY(%s)",
                      (_to_text(key), [_to_text(f) for f in fields]))
            return c.rowcount

    # ---- sorted sets ----
    def zadd(self, key, mapping: dict, **kw):
        key = _to_text(key)
        with self._cur() as c:
            for member, score in mapping.items():
                c.execute(
                    "INSERT INTO bus.zsets(key,member,score) VALUES(%s,%s,%s) "
                    "ON CONFLICT(key,member) DO UPDATE SET score=EXCLUDED.score",
                    (key, _to_text(member), float(score)),
                )
        return len(mapping)

    def _zout(self, rows, withscores):
        m = (lambda s: s) if self.decode else (lambda s: s.encode())
        if withscores:
            return [(m(member), score) for member, score in rows]
        return [m(member) for member, _ in rows]

    def zrange(self, key, start, end, desc=False, withscores=False):
        order = "DESC" if desc else "ASC"
        with self._cur() as c:
            c.execute(f"SELECT member,score FROM bus.zsets WHERE key=%s ORDER BY score {order}, member {order}",
                      (_to_text(key),))
            rows = c.fetchall()
        end = None if end == -1 else end + 1
        return self._zout(rows[start:end], withscores)

    def zrevrange(self, key, start, end, withscores=False):
        return self.zrange(key, start, end, desc=True, withscores=withscores)

    def zrangebyscore(self, key, min, max, withscores=False):
        lo = float("-inf") if min in ("-inf", b"-inf") else float(min)
        hi = float("inf") if max in ("+inf", b"+inf") else float(max)
        with self._cur() as c:
            c.execute("SELECT member,score FROM bus.zsets WHERE key=%s AND score>=%s AND score<=%s ORDER BY score ASC",
                      (_to_text(key), lo, hi))
            rows = c.fetchall()
        return self._zout(rows, withscores)

    # ---- sets ----
    def sadd(self, key, *members):
        key = _to_text(key)
        with self._cur() as c:
            n = 0
            for m in members:
                c.execute("INSERT INTO bus.sets(key,member) VALUES(%s,%s) ON CONFLICT DO NOTHING",
                          (key, _to_text(m)))
                n += c.rowcount
        return n

    def smembers(self, key):
        with self._cur() as c:
            c.execute("SELECT member FROM bus.sets WHERE key=%s", (_to_text(key),))
            rows = c.fetchall()
        m = (lambda s: s) if self.decode else (lambda s: s.encode())
        return {m(r[0]) for r in rows}

    # ---- kv + ttl ----
    def set(self, key, value, ex=None, px=None, nx=False):
        ttl = ex if ex else (px / 1000.0 if px else None)
        exp = "now() + (%s || ' seconds')::interval" if ttl else "NULL"
        with self._cur() as c:
            sql = (f"INSERT INTO bus.kv(key,value,expires_at) VALUES(%s,%s,{exp}) "
                   "ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value, expires_at=EXCLUDED.expires_at")
            params = [_to_text(key), psycopg2.Binary(_to_bytes(value))]
            if ttl:
                params.append(str(ttl))
            if nx:
                sql = sql.replace("ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value, expires_at=EXCLUDED.expires_at",
                                  "ON CONFLICT(key) DO NOTHING")
            c.execute(sql, params)
        return True

    def setex(self, key, ttl, value):
        return self.set(key, value, ex=int(ttl))

    def get(self, key):
        with self._cur() as c:
            c.execute("SELECT value FROM bus.kv WHERE key=%s AND (expires_at IS NULL OR expires_at>now())",
                      (_to_text(key),))
            row = c.fetchone()
        return self._out(row[0]) if row else None

    def expire(self, key, ttl):
        with self._cur() as c:
            c.execute("UPDATE bus.kv SET expires_at = now() + (%s || ' seconds')::interval WHERE key=%s",
                      (str(int(ttl)), _to_text(key)))
            return c.rowcount > 0

    def delete(self, *keys):
        ks = [_to_text(k) for k in keys]
        with self._cur() as c:
            c.execute("DELETE FROM bus.kv WHERE key = ANY(%s)", (ks,))
            return c.rowcount

    def incr(self, key, amount=1):
        with self._cur() as c:
            c.execute(
                "INSERT INTO bus.kv(key,value) VALUES(%s,%s) "
                "ON CONFLICT(key) DO UPDATE SET value = "
                "(coalesce(convert_from(bus.kv.value,'UTF8')::bigint,0) + %s)::text::bytea",
                (_to_text(key), psycopg2.Binary(_to_bytes(str(amount))), amount),
            )
            c.execute("SELECT convert_from(value,'UTF8')::bigint FROM bus.kv WHERE key=%s", (_to_text(key),))
            return c.fetchone()[0]

    def keys(self, pattern="*"):
        pat = _to_text(pattern)
        with self._cur() as c:
            c.execute("SELECT key FROM bus.kv WHERE expires_at IS NULL OR expires_at>now()")
            allk = [r[0] for r in c.fetchall()]
        matched = [k for k in allk if fnmatch.fnmatch(k, pat)]
        return matched if self.decode else [k.encode() for k in matched]
