"""W2-22 driver. python -B p1_run.py TAG STRUCT MECH s0 n   (MECH = NONE | KIN_COSTLY | NO_REPAIR)
BASE, PARTNER BANK, CTX CARRY, MUT ON, T 300, stop='xk'; seed 9_998_000 + s. Appends to runs_TAG.jsonl (traj kept if maxA >= 10)."""
import json, pickle, sys, time
import multiprocessing as mp
import w22
F = w22.F
BANKS = None
def job(a):
    global BANKS
    struct, mech, s = a
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    t0 = time.process_time()
    res = w22.run2("BASE", 9_998_000 + s, struct, "BANK", "CARRY", True, T=300, bank=BANKS["BASE"], pool=BANKS["POOL"],
                   traj=True, mech=None if mech == "NONE" else mech, stop="xk")
    if res["maxA"] < 10:
        res.pop("traj")
    res["s"] = s
    res["cpu_s"] = round(time.process_time() - t0, 2)
    return res
if __name__ == "__main__":
    tag, struct, mech, s0, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    t0 = time.time(); cpu = 0.0
    with mp.Pool(6) as p, open(w22.HERE / ("runs_%s.jsonl" % tag), "a") as fh:
        for k, res in enumerate(p.imap_unordered(job, [(struct, mech, s) for s in range(s0, s0 + n)], chunksize=4)):
            fh.write(json.dumps(res) + "\n"); fh.flush(); cpu += res["cpu_s"]
            if res["B"] >= 27 or k % 100 == 0:
                print(k, res["s"], res["stop"], res["epochs"], "B", res["B"], "Bxk", res["Bxk"], "maxA", res["maxA"], "cpu_tot %.0f" % cpu, flush=True)
    print("DONE", tag, "cpu_s %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
