"""Frames: per-shard keyframes and per-tick log, integrity-checked (DESIGN D8, D11).

Layout of a run directory (one per run; on a fleet, each machine holds
the shard directories it ran):

    run.json                          spec, run_id, keyframe interval
    shard_0003/log.bin                file header + one record per tick
    shard_0003/keyframes/kf_000000000030.bin
                                      raw state bytes, then a trailer

The keyframe puts the state FIRST so it can be memory-mapped at offset 0
(copy-on-write forks, DESIGN D12; Windows requires mapping offsets that
are multiples of the allocation granularity).
"""
import collections
import hashlib
import json
import os
import struct
import zlib
from pathlib import Path

from .model import ModelSpec

RUN_FORMAT = "odysseus.run.v0"

LOG_HEAD_FMT = "<4sHHQ32s"  # magic, version, shard, run_id, spec_hash
LOG_HEAD_MAGIC = b"OLG0"
REC_MAGIC = b"OLR0"
REC_FIXED_FMT = "<QII32s"  # tick, n_in, n_out, state_hash
REC_FIXED = struct.calcsize(REC_FIXED_FMT)
KF_TRAILER_FMT = "<4sIQQ32sI"  # magic, shard, run_id, tick, sha256(state), crc32
KF_MAGIC = b"OKF0"

Record = collections.namedtuple("Record", "tick inbound outbound state_hash")


class CorruptFrame(ValueError):
    pass


def merkle_root(leaves):
    level = [hashlib.sha256(b"\x00" + bytes(x)).digest() for x in leaves]
    if not level:
        return hashlib.sha256(b"").digest()
    while len(level) > 1:
        nxt = [hashlib.sha256(b"\x01" + level[i] + level[i + 1]).digest()
               for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
    return level[0]


def _atomic_write(path, data):
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _encode_record(tick, inbound, outbound, state_hash):
    body = struct.pack(REC_FIXED_FMT, tick, len(inbound), len(outbound), state_hash)
    body += struct.pack("<%dI" % len(inbound), *inbound)
    body += struct.pack("<%dI" % len(outbound), *outbound)
    head = REC_MAGIC + struct.pack("<I", len(body))
    return head + body + struct.pack("<I", zlib.crc32(head + body) & 0xFFFFFFFF)


def shard_dir_name(shard):
    return "shard_%04d" % shard


class RunDir:
    def __init__(self, path, meta):
        self.path = Path(path)
        self.meta = meta
        self.spec = ModelSpec.from_json(json.dumps(meta["spec"]))
        self.run_id = meta["run_id"]
        self.keyframe_interval = meta["keyframe_interval"]
        self._logs = {}

    @classmethod
    def create(cls, path, spec, keyframe_interval, run_id=None, exist_ok=False):
        path = Path(path)
        if run_id is None:
            run_id = int.from_bytes(os.urandom(8), "little") >> 1
        meta = {
            "format": RUN_FORMAT,
            "run_id": run_id,
            "keyframe_interval": keyframe_interval,
            "spec": json.loads(spec.to_json()),
            "spec_hash": spec.spec_hash().hex(),
        }
        if (path / "run.json").exists():
            if not exist_ok:
                raise FileExistsError(path / "run.json")
            existing = cls.open(path)
            if existing.meta != meta:
                raise ValueError("run.json exists with a different spec or run_id")
            return existing
        path.mkdir(parents=True, exist_ok=True)
        _atomic_write(path / "run.json", json.dumps(meta, sort_keys=True, indent=1).encode())
        return cls(path, meta)

    @classmethod
    def open(cls, path):
        meta = json.loads((Path(path) / "run.json").read_text())
        if meta.get("format") != RUN_FORMAT:
            raise CorruptFrame("unknown run format")
        return cls(path, meta)

    def recorder(self, shard):
        return ShardRecorder(self, shard)

    def shard_log(self, shard, allow_truncated_tail=False):
        key = (shard, allow_truncated_tail)
        if key not in self._logs:
            self._logs[key] = ShardLog(self, shard, allow_truncated_tail)
        return self._logs[key]

    def tick_root(self, tick):
        return merkle_root(
            [self.shard_log(s).record(tick).state_hash for s in range(self.spec.n_shards)]
        )


class ShardRecorder:
    def __init__(self, run, shard):
        self.run, self.shard = run, shard
        self.dir = run.path / shard_dir_name(shard)
        (self.dir / "keyframes").mkdir(parents=True, exist_ok=True)
        log_path = self.dir / "log.bin"
        new = not log_path.exists() or log_path.stat().st_size == 0
        self._log = open(log_path, "ab")
        if new:
            self._log.write(struct.pack(LOG_HEAD_FMT, LOG_HEAD_MAGIC, 0, shard,
                                        run.run_id, run.spec.spec_hash()))
            self._log.flush()

    def record(self, tick, inbound, outbound, state_hash):
        self._log.write(_encode_record(tick, list(inbound), list(outbound), state_hash))
        self._log.flush()

    def keyframe(self, tick, state_bytes):
        body = struct.pack("<4sIQQ32s", KF_MAGIC, self.shard, self.run.run_id, tick,
                           hashlib.sha256(state_bytes).digest())
        trailer = body + struct.pack("<I", zlib.crc32(body) & 0xFFFFFFFF)
        _atomic_write(self.dir / "keyframes" / ("kf_%012d.bin" % tick), state_bytes + trailer)

    def close(self):
        self._log.flush()
        os.fsync(self._log.fileno())
        self._log.close()


class ShardLog:
    def __init__(self, run, shard, allow_truncated_tail=False):
        self.run, self.shard = run, shard
        self.dir = run.path / shard_dir_name(shard)
        self.truncated_tail = False
        self._records = {}
        self._parse((self.dir / "log.bin").read_bytes(), allow_truncated_tail)

    def _parse(self, data, allow_truncated_tail):
        hs = struct.calcsize(LOG_HEAD_FMT)
        if len(data) < hs:
            raise CorruptFrame("log header truncated")
        magic, _ver, shard, run_id, spec_hash = struct.unpack(LOG_HEAD_FMT, data[:hs])
        if (magic != LOG_HEAD_MAGIC or shard != self.shard or run_id != self.run.run_id
                or spec_hash != self.run.spec.spec_hash()):
            raise CorruptFrame("log header does not match run")
        pos, expect = hs, None
        while pos < len(data):
            if len(data) - pos < 8:
                self._tail(allow_truncated_tail, pos)
                break
            magic, (blen,) = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])
            if magic != REC_MAGIC:
                raise CorruptFrame("record magic at byte %d" % pos)
            end = pos + 8 + blen + 4
            if end > len(data):
                self._tail(allow_truncated_tail, pos)
                break
            (crc,) = struct.unpack("<I", data[end - 4:end])
            if zlib.crc32(data[pos:end - 4]) & 0xFFFFFFFF != crc:
                raise CorruptFrame("record crc at byte %d" % pos)
            body = data[pos + 8:end - 4]
            if blen < REC_FIXED:
                raise CorruptFrame("record too short at byte %d" % pos)
            tick, n_in, n_out, h = struct.unpack(REC_FIXED_FMT, body[:REC_FIXED])
            if blen != REC_FIXED + 4 * (n_in + n_out):
                raise CorruptFrame("record length at byte %d" % pos)
            ids = struct.unpack("<%dI" % (n_in + n_out), body[REC_FIXED:])
            if expect is not None and tick != expect:
                raise CorruptFrame("tick %d follows %d" % (tick, expect - 1))
            self._records[tick] = Record(tick, list(ids[:n_in]), list(ids[n_in:]), h)
            expect = tick + 1
            pos = end
        if not self._records:
            raise CorruptFrame("empty log")
        self.first_tick = min(self._records)
        self.last_tick = max(self._records)

    def _tail(self, allow, pos):
        if not allow:
            raise CorruptFrame("truncated record at byte %d" % pos)
        self.truncated_tail = True

    def record(self, tick):
        try:
            return self._records[tick]
        except KeyError:
            raise IndexError("tick %d not in log of shard %d" % (tick, self.shard)) from None

    def keyframe_path(self, tick):
        return self.dir / "keyframes" / ("kf_%012d.bin" % tick)

    def keyframe_ticks(self):
        ticks = []
        for p in (self.dir / "keyframes").glob("kf_*.bin"):
            t = int(p.stem[3:])
            if self.first_tick <= t <= self.last_tick:
                ticks.append(t)
        return sorted(ticks)

    def load_keyframe(self, tick):
        data = self.keyframe_path(tick).read_bytes()
        ts = struct.calcsize(KF_TRAILER_FMT)
        if len(data) < ts:
            raise CorruptFrame("keyframe truncated")
        state, trailer = data[:-ts], data[-ts:]
        magic, shard, run_id, t, digest, crc = struct.unpack(KF_TRAILER_FMT, trailer)
        if zlib.crc32(trailer[:-4]) & 0xFFFFFFFF != crc or magic != KF_MAGIC:
            raise CorruptFrame("keyframe trailer")
        if (shard, run_id, t) != (self.shard, self.run.run_id, tick):
            raise CorruptFrame("keyframe identity")
        if hashlib.sha256(state).digest() != digest:
            raise CorruptFrame("keyframe state hash (tick %d, shard %d)" % (tick, shard))
        if digest != self.record(tick).state_hash:
            raise CorruptFrame("keyframe disagrees with log at tick %d" % tick)
        return state

    def state_size(self, tick):
        return self.keyframe_path(tick).stat().st_size - struct.calcsize(KF_TRAILER_FMT)


def rewrite_record_for_test(run_path, shard, tick, inbound=None, outbound=None):
    """Rewrite one log record with a VALID crc (tests: a log that lies consistently)."""
    run = RunDir.open(run_path)
    log = ShardLog(run, shard)
    path = log.dir / "log.bin"
    hs = struct.calcsize(LOG_HEAD_FMT)
    out = bytearray(path.read_bytes()[:hs])
    for t in range(log.first_tick, log.last_tick + 1):
        r = log.record(t)
        if t == tick:
            r = r._replace(inbound=r.inbound if inbound is None else sorted(inbound),
                           outbound=r.outbound if outbound is None else sorted(outbound))
        out += _encode_record(r.tick, r.inbound, r.outbound, r.state_hash)
    path.write_bytes(bytes(out))
