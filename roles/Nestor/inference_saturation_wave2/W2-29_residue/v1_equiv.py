"""W2-29 v1: equivalence gate. run3(stop='orig') with rec on AND off == w22.run2(stop='orig') on all shared fields;
FULL also == ffield.run. Seeds s = 1000..1005 (production seeds; deterministic, so no information leaks into the rule)."""
import json, pickle, time, sys
import multiprocessing as mp
import w29
F = w29.F
KEYS = ["epochs", "stop", "B", "Ball", "maxA", "A_end", "N_end", "depth_f", "depth_world", "calls"]
def job(a):
    partner, s = a
    t0 = time.process_time()
    bk = pickle.load(open(F.HERE / "banks.pkl", "rb")) if partner == "BANK" else None
    kw = dict(bank=bk["BASE"], pool=bk["POOL"]) if bk else {}
    sd = 9_998_000 + s
    ref = w29.w22.run2("BASE", sd, "FIELD", partner, "CARRY", True, T=300, stop="orig", **kw)
    m1, _, _ = w29.run3("BASE", sd, "FIELD", partner, stop="orig", rec=False, **kw)
    m2, G, _ = w29.run3("BASE", sd, "FIELD", partner, stop="orig", rec=True, **kw)
    ok = all(ref[k] == m1[k] == m2[k] for k in KEYS + ["Bxk", "kin"])
    ok_f = True
    if partner == "FULL":
        f = F.run("BASE", sd, "FIELD", "FULL", T=300, **kw)
        ok_f = all(f[k] == m1[k] for k in KEYS)
    return {"partner": partner, "s": s, "ok_run2": ok, "ok_ffield": ok_f, "B": m1["B"], "stop": m1["stop"],
            "n_genomes": len(G), "cpu_s": round(time.process_time() - t0, 1)}
if __name__ == "__main__":
    jobs = [(p, s) for p in ("FULL", "BANK") for s in range(1000, 1006)]
    with mp.Pool(5) as p:
        rows = p.map(job, jobs)
    for r in rows: print(r)
    out = {"rows": rows, "all_ok": all(r["ok_run2"] and r["ok_ffield"] for r in rows)}
    json.dump(out, open(w29.HERE / "v1_equiv.json", "w"), indent=1)
    print("ALL_OK", out["all_ok"], "cpu", sum(r["cpu_s"] for r in rows))
