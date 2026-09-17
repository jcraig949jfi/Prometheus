"""E-R5-2 child: run ONE GPU job function inside its nv venv. fn(emit, **kwargs); every emitted row is appended to OUT
as a JSON line and flushed at once, so rows written before a timeout kill survive. No Redis, no lease: the arbiter
(primordial.nv.gpuq, gw-venv) holds the O5 lease for this process's whole life and stamps the rows.

    <nv venv python> -m primordial.nv.gpu_child module:function '{"kw": 1}' OUT.jsonl
"""
from __future__ import annotations

import importlib
import json
import sys


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    fn, kwargs, out = argv[0], json.loads(argv[1]), argv[2]
    mod, _, name = fn.partition(":")
    with open(out, "a", encoding="utf-8", newline="\n") as fh:
        def emit(row: dict) -> None:
            fh.write(json.dumps(row, sort_keys=True, default=str) + "\n")
            fh.flush()
        getattr(importlib.import_module(mod), name)(emit, checkpoint_path=out + ".ckpt", **kwargs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
