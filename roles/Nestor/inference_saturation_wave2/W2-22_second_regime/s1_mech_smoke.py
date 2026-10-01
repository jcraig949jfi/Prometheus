"""W2-22 s1: smoke test only (NOT a mechanism arm): M1/M2 counterfactual switches run and fire, on FIELD BANK seeds that
were runaways in the primary (s 1579, 1357, 1346). -> s1_mech_smoke.json"""
import json, pickle, time
import multiprocessing as mp
import w22
F = w22.F
def job(a):
    mech, s = a
    B = pickle.load(open(F.HERE / "banks.pkl", "rb")); t0 = time.process_time()
    r = w22.run2("BASE", 9_998_000 + s, "FIELD", "BANK", "CARRY", True, T=300, bank=B["BASE"], pool=B["POOL"], mech=mech, stop="xk")
    return {k: r[k] for k in ("mech", "stop", "epochs", "B", "Bxk", "kin", "n_mech", "maxA", "A_end", "depth_f")} | {"s": s, "cpu_s": round(time.process_time() - t0, 1)}
if __name__ == "__main__":
    with mp.Pool(6) as p:
        rows = p.map(job, [(m, s) for m in ("KIN_COSTLY", "NO_REPAIR") for s in (1579, 1357, 1346)])
    json.dump(rows, open(w22.HERE / "s1_mech_smoke.json", "w"), indent=1)
    for r in rows: print(r)
