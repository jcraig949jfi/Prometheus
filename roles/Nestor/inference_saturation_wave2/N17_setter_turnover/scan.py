"""N17: why are 7ae3 positions 30/34/49 essential (W2-3 K1 E~0.67 from only 3 replacement values) yet lost
in 26-27/27 C-CORE runaways? Full 256-value substitution scan at each position, conversion rate of the
variant against random partners, both sides, ZERO and RAND contexts, copy errors off. Positions 23 and 52
(SELF / LDIR first bytes, retained 27/27) are controls. Static single interactions only."""
import json, random, sys, time, pathlib
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-3_no_vocabulary"))
import common as C

NP = 40
POS = [23, 30, 34, 49, 52]


def work(p):
    r = C.runner_for_spec(C.run_ds.DONOR)
    x = C.run_ds.donor_genome()
    n = r.L
    rng = random.Random("N17-%d" % 0)
    panel = [(C.rand_genome(rng, n), C.rand_ctx(rng), C.rand_ctx(rng)) for _ in range(NP)]
    out = {}
    for v in range(256):
        g = bytearray(x); g[p] = v; g = bytes(g)
        row = {}
        for cm in ("ZERO", "RAND"):
            for side in (0, 1):
                c = 0
                for y, sx, sy in panel:
                    if cm == "ZERO":
                        sx = sy = C.ZERO
                    c += C.outcome(r, g, y, side, sx, sy, 0.0, rng)["conv"]
                row["%s_s%d" % (cm, side)] = c / NP
        out[v] = row
    return p, out


if __name__ == "__main__":
    t0 = time.time()
    with mp.Pool(5) as pool:
        res = dict(pool.map(work, POS))
    x = C.run_ds.donor_genome()
    summ = {}
    for p, out in res.items():
        wt = out[x[p]]
        s = {"wt_byte": "%02x" % x[p], "wt": wt}
        for k in wt:
            vals = [out[v][k] for v in range(256) if v != x[p]]
            s[k] = {"n_ge_wt": sum(1 for q in vals if q >= wt[k] - 1e-9),
                    "n_gt_wt+0.1": sum(1 for q in vals if q > wt[k] + 0.1),
                    "n_dead(<0.1wt)": sum(1 for q in vals if q < 0.1 * max(wt[k], 1e-9)),
                    "best": max((out[v][k], "%02x" % v) for v in range(256))}
        summ[p] = s
    json.dump({"summary": summ, "raw": res, "cpu_wall_s": round(time.time() - t0, 1)}, open(HERE / "scan.json", "w"), indent=1)
    print(json.dumps(summ, indent=1)); print("wall", round(time.time() - t0, 1))
