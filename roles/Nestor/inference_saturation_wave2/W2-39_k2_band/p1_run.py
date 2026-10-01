"""W2-39 driver. python -B p1_run.py s0 n GENO[,GENO...]   seeds 39_390_000 + s (fresh; disjoint from every offset in
inference_saturation_wave2/*.py: nearest used 31_700_000 and 50_100_149). Same seeds across genotypes (paired).
M* = mstar.run (W2-22 FREE BANK CARRY MUT-ON, stop='xk', T=300). Appends runs_GENO.jsonl. 6 processes."""
import json, sys, time
import multiprocessing as mp
import mstar as M
BASE_SEED = 39_390_000


def job(a):
    g, s = a
    t0 = time.process_time()
    res = M.run(g, BASE_SEED + s)
    res.update(geno=g, s=s, cpu_s=round(time.process_time() - t0, 2))
    return res


if __name__ == "__main__":
    s0, n, genos = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3].split(",")
    t0 = time.time(); cpu = {g: 0.0 for g in genos}; cnt = {g: 0 for g in genos}
    fhs = {g: open(M.HERE / ("runs_%s.jsonl" % g.replace("+", "_")), "a") for g in genos}
    jobs = [(g, s) for s in range(s0, s0 + n) for g in genos]
    with mp.Pool(6) as p:
        for res in p.imap_unordered(job, jobs, chunksize=2):
            g = res["geno"]; fhs[g].write(json.dumps(res) + "\n"); fhs[g].flush()
            cpu[g] += res["cpu_s"]; cnt[g] += 1
    for f in fhs.values():
        f.close()
    print("DONE", s0, n, {g: (cnt[g], round(cpu[g], 1)) for g in genos}, "wall %.0f" % (time.time() - t0), flush=True)
