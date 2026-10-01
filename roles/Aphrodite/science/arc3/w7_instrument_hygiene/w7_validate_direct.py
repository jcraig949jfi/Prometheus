"""W7: validate program-level direct T4 scoring (tribunal_t4_v1a.direct_score)
against the REAL tribunals scoring the EMITTED artifact:
  v1  : a18_c1.t4_qualified (the frozen T4 v1 path)
  v1a : tribunal_t4_v1a.TribunalT4v1a.after_freeze(artifact).score/qualified
on (i) every query-1/2-divergent example program recorded in
W7_T4DEV_ROWS.jsonl, (ii) up to 40 walked first hits. Single core.
Writes W7_DIRECT_VALIDATION.json.
"""
import json
import random

from w7_common import *              # noqa: F401,F403
import tribunal_t4 as T4             # noqa: E402
import tribunal_t4_v1a as T4A        # noqa: E402

if __name__ == "__main__":
    a18.worker_init()
    byname = {(r["_tag"], r["name"]): r for t in ("A19", "A20") for r in rows(t, t4=False)}
    items = []
    walked = []
    for x in map(json.loads, open(HERE / "W7_T4DEV_ROWS.jsonl")):
        for e in x.get("div_examples", []):
            items.append((x["tag"], x["name"], tuple(e["prog"]), "div"))
        for arm in ("PRISTINE", "L1"):
            for c in x.get("cells_" + arm, []):
                if c.get("prog"):
                    walked.append((x["tag"], x["name"], tuple(c["prog"]), "walk"))
    walked = sorted(set(walked))
    random.Random("W7/VAL").shuffle(walked)
    items += walked[:40]
    res, mism = [], 0
    for tag, name, prog, kind in items:
        r = byname[(tag, name)]
        prov = prov_of(r)
        a17.M.use_provider(prov)
        T4.use_provider(prov)
        w = ("fold", r["init"], r["body"], r["final"])
        real1 = C.t4_qualified(prov, name, prog)[0]
        art = a17.M.artifact_for(name, prog, a17.EMITTER)
        tr = T4A.TribunalT4v1a.after_freeze(art, name)
        reala = tr.qualified(tr.score(art))
        d1 = T4A.direct_score(prog, name, w, "v1")["qualified"]
        da = T4A.direct_score(prog, name, w, "v1a")["qualified"]
        ok = (real1 == d1) and (reala == da)
        mism += not ok
        res.append({"tag": tag, "name": name, "prog": list(prog), "kind": kind, "real_v1": real1, "direct_v1": d1,
                    "real_v1a": reala, "direct_v1a": da, "agree": ok})
        print(kind, name, prog, real1, d1, reala, da, flush=True)
    out = {"n": len(res), "mismatches": mism, "rows": res}
    (HERE / "W7_DIRECT_VALIDATION.json").write_text(json.dumps(out, indent=1))
    print("n", len(res), "mismatches", mism)
