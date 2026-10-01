"""W2-22 v1: run2(mech=None, stop='orig') must equal ffield.run exactly (all fields + traj N,A,B) on seeds that include
W2-14's big runs (FIELD BANK s12 runaway, s36 horizon-ish; FREE BANK s37 cap256). -> v1_equiv.json"""
import json, pickle, sys, time
import multiprocessing as mp
import w22
F = w22.F
BANKS = None
def job(a):
    global BANKS
    struct, s = a
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    t0 = time.process_time()
    seed = 9_998_000 + s
    kw = dict(bank=BANKS["BASE"], pool=BANKS["POOL"], traj=True)
    o = F.run("BASE", seed, struct, "BANK", "CARRY", True, T=300, **kw)
    n = w22.run2("BASE", seed, struct, "BANK", "CARRY", True, T=300, stop="orig", **kw)
    same = all(o[k] == n[k] for k in o if k != "traj") and [list(x) for x in o["traj"]] == [list(x[:3]) for x in n["traj"]]
    return {"struct": struct, "s": s, "match": same, "B": o["B"], "Bxk": n["Bxk"], "kin": n["kin"], "stop": o["stop"],
            "cpu_s": round(time.process_time() - t0, 2)}
if __name__ == "__main__":
    jobs = [("FIELD", s) for s in list(range(20)) + [36, 12]] + [("FREE", s) for s in list(range(20)) + [37]]
    with mp.Pool(6) as p:
        rows = p.map(job, jobs)
    out = {"all_match": all(r["match"] for r in rows), "n": len(rows), "cpu_s": round(sum(r["cpu_s"] for r in rows), 1), "rows": rows}
    json.dump(out, open(w22.HERE / "v1_equiv.json", "w"), indent=1)
    print(out["all_match"], out["n"], out["cpu_s"])
    for r in rows:
        if not r["match"] or r["B"] >= 20: print(r)
