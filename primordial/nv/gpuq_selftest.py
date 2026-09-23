"""E-R5-2 self-test job functions for primordial.nv.gpuq (no GPU needed; run in any interpreter)."""
from __future__ import annotations

import pathlib
import time


def two_rows(emit, checkpoint_path=None):
    full = {"kind": "timing", "batch_size": 64, "transfer_included": True, "warm_state": "warm",
            "comparison_backend": "numba_t1", "exactness": "PASS", "wall_s": 0.01}
    emit(full)
    emit({k: v for k, v in full.items() if k != "comparison_backend"})       # a timing row missing a 19 s6 field
    emit({"kind": "info", "note": "not a timing row"})


def sleeper(emit, seconds: float = 30.0, checkpoint_path=None):
    emit({"kind": "timing", "batch_size": 1, "transfer_included": False, "warm_state": "cold",
          "comparison_backend": "none", "exactness": True, "wall_s": 0.0})
    if checkpoint_path:
        pathlib.Path(checkpoint_path).write_text("{\"completed_units\": 1}", encoding="utf-8")
    time.sleep(seconds)


def crash(emit, checkpoint_path=None):
    raise RuntimeError("planted child failure")
