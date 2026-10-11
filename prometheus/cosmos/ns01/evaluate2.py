"""NS-02 evaluation against ARCHIVE v2 (witnesses + W-REL + every tried NS-01 proposal), de-saturated equivalence.

    python -m prometheus.cosmos.ns01.evaluate2 build <ns02_dir> <engine2.jsonl> <remeasure.jsonl>
    python -m prometheus.cosmos.ns01.evaluate2 one <ns02_dir> <arm> <idx> <source.py | spec.json>
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

from prometheus.cosmos.ns01.evaluate import _sigjson, compliance, dry_run, load_llm


def _unpack(r):
    sig = {k: ({int(kk): vv for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in r["sig"].items()}
    st = r["stress"]
    sig["stress"] = {"corr": {float(q): v for q, v in st["corr"].items()}, "dual1": st["dual1"], "dual2": st["dual2"]}
    return sig


def _pack(sig):
    sig = dict(sig)
    st = sig.pop("stress")
    return {"sig": _sigjson(sig), "stress": {"corr": {str(q): v for q, v in st["corr"].items()}, "dual1": st["dual1"],
                                             "dual2": st["dual2"]}}


def build(ns02, engine2, remeasure):
    from prometheus.cosmos.ns01 import signature2 as S2
    from prometheus.cosmos.ns01.f15 import RelationalWitness
    arch = {}
    for x in Path(engine2).read_text().splitlines():
        r = json.loads(x)
        if r["kind"] == "witness":
            arch[f"witness:{r['name']}"] = {"sig": r["sig"], "stress": r["stress"]}
    arch["witness:W-REL"] = _pack(S2.signature2(lambda t: RelationalWitness(t)))
    for x in Path(remeasure).read_text().splitlines():
        r = json.loads(x)
        arch[f"ns01:{r['key']}"] = {"sig": r["sig"], "stress": r["stress"]}
    Path(ns02, "ARCHIVE_V2_SIGNATURES.json").write_text(json.dumps(arch))
    return len(arch)


def relational(sig):
    from prometheus.cosmos.ns01.signature import KS
    return max(sig["rf"][k] - sig["full"][k] for k in KS) >= 0.20


def evaluate(ns02: Path, arm: str, idx: int, path: Path) -> dict:
    from prometheus.cosmos.ns01 import signature as S1
    from prometheus.cosmos.ns01 import signature2 as S2
    from prometheus.cosmos.ns01.grammar import make_from_spec
    raw = path.read_text()
    sha = hashlib.sha256(raw.encode()).hexdigest()
    with open(ns02 / "CANDIDATES.jsonl", "a") as fh:
        fh.write(json.dumps({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "arm": arm, "idx": idx,
                             "file": str(path), "sha256": sha}, sort_keys=True) + "\n")
    t0 = time.process_time()
    res = {"arm": arm, "idx": idx, "sha256": sha}
    try:
        if path.suffix == ".json":
            make = make_from_spec(json.loads(raw))
        else:
            bad = compliance(raw)
            if bad:
                raise ValueError("compliance: " + bad)
            make = load_llm(raw)
        res["step_s_E4000"] = dry_run(make)
        sig = S2.signature2(make)
        cls = S1.classify(sig)
        if relational(sig):
            cls["fired"].append("M-RELATIONAL")
        arch = {n: _unpack(r) for n, r in json.loads((ns02 / "ARCHIVE_V2_SIGNATURES.json").read_text()).items()}
        prev = {}
        if (ns02 / "EXCLUSION_RESULTS.jsonl").exists():
            for x in (ns02 / "EXCLUSION_RESULTS.jsonl").read_text().splitlines():
                r = json.loads(x)
                if r["arm"] == arm and "sig" in r:
                    prev[f"ns02:{arm}{r['idx']:02d}"] = _unpack(r)
        eq = [n for n, s in arch.items() if S2.equivalent(sig, s)]
        rep = [n for n, s in prev.items() if S2.equivalent(sig, s)]
        near = min(arch, key=lambda n: sum(S2.distances(sig, arch[n])))
        f = [x for x in cls["fired"]]
        if "DEGENERATE" in f:
            lab = "DEGENERATE"
        elif eq:
            lab = "KNOWN_EQUIVALENCE"
        elif not cls["viable"] and f:
            lab = "KNOWN_FAILURE"
        elif cls["viable"] and f:
            lab = "VIABLE_KNOWN_STRUCTURE"
        elif cls["viable"]:
            lab = "VIABLE_DISTINCT"
        else:
            lab = "DISTINCT_BEHAVIOR_UNEXPLAINED"
        res.update({**_pack(sig), "cls": cls, "equivalent_to": eq, "repeat_of_own_run": rep, "nearest": near,
                    "d_nearest": S2.distances(sig, arch[near]), "label": lab})
    except Exception as e:
        res.update({"label": "NONEXECUTABLE", "error": repr(e)[:500], "cls": {"fired": [], "viable": False}})
    res["cpu_s"] = round(time.process_time() - t0, 1)
    from prometheus.cosmos.ns01.evaluate import signal
    res["signal"] = signal(res["label"], res["cls"])
    with open(ns02 / "EXCLUSION_RESULTS.jsonl", "a") as fh:
        fh.write(json.dumps(res, sort_keys=True, default=float) + "\n")
    return res


if __name__ == "__main__":
    a = sys.argv
    if a[1] == "build":
        print(build(a[2], a[3], a[4]))
    else:
        r = evaluate(Path(a[2]), a[3], int(a[4]), Path(a[5]))
        print(json.dumps({"label": r["label"], "signal": r["signal"], "fired": r["cls"]["fired"],
                          "eq": r.get("equivalent_to", [])[:3], "nearest": r.get("nearest"), "err": r.get("error")},
                         default=float))
