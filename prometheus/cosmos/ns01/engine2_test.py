"""NS-02 engine requalification with the de-saturated signature (criteria fixed in NS-02 PROTOCOL before this run):
FR <= .10 on disguised witnesses; FA <= 1/7 on the NS-01 look-alike pairs; >= 4/6 of the NS-01 COLLAPSED perfect-memory
pairs separate (stress distance > TAU_S).

    python -m prometheus.cosmos.ns01.engine2_test run <campaign_dir_ns01> <rundir> | analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from prometheus.cosmos.ns01.engine_test import DISGUISES, DISTINCT_PAIRS

COLLAPSED_PAIRS = [("A02", "A03"), ("A02", "B07"), ("A06", "C05"), ("B07", "C05"), ("A03", "C03"), ("A01", "B04")]


def _make(spec):
    from prometheus.cosmos.ns01 import transforms as T
    from prometheus.cosmos.ns01.evaluate import load_llm
    from prometheus.cosmos.ns01.witnesses import WITNESSES
    if spec["kind"] == "proposal":
        return load_llm((Path(spec["camp"]) / "proposals" / spec["name"][0] / f"{int(spec['name'][1:]):02d}.py").read_text())
    base = WITNESSES[spec["name"]][0]
    if spec["kind"] == "witness":
        return base
    cls = getattr(T, spec["disguise"])
    return (lambda t: cls(base(t))) if spec["disguise"] in ("Rescale", "RenameState") else (lambda t: cls(base(t), seed=3))


def jobs(camp):
    from prometheus.cosmos.ns01.witnesses import WITNESSES
    out = [{"key": f"witness:{n}", "kind": "witness", "name": n} for n in WITNESSES]
    out += [{"key": f"{d}:{n}", "kind": "disguise", "name": n, "disguise": d} for n in WITNESSES for d in DISGUISES]
    props = sorted({p for pr in COLLAPSED_PAIRS for p in pr})
    out += [{"key": f"proposal:{p}", "kind": "proposal", "name": p, "camp": str(camp)} for p in props]
    return out


def one(spec):
    from prometheus.cosmos.ns01 import signature2 as S2
    from prometheus.cosmos.ns01.evaluate import _sigjson
    sig = S2.signature2(_make(spec))
    st = sig.pop("stress")
    return {**{k: spec[k] for k in ("key", "kind", "name")}, "disguise": spec.get("disguise"), "sig": _sigjson(sig),
            "stress": {"corr": {str(q): v for q, v in st["corr"].items()}, "dual1": st["dual1"], "dual2": st["dual2"]}}


def _load(rundir):
    rows = []
    for x in (Path(rundir) / "engine2.jsonl").read_text().splitlines():
        r = json.loads(x)
        r["sig"] = {k: ({int(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in r["sig"].items()}
        r["sig"]["stress"] = {"corr": {float(q): v for q, v in r["stress"]["corr"].items()}, "dual1": r["stress"]["dual1"],
                              "dual2": r["stress"]["dual2"]}
        rows.append(r)
    return rows


def analyse(rundir):
    from prometheus.cosmos.ns01 import signature2 as S2
    rows = _load(rundir)
    W = {r["name"]: r["sig"] for r in rows if r["kind"] == "witness"}
    P = {r["name"]: r["sig"] for r in rows if r["kind"] == "proposal"}
    dis = [r for r in rows if r["kind"] == "disguise"]
    fr = [r["key"] for r in dis if not S2.equivalent(r["sig"], W[r["name"]])]
    fa = [list(p) for p in DISTINCT_PAIRS if S2.equivalent(W[p[0]], W[p[1]])]
    col = [{"pair": list(p), "d_base": S2.distances(P[p[0]], P[p[1]])[0], "d_stress": S2.distances(P[p[0]], P[p[1]])[1],
            "separated": S2.distances(P[p[0]], P[p[1]])[1] > S2.TAU_S} for p in COLLAPSED_PAIRS]
    nsep = sum(c["separated"] for c in col)
    ok = len(fr) / len(dis) <= .10 and len(fa) <= 1 and nsep >= 4
    return {"false_rejections": fr, "fr_rate": len(fr) / len(dis), "false_acceptances": fa, "collapsed_pairs": col,
            "n_collapsed_separated": nsep, "qualified": ok,
            "stress_profiles": {n: {"corr": s["stress"]["corr"], "dual1": s["stress"]["dual1"], "dual2": s["stress"]["dual2"]}
                                for n, s in {**W, **P}.items()}}


def run(camp, rundir):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(camp), rundir, key="key", out="engine2.jsonl", workers=2, max_failures=0)


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], a[3])
    else:
        print(json.dumps(analyse(a[2]), indent=1, default=str))
