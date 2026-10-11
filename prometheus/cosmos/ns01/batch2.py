"""NS-02 batch drivers: evaluate frozen A/B proposals; Arm D grammar loop (seed 20261012) -- against archive v2.

    python -m prometheus.cosmos.ns01.batch2 ab|d <ns02_dir> <rundir>
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

N = 8
D_SEED = 20261012


def _ab_one(j):
    from prometheus.cosmos.ns01.evaluate2 import evaluate
    r = evaluate(Path(j["camp"]), j["arm"], j["idx"], Path(j["file"]))
    return {"key": j["key"], "label": r["label"], "signal": r["signal"]}


def ab(camp, rundir):
    from prometheus.cosmos import supervise as SV
    camp = Path(camp)
    jobs = [{"key": f"{a}{i:02d}", "camp": str(camp), "arm": a, "idx": i,
             "file": str(camp / "proposals" / a / f"{i:02d}.py")} for a in ("A", "B") for i in range(1, N + 1)]
    return SV.run_jobs(_ab_one, jobs, rundir, key="key", out="ab.jsonl", workers=1, max_failures=0)


def d(camp, rundir):
    from prometheus.cosmos import supervise as SV
    from prometheus.cosmos.ns01.evaluate2 import evaluate
    from prometheus.cosmos.ns01.grammar import Grammar, spec_json
    SV.assert_spawn_safe()
    camp, rd = Path(camp), Path(rundir)
    rd.mkdir(parents=True, exist_ok=True)
    g = Grammar(D_SEED)
    prog = {"status": "RUNNING", "pid": os.getpid(), "start_utc": SV.utc(), "heartbeat_utc": SV.utc(),
            "last_result_utc": None, "n_total": N, "n_done": 0, "n_failed": 0}
    SV._atomic_json(rd / SV.PROGRESS, prog)
    for i in range(1, N + 1):
        spec = g.sample()
        p = camp / "proposals" / "D" / f"{i:02d}.json"
        p.write_text(spec_json(spec))
        r = evaluate(camp, "D", i, p)
        g.feedback(spec, r["signal"] == "ACCEPTED")
        with open(rd / "d.jsonl", "a") as fh:
            fh.write(json.dumps({"key": f"D{i:02d}", "label": r["label"], "signal": r["signal"]}) + "\n")
        prog.update({"n_done": i, "last_result_utc": SV.utc(), "heartbeat_utc": SV.utc()})
        SV._atomic_json(rd / SV.PROGRESS, prog)
    prog["status"] = "DONE"
    SV._atomic_json(rd / SV.PROGRESS, prog)


if __name__ == "__main__":
    a = sys.argv
    {"ab": ab, "d": d}[a[1]](a[2], a[3])
