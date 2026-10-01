"""W2-37 v1: (V1) run2(stop='orig') == ffield.run on fresh s = 49990..49993, both arms (all fields + traj N,A,B);
(V2) run2(stop='xk') reproduces W2-22's logged records exactly (all logged fields except cpu_s/traj) for
FREE s 1027,1156 (cap256, B<27), 1039, 1498 and FIELD s 1400, 1385, 1050. -> v1_validate.json"""
import json, pickle, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
W22D = HERE.parent / "W2-22_second_regime"
sys.path.insert(0, str(W22D))
import w22  # noqa: E402
F = w22.F
BANKS = None


def job(a):
    global BANKS
    kind, struct, s = a
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    t0 = time.process_time()
    seed = 9_998_000 + s
    kw = dict(bank=BANKS["BASE"], pool=BANKS["POOL"], traj=True)
    if kind == "V1":
        o = F.run("BASE", seed, struct, "BANK", "CARRY", True, T=300, **kw)
        n = w22.run2("BASE", seed, struct, "BANK", "CARRY", True, T=300, stop="orig", **kw)
        same = all(o[k] == n[k] for k in o if k != "traj") and [list(x) for x in o["traj"]] == [list(x[:3]) for x in n["traj"]]
        return {"kind": kind, "struct": struct, "s": s, "match": same, "B": o["B"], "stop": o["stop"],
                "cpu_s": round(time.process_time() - t0, 2)}
    n = w22.run2("BASE", seed, struct, "BANK", "CARRY", True, T=300, stop="xk", **kw)
    logged = next(json.loads(l) for l in open(W22D / ("runs_%s.jsonl" % struct)) if json.loads(l)["s"] == s)
    keys = [k for k in logged if k not in ("cpu_s", "traj", "s")]
    same = all(logged[k] == n[k] for k in keys)
    return {"kind": kind, "struct": struct, "s": s, "match": same, "B": n["B"], "stop": n["stop"],
            "cpu_s": round(time.process_time() - t0, 2)}


if __name__ == "__main__":
    jobs = [("V1", st, s) for st in ("FIELD", "FREE") for s in range(49990, 49994)]
    jobs += [("V2", "FREE", s) for s in (1027, 1156, 1039, 1498)] + [("V2", "FIELD", s) for s in (1400, 1385, 1050)]
    with mp.Pool(6) as p:
        rows = p.map(job, jobs, chunksize=1)
    out = {"all_match": all(r["match"] for r in rows), "n": len(rows), "cpu_s": round(sum(r["cpu_s"] for r in rows), 1),
           "rows": rows}
    json.dump(out, open(HERE / "v1_validate.json", "w"), indent=1)
    print(out["all_match"], out["n"], out["cpu_s"])
    for r in rows:
        print(r)
