"""NS-01 exclusion-engine qualification (directive s8): can the signature recognise archived mechanisms under
disguise, and does it keep superficially similar but causally different mechanisms apart?

    python -m prometheus.cosmos.supervise launch <rundir> --stall 900 -- \
        python -m prometheus.cosmos.ns01.engine_test run <rundir> [workers]
    python -m prometheus.cosmos.ns01.engine_test analyse <rundir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DISGUISES = ("Permute", "LinearEncode", "Rescale", "RenameState")
# causally different pairs that look alike (same code with a different readout cut; same family, different knob
# regime; same register with a different encoding or carrier)
DISTINCT_PAIRS = [("register", "register_unread"), ("reservoir_fast", "reservoir_slow"),
                  ("stig_static", "stig_moving"), ("register", "signmasked"), ("register", "hidden"),
                  ("stig_moving", "stig_diffusing"), ("nomemory", "register_unread")]


def _make(spec):
    from prometheus.cosmos.ns01 import transforms as T
    from prometheus.cosmos.ns01.witnesses import WITNESSES
    from prometheus.cosmos.c4.planted import Reservoir
    if spec["kind"] == "witness":
        return WITNESSES[spec["name"]][0]
    if spec["kind"] == "disguise":
        base, cls = WITNESSES[spec["name"]][0], getattr(T, spec["disguise"])
        return lambda t: cls(base(t)) if spec["disguise"] in ("Rescale", "RenameState") else cls(base(t), seed=3)
    if spec["key"] == "refactor:delayline":
        return lambda t: T.ShiftRegisterDelay(t)
    if spec["key"] == "param:reservoir_fast":
        return lambda t: Reservoir(t, 0.45, 0.3, wseed=1)
    raise ValueError(spec)


def jobs():
    from prometheus.cosmos.ns01.witnesses import WITNESSES
    out = [{"key": f"witness:{n}", "kind": "witness", "name": n} for n in WITNESSES]
    out += [{"key": f"{d}:{n}", "kind": "disguise", "name": n, "disguise": d} for n in WITNESSES for d in DISGUISES]
    out += [{"key": "refactor:delayline", "kind": "refactor", "name": "delayline"},
            {"key": "param:reservoir_fast", "kind": "param", "name": "reservoir_fast"}]
    return out


def one(spec):
    from prometheus.cosmos.ns01 import signature as S
    sig = S.signature(_make(spec))
    return {**spec, "sig": {k: ({str(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v)
                            for k, v in sig.items()}, "cls": S.classify(sig)}


def _load(rundir):
    rows = [json.loads(x) for x in (Path(rundir) / "engine.jsonl").read_text().splitlines() if x.strip()]
    for r in rows:
        r["sig"] = {k: ({int(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in r["sig"].items()}
    return rows


def analyse(rundir):
    from prometheus.cosmos.ns01 import signature as S
    rows = _load(rundir)
    W = {r["name"]: r for r in rows if r["kind"] == "witness"}
    rec = []
    for r in rows:
        if r["kind"] == "witness":
            continue
        d = {n: S.distance(r["sig"], w["sig"]) for n, w in W.items()}
        near = min(d, key=d.get)
        src = W[r["name"]]
        same_cls = sorted(r["cls"]["fired"]) == sorted(src["cls"]["fired"]) and r["cls"]["viable"] == src["cls"]["viable"]
        rec.append({"key": r["key"], "d_source": d[r["name"]], "nearest": near, "nearest_is_source_or_tie":
                    d[near] >= d[r["name"]] - 1e-12 or d[r["name"]] <= S.TAU, "within_tau": d[r["name"]] <= S.TAU,
                    "same_class": same_cls})
    pairs = []
    for a, b in DISTINCT_PAIRS:
        da = S.distance(W[a]["sig"], W[b]["sig"])
        diff_cls = (sorted(W[a]["cls"]["fired"]), W[a]["cls"]["viable"]) != (sorted(W[b]["cls"]["fired"]), W[b]["cls"]["viable"])
        pairs.append({"pair": [a, b], "distance": da, "kept_apart": da > S.TAU or diff_cls,
                      "apart_by_distance": da > S.TAU, "apart_by_class": diff_cls})
    collapses = []
    names = sorted(W)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if S.distance(W[a]["sig"], W[b]["sig"]) <= S.TAU:
                collapses.append([a, b])
    fr = sum(not (x["within_tau"] and x["same_class"]) for x in rec)
    fa = sum(not p["kept_apart"] for p in pairs)
    return {"n_disguised": len(rec), "false_rejections": fr, "false_rejection_rate": fr / max(len(rec), 1),
            "n_distinct_pairs": len(pairs), "false_acceptances": fa, "false_acceptance_rate": fa / len(pairs),
            "witness_collapses_at_tau": collapses,
            "classes": {n: W[n]["cls"] for n in names}, "disguised": rec, "pairs": pairs}


def run(rundir, workers=1):
    from prometheus.cosmos import supervise as SV
    return SV.run_jobs(one, jobs(), rundir, key="key", out="engine.jsonl", workers=workers, max_failures=0)


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "run":
        run(a[2], int(a[3]) if len(a) > 3 else 1)
    elif a[1] == "analyse":
        print(json.dumps(analyse(a[2]), indent=1, default=str))
