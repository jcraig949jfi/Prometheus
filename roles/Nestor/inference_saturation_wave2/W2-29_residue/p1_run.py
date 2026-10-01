"""W2-29 driver. python -B p1_run.py TAG PARTNER CAP_CPU_MIN s0 s1 [seedfile]
BASE FIELD, stop xk163, T 300, seed 9_998_000 + s. Batches of 50 seeds (p.map, Pool(5)); stops dispatching when the
cumulative CPU exceeds CAP (completed set = contiguous batch prefix). seedfile: optional JSON list of seeds (BANK replay)."""
import json, pickle, sys, time
import multiprocessing as mp
import w29
F = w29.F
BANKS = None
def job(a):
    global BANKS
    partner, s = a
    kw = {}
    if partner == "BANK":
        if BANKS is None:
            BANKS = pickle.load(open(F.HERE / "banks.pkl", "rb"))
        kw = dict(bank=BANKS["BASE"], pool=BANKS["POOL"])
    t0 = time.process_time()
    res, G, gf = w29.run3("BASE", 9_998_000 + s, "FIELD", partner, stop="xk163", rec=True, **kw)
    res["s"] = s
    res["cpu_s"] = round(time.process_time() - t0, 2)
    gen = None
    if res["B"] >= 27:
        gen = {"s": s, "partner": partner, "founder": gf.hex(),
               "genomes": [[g.hex(), e[0], e[1], e[2]] for g, e in G.items()]}
    res["n_genomes"] = len(G)
    return res, gen
if __name__ == "__main__":
    tag, partner, cap, s0, s1 = sys.argv[1], sys.argv[2], float(sys.argv[3]) * 60, int(sys.argv[4]), int(sys.argv[5])
    seeds = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else list(range(s0, s1))
    t0 = time.time(); cpu = 0.0; done = 0
    with mp.Pool(5) as p, open(w29.HERE / ("runs_%s.jsonl" % tag), "a") as fh, \
            open(w29.HERE / ("genomes_%s.jsonl" % tag), "a") as gh:
        for b in range(0, len(seeds), 50):
            if cpu > cap:
                print("CAP reached before batch", b, flush=True); break
            for res, gen in p.map(job, [(partner, s) for s in seeds[b:b + 50]], chunksize=1):
                fh.write(json.dumps(res) + "\n"); cpu += res["cpu_s"]; done += 1
                if gen: gh.write(json.dumps(gen) + "\n")
                if res["B"] >= 27:
                    print("COND", res["s"], res["stop"], res["epochs"], "B", res["B"], "Bxk", res["Bxk"], "maxA", res["maxA"], "cpu", res["cpu_s"], flush=True)
            fh.flush(); gh.flush()
            print("batch", b, "last_seed", seeds[min(b + 49, len(seeds) - 1)], "cpu_tot %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
    print("DONE", tag, "n", done, "cpu_s %.0f wall %.0f" % (cpu, time.time() - t0), flush=True)
