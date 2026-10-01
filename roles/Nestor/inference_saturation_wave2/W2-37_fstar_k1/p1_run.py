"""W2-37 driver. python -B p1_run.py STRUCT s0 n CAP_CPU_MIN [CPU_ALREADY_S]
w22.run2 exactly as W2-22 p1_run.py (BASE, BANK, CARRY, MUT ON, T 300, stop 'xk', mech None); seed 9_998_000 + s.
Ordered batches of 60 seeds (Pool(6).map); dispatch stops once cumulative CPU (incl. CPU_ALREADY_S) exceeds CAP;
completed set = contiguous batch prefix. Appends to runs_STRUCT.jsonl (traj kept if maxA >= 10)."""
import json, pickle, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-22_second_regime"))
import w22  # noqa: E402
F = w22.F
BANKS = None


def job(a):
    global BANKS
    struct, s = a
    if BANKS is None:
        BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
    t0 = time.process_time()
    res = w22.run2("BASE", 9_998_000 + s, struct, "BANK", "CARRY", True, T=300, bank=BANKS["BASE"], pool=BANKS["POOL"],
                   traj=True, mech=None, stop="xk")
    if res["maxA"] < 10:
        res.pop("traj")
    res["s"] = s
    res["cpu_s"] = round(time.process_time() - t0, 2)
    return res


if __name__ == "__main__":
    struct, s0, n, cap = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
    cpu = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
    t0 = time.time(); last = s0 - 1
    seeds = list(range(s0, s0 + n))
    with mp.Pool(6) as p, open(HERE / ("runs_%s.jsonl" % struct), "a") as fh:
        for b in range(0, n, 60):
            if cpu > cap * 60:
                print("CAP_STOP before batch", b, "cpu_tot %.0f" % cpu, flush=True)
                break
            for res in p.map(job, [(struct, s) for s in seeds[b:b + 60]], chunksize=1):
                fh.write(json.dumps(res) + "\n"); cpu += res["cpu_s"]
            fh.flush()
            last = seeds[min(b + 59, n - 1)]
            print("batch", b, "last_seed", last, "cpu_tot %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
    print("DONE", struct, "last_seed", last, "cpu_tot %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
