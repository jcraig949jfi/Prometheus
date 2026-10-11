"""NS-02 stage 1b: re-measure every frozen NS-01 proposal with the de-saturated signature (retrospective; the proposals
are unchanged and were frozen before NS-01 evaluation). Output = NS-01 baseline for the NS-02 learning test.

    python -m prometheus.cosmos.ns01.remeasure run <ns01_campaign_dir> <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def one(j):
    from prometheus.cosmos.ns01 import signature2 as S2
    from prometheus.cosmos.ns01.engine2_test import _make
    from prometheus.cosmos.ns01.evaluate import _sigjson
    from prometheus.cosmos.ns01.grammar import make_from_spec
    if j["arm"] == "D":
        mk = make_from_spec(json.loads((Path(j["camp"]) / "proposals" / "D" / f"{j['idx']:02d}.json").read_text()))
    else:
        mk = _make({"kind": "proposal", "name": f"{j['arm']}{j['idx']:02d}", "camp": j["camp"]})
    sig = S2.signature2(mk)
    st = sig.pop("stress")
    return {"key": j["key"], "arm": j["arm"], "idx": j["idx"], "sig": _sigjson(sig),
            "stress": {"corr": {str(q): v for q, v in st["corr"].items()}, "dual1": st["dual1"], "dual2": st["dual2"]}}


def run(camp, rundir):
    from prometheus.cosmos import supervise as SV
    rows = [json.loads(x) for x in (Path(camp) / "EXCLUSION_RESULTS.jsonl").read_text().splitlines() if x.strip()]
    jobs = [{"key": f"{r['arm']}{r['idx']:02d}", "arm": r["arm"], "idx": r["idx"], "camp": str(camp)}
            for r in rows if r["label"] != "NONEXECUTABLE"]
    return SV.run_jobs(one, jobs, rundir, key="key", out="remeasure.jsonl", workers=2, max_failures=0)


if __name__ == "__main__":
    a = sys.argv
    run(a[2], a[3])
