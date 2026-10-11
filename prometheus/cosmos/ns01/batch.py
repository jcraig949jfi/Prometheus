"""NS-01 batch drivers (run under prometheus.cosmos.supervise).

    python -m prometheus.cosmos.ns01.batch ab <campaign_dir> <rundir>     # evaluate frozen Arm A / B proposals
    python -m prometheus.cosmos.ns01.batch d  <campaign_dir> <rundir>     # Arm D: 8 grammar draws with feedback
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

D_SEED = 20261011
N = 8


def _ab_one(j):
    from prometheus.cosmos.ns01.evaluate import evaluate
    r = evaluate(Path(j["camp"]), j["arm"], j["idx"], Path(j["file"]))
    return {"key": j["key"], "label": r["label"], "signal": r["signal"]}


def ab(camp, rundir):
    from prometheus.cosmos import supervise as SV
    camp = Path(camp)
    jobs = [{"key": f"{a}{i:02d}", "camp": str(camp), "arm": a, "idx": i,
             "file": str(camp / "proposals" / a / f"{i:02d}.py")} for a in ("A", "B") for i in range(1, N + 1)]
    return SV.run_jobs(_ab_one, jobs, rundir, key="key", out="ab.jsonl", workers=1, max_failures=0)


def d(camp, rundir):
    """Sequential by construction (feedback); progress is recorded through run_jobs with one job per draw."""
    from prometheus.cosmos import supervise as SV
    SV.assert_spawn_safe()
    camp = Path(camp)
    out = camp / "proposals" / "D"
    out.mkdir(parents=True, exist_ok=True)
    rd = Path(rundir)
    rd.mkdir(parents=True, exist_ok=True)
    from prometheus.cosmos.ns01.evaluate import evaluate
    from prometheus.cosmos.ns01.grammar import Grammar, spec_json
    import time
    g = Grammar(D_SEED)
    prog = {"status": "RUNNING", "pid": __import__("os").getpid(), "start_utc": SV.utc(), "heartbeat_utc": SV.utc(),
            "last_result_utc": None, "n_total": N, "n_done": 0, "n_failed": 0}
    SV._atomic_json(rd / SV.PROGRESS, prog)
    for i in range(1, N + 1):
        spec = g.sample()
        p = out / f"{i:02d}.json"
        p.write_text(spec_json(spec))
        r = evaluate(camp, "D", i, p, meta={"weights_before": json.loads(json.dumps(g.w))})
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
