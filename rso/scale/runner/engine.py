"""The runtime-agnostic engine interface (C-013-T022; architecture s3.4 tier C).

An engine is five pure operations over an opaque state plus a probe:

    init(params)              -> state          the state at counter 0, from the partition's params alone
    step(state, n)            -> state          advance n counter units (ticks, generations, evaluations)
    save_state(state)         -> bytes          every bit the future depends on, RNG state included
    load_state(params, bytes) -> state          inverse of save_state; refuses bytes it did not write
    digest(state)             -> str            sha256 hex of the canonical subset compared for replay equality
    probe()                   -> dict           the EnvironmentSpec a host must match (s3.2)

The runner never looks inside a state. The engine owner owns save/load (rso-builder-role s2.1); an adapter only
wraps. Engines are found by Moonshot runtime identity {name, version} (moonshot/epoch/runtime.py:67-75).
"""
import hashlib
import os
import platform
import struct

from moonshot.epoch import canonical as C

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUNNER_FILES = ("rso/scale/runner/engine.py",)


def file_sha256(rel):
    """sha256 of a repository file with CRLF normalised to LF, so a Windows checkout and a Linux checkout of
    the same blob probe equal (git autocrlf rewrites line endings, not content)."""
    with open(os.path.join(REPO, rel), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def base_probe(files):
    return {"python": "{}.{}".format(*platform.python_version_tuple()[:2]),
            "engine_files": {rel: file_sha256(rel) for rel in sorted(set(files))}}


class Engine:
    runtime = None

    def init(self, params):
        raise NotImplementedError

    def step(self, state, n):
        raise NotImplementedError

    def save_state(self, state):
        raise NotImplementedError

    def load_state(self, params, data):
        raise NotImplementedError

    def digest(self, state):
        raise NotImplementedError

    def probe(self):
        raise NotImplementedError


class ToyState:
    __slots__ = ("params", "tick", "h")

    def __init__(self, params, tick, h):
        self.params, self.tick, self.h = params, tick, h


class ToyEngine(Engine):
    """A pure-Python hash chain: cheap, exact, and with a tunable cost per tick (work_per_tick sha256 calls), so
    the runner can be tested without numpy. It computes nothing of scientific interest."""
    runtime = {"name": "rso.runner.toy", "version": 1}
    MAGIC = b"RSOTOY01"

    def init(self, params):
        seed = C.canonical_bytes({"seed": params["seed"]})
        return ToyState(params, 0, hashlib.sha256(b"rso.runner.toy\x00" + seed).digest())

    def step(self, state, n):
        h, t, work = state.h, state.tick, state.params["work_per_tick"]
        sha = hashlib.sha256
        for _ in range(n):
            for _ in range(work):
                h = sha(h).digest()
            h = sha(h + t.to_bytes(8, "big")).digest()
            t += 1
        return ToyState(state.params, t, h)

    def save_state(self, state):
        return self.MAGIC + struct.pack(">Q", state.tick) + state.h

    def load_state(self, params, data):
        if not isinstance(data, (bytes, bytearray)) or len(data) != 48 or data[:8] != self.MAGIC:
            raise ValueError("not a rso.runner.toy v1 checkpoint")
        return ToyState(params, struct.unpack(">Q", data[8:16])[0], bytes(data[16:]))

    def digest(self, state):
        return C.tagged_digest("rso.runner.toy.state.v1", {"tick": state.tick, "h": state.h.hex()})

    def probe(self):
        return base_probe(RUNNER_FILES)


def _aether():
    from rso.scale.runner import aether
    return aether.AetherKernelEngine


REGISTRY = {("rso.runner.toy", 1): lambda: ToyEngine, ("rso.runner.aether_kernel", 1): _aether}


def lookup(runtime):
    """The engine class for a runtime {name, version}, or None. Strict, as moonshot.epoch.runtime.lookup."""
    if not isinstance(runtime, dict) or sorted(runtime) != ["name", "version"]:
        return None
    name, version = runtime["name"], runtime["version"]
    if not isinstance(name, str) or isinstance(version, bool) or not isinstance(version, int):
        return None
    factory = REGISTRY.get((name, version))
    return factory() if factory else None


def get_engine(runtime):
    cls = lookup(runtime)
    if cls is None:
        raise LookupError("no engine registered for runtime {}".format(runtime))
    return cls()
