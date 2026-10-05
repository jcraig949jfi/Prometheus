"""TEST-8 (Beta-01): VALIDATION BREADTH on the endogenous route (rung R3). Spec: beta01/windows/T08_VB_SPEC.md.

T07 diagnostic: in 5/15 natural seeds the selector rejects even a planted CORRECT base-class candidate, because the
4 VALIDATE families do not show its saving (validation representativeness). Question: does more validation evidence
(VALIDATE 4 -> 12) rescue those seeds without harming the others?

Breadth 4 = T07's g0 run, identical roles, continuity-verified against T51/T06 (15/15).
Breadth 12 = the same OBSERVE 4 and TRANSFER 32, with VALIDATE = the original 4 + 8 extra families. The extra
families are drawn (seeded `APHRODITE/T08/VAL/<seed>`) from the seed's qualified head (p_PRISTINE <= .75), never
used in any role. Donor = gtc.donor_g('g0') (I_0), kind P, escrow 30k, R_VAL as T51.
Endpoint (as T07): gain = families of the 32 TRANSFER where SEL reaches a T4-v1a-qualified program <= 1M in >= 1 of 2
cells AND PRISTINE is censored. PRISTINE walks are reused from T07.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402
import identity as I  # noqa: E402

OUT = R.RUNS / "T08_VB"
EXTRA = 8
VALIDATION_LIMITED = [4, 9, 12, 13, 14]     # T07 diagnostic (frozen before this test)


def roles12():
    out = []
    for d, s, fams, panel in R.seeds():
        rows = R.rdl(R.RUNS / d / "T51_FOUNDRY.jsonl")
        used = {f["name"] for f in fams}
        q = sorted([r for r in rows if r.get("T4_qualified") and r["source"] == "LIN:%d" % s
                    and r.get("p_PRISTINE", 0) <= 0.75 and r["name"] not in used], key=lambda r: r["name"])
        rng = random.Random(I._seed("APHRODITE/T08/VAL/%d" % s))
        rng.shuffle(q)
        add = [dict(r, role="VALIDATE") for r in q[:EXTRA]]
        keep = [{k: f[k] for k in ("name", "role", "body", "init", "final", "Q2_size", "p_PRISTINE")} for f in fams]
        out.append((d, s, keep + [{k: r[k] for k in ("name", "role", "body", "init", "final", "Q2_size", "p_PRISTINE")}
                                  for r in add], panel, len(add)))
    return out


def stage_run(w=4):
    OUT.mkdir(parents=True, exist_ok=True)
    plan = roles12()
    (OUT / "T08_ROLES.json").write_text(json.dumps([{"src": d, "seed": s, "families": f, "extra": n}
                                                    for d, s, f, _p, n in plan]), encoding="utf-8")
    done = {x["seed"] for x in R.rdl(OUT / "T08_DONORS.jsonl")}
    jobs = [(d, s, f, p, "g0") for d, s, f, p, n in plan if s not in done and n == EXTRA]
    R.log("T08 donor jobs %d (supply: %s)" % (len(jobs), {s: n for _d, s, _f, _p, n in plan}))
    with open(OUT / "T08_DONORS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._donor, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            R.log("seed %d B12 sel=%s" % (r["seed"], r["selected_schema"]))


def stage_score(w=4):
    import hashlib
    donors = R.rdl(OUT / "T08_DONORS.jsonl")
    t07 = R.rdl(R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl")
    have = {(x["lib"], x["family"], x["cell"]) for x in t07}
    libs, todo, index = {}, [], []
    fams_by = {s: [dict(f, seed="LIN%d" % s) for f in fams if f["role"] == "TRANSFER"] for _d, s, fams, _p in R.seeds()}
    for x in donors:
        k = hashlib.sha256(json.dumps(x["selected_entries"], sort_keys=True).encode()).hexdigest()[:16]
        libs[k] = x["selected_entries"]
        for f in fams_by[x["seed"]]:
            for ci in range(2):
                index.append({"seed": x["seed"], "family": f["name"], "cell": ci, "lib": k})
                if (k, f["name"], ci) not in have:
                    todo.append((k, libs[k], f, ci))
    (OUT / "T08_INDEX.json").write_text(json.dumps({"index": index}), encoding="utf-8")
    todo = list({(a[0], a[2]["name"], a[3]): a for a in todo}.values())
    R.log("T08 new walks %d (others reused from T07)" % len(todo))
    with open(OUT / "T08_WALKS.jsonl", "a", encoding="utf-8") as fh, \
            ProcessPoolExecutor(max_workers=w, initializer=R.T.init_worker) as ex:
        for r in ex.map(R._walk, todo, chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()


def stage_report():
    """Frozen rules: T08_VB_SPEC.md s4."""
    t07r = json.loads((R.RUNS / "T07_R7E" / "R7E_RESULT.json").read_text())
    g4 = {int(k): v for k, v in t07r["gain"]["g0"].items()}
    W = {(w["lib"], w["family"], w["cell"]): w["result"] for w in
         R.rdl(R.RUNS / "T07_R7E" / "R7E_WALKS.jsonl") + R.rdl(OUT / "T08_WALKS.jsonl")}
    t07idx = json.loads((R.RUNS / "T07_R7E" / "R7E_INDEX.json").read_text())["index"]
    pristine = {(e["seed"], e["family"], e["cell"]): e["lib"] for e in t07idx if e["genome"] == "PRISTINE"}
    ok = lambda r: bool(r) and not r.get("censored", True)  # noqa: E731
    idx = json.loads((OUT / "T08_INDEX.json").read_text())["index"]
    from collections import defaultdict
    fam_hit = defaultdict(set)
    for e in idx:
        r = W.get((e["lib"], e["family"], e["cell"]))
        p = W.get((pristine[(e["seed"], e["family"], e["cell"])], e["family"], e["cell"]))
        if ok(r) and not ok(p):
            fam_hit[e["seed"]].add(e["family"])
    seeds = sorted({e["seed"] for e in idx})
    g12 = {s: len(fam_hit[s]) for s in seeds}
    better = sum(1 for s in seeds if g12[s] > g4.get(s, 0))
    worse = sum(1 for s in seeds if g12[s] < g4.get(s, 0))
    p = R._sign_p(better, worse)
    rescued = [s for s in VALIDATION_LIMITED if g12.get(s, 0) > 0]
    donors = {x["seed"]: x["selected_schema"] for x in R.rdl(OUT / "T08_DONORS.jsonl")}
    res = {"gain_B4": g4, "gain_B12": g12, "better": better, "worse": worse, "sign_p": round(p, 4),
           "total_B4": sum(g4.get(s, 0) for s in seeds), "total_B12": sum(g12.values()),
           "validation_limited_rescued": rescued, "selections_B12": donors,
           "VB_POSITIVE": p < 0.05 and sum(g12.values()) > sum(g4.get(s, 0) for s in seeds),
           "RESCUES_VALIDATION_LIMITED": len(rescued) >= 3,
           "disposition": "MEASURED" if len(seeds) >= 12 else "SUPPLY_LIMITED"}
    (OUT / "T08_RESULT.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    R.log("T08 %s VB_POSITIVE=%s rescued=%s totals %d -> %d (p %.4f)" % (res["disposition"], res["VB_POSITIVE"], rescued,
                                                                       res["total_B4"], res["total_B12"], p))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    {"run": lambda: stage_run(w), "score": lambda: stage_score(w), "report": stage_report}[st]()
