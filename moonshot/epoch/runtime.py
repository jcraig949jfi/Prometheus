"""Runtimes: pure functions (input_checkpoint, spec) -> (trace, output_checkpoint). CONTRACT s2.

A runtime may not read clock, environment, host, filesystem, network or unseeded randomness, so its
trace cannot carry attempt metadata.

synthetic.v1 is deterministic CPU busy-work (Lane C: no organisms, no world, no science):

    seed  = sha256("moonshot.synthetic.v1" 0x00 || sha256(input) || sha256(canonical(spec)))
    state = seed; for i in 1..work_iterations: state = sha256(state)
            and at every i divisible by trace_every, and at the last i, emit the trace line
            canonical({"i": i, "s": hex(state)}) + "\\n"
    checkpoint = first checkpoint_bytes of sha256("moonshot.synthetic.v1.ckpt" 0x00 || state || u64be(c)),
                 c = 0, 1, 2, ...
"""
import hashlib

from .canonical import canonical_bytes

SYNTHETIC_V1 = {"name": "moonshot.synthetic", "version": 1}
_PARAMS = ("checkpoint_bytes", "trace_every", "work_iterations")
MAX_ITERATIONS = 10 ** 10
MAX_CHECKPOINT_BYTES = 1 << 26


def _params(spec: dict) -> dict:
    p = spec.get("params") if isinstance(spec, dict) else None
    if not isinstance(p, dict) or sorted(p) != list(_PARAMS):
        raise ValueError("synthetic.v1 params must be exactly {}".format(_PARAMS))
    for k in _PARAMS:
        if isinstance(p[k], bool) or not isinstance(p[k], int):
            raise ValueError("synthetic.v1 param {} must be an integer".format(k))
    if not 1 <= p["work_iterations"] <= MAX_ITERATIONS:
        raise ValueError("work_iterations out of range")
    if p["trace_every"] < 1:
        raise ValueError("trace_every must be >= 1")
    if not 0 <= p["checkpoint_bytes"] <= MAX_CHECKPOINT_BYTES:
        raise ValueError("checkpoint_bytes out of range")
    return p


def run_synthetic_v1(input_checkpoint: bytes, spec: dict):
    p = _params(spec)
    sha = hashlib.sha256
    state = sha(b"moonshot.synthetic.v1\x00" + sha(input_checkpoint).digest()
                + sha(canonical_bytes(spec)).digest()).digest()
    n, every = p["work_iterations"], p["trace_every"]
    lines, i = [], 0
    while i < n:
        stop = min((i // every + 1) * every, n)       # the next trace point, or the last iteration
        for _ in range(stop - i):
            state = sha(state).digest()
        i = stop
        lines.append(canonical_bytes({"i": i, "s": state.hex()}) + b"\n")
    out, c = [], 0
    size = 0
    while size < p["checkpoint_bytes"]:
        block = sha(b"moonshot.synthetic.v1.ckpt\x00" + state + c.to_bytes(8, "big")).digest()
        out.append(block)
        size += len(block)
        c += 1
    return b"".join(lines), b"".join(out)[:p["checkpoint_bytes"]]


def _native_wforge_v1(input_checkpoint: bytes, spec: dict):
    """moonshot.native.wforge v1 (C-012-T007), imported on first use: synthetic-only hosts never load wforge."""
    from .native_wforge import run_native_wforge_v1
    return run_native_wforge_v1(input_checkpoint, spec)


REGISTRY = {("moonshot.synthetic", 1): run_synthetic_v1, ("moonshot.native.wforge", 1): _native_wforge_v1}


def lookup(runtime: dict):
    """The registered implementation of a semantic runtime {name, version}, or None. Strict types: a
    version of True is not 1."""
    if not isinstance(runtime, dict) or sorted(runtime) != ["name", "version"]:
        return None
    name, version = runtime["name"], runtime["version"]
    if not isinstance(name, str) or isinstance(version, bool) or not isinstance(version, int):
        return None
    return REGISTRY.get((name, version))
