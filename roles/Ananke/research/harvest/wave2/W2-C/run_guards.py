"""Guard score: the REAL held stage (search.evolve -> classify) and plant stage, run under every operator with
the proposed guards (pte_mut/guards.py) observing. Small: relay64 + hold64 held, relay64 plant.

    python run_guards.py            -> out/guard_score.json
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pte_mut import env as _env  # noqa: E402,F401
from pte_mut import fixtures as F, guards as G, operators as O, stages as ST  # noqa: E402

CASES = [("held", "relay64"), ("held", "hold64"), ("plant", "relay64")]
FX = {"relay64": F.relay64(), "hold64": F.hold64()}


def one(stage, fname, op):
    fx = FX[fname]
    with G.guarded(op) as g:
        so = ST.RUNNERS[stage](fx, op)
        if stage == "held":
            g.champion = fx.genome            # the champion the search returned (== fixture by construction)
        al = g.check()
    assert O.originals_intact()
    return so, al


def main():
    cat = O.catalogue()
    out = {}
    c0 = time.process_time()
    base = {c: one(*c, None)[1] for c in CASES}
    out["baseline"] = {f"{s}|{f}": a for (s, f), a in base.items()}
    for name, op in cat.items():
        for st, fname in CASES:
            if st not in op.stages:
                continue
            so, al = one(st, fname, op)
            new = sorted(set(al) - set(base[(st, fname)]))
            out[f"{name}|{st}|{fname}"] = {"guard_alarms": al, "new": new, "pipeline_alarms": so.alarms,
                                           "verdict": so.verdict}
            print(f"{name:24s} {st:6s} {fname:8s} new guard alarms {new}", flush=True)
    out["cpu_s"] = round(time.process_time() - c0, 1)
    (HERE / "out/guard_score.json").write_text(json.dumps(out, indent=1, default=str))
    print("cpu_s", out["cpu_s"])


if __name__ == "__main__":
    main()
