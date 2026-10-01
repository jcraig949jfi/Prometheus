"""Task 1 dynamic: stratified sample of comm-family C1 evolve champions; 32 fresh worlds (16 mirror pairs).
Per champion: acc, sens_act, sens_any (exact assays.evaluate semantics), X = sens_act - max(0, 2acc-1),
common-mode ratio CM = mean|S0_lead + S0_twin| / mean|S0_lead - S0_twin| at scored readouts,
and on the first 8 worlds: distinct S0 values, top-3 value mass, |S0| quantiles, frac S0 == 0."""
from r_common import *
import collections
ck = Clock()
W = {x["cell"]: x for x in json.load(open(OUT / "static_weighted.json"))}
E = [r for r in rows() if r["kind"] == "evolve" and r["env"]["family"] in ("RELAY", "XOR", "MAJ", "FLIP")]
g = np.random.default_rng(0x57325201)
def major(x):
    w = x["w"]
    if w.get("LIN_COMM", 0) >= .5:
        return "LINC"
    if w.get("THRESH", 0) >= .5:
        return "THR"
    return "OTHER"
sample = []
for nz in (0, 16, 64):
    for sig in (False, True):
        pool = [r for r in E if r["physics"]["noise"] == nz and bool(r["labels"]["SIGNAL"]) == sig]
        by = collections.defaultdict(list)
        for r in pool:
            by[major(W[r["cell_id"]])].append(r)
        quota = {"LINC": 8, "THR": 6, "OTHER": 4} if not sig else {"LINC": 8, "THR": 8, "OTHER": 4}
        for k, q in quota.items():
            xs = by[k]
            idx = g.permutation(len(xs))[:q]
            sample += [xs[i] for i in idx]
print("sample", len(sample), flush=True)
res = []
for j, r in enumerate(sample):
    ph, env = spec_of(r); G = genome_of(r)
    s = seeds(H_int(NS, 0xD1, int(r["cell_id"][:8], 16)), 32)
    o = eval_full(ph, G, env, s)
    sc = o["scored"].astype(bool)
    s0 = o["s0"].astype(np.float64)
    lead, twin = s0[0::2], s0[1::2]
    m = sc[0::2]
    cm = float(np.abs(lead + twin)[m].mean() / max(np.abs(lead - twin)[m].mean(), 1e-9))
    v8 = s0[:8][sc[:8]]
    vals, cnts = np.unique(v8, return_counts=True)
    top3 = float(np.sort(cnts)[::-1][:3].sum() / cnts.sum())
    acc = float(o["acc"].mean())
    rec = {"cell": r["cell_id"], "fam": r["env"]["family"], "noise": r["physics"]["noise"],
           "SIG": bool(r["labels"]["SIGNAL"]), "held": r["result"]["held"]["acc"], "static": major(W[r["cell_id"]]),
           "w": W[r["cell_id"]]["w"], "acc": acc, "sens_act": o["sens_act"], "sens_any": o["sens_any"],
           "X": o["sens_act"] - max(0.0, 2 * acc - 1), "bonus": 0.10 * max(o["sens_act"], 0),
           "CM": cm, "n_distinct8": int(len(vals)), "top3_8": top3,
           "absS0_q": np.quantile(np.abs(v8), [.1, .5, .9]).tolist(), "frac0_8": float((v8 == 0).mean())}
    res.append(rec)
    print(j, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in rec.items() if k not in ("w", "absS0_q")}, flush=True)
    if j % 10 == 0:
        save("dyn.json", {"rows": res, "clock": ck.done()})
save("dyn.json", {"rows": res, "clock": ck.done()})
print(ck.done())
